"""
CP-MVP2-03 — LLM reasoning boundary.

Per the frozen specification (docs/CP-MVP2-03-SPECIFICATION-v1.0.md, secs.
4/15/16): "RAG supplies the evidence. LLM performs the reasoning.
Deterministic code decides whether the output compliant." Concretely that
means every `LLMClient` implementation here MUST:
  - receive only the governed `requirement_context` dict that
    testcases.generate already built from the MVP2 Knowledge Base/RAG
    layer (never raw file access, never independent scraping);
  - return narrative/reasoning fields only (title, preconditions,
    test_steps, expected_result, priority) — never a testcase_id,
    requirement_ids, or source_attribution. Those are assembled and
    verified by deterministic code in testcases/generate.py and
    testcases/validate.py, which is the final governance authority.

Three implementations are provided:
  - OpenAILLMClient: a real backend. Reuses the `openai` package that is
    already part of this project's environment (see `pip list`) and the
    standard OPENAI_API_KEY / CP_MVP2_03_LLM_MODEL environment-variable
    convention. It fails fast with LLMUnavailableError when the key is not
    configured — it never silently degrades to fabricated output.
  - ClaudeLLMClient: a real backend using the user's already-authenticated
    Claude Code / Claude Pro subscription via the locally installed
    `claude` CLI in non-interactive print mode — see its own docstring
    below and docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md for the
    approved architecture. This is NOT the Anthropic REST API and does
    NOT use ANTHROPIC_API_KEY.
  - StubLLMClient: a deterministic, offline stand-in used by the test
    suite (and by anyone running this pipeline without LLM credentials
    configured). It performs a fixed, disclosed mechanical transformation
    of the governed evidence it is given — it never invents a scenario
    that the evidence passed to it does not justify. generation_metadata
    always records which backend produced a given testcase so evidence
    is never confused between the two.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class LLMUnavailableError(RuntimeError):
    """Raised when a real LLM call is required but the environment is not
    configured for it (e.g. missing OPENAI_API_KEY). This is a governance
    signal, not a bug: callers must surface the limitation rather than
    fabricate a successful generation."""


class LLMOutputError(RuntimeError):
    """Raised when a real LLM response cannot be parsed into the expected
    structured candidate format. Deterministic code must never silently
    accept malformed model output."""


class ClaudeProviderError(RuntimeError):
    """Raised for every ClaudeLLMClient failure mode: CLI not found,
    ANTHROPIC_API_KEY billing-safety guard tripped, non-zero exit,
    timeout, or an unparsable/unexpected response envelope. Deterministic
    code must never convert one of these into a fabricated testcase."""


class LLMClient(ABC):
    """Reasoning-only interface. See module docstring for the governance
    boundary this class exists to enforce."""

    #: Identifier recorded in generation_metadata so evidence never
    #: confuses a real model call with the deterministic stub.
    model_name: str = "unknown"

    @abstractmethod
    def propose_testcases(
        self, requirement_context: Dict, scenario_types: List[str]
    ) -> List[Dict]:
        """Given governed requirement_context (see
        testcases.generate._requirement_context for its exact shape) and
        the list of scenario types the caller has authorized, return a
        list of raw candidate dicts, each with only:
            {"scenario_type", "title", "preconditions", "test_steps",
             "expected_result", "priority"}
        A candidate whose scenario_type is not justified by the evidence
        in requirement_context must simply be omitted — never fabricated.
        An empty list is a valid, expected response, not an error.
        """


class OpenAILLMClient(LLMClient):
    """Real LLM backend, built on the `openai` package already present in
    this project's environment. No API key is hard-coded anywhere in this
    repository: it is read from OPENAI_API_KEY at construction time, and
    construction fails fast (LLMUnavailableError) if that variable is
    unset, rather than silently returning fabricated testcases.

    Required environment variables:
      OPENAI_API_KEY          - required. No default; never committed.
      CP_MVP2_03_LLM_MODEL    - optional. Defaults to "gpt-4o-mini".
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, model: Optional[str] = None) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMUnavailableError(
                "OPENAI_API_KEY is not set. Real CP-MVP2-03 LLM generation "
                "requires this environment variable. Use StubLLMClient for "
                "offline/deterministic runs, or set OPENAI_API_KEY to "
                "enable live generation."
            )
        import openai  # local import: only required when this backend is used

        self._client = openai.OpenAI(api_key=api_key)
        self.model = model or os.environ.get("CP_MVP2_03_LLM_MODEL", self.DEFAULT_MODEL)
        self.model_name = f"openai:{self.model}"

    def propose_testcases(self, requirement_context: Dict, scenario_types: List[str]) -> List[Dict]:
        import json

        system_prompt = (
            "You are a governed test-case reasoning assistant for the "
            "Agentic QE MVP2 project (CP-MVP2-03). You are given ONLY the "
            "governed requirement evidence retrieved from the approved "
            "MVP2 Knowledge Base — you MUST NOT use outside knowledge of "
            "the application, invent business rules, or invent scenarios "
            "not justified by the evidence provided. For each scenario "
            "type in the requested list that the evidence genuinely "
            "justifies, propose exactly one candidate test case. If the "
            "evidence does not justify a requested scenario type, omit it "
            "— do not force a scenario to appear. Respond with ONLY a "
            "JSON array (no prose, no markdown fences). Each array "
            "element must be an object with exactly these keys: "
            "scenario_type (one of POSITIVE, ALTERNATE, EXCEPTIONAL), "
            "title, preconditions (array of strings), test_steps (array "
            "of strings), expected_result (string), priority (one of "
            "HIGH, MEDIUM, LOW). Do not include any other keys."
        )
        user_prompt = json.dumps(
            {
                "requirement_id": requirement_context["requirement_id"],
                "requirement_text": requirement_context["requirement_text"],
                "approval_status": requirement_context["approval_status"],
                "evidence": requirement_context["evidence"],
                "requested_scenario_types": scenario_types,
            },
            ensure_ascii=False,
        )
        raw = self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = raw.choices[0].message.content or ""
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMOutputError(f"CP-MVP2-03: model output was not valid JSON: {exc}") from exc
        if not isinstance(parsed, list):
            raise LLMOutputError("CP-MVP2-03: model output JSON was not a list of candidates")
        return parsed


class ClaudeLLMClient(LLMClient):
    """Real LLM backend using the user's authenticated Claude Code /
    Claude Pro subscription, via the locally installed `claude` CLI in
    non-interactive print mode — this is NOT the Anthropic REST API and
    NOT a second, independent LLM integration; it is the officially
    supported subscription-authenticated invocation path documented in
    docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md.

    Authentication (billing safety): this class relies entirely on the
    already-authenticated local Claude Code session. It never reads,
    sets, requires, prints, or persists ANTHROPIC_API_KEY. Per the
    approved decision doc sec. 11/7, if ANTHROPIC_API_KEY IS present in
    the environment, this class does not attempt to "ignore" it — the
    `claude` CLI's own documented precedence rules (API key overrides
    subscription auth) are outside this class's control, so there is no
    way to *deterministically* guarantee the call would still be
    subscription-billed. Construction therefore fails fast with
    ClaudeProviderError instead, per the decision doc's explicitly
    allowed "fail clearly and report the condition" option.

    Invocation: `claude -p <prompt> --append-system-prompt <system>
    --output-format json --restricted [--model <model>]`, executed via
    `subprocess.run` with an argument LIST — never `shell=True`, never
    string concatenation — so no requirement text or generated prompt
    content can be interpreted as shell syntax regardless of quotes,
    metacharacters, or Unicode content. `--restricted` is Claude Code's
    own documented flag for removing built-in code-running tools (Bash,
    PowerShell, REPL) and WebFetch, so this call cannot read or modify
    repository files — it is used purely as a reasoning/text-generation
    call, never as an agentic coding session. An explicit, configurable
    timeout (CP_MVP2_03_CLAUDE_TIMEOUT_SECONDS, default 120s) is always
    applied; stdout and stderr are captured separately, and a non-zero
    exit code is always treated as a failure, never as a response to
    parse.

    Response envelope: `--output-format json` (Claude Code's documented
    non-interactive print-mode contract) returns a single JSON object
    with an `is_error` flag and a `result` string (the model's final
    text). This class parses that envelope, checks `is_error`, then
    parses `result` itself as the JSON array of candidate testcases the
    system prompt requested — the same contract OpenAILLMClient's
    response follows. IMPORTANT / DISCLOSED LIMITATION: this envelope
    shape has been implemented from Claude Code's documented print-mode
    output contract, not from a real invocation — a live Claude call is
    explicitly out of scope for the task that added this class (see
    docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md secs. 21/29; the live
    smoke test is a separate, later task). Any envelope mismatch raises
    ClaudeProviderError; it is never silently reinterpreted as success.
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
                "approved CP-MVP2-03 Claude provider decision (billing "
                "safety), ClaudeLLMClient never silently proceeds when this "
                "variable could override the intended subscription-"
                "authenticated path — unset it to use the Claude Pro "
                "subscription via this client, or use OpenAILLMClient if "
                "API-key billing is genuinely intended."
            )

        self._executable = executable or os.environ.get("CP_MVP2_03_CLAUDE_EXECUTABLE", "claude")
        if shutil.which(self._executable) is None:
            raise ClaudeProviderError(
                f"Claude CLI executable '{self._executable}' was not found on PATH. "
                "ClaudeLLMClient requires a locally installed, authenticated Claude "
                "Code CLI (subscription auth); it does not fall back to an API key."
            )

        self.model = model or os.environ.get("CP_MVP2_03_CLAUDE_MODEL") or None
        self.timeout_seconds = timeout_seconds or float(
            os.environ.get("CP_MVP2_03_CLAUDE_TIMEOUT_SECONDS", self.DEFAULT_TIMEOUT_SECONDS)
        )
        self.model_name = f"claude-cli:{self.model or 'default'}"

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a governed test-case reasoning assistant for the "
            "Agentic QE MVP2 project (CP-MVP2-03). You are given ONLY the "
            "governed requirement evidence retrieved from the approved "
            "MVP2 Knowledge Base — you MUST NOT use outside knowledge of "
            "the application, invent business rules, or invent scenarios "
            "not justified by the evidence provided, and you MUST NOT use "
            "any tool. For each scenario type in the requested list that "
            "the evidence genuinely justifies, propose exactly one "
            "candidate test case. If the evidence does not justify a "
            "requested scenario type, omit it — do not force a scenario "
            "to appear. Respond with ONLY a JSON array as your entire "
            "final answer (no prose, no markdown fences). Each array "
            "element must be an object with exactly these keys: "
            "scenario_type (one of POSITIVE, ALTERNATE, EXCEPTIONAL), "
            "title, preconditions (array of strings), test_steps (array "
            "of strings), expected_result (string), priority (one of "
            "HIGH, MEDIUM, LOW). Do not include any other keys."
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

    def propose_testcases(self, requirement_context: Dict, scenario_types: List[str]) -> List[Dict]:
        user_prompt = json.dumps(
            {
                "requirement_id": requirement_context["requirement_id"],
                "requirement_text": requirement_context["requirement_text"],
                "approval_status": requirement_context["approval_status"],
                "evidence": requirement_context["evidence"],
                "requested_scenario_types": scenario_types,
            },
            ensure_ascii=False,
        )
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
                f"for requirement {requirement_context.get('requirement_id')!r}."
            ) from exc
        except OSError as exc:
            raise ClaudeProviderError(f"Failed to start the Claude CLI process: {exc}") from exc

        if completed.returncode != 0:
            stderr_excerpt = (completed.stderr or "")[:2000]
            raise ClaudeProviderError(
                f"Claude CLI exited with non-zero status {completed.returncode} "
                f"for requirement {requirement_context.get('requirement_id')!r}. "
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


class StubLLMClient(LLMClient):
    """Deterministic, offline reasoning stand-in. See module docstring.

    Rules (fixed, disclosed, never varying run-to-run for the same input):
      - POSITIVE: always proposed directly from the requirement text
        itself (the requirement statement IS the positive expected
        behavior) — proposed whenever POSITIVE is requested.
      - ALTERNATE: proposed only when requirement_context["evidence"]
        contains an APPROVED business_rule chunk (deterministically
        gathered by testcases.generate from the governed KB) describing
        an alternate handling path.
      - EXCEPTIONAL: proposed only when requirement_context["evidence"]
        contains an APPROVED negative_case chunk gathered from the same
        journey as the requirement (again, gathered deterministically by
        testcases.generate, never invented here).
      A requested scenario type with no matching evidence in the context
      simply produces no candidate for that type.
    """

    model_name = "stub-deterministic-v1"

    def propose_testcases(self, requirement_context: Dict, scenario_types: List[str]) -> List[Dict]:
        candidates: List[Dict] = []
        req_id = requirement_context["requirement_id"]
        req_text = requirement_context["requirement_text"]
        evidence = requirement_context.get("evidence", [])

        if "POSITIVE" in scenario_types:
            candidates.append(
                {
                    "scenario_type": "POSITIVE",
                    "title": f"Verify {req_id}: primary approved behavior",
                    "preconditions": [f"Approved requirement {req_id} is in effect"],
                    "test_steps": [
                        "Perform the action described by the approved requirement.",
                        "Observe the resulting system behavior.",
                    ],
                    "expected_result": req_text,
                    "priority": "MEDIUM",
                }
            )

        if "ALTERNATE" in scenario_types:
            business_rules = [
                e for e in evidence
                if e["content_type"] == "business_rule" and e["approval_status"] == "APPROVED_BASELINED_V1_0"
            ]
            if business_rules:
                br = business_rules[0]
                candidates.append(
                    {
                        "scenario_type": "ALTERNATE",
                        "title": f"Verify {req_id}: alternate handling per {br['chunk_id']}",
                        "preconditions": [f"Approved requirement {req_id} is in effect"],
                        "test_steps": [
                            "Drive the alternate path described by the approved business rule.",
                            "Observe the resulting system behavior.",
                        ],
                        "expected_result": br["text"],
                        "priority": "MEDIUM",
                    }
                )

        if "EXCEPTIONAL" in scenario_types:
            negative_cases = [
                e for e in evidence
                if e["content_type"] == "negative_case" and e["approval_status"] == "APPROVED_BASELINED_V1_0"
            ]
            if negative_cases:
                neg = negative_cases[0]
                candidates.append(
                    {
                        "scenario_type": "EXCEPTIONAL",
                        "title": f"Verify {req_id}: exceptional/negative path per {neg['chunk_id']}",
                        "preconditions": [f"Approved requirement {req_id} is in effect"],
                        "test_steps": [
                            "Drive the exceptional/negative condition described by the approved negative case.",
                            "Observe the resulting system behavior.",
                        ],
                        "expected_result": neg["text"],
                        "priority": "HIGH",
                    }
                )

        return candidates
