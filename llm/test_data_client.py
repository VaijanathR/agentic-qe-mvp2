"""
CP-MVP2-04 — LLM test-data reasoning boundary.

**Design decision, disclosed:** `llm/client.py` is formally frozen as
part of the CP-MVP2-03 checkpoint (see
docs/CP-MVP2-03-FINAL-FREEZE-CHECKPOINT.md sec. 8, which explicitly
lists "Claude provider adapter (llm/client.py: ClaudeLLMClient,
ClaudeProviderError, ...)" as frozen). `LLMClient.propose_testcases()`
is the only abstract method on that frozen interface, and its
implementations hard-code a testcase-shaped system prompt
(scenario_type/title/preconditions/test_steps/expected_result/priority)
— it cannot be reused for a genuinely different reasoning contract
(propose field VALUES for a fixed, deterministically-supplied field
list) without either modifying the frozen file or repurposing a
wrong-shaped call, both of which this project's governance forbids.

This module therefore defines a **new, parallel** small interface for
the CP-MVP2-04 reasoning step, in a **new** file — `llm/client.py`
itself is never imported for modification, only `ClaudeProviderError`
is reused (imported, not redefined) so both checkpoints' real backends
raise the same exception taxonomy. The real backend here
(`ClaudeTestDataClient`) reuses the *exact same* Claude Pro
subscription/provider mechanism as `ClaudeLLMClient` — the local
`claude` CLI, `--restricted` mode, an argument-list subprocess call
(`shell=False`), an explicit timeout, and the same billing-safety
`ANTHROPIC_API_KEY` guard — it does not introduce the Anthropic REST
API, does not require an API key, and installs no new SDK.

Per the frozen CP-MVP2-04 specification (sec. 11): the LLM here may
propose only **field values** for the fields it is told about — never
`data_set_id`, `testcase_id`, `requirement_ids`, `source_attribution`,
`validation_status`, `uniqueness_requirement`, `boundary_classification`,
or `value_type`. All of those are assembled/confirmed deterministically
by `testdata/generate.py` and `testdata/validate.py`, from the
deterministic constraint profile in `testdata/constraints.py` — never
trusted from the model.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from llm.client import ClaudeProviderError  # reused, not redefined; llm/client.py itself is not modified


class TestDataLLMClient(ABC):
    """Reasoning-only interface for CP-MVP2-04. See module docstring for
    why this is not `llm.client.LLMClient` (that ABC's only method is
    testcase-shaped and inapplicable here)."""

    model_name: str = "unknown"

    @abstractmethod
    def propose_field_values(self, dataset_context: Dict) -> List[Dict]:
        """Given a governed `dataset_context` (see
        testdata.generate.requirement_context for its exact shape),
        return a list of raw candidate dicts, each:
            {"data_category", "purpose", "validity",
             "fields": [{"field_name", "field_value"}, ...]}
        Only field VALUES are trusted from this return value — nothing
        else. A candidate for a data_category the evidence does not
        justify must simply be omitted, never fabricated. An empty list
        is a valid, expected response, not an error.
        """


class ClaudeTestDataClient(TestDataLLMClient):
    """Real backend: the same authenticated Claude Code / Claude Pro
    subscription `ClaudeLLMClient` uses, via the same `claude -p
    --restricted --output-format json` mechanism, constructed
    independently here because the reasoning contract (field-value
    proposal, not testcase proposal) is genuinely different — not
    because the provider or its safety properties differ.
    """

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
                "same billing-safety rule applied to ClaudeLLMClient, "
                "ClaudeTestDataClient never silently proceeds when this "
                "variable could override the intended subscription-"
                "authenticated path."
            )

        self._executable = executable or os.environ.get("CP_MVP2_04_CLAUDE_EXECUTABLE", "claude")
        if shutil.which(self._executable) is None:
            raise ClaudeProviderError(
                f"Claude CLI executable '{self._executable}' was not found on PATH. "
                "ClaudeTestDataClient requires a locally installed, authenticated Claude "
                "Code CLI (subscription auth); it does not fall back to an API key."
            )

        self.model = model or os.environ.get("CP_MVP2_04_CLAUDE_MODEL") or None
        self.timeout_seconds = timeout_seconds or float(
            os.environ.get("CP_MVP2_04_CLAUDE_TIMEOUT_SECONDS", self.DEFAULT_TIMEOUT_SECONDS)
        )
        self.model_name = f"claude-cli:{self.model or 'default'}"

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a governed test-data reasoning assistant for the "
            "Agentic QE MVP2 project (CP-MVP2-04). You are given ONLY a "
            "fixed list of field names/types/mandatory-ness that a "
            "deterministic constraint table has already extracted from "
            "the approved MVP2 requirements — you MUST NOT invent a "
            "field not listed, invent a business rule, invent a boundary "
            "or allowed-value not supplied to you, or use any tool. For "
            "each requested data category that the supplied evidence "
            "justifies, propose exactly one dataset: concrete field "
            "VALUES only, for exactly the fields listed. If a documented "
            "example value is supplied for a field, prefer it verbatim "
            "over inventing your own. If a category is requested but "
            "not justified by the supplied evidence, omit it — do not "
            "force it. Respond with ONLY a JSON array as your entire "
            "final answer (no prose, no markdown fences). Each array "
            "element must be an object with exactly these keys: "
            "data_category, purpose (short string), validity (VALID or "
            "INVALID), fields (array of objects, each with exactly "
            "field_name and field_value). Do not include any other keys."
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

    def propose_field_values(self, dataset_context: Dict) -> List[Dict]:
        user_prompt = json.dumps(dataset_context, ensure_ascii=False)
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
                f"for testcase {dataset_context.get('testcase_id')!r}."
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


class StubTestDataClient(TestDataLLMClient):
    """Deterministic, offline stand-in used by the automated test suite.
    Performs a fixed, disclosed mechanical transformation: for each
    requested category, if the dataset_context's constraint profile
    supplies a documented case for it, use that documented case's exact
    values; for POSITIVE/ALTERNATE, synthesize clearly-synthetic
    placeholder values satisfying every mandatory field. It never
    invents a category the supplied context does not justify."""

    model_name = "stub-deterministic-v1"

    def propose_field_values(self, dataset_context: Dict) -> List[Dict]:
        candidates: List[Dict] = []
        requirement_id = dataset_context["requirement_id"]
        requested_categories = dataset_context["requested_categories"]
        field_specs = dataset_context["field_specs"]
        documented_exceptional = dataset_context.get("documented_exceptional", {})
        documented_boundary = dataset_context.get("documented_boundary")
        documented_alternate = dataset_context.get("documented_alternate")

        def _positive_fields() -> List[Dict]:
            values: Dict[str, object] = {}
            # First pass: independent fields.
            for spec in field_specs:
                if spec.get("dependency_reference"):
                    continue
                if spec["value_type"] == "ENUM" and spec.get("allowed_values"):
                    value = spec["allowed_values"][0]
                elif spec["value_type"] == "EMAIL":
                    value = f"synthetic.{requirement_id.lower()}@example.test"
                elif spec["value_type"] == "INTEGER":
                    value = 1
                else:
                    value = f"Synthetic-{spec['field_name']}"
                values[spec["field_name"]] = value
            # Second pass: dependent fields copy their referenced field's
            # value exactly, so e.g. confirm_password == password by
            # construction for a POSITIVE dataset — never independently
            # guessed into an accidental mismatch.
            for spec in field_specs:
                dep = spec.get("dependency_reference")
                if dep:
                    values[spec["field_name"]] = values.get(dep, f"Synthetic-{spec['field_name']}")
            return [{"field_name": name, "field_value": val} for name, val in values.items()]

        if "POSITIVE" in requested_categories:
            candidates.append(
                {
                    "data_category": "POSITIVE",
                    "purpose": f"Valid data satisfying all mandatory fields for {requirement_id}",
                    "validity": "VALID",
                    "fields": _positive_fields(),
                }
            )

        if "ALTERNATE" in requested_categories and documented_alternate:
            candidates.append(
                {
                    "data_category": "ALTERNATE",
                    "purpose": documented_alternate.get("evidence", ""),
                    "validity": "VALID",
                    "fields": _positive_fields(),
                }
            )

        if "EXCEPTIONAL" in requested_categories:
            for name, spec in documented_exceptional.items():
                base = {f["field_name"]: f["field_value"] for f in _positive_fields()}
                for blank_field in spec.get("blank_fields", []):
                    base[blank_field] = ""
                for field_name, value in spec.get("override_fields", {}).items():
                    if value == "__DELIBERATELY_DIFFERENT_FROM_PASSWORD__":
                        value = base.get("password", "Synthetic-password") + "-DIFFERENT"
                    base[field_name] = value
                candidates.append(
                    {
                        "data_category": "EXCEPTIONAL",
                        "purpose": spec.get("evidence", name),
                        "validity": "INVALID",
                        "fields": [{"field_name": k, "field_value": v} for k, v in base.items()],
                    }
                )

        if "INVALID" in requested_categories and "all_fields_blank" in documented_exceptional:
            spec = documented_exceptional["all_fields_blank"]
            base = {f["field_name"]: f["field_value"] for f in _positive_fields()}
            for blank_field in spec.get("blank_fields", []):
                base[blank_field] = ""
            candidates.append(
                {
                    "data_category": "INVALID",
                    "purpose": spec.get("evidence", "all_fields_blank"),
                    "validity": "INVALID",
                    "fields": [{"field_name": k, "field_value": v} for k, v in base.items()],
                }
            )

        if "BOUNDARY" in requested_categories and documented_boundary:
            candidates.append(
                {
                    "data_category": "BOUNDARY",
                    "purpose": documented_boundary.get("evidence", ""),
                    "validity": "VALID",
                    "fields": [
                        {"field_name": documented_boundary["field_name"], "field_value": documented_boundary["field_value"]}
                    ],
                }
            )

        return candidates
