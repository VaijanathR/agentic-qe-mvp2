"""Tests for orchestration/state.py -- the explicit lifecycle state machine."""
from __future__ import annotations

import pytest

from orchestration.state import (
    ALL_STATES,
    InvalidTransitionError,
    OrchestrationState,
    UnknownStateError,
    VALID_TRANSITIONS,
    validate_transition,
)


def test_every_valid_transition_target_is_a_known_state():
    for source, targets in VALID_TRANSITIONS.items():
        assert source in ALL_STATES
        for t in targets:
            assert t in ALL_STATES


def test_happy_path_full_lifecycle_is_valid():
    path = [
        OrchestrationState.RECEIVED, OrchestrationState.UNDERSTANDING, OrchestrationState.VALIDATED,
        OrchestrationState.IMPACT_ANALYZED, OrchestrationState.RISK_ASSESSED, OrchestrationState.TEST_STRATEGY_READY,
        OrchestrationState.TESTCASES_READY, OrchestrationState.DATA_READY, OrchestrationState.TRACEABILITY_VALID,
        OrchestrationState.AUTOMATION_READY, OrchestrationState.EXECUTION_PLANNED, OrchestrationState.EXECUTING,
        OrchestrationState.EVIDENCE_COLLECTED, OrchestrationState.RESULT_ANALYZED, OrchestrationState.REGRESSION,
        OrchestrationState.FINAL_REPORT,
    ]
    for a, b in zip(path, path[1:]):
        validate_transition(a, b)  # must not raise


def test_failure_path_through_rca_replan_is_valid():
    path = [
        OrchestrationState.RESULT_ANALYZED, OrchestrationState.RCA_REQUIRED, OrchestrationState.RCA_COMPLETE,
        OrchestrationState.REPLAN_ASSESSED, OrchestrationState.HUMAN_REVIEW, OrchestrationState.REEXECUTION,
        OrchestrationState.REGRESSION, OrchestrationState.FINAL_REPORT,
    ]
    for a, b in zip(path, path[1:]):
        validate_transition(a, b)


def test_skipping_stages_is_rejected():
    """RECEIVED -> FINAL_REPORT directly must be rejected -- an
    orchestration cannot silently skip every intermediate stage."""
    with pytest.raises(InvalidTransitionError):
        validate_transition(OrchestrationState.RECEIVED, OrchestrationState.FINAL_REPORT)


def test_final_report_is_terminal():
    with pytest.raises(InvalidTransitionError):
        validate_transition(OrchestrationState.FINAL_REPORT, OrchestrationState.RECEIVED)


def test_blocked_is_terminal():
    with pytest.raises(InvalidTransitionError):
        validate_transition(OrchestrationState.BLOCKED, OrchestrationState.EXECUTING)


def test_every_state_can_reach_blocked_except_the_two_terminal_states():
    for s in ALL_STATES:
        if s in (OrchestrationState.FINAL_REPORT, OrchestrationState.BLOCKED):
            continue
        assert OrchestrationState.BLOCKED in VALID_TRANSITIONS[s], f"{s} cannot transition to BLOCKED"


def test_unknown_state_is_rejected():
    with pytest.raises(UnknownStateError):
        validate_transition("NOT_A_REAL_STATE", OrchestrationState.RECEIVED)
    with pytest.raises(UnknownStateError):
        validate_transition(OrchestrationState.RECEIVED, "NOT_A_REAL_STATE")
