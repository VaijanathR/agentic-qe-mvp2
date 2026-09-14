"""
Tests for automation/multi_locator/ — the new, additive multi-locator-
candidate package (CP-MVP2-CR-002 proposal; see
docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md for why runtime
fallback-retry is explicitly NOT implemented or tested here — only
generation-time/persistence-time candidate resolution, and real
execution using the single, highest-priority candidate only).

Categories: UNIT (schema/evidence/generate/validate), PERSISTENCE
(roundtrip via the unmodified persistence/envelope.py), BRIDGE
(GovernedMultiLocatorArtifact -> real, standard GovernedPlaywrightArtifact),
INTEGRATION (mocked BrowserExecutor, patched at its real frozen import
site exactly like every other CP-06 test in this project — never a real
browser in this file).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from automation.multi_locator.bridge import build_executable_artifact
from automation.multi_locator.evidence import candidates_for_field, submit_candidates
from automation.multi_locator.generate import build_multi_locator_artifact
from automation.multi_locator.persist import (
    BASE_DIR as ML_BASE_DIR,
    list_persisted_multi_locator_ids,
    load_persisted_multi_locator_artifact,
    persist_governed_multi_locator_artifact,
)
from automation.multi_locator.schema import AutomationHealth, Confidence, MultiLocatorGovernanceStatus
from automation.multi_locator.validate import govern_multi_locator_artifact
from automation.persist import BASE_DIR as AUTOMATION_BASE_DIR
from automation.schema import ActionType, GovernanceStatus as AutoGovStatus
from execution.persisted_lifecycle import execute_persisted_candidate
from execution.schema import OverallStatus, StepResult, StepStatus
from persistence.envelope import load_latest


@pytest.fixture(scope="module")
def real_aco03_payload():
    """The real, previously-persisted, frozen-CP-05-generated automation
    artifact for TC-REQ-ACO-03-01 — read from the real corpus, never
    regenerated. This module's tests exercise real DOM evidence, not a
    synthetic fixture, because this package's whole purpose is resolving
    a real, previously-established ambiguity."""
    payload = load_latest(AUTOMATION_BASE_DIR, "PW-TC-REQ-ACO-03-01-01")
    if payload is None:
        pytest.skip("Real corpus artifact PW-TC-REQ-ACO-03-01-01 not present on disk in this environment")
    return payload


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

def test_submit_candidates_for_req_aco_03_returns_two_priority_ordered_real_candidates():
    candidates = submit_candidates("REQ-ACO-03")
    assert len(candidates) == 2
    assert candidates[0].priority < candidates[1].priority
    assert candidates[0].confidence == Confidence.HIGH
    assert candidates[1].confidence == Confidence.MEDIUM
    assert "billing-buttons-container" in candidates[0].locator
    assert 'onclick="Billing.save()"' in candidates[1].locator
    for c in candidates:
        assert c.evidence_source == "knowledge/historical/discovery_evidence/captures/checkout_00.html"


def test_submit_candidates_for_unrelated_requirement_returns_empty_not_fabricated():
    assert submit_candidates("REQ-DOES-NOT-EXIST") == []


def test_candidates_for_field_wraps_the_frozen_single_lookup_exactly():
    candidates = candidates_for_field("REQ-ACO-03", "first_name")
    assert len(candidates) == 1
    assert candidates[0].locator == "#BillingNewAddress_FirstName"


def test_candidates_for_field_with_no_evidence_returns_empty():
    assert candidates_for_field("REQ-ACO-03", "field_with_no_evidence_anywhere") == []


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def test_build_multi_locator_artifact_resolves_the_real_aco03_ambiguity(real_aco03_payload):
    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-01")
    assert artifact.source_automation_id == "PW-TC-REQ-ACO-03-01-01"
    assert artifact.testcase_id == "TC-REQ-ACO-03-01"
    assert artifact.requirement_ids == ["REQ-ACO-03"]
    submit_step = next(s for s in artifact.step_candidate_sets if s.field_name is None)
    assert len(submit_step.candidates) == 2
    assert submit_step.original_locator_was_evidenced is False  # frozen lookup found this UNSUPPORTED
    fill_step = next(s for s in artifact.step_candidate_sets if s.field_name == "first_name")
    assert fill_step.original_locator_was_evidenced is True
    assert artifact.automation_health == AutomationHealth.YELLOW


def test_source_artifact_is_never_mutated(real_aco03_payload):
    import copy
    before = copy.deepcopy(real_aco03_payload)
    build_multi_locator_artifact(real_aco03_payload, "ML-TEST-02")
    assert real_aco03_payload == before


def test_health_is_red_when_a_load_bearing_step_has_zero_candidates():
    fabricated_payload = {
        "automation_id": "PW-FAKE-01", "testcase_id": "TC-FAKE-01",
        "requirement_ids": ["REQ-DOES-NOT-EXIST"], "test_data_set_id": "TD-FAKE-01",
        "journey_id": None, "scenario_type": "POSITIVE", "browser_intent": "chromium-headless",
        "preconditions": [], "evidence_requirements": [], "failure_handling_metadata": {},
        "source_attribution": [], "validation_status": "UNSUPPORTED_NEEDS_CLARIFICATION",
        "steps": [
            {"step_order": 1, "action_type": ActionType.FILL, "input_mapping": "nonexistent_field",
             "locator": None, "synchronization_strategy": "NONE"},
        ],
        "assertions": [],
    }
    artifact = build_multi_locator_artifact(fabricated_payload, "ML-FAKE-01")
    assert artifact.automation_health == AutomationHealth.RED
    assert artifact.step_candidate_sets[0].candidates == []


def test_health_is_green_when_no_new_resolution_was_needed():
    payload = {
        "automation_id": "PW-GREEN-01", "testcase_id": "TC-GREEN-01",
        "requirement_ids": ["REQ-ACO-03"], "test_data_set_id": "TD-GREEN-01",
        "journey_id": None, "scenario_type": "POSITIVE", "browser_intent": "chromium-headless",
        "preconditions": [], "evidence_requirements": [], "failure_handling_metadata": {},
        "source_attribution": [], "validation_status": "ACCEPTED",
        "steps": [
            {"step_order": 1, "action_type": ActionType.FILL, "input_mapping": "first_name",
             "locator": {"strategy": "STABLE_ATTRIBUTE", "value": "#BillingNewAddress_FirstName",
                         "evidence_source": "x", "status": "EVIDENCED"},
             "synchronization_strategy": "WAIT_FOR_VISIBLE"},
        ],
        "assertions": [],
    }
    artifact = build_multi_locator_artifact(payload, "ML-GREEN-01")
    assert artifact.automation_health == AutomationHealth.GREEN


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

def test_governance_accepted_when_every_step_resolved(real_aco03_payload):
    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-03")
    governed = govern_multi_locator_artifact(artifact)
    assert governed.governance_status == MultiLocatorGovernanceStatus.ACCEPTED


def test_governance_unsupported_when_a_step_has_no_candidates():
    from automation.multi_locator.schema import MultiLocatorArtifact, StepLocatorCandidateSet
    artifact = MultiLocatorArtifact(
        ml_automation_id="ML-X", source_automation_id="PW-X", testcase_id="TC-X",
        requirement_ids=["REQ-X"], test_data_set_id="TD-X",
        step_candidate_sets=[StepLocatorCandidateSet(step_order=1, field_name="f", candidates=[])],
    )
    governed = govern_multi_locator_artifact(artifact)
    assert governed.governance_status == MultiLocatorGovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION
    assert any("UNRESOLVED_STEPS" in r for r in governed.reasons)


# ---------------------------------------------------------------------------
# Persistence (reuses the unmodified persistence/envelope.py)
# ---------------------------------------------------------------------------

def test_persist_and_reload_roundtrip(tmp_path, monkeypatch, real_aco03_payload):
    import automation.multi_locator.persist as mlp
    monkeypatch.setattr(mlp, "BASE_DIR", tmp_path)

    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-04")
    governed = govern_multi_locator_artifact(artifact)
    result = mlp.persist_governed_multi_locator_artifact(governed, generator="test")
    assert result["reused"] is False

    loaded = mlp.load_persisted_multi_locator_artifact("ML-TEST-04")
    assert loaded["validation_status"] == "ACCEPTED"
    assert loaded["source_automation_id"] == "PW-TC-REQ-ACO-03-01-01"
    assert mlp.list_persisted_multi_locator_ids() == ["ML-TEST-04"]


# ---------------------------------------------------------------------------
# Bridge — real execution uses only the primary candidate, no fallback
# ---------------------------------------------------------------------------

def test_bridge_produces_a_standard_artifact_with_only_primary_locators(real_aco03_payload):
    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-05")
    governed = govern_multi_locator_artifact(artifact)
    executable = build_executable_artifact(governed, real_aco03_payload)

    assert executable.governance_status == AutoGovStatus.ACCEPTED
    assert executable.artifact.automation_id == "ML-TEST-05"
    submit_step = next(s for s in executable.artifact.steps if s.action_type == ActionType.CLICK)
    assert submit_step.locator.value == "#billing-buttons-container .new-address-next-step-button"
    # traceability preserved
    assert executable.artifact.testcase_id == "TC-REQ-ACO-03-01"
    assert executable.artifact.requirement_ids == ["REQ-ACO-03"]
    # Preserved from whichever real, persisted version load_latest()
    # actually returned -- NOT hardcoded, because PW-TC-REQ-ACO-03-01-01
    # is itself subject to the pre-existing AUTOMATION_ID_COLLISION_ADVISORY
    # (multiple persisted versions with different test_data_set_id values
    # share this automation_id); this test must not assume which one.
    assert executable.artifact.test_data_set_id == real_aco03_payload["test_data_set_id"]


def test_bridge_never_mutates_the_source_payload(real_aco03_payload):
    import copy
    before = copy.deepcopy(real_aco03_payload)
    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-06")
    governed = govern_multi_locator_artifact(artifact)
    build_executable_artifact(governed, real_aco03_payload)
    assert real_aco03_payload == before


# ---------------------------------------------------------------------------
# Integration — mocked BrowserExecutor, patched at its real frozen import
# site (execution.pipeline.BrowserExecutor), never a real browser here.
# ---------------------------------------------------------------------------

def test_resolved_artifact_reaches_the_browser_layer_via_the_unmodified_cp06_pipeline(
    tmp_path, monkeypatch, real_aco03_payload
):
    import automation.persist as ap
    import execution.persist as exec_persist
    monkeypatch.setattr(ap, "BASE_DIR", tmp_path / "automation")
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path / "runs")

    import execution.persisted_lifecycle as plc
    monkeypatch.setattr(plc, "AUTOMATION_BASE_DIR", tmp_path / "automation")

    artifact = build_multi_locator_artifact(real_aco03_payload, "ML-TEST-07")
    governed = govern_multi_locator_artifact(artifact)
    assert governed.governance_status == MultiLocatorGovernanceStatus.ACCEPTED
    executable = build_executable_artifact(governed, real_aco03_payload)
    ap.persist_governed_artifact(executable, generator="test", batch_id="TEST")

    mock_executor = MagicMock()
    mock_executor.run_steps.return_value = (
        [StepResult(step_order=1, action_type=ActionType.NAVIGATE, target_locator_reference=None, status=StepStatus.PASS)],
        "chromium/999.0",
    )
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_executor) as mock_cls:
        out = execute_persisted_candidate("ML-TEST-07", "https://demowebshop.tricentis.com/", execution_id="T-ML")
    mock_cls.assert_called_once()
    assert out["result"].automation_id == "ML-TEST-07"
    assert out["result"].testcase_id == "TC-REQ-ACO-03-01"


def test_unresolved_artifact_never_reaches_the_browser_layer(tmp_path, monkeypatch):
    import automation.persist as ap
    monkeypatch.setattr(ap, "BASE_DIR", tmp_path / "automation")
    import execution.persisted_lifecycle as plc
    monkeypatch.setattr(plc, "AUTOMATION_BASE_DIR", tmp_path / "automation")

    from automation.multi_locator.schema import MultiLocatorArtifact, StepLocatorCandidateSet
    from automation.multi_locator.schema import GovernedMultiLocatorArtifact
    artifact = MultiLocatorArtifact(
        ml_automation_id="ML-UNRESOLVED-01", source_automation_id="PW-X", testcase_id="TC-X",
        requirement_ids=["REQ-X"], test_data_set_id="TD-X",
        step_candidate_sets=[StepLocatorCandidateSet(step_order=1, field_name="f", candidates=[])],
    )
    governed = govern_multi_locator_artifact(artifact)
    payload_stub = {
        "steps": [{"step_order": 1, "action_type": ActionType.FILL, "input_mapping": "f", "locator": None, "synchronization_strategy": "NONE"}],
        "assertions": [], "scenario_type": "POSITIVE", "browser_intent": "chromium-headless",
        "preconditions": [], "evidence_requirements": [], "failure_handling_metadata": {}, "journey_id": None,
    }
    executable = build_executable_artifact(governed, payload_stub)
    assert executable.governance_status == AutoGovStatus.UNSUPPORTED_NEEDS_CLARIFICATION
    ap.persist_governed_artifact(executable, generator="test", batch_id="TEST")

    with patch("execution.pipeline.BrowserExecutor") as mock_cls:
        out = execute_persisted_candidate("ML-UNRESOLVED-01", "https://demowebshop.tricentis.com/", execution_id="T-UNRESOLVED")
    mock_cls.assert_not_called()
    assert out["result"].overall_status == OverallStatus.NOT_EXECUTED
