"""
CP-MVP2-03 — end-to-end governed pipeline.

Ties together the full flow from the frozen specification (sec. 3):
    APPROVED SRS -> KB/RAG -> RETRIEVED CONTEXT -> LLM ->
    STRUCTURED TESTCASE OUTPUT -> DETERMINISTIC VALIDATORS ->
    COVERAGE/TRACEABILITY/GOVERNANCE -> CP-MVP2-03 RESULT

This module performs no reasoning and no governance decisions itself — it
only sequences testcases.generate (RAG + LLM) and testcases.validate
(deterministic governance), exactly the boundary the specification
requires.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.client import LLMClient
from testcases.generate import generate_for_requirements
from testcases.schema import Testcase
from testcases.validate import build_report


def run_cp_mvp2_03(
    kb: KnowledgeBase,
    llm: LLMClient,
    requirement_ids: Optional[List[str]] = None,
    scenario_types: Optional[List[str]] = None,
) -> Dict:
    """Runs CP-MVP2-03 generation + governance for `requirement_ids`
    (defaults to every APPROVED requirement in the Approved SRS manifest,
    i.e. a full-coverage run) and returns the governed CP-MVP2-03 result:
    generated candidates, per-testcase governance decisions, duplicate
    checks, coverage, and any UNSUPPORTED/NEEDS CLARIFICATION findings.
    """
    applicable_ids = requirement_ids or list(kb.manifests["approved_srs"]["ids"]["requirements"])

    generation_results = generate_for_requirements(kb, applicable_ids, llm, scenario_types)

    all_candidates: List[Testcase] = []
    unsupported_requirements: List[Dict] = []
    for result in generation_results:
        all_candidates.extend(result.testcases)
        if result.unsupported:
            unsupported_requirements.append(result.unsupported)

    report = build_report(all_candidates, kb, applicable_requirement_ids=set(applicable_ids))
    report["unsupported_requirements"] = unsupported_requirements
    report["requirement_ids_processed"] = applicable_ids
    report["generator"] = llm.model_name
    return report
