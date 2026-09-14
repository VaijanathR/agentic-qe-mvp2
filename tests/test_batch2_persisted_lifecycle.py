"""
CP-MVP2 Batch 2 — tests for execution/persisted_lifecycle.py, the new
integration surface between Batch 1's persisted artifacts and the
frozen, unmodified CP-MVP2-06 execution pipeline.

All fixtures here are explicitly-labeled test fixtures persisted to an
isolated tmp_path directory (never the real, authoritative
testcases/generated//testdata/generated//automation/generated/ trees) —
per the Batch 2 instruction's own rule against overwriting authoritative
persisted artifacts for test purposes.

Categories, mirroring the project-wide convention (see
tests/test_cp_mvp2_06_execution.py's own docstring): UNIT (deserialize/
resolve stage logic), INTEGRATION (mocked BrowserExecutor -- patched at
its real import site, execution.pipeline.BrowserExecutor, exactly as
Batch 1's own CP-06 tests do), TRACEABILITY, TIMESTAMPING, and
BACKWARD-COMPATIBILITY. No test in this file performs a real browser
launch.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import execution.persisted_lifecycle as plc
from automation.schema import (
    ActionType,
    Assertion,
    AssertionType,
    GovernanceStatus as AutoGovStatus,
    GovernedPlaywrightArtifact,
    PlaywrightArtifact,
    PlaywrightStep,
)
from execution.schema import OverallStatus, StepResult, StepStatus
from persistence.envelope import persist_artifact
from testcases.schema import GovernanceStatus as TCGovStatus, GovernedTestcase, Priority, ScenarioType, Testcase
from testdata.schema import DataCategory, DataGovernanceStatus, DataValidity, GovernedTestDataSet, TestDataField, TestDataSet, ValueType


@pytest.fixture(autouse=True)
def isolate_persistence(tmp_path, monkeypatch):
    """Every test in this file operates on an isolated tmp_path tree --
    never the real, authoritative Batch 1 persisted artifacts."""
    monkeypatch.setattr(plc, "AUTOMATION_BASE_DIR", tmp_path / "automation")
    monkeypatch.setattr(plc, "TESTCASE_BASE_DIR", tmp_path / "testcases")
    monkeypatch.setattr(plc, "TESTDATA_BASE_DIR", tmp_path / "testdata")
    return tmp_path


def _persist_testcase(base_dir, governance_status=TCGovStatus.ACCEPTED, **overrides):
    base = dict(
        testcase_id="TC-X-01", title="t", requirement_ids=["REQ-REG-01"],
        scenario_type=ScenarioType.POSITIVE, preconditions=[], test_steps=["s"],
        expected_result="r", priority=Priority.HIGH,
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    tc = Testcase(**base)
    gtc = GovernedTestcase(tc, governance_status, [])
    persist_artifact(base_dir, tc.testcase_id, gtc.to_dict(), generator="test-fixture")
    return gtc


def _persist_dataset(base_dir, governance_status=DataGovernanceStatus.ACCEPTED, **overrides):
    base = dict(
        data_set_id="TD-X-01", testcase_id="TC-X-01", requirement_ids=["REQ-REG-01"],
        data_category=DataCategory.POSITIVE, purpose="p", validity=DataValidity.VALID,
        fields=[TestDataField("email", "a@b.com", ValueType.EMAIL)],
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    ds = TestDataSet(**base)
    gds = GovernedTestDataSet(ds, governance_status, [])
    persist_artifact(base_dir, ds.data_set_id, gds.to_dict(), generator="test-fixture")
    return gds


def _persist_automation(base_dir, governance_status=AutoGovStatus.ACCEPTED, **overrides):
    base = dict(
        automation_id="PW-X-01", testcase_id="TC-X-01", requirement_ids=["REQ-REG-01"],
        test_data_set_id="TD-X-01", journey_id="J-01", scenario_type=ScenarioType.POSITIVE,
        browser_intent="chromium-headless", preconditions=[],
        steps=[PlaywrightStep(1, ActionType.NAVIGATE)],
        assertions=[Assertion(AssertionType.BUSINESS_REQUIRED, "r", "testcase:TC-X-01.expected_result", True)],
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    artifact = PlaywrightArtifact(**base)
    gpa = GovernedPlaywrightArtifact(artifact, governance_status, [])
    persist_artifact(base_dir, artifact.automation_id, gpa.to_dict(), generator="test-fixture")
    return gpa


def _full_valid_fixture(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR)


# ---------------------------------------------------------------------------
# UNIT: persistence loading / resolution stages
# ---------------------------------------------------------------------------

def test_valid_persisted_automation_resolves_ready(tmp_path):
    _full_valid_fixture(tmp_path)
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is True
    assert all(s.get("passed", True) for s in r["stages"].values())
    assert r["governed_artifact"].artifact.testcase_id == "TC-X-01"
    assert r["governed_dataset"].dataset.data_set_id == "TD-X-01"


def test_missing_automation_not_found(tmp_path):
    r = plc.resolve_persisted_execution_candidate("PW-DOES-NOT-EXIST")
    assert r["ready"] is False
    assert r["early_result"].overall_status == OverallStatus.NOT_EXECUTED
    assert "PERSISTED_AUTOMATION_NOT_FOUND" in r["early_result"].notes[0]


def test_malformed_automation_missing_required_keys(tmp_path):
    persist_artifact(plc.AUTOMATION_BASE_DIR, "PW-BAD-01", {"automation_id": "PW-BAD-01"}, generator="test-fixture")
    r = plc.resolve_persisted_execution_candidate("PW-BAD-01")
    assert r["ready"] is False
    assert r["early_result"].overall_status == OverallStatus.NOT_EXECUTED
    assert "MALFORMED_PERSISTED_ENVELOPE" in r["early_result"].notes[0]
    assert r["stages"]["envelope_validated"]["missing_keys"]


def test_invalid_envelope_deserialization_failure(tmp_path):
    payload = {
        "automation_id": "PW-BAD-02", "testcase_id": "TC-X-01", "requirement_ids": ["REQ-REG-01"],
        "test_data_set_id": "TD-X-01", "validation_status": "ACCEPTED",
        "steps": [{"step_order": 1}],  # missing required "action_type"
        "assertions": [],
    }
    persist_artifact(plc.AUTOMATION_BASE_DIR, "PW-BAD-02", payload, generator="test-fixture")
    r = plc.resolve_persisted_execution_candidate("PW-BAD-02")
    assert r["ready"] is False
    assert "AUTOMATION_SCHEMA_DESERIALIZATION_FAILURE" in r["early_result"].notes[0]


def test_automation_id_collision_detected_without_disambiguation_blocks(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-02")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-01")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-02")  # same automation_id, different dataset -> collision

    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is False
    assert r["stages"]["automation_id_validated"]["automation_id_collision_advisory"] is True
    assert set(r["stages"]["automation_id_validated"]["distinct_test_data_set_ids"]) == {"TD-X-01", "TD-X-02"}
    assert r["early_result"].overall_status == OverallStatus.BLOCKED
    assert "AUTOMATION_ID_COLLISION_DETECTED" in r["early_result"].notes[0]


def test_automation_id_collision_resolved_with_expected_test_data_set_id(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-02")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-01")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-02")

    r = plc.resolve_persisted_execution_candidate("PW-X-01", expected_test_data_set_id="TD-X-02")
    assert r["ready"] is True
    assert r["governed_dataset"].dataset.data_set_id == "TD-X-02"
    assert r["governed_artifact"].artifact.test_data_set_id == "TD-X-02"


def test_collision_never_invents_a_winner_for_an_unresolvable_expectation(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-02")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-01")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-02")

    r = plc.resolve_persisted_execution_candidate("PW-X-01", expected_test_data_set_id="TD-DOES-NOT-EXIST")
    assert r["ready"] is False
    assert "AUTOMATION_ID_COLLISION_UNRESOLVED" in r["early_result"].notes[0]


def test_missing_testcase_not_found(tmp_path):
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR)
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is False
    assert "PERSISTED_TESTCASE_NOT_FOUND" in r["early_result"].notes[0]
    assert r["early_result"].testcase_id == "TC-X-01"


def test_missing_test_data_not_found(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR)
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is False
    assert "PERSISTED_TEST_DATA_NOT_FOUND" in r["early_result"].notes[0]


def test_invalid_requirement_reference_mismatch(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR, requirement_ids=["REQ-REG-01"])
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, requirement_ids=["REQ-DIFFERENT-01"])
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is False
    assert "REQUIREMENT_ID_TRACEABILITY_MISMATCH" in r["early_result"].notes[0]


def test_broken_traceability_dataset_testcase_mismatch(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR, testcase_id="TC-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, testcase_id="TC-DIFFERENT-01")
    _persist_automation(plc.AUTOMATION_BASE_DIR, testcase_id="TC-X-01")
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is False
    assert "TESTDATA_TESTCASE_TRACEABILITY_MISMATCH" in r["early_result"].notes[0]


def test_unsupported_automation_still_resolves_structurally(tmp_path):
    """Resolution (steps 1-10) is orthogonal to CP-06 eligibility (step
    11, owned entirely by the frozen execution.validate module) --
    an UNSUPPORTED_NEEDS_CLARIFICATION artifact still resolves+loads
    correctly; only run_cp_mvp2_06 itself later refuses to execute it."""
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is True
    assert r["governed_artifact"].governance_status == AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION


def test_possible_duplicate_automation_resolves_ready(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.POSSIBLE_DUPLICATE)
    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    assert r["ready"] is True
    assert r["governed_artifact"].governance_status == AutoGovStatus.POSSIBLE_DUPLICATE


# ---------------------------------------------------------------------------
# INTEGRATION: execute_persisted_candidate against the real, frozen
# execution.pipeline.run_cp_mvp2_06 with a MOCKED BrowserExecutor
# ---------------------------------------------------------------------------

def _mock_step_results():
    return [StepResult(step_order=1, action_type=ActionType.NAVIGATE, target_locator_reference=None, status=StepStatus.PASS)]


def test_ineligible_automation_never_reaches_the_browser_layer(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    with patch("execution.pipeline.BrowserExecutor") as mock_cls:
        out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T1")
    mock_cls.assert_not_called()
    assert out["result"].overall_status == OverallStatus.NOT_EXECUTED


def test_eligible_accepted_automation_reaches_the_browser_layer(tmp_path):
    # REQ-WISH-01 is deliberately used here instead of the fixtures'
    # default REQ-REG-01: REQ-REG-01 is state-mutating (DATA-OQ-01,
    # execution.validate.STATE_MUTATING_REQUIREMENT_IDS) and the frozen
    # CP-06 gate correctly BLOCKs it before the browser layer -- this
    # test wants to verify the browser layer specifically, so it uses a
    # non-state-mutating requirement to isolate that concern.
    _persist_testcase(plc.TESTCASE_BASE_DIR, requirement_ids=["REQ-WISH-01"])
    _persist_dataset(plc.TESTDATA_BASE_DIR, requirement_ids=["REQ-WISH-01"])
    _persist_automation(plc.AUTOMATION_BASE_DIR, requirement_ids=["REQ-WISH-01"], governance_status=AutoGovStatus.ACCEPTED)

    mock_executor = MagicMock()
    mock_executor.run_steps.return_value = (_mock_step_results(), "chromium/999.0")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_executor) as mock_cls:
        out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T2")
    mock_cls.assert_called_once()
    assert out["result"].overall_status == OverallStatus.PASS
    assert out["result"].browser == "chromium/999.0"


def test_eligible_possible_duplicate_automation_reaches_the_browser_layer(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR, requirement_ids=["REQ-WISH-01"])
    _persist_dataset(plc.TESTDATA_BASE_DIR, requirement_ids=["REQ-WISH-01"])
    _persist_automation(plc.AUTOMATION_BASE_DIR, requirement_ids=["REQ-WISH-01"], governance_status=AutoGovStatus.POSSIBLE_DUPLICATE)

    mock_executor = MagicMock()
    mock_executor.run_steps.return_value = (_mock_step_results(), "chromium/999.0")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_executor) as mock_cls:
        out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T3")
    mock_cls.assert_called_once()
    assert out["result"].overall_status == OverallStatus.PASS


def test_collision_blocked_execution_never_reaches_the_browser_layer(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-02")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-01")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-02")

    with patch("execution.pipeline.BrowserExecutor") as mock_cls:
        out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T4")
    mock_cls.assert_not_called()
    assert out["result"].overall_status == OverallStatus.BLOCKED


def test_execute_persisted_candidate_persists_execution_result(tmp_path, monkeypatch):
    import execution.persist as exec_persist
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path / "runs")

    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T5")
    persisted_dir = (tmp_path / "runs").glob("*/*/*/T5")
    assert any(True for _ in persisted_dir)


def test_persisted_to_execution_handoff_field_fidelity(tmp_path):
    original = _persist_automation(plc.AUTOMATION_BASE_DIR)
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)

    r = plc.resolve_persisted_execution_candidate("PW-X-01")
    loaded = r["governed_artifact"]
    assert loaded.artifact.to_dict() == original.artifact.to_dict()
    assert loaded.governance_status == original.governance_status


# ---------------------------------------------------------------------------
# TRACEABILITY
# ---------------------------------------------------------------------------

def test_execution_result_carries_full_requirement_traceability_chain(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)
    out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T6")
    result = out["result"]
    assert result.automation_id == "PW-X-01"
    assert result.testcase_id == "TC-X-01"
    assert result.requirement_ids == ["REQ-REG-01"]


def test_execution_result_carries_test_data_chain(tmp_path):
    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)
    out = plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T7")
    assert out["result"].test_data_set_id == "TD-X-01"


# ---------------------------------------------------------------------------
# TIMESTAMPING
# ---------------------------------------------------------------------------

def test_execution_timestamp_is_real_current_time_not_fabricated(tmp_path, monkeypatch):
    import datetime
    import execution.persist as exec_persist
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path / "runs")

    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    before = datetime.datetime.now(datetime.timezone.utc)
    plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T8")
    after = datetime.datetime.now(datetime.timezone.utc)

    expected_dir = tmp_path / "runs" / f"{before.year:04d}" / f"{before.month:02d}" / f"{before.day:02d}" / "T8"
    assert expected_dir.exists()
    assert before <= after  # sanity: real wall-clock time elapsed, nothing pre-computed


# ---------------------------------------------------------------------------
# BACKWARD COMPATIBILITY
# ---------------------------------------------------------------------------

def test_persisted_lifecycle_never_touches_frozen_evidence_default(tmp_path):
    import execution.evidence as frozen_evidence
    original_runs_dir = frozen_evidence.RUNS_DIR

    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    plc.execute_persisted_candidate("PW-X-01", "https://demowebshop.tricentis.com/", execution_id="T9")
    assert frozen_evidence.RUNS_DIR is original_runs_dir


# ---------------------------------------------------------------------------
# BATCH-LEVEL RUNNER
# ---------------------------------------------------------------------------

def test_batch_runner_examines_every_variant_of_a_colliding_id_separately(tmp_path, monkeypatch):
    import execution.persist as exec_persist
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path / "runs")

    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-01")
    _persist_dataset(plc.TESTDATA_BASE_DIR, data_set_id="TD-X-02")
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-01", governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)
    _persist_automation(plc.AUTOMATION_BASE_DIR, test_data_set_id="TD-X-02", governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    out = plc.run_batch2_persisted_execution("https://demowebshop.tricentis.com/", batch_id="BATCH2-TEST")
    assert out["candidates_examined"] == 2  # both distinct variants attempted separately, neither silently dropped
    assert len(out["automation_ids_examined"]) == 1  # one colliding automation_id
    # The batch runner never leaves a collision unresolved (it always
    # supplies an explicit expected_test_data_set_id per variant), so
    # BLOCKED-due-to-collision never fires here -- each variant reaches
    # the frozen CP-06 eligibility gate on its own merits and is
    # correctly NOT_EXECUTED (both fixtures are UNSUPPORTED_NEEDS_CLARIFICATION).
    assert out["summary"]["counts_by_status"][OverallStatus.BLOCKED] == 0
    assert out["summary"]["counts_by_status"][OverallStatus.NOT_EXECUTED] == 2


def test_batch_runner_reports_honestly_when_nothing_is_eligible(tmp_path, monkeypatch):
    import execution.persist as exec_persist
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path / "runs")

    _persist_testcase(plc.TESTCASE_BASE_DIR)
    _persist_dataset(plc.TESTDATA_BASE_DIR)
    _persist_automation(plc.AUTOMATION_BASE_DIR, governance_status=AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION)

    out = plc.run_batch2_persisted_execution("https://demowebshop.tricentis.com/", batch_id="BATCH2-TEST2")
    assert out["summary"]["counts_by_status"][OverallStatus.PASS] == 0
    assert out["by_governance_status"] == {AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION: 1}
