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

Two implementations are provided:
  - OpenAILLMClient: the real backend. Reuses the `openai` package that is
    already part of this project's environment (see `pip list`) and the
    standard OPENAI_API_KEY / CP_MVP2_03_LLM_MODEL environment-variable
    convention. It fails fast with LLMUnavailableError when the key is not
    configured — it never silently degrades to fabricated output.
  - StubLLMClient: a deterministic, offline stand-in used by the test
    suite (and by anyone running this pipeline without LLM credentials
    configured). It performs a fixed, disclosed mechanical transformation
    of the governed evidence it is given — it never invents a scenario
    that the evidence passed to it does not justify. generation_metadata
    always records which backend produced a given testcase so evidence
    is never confused between the two.
"""
from __future__ import annotations

import os
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
