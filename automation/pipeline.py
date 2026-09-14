"""
CP-MVP2-05 — end-to-end governed pipeline.

Ties together automation.generate (RAG + evidence lookup + LLM step
reasoning) and automation.validate (deterministic governance) into one
CP-MVP2-05 result, scoped strictly to CP-MVP2-03's own ACCEPTED
testcases paired with their CP-MVP2-04 ACCEPTED/POSSIBLE_DUPLICATE
datasets. Performs no reasoning and no governance decisions itself.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.automation_client import AutomationLLMClient
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase
from testdata.schema import DataGovernanceStatus, GovernedTestDataSet
from automation.generate import ELIGIBLE_DATASET_STATUSES, generate_for_testcases
from automation.schema import PlaywrightArtifact
from automation.validate import build_report


def run_cp_mvp2_05(
    kb: KnowledgeBase,
    llm: AutomationLLMClient,
    cp03_governed_testcases: List[GovernedTestcase],
    cp04_governed_datasets: List[GovernedTestDataSet],
) -> Dict:
    """Runs CP-MVP2-05 generation + governance for every ACCEPTED
    testcase paired with each of its eligible (ACCEPTED/
    POSSIBLE_DUPLICATE) CP-MVP2-04 datasets. A testcase with no eligible
    dataset is simply not paired -- it will not appear in the applicable
    universe's numerator, and generate_for_testcase's own checks are the
    second line of defense if a pairing were attempted anyway."""
    accepted_testcases = [tc for tc in cp03_governed_testcases if tc.governance_status == TestcaseGovernanceStatus.ACCEPTED]
    accepted_testcases_by_id = {tc.testcase.testcase_id: tc for tc in accepted_testcases}

    eligible_datasets = [ds for ds in cp04_governed_datasets if ds.governance_status in ELIGIBLE_DATASET_STATUSES]
    eligible_datasets_by_id = {ds.dataset.data_set_id: ds for ds in eligible_datasets}

    pairs = [
        (accepted_testcases_by_id[ds.dataset.testcase_id], ds)
        for ds in eligible_datasets
        if ds.dataset.testcase_id in accepted_testcases_by_id
    ]

    generation_results = generate_for_testcases(kb, pairs, llm)

    all_artifacts: List[PlaywrightArtifact] = []
    unsupported_testcases: List[Dict] = []
    for result in generation_results:
        if result.artifact:
            all_artifacts.append(result.artifact)
        if result.unsupported:
            unsupported_testcases.append(result.unsupported)

    applicable_ids = set(accepted_testcases_by_id)
    report = build_report(all_artifacts, accepted_testcases_by_id, eligible_datasets_by_id, applicable_testcase_ids=applicable_ids)
    report["unsupported_testcases"] = unsupported_testcases
    report["testcase_ids_processed"] = sorted(applicable_ids)
    report["generator"] = llm.model_name
    return report
