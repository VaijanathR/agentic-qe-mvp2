"""
CP-MVP2-05 — LLM Playwright-step reasoning boundary.

**Design decision, disclosed (mirrors llm/test_data_client.py's own
precedent):** `llm/client.py` is formally frozen (CP-MVP2-03 checkpoint).
Its only abstract method, `propose_testcases()`, is inapplicable here.
This module adds a **new, parallel** interface rather than modifying the
frozen file, reusing `ClaudeProviderError` (imported, not redefined) and
the identical Claude Pro subscription/subprocess-safety mechanism used by
both `ClaudeLLMClient` and `ClaudeTestDataClient`.

Per the frozen CP-MVP2-05 specification (secs. 3/5/6): the LLM here may
propose only the **step structure** — which action_type happens in what
order, and which governed dataset field (if any) each step targets. It
returns NO locator value, NO field value, and NO governance status.
Every locator is looked up deterministically afterward, from real,
evidenced DOM captures (automation/evidence.py) — never proposed by the
model. Every field value comes from the linked CP-MVP2-04 dataset —
never proposed by the model. This is a stricter narrowing of the LLM's
role than CP-MVP2-04's (which at least let the model propose field
*values*): CP-MVP2-05's spec explicitly and repeatedly prohibits locator
fabrication, so the model is not given any surface to fabricate one on.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from llm.client import ClaudeProviderError  # reused, not redefined; llm/client.py itself is not modified


class AutomationLLMClient(ABC):
    """Reasoning-only interface for CP-MVP2-05. See module docstring."""

    model_name: str = "unknown"

    @abstractmethod
    def propose_steps(self, artifact_context: Dict) -> List[Dict]:
        """Given a governed `artifact_context` (testcase_id, test_steps,
        expected_result, available_fields, requirement_id), return a
        list of raw candidate step dicts, each:
            {"action_type", "field_name" (or null),
             "synchronization_strategy" (or null),
             "assertion_condition" (or null, narrative only)}
        No locator, no field value, no governance status. An empty list
        is a valid response (nothing to propose), never an error.
        """


class ClaudeAutomationClient(AutomationLLMClient):
    """Real backend: identical Claude Pro subscription / subprocess
    mechanism as ClaudeLLMClient / ClaudeTestDataClient — a new,
    parallel construction because the reasoning contract (step
    structure only, zero locator/value surface) is genuinely different,
    not because the provider or its safety properties differ."""

    DEFAULT_TIMEOUT_SECONDS = 120.0

    def __init__(
        self,
        executable: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> None:
        if os.environ.get("ANTHROPIC_API_KEY"):
            raise ClaudeProviderError(
                "ANTHROPIC_API_KEY is present in the environment. Per the "
                "same billing-safety rule applied to ClaudeLLMClient/"
                "ClaudeTestDataClient, ClaudeAutomationClient never "
                "silently proceeds when this variable could override the "
                "intended subscription-authenticated path."
            )

        self._executable = executable or os.environ.get("CP_MVP2_05_CLAUDE_EXECUTABLE", "claude")
        if shutil.which(self._executable) is None:
            raise ClaudeProviderError(
                f"Claude CLI executable '{self._executable}' was not found on PATH. "
                "ClaudeAutomationClient requires a locally installed, authenticated "
                "Claude Code CLI (subscription auth); it does not fall back to an API key."
            )

        self.model = model or os.environ.get("CP_MVP2_05_CLAUDE_MODEL") or None
        self.timeout_seconds = timeout_seconds or float(
            os.environ.get("CP_MVP2_05_CLAUDE_TIMEOUT_SECONDS", self.DEFAULT_TIMEOUT_SECONDS)
        )
        self.model_name = f"claude-cli:{self.model or 'default'}"

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a governed Playwright-step-structure reasoning "
            "assistant for the Agentic QE MVP2 project (CP-MVP2-05). You "
            "are given ONLY a testcase's test_steps/expected_result text "
            "and a fixed list of governed data field names already "
            "available for this scenario. You MUST NOT invent a UI "
            "locator, a CSS selector, an XPath, a field value, or any "
            "field name not in the supplied list, and you MUST NOT use "
            "any tool. Propose an ordered list of steps representing "
            "the interaction sequence implied by test_steps. For a step "
            "that fills or selects a value, name the exact field_name "
            "from the supplied list — never a new one. Do not propose a "
            "locator, CSS selector, or XPath for any step; that is "
            "supplied separately by deterministic evidence lookup, not "
            "by you. Respond with ONLY a JSON array as your entire "
            "final answer (no prose, no markdown fences). Each element "
            "must be an object with exactly these keys: action_type "
            "(one of NAVIGATE, FILL, CLICK, SELECT, WAIT, ASSERT), "
            "field_name (string from the supplied list, or null), "
            "synchronization_strategy (one of WAIT_FOR_VISIBLE, "
            "WAIT_FOR_NETWORK_IDLE, NONE), assertion_condition (a short "
            "string describing what to check, or null). Do not include "
            "any other keys."
        )

    def _build_argv(self, user_prompt: str) -> List[str]:
        argv = [
            self._executable,
            "-p", user_prompt,
            "--append-system-prompt", self._system_prompt(),
            "--output-format", "json",
            "--restricted",
        ]
        if self.model:
            argv += ["--model", self.model]
        return argv

    def propose_steps(self, artifact_context: Dict) -> List[Dict]:
        user_prompt = json.dumps(artifact_context, ensure_ascii=False)
        argv = self._build_argv(user_prompt)

        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ClaudeProviderError(
                f"Claude CLI invocation timed out after {self.timeout_seconds}s "
                f"for testcase {artifact_context.get('testcase_id')!r}."
            ) from exc
        except OSError as exc:
            raise ClaudeProviderError(f"Failed to start the Claude CLI process: {exc}") from exc

        if completed.returncode != 0:
            stderr_excerpt = (completed.stderr or "")[:2000]
            raise ClaudeProviderError(
                f"Claude CLI exited with non-zero status {completed.returncode}. "
                f"stderr (truncated to 2000 chars): {stderr_excerpt}"
            )

        stdout = completed.stdout or ""
        if not stdout.strip():
            raise ClaudeProviderError("Claude CLI returned empty stdout despite a zero exit code.")

        try:
            envelope = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise ClaudeProviderError(f"Claude CLI stdout was not valid JSON: {exc}") from exc

        if not isinstance(envelope, dict):
            raise ClaudeProviderError("Claude CLI JSON envelope was not a JSON object.")

        if envelope.get("is_error"):
            raise ClaudeProviderError(
                f"Claude CLI reported is_error=true. result field: {envelope.get('result')!r}"
            )

        result_text = envelope.get("result")
        if not isinstance(result_text, str) or not result_text.strip():
            raise ClaudeProviderError(
                "Claude CLI JSON envelope did not contain a non-empty string 'result' field."
            )

        try:
            candidates = json.loads(result_text)
        except json.JSONDecodeError as exc:
            raise ClaudeProviderError(f"Claude CLI 'result' text was not valid JSON: {exc}") from exc

        if not isinstance(candidates, list):
            raise ClaudeProviderError("Claude CLI 'result' JSON was not a list of candidates.")

        return candidates


class StubAutomationClient(AutomationLLMClient):
    """Deterministic, offline stand-in used by the automated test suite.
    Proposes a fixed, disclosed mechanical step sequence: one NAVIGATE,
    one FILL per available governed field (in the order supplied), then
    one CLICK with no field_name (a page-level action such as
    "submit"/"continue"). It never invents a field beyond
    `available_fields`."""

    model_name = "stub-deterministic-v1"

    def propose_steps(self, artifact_context: Dict) -> List[Dict]:
        steps: List[Dict] = [
            {"action_type": "NAVIGATE", "field_name": None, "synchronization_strategy": "WAIT_FOR_NETWORK_IDLE", "assertion_condition": None}
        ]
        for field_name in artifact_context.get("available_fields", []):
            steps.append(
                {
                    "action_type": "FILL",
                    "field_name": field_name,
                    "synchronization_strategy": "WAIT_FOR_VISIBLE",
                    "assertion_condition": None,
                }
            )
        steps.append(
            {
                "action_type": "CLICK",
                "field_name": None,
                "synchronization_strategy": "WAIT_FOR_NETWORK_IDLE",
                "assertion_condition": artifact_context.get("expected_result"),
            }
        )
        return steps
