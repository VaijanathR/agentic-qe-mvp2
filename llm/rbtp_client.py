"""
CP-MVP2-CR-001 Batch 1 — LLM RBTP (Risk-Based Test Prioritization)
narrative-elaboration boundary.

**Design decision, disclosed (mirrors llm/test_data_client.py and
llm/automation_client.py's own precedent):** `llm/client.py` is formally
frozen (CP-MVP2-03 checkpoint). This module adds a **new, parallel**
interface rather than modifying the frozen file, reusing
`ClaudeProviderError` (imported, not redefined) and the identical Claude
Pro subscription/subprocess-safety mechanism used by every prior
checkpoint's LLM client.

This is the narrowest LLM surface in the project so far. Per CR-001 sec.
6/20 ("Do NOT fabricate risk values... the LLM must never silently
override deterministic governance"), the model here may propose **only**
a short narrative elaboration string appended, for human readability, to
a rationale that deterministic code (`rbtp/generate.py`) has already
fully computed. It never receives a surface to propose a risk-factor
value, a priority, or an execution recommendation — those three things
are computed before this client is ever called, and are never revised
by anything this client returns.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, Optional

from llm.client import ClaudeProviderError  # reused, not redefined; llm/client.py itself is not modified


class RBTPLLMClient(ABC):
    """Narrative-elaboration-only interface. See module docstring."""

    model_name: str = "unknown"

    @abstractmethod
    def propose_rationale_elaboration(self, rbtp_context: Dict) -> Optional[str]:
        """Given `rbtp_context` (testcase_id, requirement_ids, the
        already-final `deterministic_rationale` string), return an
        optional short narrative string elaborating on it for a human
        reader, or None. Must not attempt to change any factor value,
        priority, or execution recommendation — the caller ignores any
        such attempt by construction (this method's return type carries
        no such field)."""


class ClaudeRBTPClient(RBTPLLMClient):
    """Real backend: identical Claude Pro subscription/subprocess
    mechanism as every other checkpoint's Claude client."""

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
                "same billing-safety rule applied to every prior Claude "
                "client in this project, ClaudeRBTPClient never silently "
                "proceeds when this variable could override the intended "
                "subscription-authenticated path."
            )

        self._executable = executable or os.environ.get("CP_MVP2_CR001_CLAUDE_EXECUTABLE", "claude")
        if shutil.which(self._executable) is None:
            raise ClaudeProviderError(
                f"Claude CLI executable '{self._executable}' was not found on PATH. "
                "ClaudeRBTPClient requires a locally installed, authenticated "
                "Claude Code CLI (subscription auth); it does not fall back to an API key."
            )

        self.model = model or os.environ.get("CP_MVP2_CR001_CLAUDE_MODEL") or None
        self.timeout_seconds = timeout_seconds or float(
            os.environ.get("CP_MVP2_CR001_CLAUDE_TIMEOUT_SECONDS", self.DEFAULT_TIMEOUT_SECONDS)
        )
        self.model_name = f"claude-cli:{self.model or 'default'}"

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a governed RBTP (Risk-Based Test Prioritization) "
            "narrative-elaboration assistant for the Agentic QE MVP2 "
            "project. You are given a testcase ID, its requirement IDs, "
            "and a deterministic risk rationale that has ALREADY been "
            "fully computed by non-LLM code. Your ONLY job is to write "
            "one short, plain-language sentence (no more than 40 words) "
            "that restates this rationale for a human reader. You MUST "
            "NOT propose, change, or imply a different risk factor "
            "value, priority, or execution recommendation than what the "
            "deterministic rationale already states — any such attempt "
            "is discarded by the caller regardless of what you write. "
            "You MUST NOT use any tool. Respond with ONLY a JSON object "
            "as your entire final answer (no prose, no markdown fences) "
            "with exactly one key: narrative (a string)."
        )

    def _build_argv(self, user_prompt: str) -> list:
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

    def propose_rationale_elaboration(self, rbtp_context: Dict) -> Optional[str]:
        user_prompt = json.dumps(rbtp_context, ensure_ascii=False)
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
                f"for testcase {rbtp_context.get('testcase_id')!r}."
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
            parsed = json.loads(result_text)
        except json.JSONDecodeError as exc:
            raise ClaudeProviderError(f"Claude CLI 'result' text was not valid JSON: {exc}") from exc

        if not isinstance(parsed, dict) or "narrative" not in parsed:
            raise ClaudeProviderError("Claude CLI 'result' JSON did not contain a 'narrative' key.")

        narrative = parsed["narrative"]
        return str(narrative) if narrative else None


class StubRBTPClient(RBTPLLMClient):
    """Deterministic, offline stand-in used by the automated test suite.
    Returns a fixed, disclosed mechanical sentence — never invents a
    risk factor or priority."""

    model_name = "stub-deterministic-v1"

    def propose_rationale_elaboration(self, rbtp_context: Dict) -> Optional[str]:
        return f"Stub narrative for {rbtp_context.get('testcase_id')}: see deterministic rationale for the authoritative factors."
