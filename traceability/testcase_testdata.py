"""
CP-MVP2-CR-001 Batch 1 — persisted Testcase <-> Test Data traceability.

Reshapes/persists what CP-MVP2-04's own frozen governance already
decided; adds no new governance rule. "Which testcases consume this
test data" / "which data does this testcase need" are answered directly
from this artifact without rerunning CP-04.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from testdata.schema import GovernedTestDataSet
from persistence.envelope import REPO_ROOT, persist_artifact

BASE_DIR = REPO_ROOT / "traceability" / "testcase_to_testdata"


def build_testcase_testdata_traceability(
    governed_datasets: List[GovernedTestDataSet],
    accepted_testcase_ids: Iterable[str],
) -> Dict:
    accepted_ids = set(accepted_testcase_ids)
    tc_to_data: Dict[str, List[str]] = defaultdict(list)
    data_to_tc: Dict[str, str] = {}
    orphan_datasets: List[Dict] = []

    for g in governed_datasets:
        tcid = g.dataset.testcase_id
        data_to_tc[g.dataset.data_set_id] = tcid
        tc_to_data[tcid].append(g.dataset.data_set_id)
        if tcid not in accepted_ids:
            orphan_datasets.append({
                "data_set_id": g.dataset.data_set_id,
                "testcase_id": tcid,
                "reason": "TESTCASE_NOT_ACCEPTED_OR_UNKNOWN",
            })

    missing_testdata = sorted(tcid for tcid in accepted_ids if tcid not in tc_to_data)

    return {
        "testcase_to_testdata": {tcid: sorted(ids) for tcid, ids in tc_to_data.items()},
        "testdata_to_testcase": data_to_tc,
        "orphan_testdata": orphan_datasets,
        "testcases_missing_testdata": missing_testdata,
        "dataset_status": {g.dataset.data_set_id: g.governance_status for g in governed_datasets},
    }


def persist_testcase_testdata_traceability(payload: Dict, generator: str, batch_id: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=batch_id,
        payload=payload,
        generator=generator,
        provenance={"checkpoint": "CP-MVP2-04", "kind": "testcase_to_testdata_traceability"},
    )
