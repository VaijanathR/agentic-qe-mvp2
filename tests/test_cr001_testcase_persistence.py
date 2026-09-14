"""
CP-MVP2-CR-001 Batch 1 — testcase persistence (testcases/persist.py) and
Requirement<->Testcase traceability (traceability/req_testcase.py).

Uses the real, unmodified CP-MVP2-03 generate/validate pipeline
(StubLLMClient, per the project's established offline-test convention)
so these tests exercise real governance output, not hand-built fixtures
alone.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

import testcases.persist as tc_persist
from knowledge.lib.retrieval import KnowledgeBase
from llm.client import StubLLMClient
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus
from testcases.validate import govern_batch
from traceability.req_testcase import build_req_testcase_traceability


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


@pytest.fixture(scope="module")
def stub():
    return StubLLMClient()


@pytest.fixture(scope="module")
def governed(kb, stub):
    result = generate_for_requirement(kb, "REQ-REG-01", stub, ["POSITIVE"])
    return govern_batch(result.testcases, kb)


def test_persist_accepted_testcase_roundtrips(tmp_path, monkeypatch, governed):
    monkeypatch.setattr(tc_persist, "BASE_DIR", tmp_path)
    accepted = [g for g in governed if g.governance_status == GovernanceStatus.ACCEPTED]
    assert accepted, "StubLLMClient must produce at least one ACCEPTED testcase for REQ-REG-01"
    g = accepted[0]

    result = tc_persist.persist_governed_testcase(g, generator="stub-deterministic-v1", batch_id="B1")
    assert result["reused"] is False

    loaded = tc_persist.load_persisted_testcase(g.testcase.testcase_id)
    assert loaded == g.to_dict()
    assert loaded["testcase_id"] == g.testcase.testcase_id
    assert loaded["requirement_ids"] == ["REQ-REG-01"]
    assert loaded["source_attribution"]


def test_regenerating_the_same_testcase_is_idempotent(tmp_path, monkeypatch, governed):
    monkeypatch.setattr(tc_persist, "BASE_DIR", tmp_path)
    g = [gg for gg in governed if gg.governance_status == GovernanceStatus.ACCEPTED][0]
    first = tc_persist.persist_governed_testcase(g, generator="stub-deterministic-v1", batch_id="B1")
    second = tc_persist.persist_governed_testcase(g, generator="stub-deterministic-v1", batch_id="B2")
    assert first["version"] == second["version"]
    assert second["reused"] is True


def test_persisted_testcase_loadable_in_a_genuinely_fresh_process(tmp_path, monkeypatch, governed):
    """Not a claim about theory: this test actually spawns a NEW Python
    process (no shared memory with the pytest process, no import-time
    module cache) and has it load the artifact strictly from disk."""
    monkeypatch.setattr(tc_persist, "BASE_DIR", tmp_path)
    g = [gg for gg in governed if gg.governance_status == GovernanceStatus.ACCEPTED][0]
    tc_persist.persist_governed_testcase(g, generator="stub-deterministic-v1", batch_id="B1")

    script = (
        "import sys; sys.path.insert(0, %r);"
        "from persistence.envelope import load_latest; from pathlib import Path;"
        "d = load_latest(Path(%r), %r);"
        "print(d['testcase_id'])"
    ) % (str(tc_persist.REPO_ROOT), str(tmp_path), g.testcase.testcase_id)

    completed = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == g.testcase.testcase_id


def test_rejected_testcase_is_also_persisted_as_real_evidence(tmp_path, monkeypatch, kb, stub):
    """A REJECTED/QUARANTINED testcase is real evidence too -- persist.py
    does not silently drop non-ACCEPTED governance outcomes."""
    monkeypatch.setattr(tc_persist, "BASE_DIR", tmp_path)
    result = generate_for_requirement(kb, "REQ-DOES-NOT-EXIST", stub, ["POSITIVE"])
    assert result.testcases == []  # no candidate at all -- nothing to persist here, confirms the unsupported path


def test_req_testcase_traceability_reports_coverage_and_bidirectional_maps(kb, governed):
    payload = build_req_testcase_traceability(governed, kb, applicable_requirement_ids={"REQ-REG-01"})
    assert payload["coverage"]["total_applicable_requirements"] == 1
    assert "REQ-REG-01" in payload["requirement_to_testcases"]
    for tcid in payload["requirement_to_testcases"]["REQ-REG-01"]:
        assert "REQ-REG-01" in payload["testcase_to_requirements"][tcid]
    assert payload["orphan_or_invalid_references"] == []


def test_req_testcase_traceability_flags_unknown_requirement_id_as_orphan(kb):
    from testcases.schema import Testcase
    from testcases.validate import govern_batch as govern

    bogus = Testcase(
        testcase_id="TC-BOGUS-01",
        title="t",
        requirement_ids=["REQ-DOES-NOT-EXIST"],
        scenario_type="POSITIVE",
        preconditions=[],
        test_steps=["step"],
        expected_result="result",
    )
    governed_bogus = govern([bogus], kb)
    payload = build_req_testcase_traceability(governed_bogus, kb, applicable_requirement_ids=set())
    assert len(payload["orphan_or_invalid_references"]) == 1
    assert payload["orphan_or_invalid_references"][0]["testcase_id"] == "TC-BOGUS-01"
