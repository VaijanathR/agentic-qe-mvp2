"""
CP-MVP2-CR-001 Batch 1 — test-data persistence (testdata/persist.py) and
Testcase<->Test Data traceability (traceability/testcase_testdata.py).
"""
from __future__ import annotations

import pytest

import testdata.persist as td_persist
from knowledge.lib.retrieval import KnowledgeBase
from llm.client import StubLLMClient
from llm.test_data_client import StubTestDataClient
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.validate import govern_batch as govern_testcases
from testdata.generate import generate_for_testcases
from testdata.schema import DataGovernanceStatus
from testdata.validate import govern_batch as govern_testdata
from traceability.testcase_testdata import build_testcase_testdata_traceability


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


@pytest.fixture(scope="module")
def governed_testcases(kb):
    stub = StubLLMClient()
    result = generate_for_requirement(kb, "REQ-REG-01", stub, ["POSITIVE"])
    return govern_testcases(result.testcases, kb)


@pytest.fixture(scope="module")
def accepted_testcases(governed_testcases):
    return [g for g in governed_testcases if g.governance_status == TestcaseGovernanceStatus.ACCEPTED]


@pytest.fixture(scope="module")
def governed_datasets(kb, accepted_testcases):
    stub_td = StubTestDataClient()
    gen_results = generate_for_testcases(kb, accepted_testcases, stub_td, None)
    all_datasets = [d for r in gen_results for d in r.datasets]
    accepted_by_id = {g.testcase.testcase_id: g for g in accepted_testcases}
    return govern_testdata(all_datasets, accepted_by_id)


def test_persist_accepted_dataset_roundtrips(tmp_path, monkeypatch, governed_datasets):
    monkeypatch.setattr(td_persist, "BASE_DIR", tmp_path)
    accepted = [g for g in governed_datasets if g.governance_status == DataGovernanceStatus.ACCEPTED]
    assert accepted
    g = accepted[0]
    result = td_persist.persist_governed_dataset(g, generator="stub-deterministic-v1", batch_id="B1")
    assert result["reused"] is False
    loaded = td_persist.load_persisted_dataset(g.dataset.data_set_id)
    assert loaded == g.to_dict()
    assert loaded["testcase_id"] == g.dataset.testcase_id


def test_regeneration_is_idempotent(tmp_path, monkeypatch, governed_datasets):
    monkeypatch.setattr(td_persist, "BASE_DIR", tmp_path)
    g = governed_datasets[0]
    first = td_persist.persist_governed_dataset(g, generator="stub-deterministic-v1", batch_id="B1")
    second = td_persist.persist_governed_dataset(g, generator="stub-deterministic-v1", batch_id="B2")
    assert first["version"] == second["version"]
    assert second["reused"] is True


def test_testcase_testdata_traceability_bidirectional(accepted_testcases, governed_datasets):
    accepted_ids = [g.testcase.testcase_id for g in accepted_testcases]
    payload = build_testcase_testdata_traceability(governed_datasets, accepted_ids)
    for tcid in accepted_ids:
        for data_id in payload["testcase_to_testdata"].get(tcid, []):
            assert payload["testdata_to_testcase"][data_id] == tcid


def test_traceability_flags_orphan_dataset_for_unknown_testcase(governed_datasets):
    from testdata.schema import GovernedTestDataSet, TestDataSet

    orphan = GovernedTestDataSet(
        dataset=TestDataSet(
            data_set_id="TD-ORPHAN-01",
            testcase_id="TC-DOES-NOT-EXIST",
            requirement_ids=["REQ-REG-01"],
            data_category="POSITIVE",
            purpose="p",
            validity="VALID",
        ),
        governance_status=DataGovernanceStatus.ACCEPTED,
    )
    payload = build_testcase_testdata_traceability([orphan], accepted_testcase_ids=[])
    assert payload["orphan_testdata"] == [
        {"data_set_id": "TD-ORPHAN-01", "testcase_id": "TC-DOES-NOT-EXIST", "reason": "TESTCASE_NOT_ACCEPTED_OR_UNKNOWN"}
    ]


def test_traceability_flags_testcase_missing_testdata():
    payload = build_testcase_testdata_traceability([], accepted_testcase_ids=["TC-NEEDS-DATA-01"])
    assert payload["testcases_missing_testdata"] == ["TC-NEEDS-DATA-01"]
