"""
CP-MVP2-04 — end-to-end governed pipeline.

Ties together testdata.generate (RAG + constraint profile + LLM
field-value reasoning) and testdata.validate (deterministic governance)
into one CP-MVP2-04 result, exactly the boundary the frozen
specification requires. Performs no reasoning and no governance
decisions itself.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.test_data_client import TestDataLLMClient
from testcases.schema import GovernanceStatus, GovernedTestcase
from testdata.generate import generate_for_testcases
from testdata.schema import TestDataSet
from testdata.validate import build_report


def run_cp_mvp2_04(
    kb: KnowledgeBase,
    llm: TestDataLLMClient,
    cp03_governed_testcases: List[GovernedTestcase],
    requested_categories: Optional[List[str]] = None,
) -> Dict:
    """Runs CP-MVP2-04 generation + governance for every ACCEPTED
    testcase in `cp03_governed_testcases` (non-ACCEPTED testcases are
    not eligible anchors — spec sec. 3/12 — and are excluded from the
    applicable/coverage universe entirely, not merely uncovered)."""
    accepted = [tc for tc in cp03_governed_testcases if tc.governance_status == GovernanceStatus.ACCEPTED]
    accepted_by_id = {tc.testcase.testcase_id: tc for tc in accepted}

    generation_results = generate_for_testcases(kb, accepted, llm, requested_categories)

    all_datasets: List[TestDataSet] = []
    unsupported_testcases: List[Dict] = []
    for result in generation_results:
        all_datasets.extend(result.datasets)
        if result.unsupported:
            unsupported_testcases.append(result.unsupported)

    report = build_report(all_datasets, accepted_by_id, applicable_testcase_ids=set(accepted_by_id))
    report["unsupported_testcases"] = unsupported_testcases
    report["testcase_ids_processed"] = sorted(accepted_by_id)
    report["generator"] = llm.model_name
    return report
