"""
Governance negative tests (governing instruction sec. 58): explicitly
verifies the orchestrator blocks or escalates each of the 8 prohibited
actions, deterministically, never silently.
"""
from __future__ import annotations

import pytest

from orchestration import governance
from orchestration.governance import GovernanceState, GovernanceViolation, enforce


# --- 1. Changing Approved SRS to make a test pass ---------------------------

def test_srs_change_is_blocked():
    baseline = governance.snapshot_srs_hash()
    assert baseline is not None
    result = governance.guard_srs_immutable(baseline)
    assert result["passed"] is True
    assert result["governance_state"] == GovernanceState.GREEN

    tampered_result = governance.guard_srs_immutable("deliberately-wrong-hash-simulating-a-real-srs-edit")
    assert tampered_result["passed"] is False
    assert tampered_result["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(tampered_result)


# --- 2. Changing expected result to make a test pass -------------------------

def test_expected_result_mutation_is_blocked():
    ok = governance.guard_no_expected_result_mutation("TC-1", "Order total is 17.00", "Order total is 17.00")
    assert ok["passed"] is True

    tampered = governance.guard_no_expected_result_mutation("TC-1", "Order total is 17.00", "Order total is anything")
    assert tampered["passed"] is False
    assert tampered["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(tampered)


# --- 3. Creating unauthorized permanent SUT state -----------------------------

def test_unauthorized_permanent_state_is_blocked():
    unauthorized = governance.guard_permanent_state_authorization("place a real order", authorized=False, authorization_reference=None)
    assert unauthorized["passed"] is False
    assert unauthorized["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(unauthorized)

    authorized = governance.guard_permanent_state_authorization(
        "place a real order", authorized=True, authorization_reference="Human + Di: Controlled REQ-GCO-03 Post-Freeze Validation"
    )
    assert authorized["passed"] is True
    assert authorized["governance_state"] == GovernanceState.GREEN


# --- 4. Silently implementing CR-002 ------------------------------------------

def test_cr002_remains_unauthorized():
    result = governance.guard_cr002_not_implemented()
    assert result["passed"] is True, (
        "CR-002 must remain OPEN / NOT AUTHORIZED. If this test fails, CR-002's own status "
        "document has changed -- STOP, this is a genuine governance event, not a test bug."
    )
    assert result["governance_state"] == GovernanceState.GREEN


# --- 5. Fabricating evidence ---------------------------------------------------

def test_fabricated_evidence_is_blocked():
    real = governance.guard_evidence_not_fabricated(["requirements/MVP2_SRS_v1.0_APPROVED.md"])
    assert real["passed"] is True

    fabricated = governance.guard_evidence_not_fabricated(["this/path/was/never/written/by/anything.png"])
    assert fabricated["passed"] is False
    assert fabricated["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(fabricated)


# --- 6. Bypassing human approval -----------------------------------------------

def test_bypassing_human_approval_is_blocked():
    bypassed = governance.guard_approval_present(requires_approval=True, approval_record=None)
    assert bypassed["passed"] is False
    assert bypassed["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(bypassed)

    present = governance.guard_approval_present(requires_approval=True, approval_record={"approval_id": "APPR-1"})
    assert present["passed"] is True

    not_required = governance.guard_approval_present(requires_approval=False, approval_record=None)
    assert not_required["passed"] is True


# --- 7. Invalid state transition ------------------------------------------------

def test_invalid_state_transition_is_blocked():
    from orchestration.state import OrchestrationState

    invalid = governance.guard_valid_state_transition(OrchestrationState.RECEIVED, OrchestrationState.FINAL_REPORT)
    assert invalid["passed"] is False
    assert invalid["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(invalid)

    valid = governance.guard_valid_state_transition(OrchestrationState.RECEIVED, OrchestrationState.UNDERSTANDING)
    assert valid["passed"] is True


# --- 8. Using an unapproved performance threshold -------------------------------

def test_unapproved_performance_threshold_is_blocked():
    invented = governance.guard_performance_threshold_approved(threshold_source="AGENT_GUESS", threshold_value=500.0)
    assert invented["passed"] is False
    assert invented["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(invented)

    inconclusive = governance.guard_performance_threshold_approved(threshold_source=None, threshold_value=None)
    assert inconclusive["passed"] is True

    approved = governance.guard_performance_threshold_approved(threshold_source="SRS_APPROVED", threshold_value=500.0)
    assert approved["passed"] is True


def test_classify_governance_decision_mapping_is_total_for_known_values():
    from rca.schema import GovernanceDecision

    assert governance.classify_governance_decision(GovernanceDecision.NO_ACTION_REQUIRED) == GovernanceState.GREEN
    assert governance.classify_governance_decision(GovernanceDecision.ACTION_DEFERRED_TO_HUMAN) == GovernanceState.YELLOW
    assert governance.classify_governance_decision(GovernanceDecision.GOVERNANCE_BLOCKED) == GovernanceState.RED
    # An unrecognized value must fail closed (RED), never default to GREEN.
    assert governance.classify_governance_decision("SOMETHING_NEW_AND_UNEXPECTED") == GovernanceState.RED
