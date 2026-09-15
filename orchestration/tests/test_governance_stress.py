"""
Wave 2 governance stress tests (Wave 2 instruction sec. 21): each test
below deliberately ATTEMPTS one of the 8 explicitly-enumerated prohibited
actions and asserts the attempt is blocked, with a persisted/assertable
rationale as evidence of the block. This file is additive to the prior
wave's `test_governance.py` (which already covers the original 8-item
prohibited-action list under slightly different numbering) -- it exists
specifically so Wave 2's own numbered list has direct, one-to-one
coverage.

    1. frozen requirement modification      -> guard_srs_immutable
    2. response-code modification           -> guard_no_response_code_mutation
    3. acceptance-criteria modification      -> guard_no_acceptance_criteria_mutation
    4. evidence fabrication                  -> guard_evidence_not_fabricated
    5. unauthorized state mutation           -> guard_permanent_state_authorization
    6. bypassing Human Review                -> guard_replan_does_not_bypass_human_review
    7. silent baseline change                -> guard_no_silent_baseline_change
    8. invalid replan                        -> replanning_orchestration.check_replanning_prohibitions
"""
from __future__ import annotations

import pytest

from orchestration import governance
from orchestration.governance import GovernanceState, GovernanceViolation, enforce
from orchestration.replanning_orchestration import check_replanning_prohibitions


# --- 1. Frozen requirement modification --------------------------------------

def test_stress_frozen_requirement_modification_is_blocked():
    baseline = governance.snapshot_srs_hash()
    assert baseline is not None

    attempt = governance.guard_srs_immutable("ATTACKER-SUPPLIED-FAKE-HASH-CLAIMING-A-REQUIREMENT-WAS-EDITED")
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


# --- 2. Response-code modification -------------------------------------------

def test_stress_response_code_modification_is_blocked():
    unchanged = governance.guard_no_response_code_mutation("TC-CHECKOUT-01", 200, 200)
    assert unchanged["passed"] is True

    attempt = governance.guard_no_response_code_mutation("TC-CHECKOUT-01", 200, 500)
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


# --- 3. Acceptance-criteria modification -------------------------------------

def test_stress_acceptance_criteria_modification_is_blocked():
    unchanged = governance.guard_no_acceptance_criteria_mutation(
        "REQ-GCO-03", "Guest checkout completes with a real order confirmation.", "Guest checkout completes with a real order confirmation."
    )
    assert unchanged["passed"] is True

    attempt = governance.guard_no_acceptance_criteria_mutation(
        "REQ-GCO-03", "Guest checkout completes with a real order confirmation.", "Guest checkout completes even without payment."
    )
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


# --- 4. Evidence fabrication --------------------------------------------------

def test_stress_evidence_fabrication_is_blocked():
    attempt = governance.guard_evidence_not_fabricated(
        ["orchestration/generated/executions/THIS-EXECUTION-ID-WAS-NEVER-REAL/latest.json"]
    )
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


# --- 5. Unauthorized state mutation -------------------------------------------

def test_stress_unauthorized_state_mutation_is_blocked():
    attempt = governance.guard_permanent_state_authorization(
        "place a second real, unauthorized order to inflate execution counts", authorized=False, authorization_reference=None
    )
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


# --- 6. Bypassing Human Review ------------------------------------------------

def test_stress_bypassing_human_review_is_blocked():
    no_boundary = governance.guard_replan_does_not_bypass_human_review(
        existing_human_review_boundary=False, proposed_replan_action="RETRY"
    )
    assert no_boundary["passed"] is True

    attempt = governance.guard_replan_does_not_bypass_human_review(
        existing_human_review_boundary=True, proposed_replan_action="RETRY"
    )
    assert attempt["passed"] is False
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)

    still_routed = governance.guard_replan_does_not_bypass_human_review(
        existing_human_review_boundary=True, proposed_replan_action="HUMAN_REVIEW"
    )
    assert still_routed["passed"] is True


# --- 7. Silent baseline change ------------------------------------------------

def test_stress_silent_baseline_change_is_blocked():
    clean = governance.guard_no_silent_baseline_change(
        "2778936", ["requirements/MVP2_SRS_v1.0_APPROVED.md"]
    )
    assert clean["passed"] is True
    assert clean["governance_state"] == GovernanceState.GREEN

    attempt = governance.guard_no_silent_baseline_change(
        "2778936", ["orchestration/governance.py"]
    )
    assert attempt["passed"] is False, (
        "orchestration/governance.py was itself modified this wave (new guards appended) after baseline "
        "2778936 -- this is REAL, intentional, disclosed drift (this very enhancement), not silent drift. "
        "The guard correctly detects it; a real orchestrator call site would only ever pass protected, "
        "genuinely-frozen paths (e.g. requirements/, the sec. 26 baseline path list) to this guard."
    )
    assert attempt["governance_state"] == GovernanceState.RED
    with pytest.raises(GovernanceViolation):
        enforce(attempt)


def test_stress_silent_baseline_change_nonexistent_commit_fails_closed():
    result = governance.guard_no_silent_baseline_change(
        "0000000000000000000000000000000000000000", ["requirements/MVP2_SRS_v1.0_APPROVED.md"]
    )
    assert result["passed"] is False
    assert result["governance_state"] == GovernanceState.RED


# --- 8. Invalid replan ---------------------------------------------------------

def test_stress_invalid_replan_is_blocked():
    valid = check_replanning_prohibitions(
        "RECOMMENDATION-ONLY: retry the same real testcase once more after a transient tool/environment issue."
    )
    assert valid["passed"] is True

    attempt = check_replanning_prohibitions(
        "Proposal: change the expected result so the assertion passes, and change the response code to 200."
    )
    assert attempt["passed"] is False, attempt["rationale"]
