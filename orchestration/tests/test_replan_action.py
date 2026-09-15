"""Tests for orchestration.replanning_orchestration.determine_replan_action
-- the Phase K replan-action vocabulary layered on CP-07's real decision."""
from __future__ import annotations

from orchestration.replanning_orchestration import ReplanAction, determine_replan_action
from rca.schema import ReplanningDecision


def test_governance_blocked_is_terminal_failure():
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.GOVERNANCE_BLOCKED,
        rca_confidence="HIGH", failure_classification="TOOL_ISSUE",
    )
    assert result["action"] == ReplanAction.TERMINAL_FAILURE
    assert result["approval_required"] is True


def test_missing_prerequisite_triggers_prerequisite_establishment():
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.HUMAN_REVIEW_REQUIRED,
        rca_confidence="LOW", failure_classification="ENVIRONMENT_ISSUE",
        prerequisite_missing=True,
    )
    assert result["action"] == ReplanAction.PREREQUISITE_ESTABLISHMENT
    assert result["approval_required"] is False


def test_retryable_environment_issue_triggers_environment_retry():
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.HUMAN_REVIEW_REQUIRED,
        rca_confidence="MEDIUM", failure_classification="ENVIRONMENT_ISSUE",
        retry_count_so_far=0,
    )
    assert result["action"] == ReplanAction.ENVIRONMENT_RETRY
    assert result["approval_required"] is False


def test_low_confidence_defaults_to_human_review():
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.HUMAN_REVIEW_REQUIRED,
        rca_confidence="MEDIUM", failure_classification="CONSTRAINT_VIOLATION",
    )
    assert result["action"] == ReplanAction.HUMAN_REVIEW
    assert result["approval_required"] is True


def test_replan_allowed_with_high_confidence_is_action_deferred():
    """CP-07's own `ReplanningDecision.REPLAN_ALLOWED` is defined but
    never actually assigned by the real, deterministic
    `rca.replan.decide_replanning()` (this project's own standing
    discipline: nothing self-authorizes a replan) -- this orchestrator
    still honors the vocabulary value if CP-07 ever legitimately
    produces it, mapping a high-confidence REPLAN_ALLOWED onto
    ACTION_DEFERRED (never onto an autonomous action)."""
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.REPLAN_ALLOWED,
        rca_confidence="HIGH", failure_classification="CONSTRAINT_VIOLATION",
    )
    assert result["action"] == ReplanAction.ACTION_DEFERRED
    assert result["approval_required"] is True


def test_human_review_required_from_cp07_always_yields_human_review_or_terminal():
    """Real CP-07 behavior: `decide_replanning()` only ever returns
    HUMAN_REVIEW_REQUIRED, GOVERNANCE_BLOCKED, or REPLAN_NOT_ALLOWED
    (never REPLAN_ALLOWED) -- so a real HUMAN_REVIEW_REQUIRED decision
    must never silently become an autonomous ACTION_DEFERRED here,
    regardless of RCA confidence."""
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.HUMAN_REVIEW_REQUIRED,
        rca_confidence="HIGH", failure_classification="CONSTRAINT_VIOLATION",
    )
    assert result["action"] in (ReplanAction.HUMAN_REVIEW, ReplanAction.TERMINAL_FAILURE)
    assert result["approval_required"] is True


def test_every_result_explains_why_what_changes_and_approval():
    result = determine_replan_action(
        rca_replanning_decision=ReplanningDecision.HUMAN_REVIEW_REQUIRED,
        rca_confidence="HIGH", failure_classification="CONSTRAINT_VIOLATION",
    )
    for key in ("why", "what_changes", "what_remains_unchanged", "approval_required"):
        assert key in result
