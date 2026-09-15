"""
Agentic QE Orchestration -- explicit lifecycle state machine (governing
instruction sec. 11).

Deterministic, pure Python -- no LLM involvement. An invalid transition
raises `InvalidTransitionError` rather than silently proceeding, per
governing instruction sec. 11 ("Invalid transitions must be rejected
deterministically").
"""
from __future__ import annotations

from typing import Dict, Set


class OrchestrationState:
    RECEIVED = "RECEIVED"
    UNDERSTANDING = "UNDERSTANDING"
    VALIDATED = "VALIDATED"
    IMPACT_ANALYZED = "IMPACT_ANALYZED"
    RISK_ASSESSED = "RISK_ASSESSED"
    TEST_STRATEGY_READY = "TEST_STRATEGY_READY"
    TESTCASES_READY = "TESTCASES_READY"
    DATA_READY = "DATA_READY"
    TRACEABILITY_VALID = "TRACEABILITY_VALID"
    AUTOMATION_READY = "AUTOMATION_READY"
    EXECUTION_PLANNED = "EXECUTION_PLANNED"
    EXECUTING = "EXECUTING"
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    RESULT_ANALYZED = "RESULT_ANALYZED"
    RCA_REQUIRED = "RCA_REQUIRED"
    RCA_COMPLETE = "RCA_COMPLETE"
    REPLAN_ASSESSED = "REPLAN_ASSESSED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    ACTION_ALLOWED = "ACTION_ALLOWED"
    REEXECUTION = "REEXECUTION"
    REGRESSION = "REGRESSION"
    FINAL_REPORT = "FINAL_REPORT"
    #: Implementation-time addition, explicitly permitted by governing
    #: instruction sec. 11 ("The implementation may use additional
    #: states where justified"): a governance conflict, frozen-spec
    #: conflict, or otherwise unsafe condition halts the orchestration
    #: without silently ending it in FINAL_REPORT.
    BLOCKED = "BLOCKED"


ALL_STATES: Set[str] = {
    v for k, v in vars(OrchestrationState).items() if not k.startswith("_") and isinstance(v, str)
}

#: The baseline model from governing instruction sec. 11, plus the
#: branch points explicitly required elsewhere in the instruction:
#: RESULT_ANALYZED may skip straight to REGRESSION on a clean PASS
#: (sec. 10 "not every requirement needs every stage" / sec. 4 branch
#: model); HUMAN_REVIEW/ACTION_ALLOWED can lead to REEXECUTION or
#: directly to REGRESSION; any state may transition to BLOCKED (a
#: governance conflict can surface at any stage); FINAL_REPORT is
#: terminal.
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    OrchestrationState.RECEIVED: {OrchestrationState.UNDERSTANDING, OrchestrationState.BLOCKED},
    OrchestrationState.UNDERSTANDING: {OrchestrationState.VALIDATED, OrchestrationState.BLOCKED},
    OrchestrationState.VALIDATED: {OrchestrationState.IMPACT_ANALYZED, OrchestrationState.BLOCKED},
    OrchestrationState.IMPACT_ANALYZED: {OrchestrationState.RISK_ASSESSED, OrchestrationState.BLOCKED},
    OrchestrationState.RISK_ASSESSED: {OrchestrationState.TEST_STRATEGY_READY, OrchestrationState.BLOCKED},
    OrchestrationState.TEST_STRATEGY_READY: {OrchestrationState.TESTCASES_READY, OrchestrationState.BLOCKED},
    OrchestrationState.TESTCASES_READY: {OrchestrationState.DATA_READY, OrchestrationState.BLOCKED},
    OrchestrationState.DATA_READY: {OrchestrationState.TRACEABILITY_VALID, OrchestrationState.BLOCKED},
    OrchestrationState.TRACEABILITY_VALID: {OrchestrationState.AUTOMATION_READY, OrchestrationState.BLOCKED},
    OrchestrationState.AUTOMATION_READY: {OrchestrationState.EXECUTION_PLANNED, OrchestrationState.BLOCKED},
    OrchestrationState.EXECUTION_PLANNED: {OrchestrationState.EXECUTING, OrchestrationState.BLOCKED},
    OrchestrationState.EXECUTING: {OrchestrationState.EVIDENCE_COLLECTED, OrchestrationState.BLOCKED},
    OrchestrationState.EVIDENCE_COLLECTED: {OrchestrationState.RESULT_ANALYZED, OrchestrationState.BLOCKED},
    OrchestrationState.RESULT_ANALYZED: {
        OrchestrationState.RCA_REQUIRED,   # a real failure occurred
        OrchestrationState.REGRESSION,     # clean PASS -- RCA stages skipped
        OrchestrationState.BLOCKED,
    },
    OrchestrationState.RCA_REQUIRED: {OrchestrationState.RCA_COMPLETE, OrchestrationState.BLOCKED},
    OrchestrationState.RCA_COMPLETE: {OrchestrationState.REPLAN_ASSESSED, OrchestrationState.BLOCKED},
    OrchestrationState.REPLAN_ASSESSED: {
        OrchestrationState.HUMAN_REVIEW,
        OrchestrationState.ACTION_ALLOWED,
        OrchestrationState.REGRESSION,     # REPLAN_NOT_ALLOWED with no further action
        OrchestrationState.BLOCKED,
    },
    OrchestrationState.HUMAN_REVIEW: {
        OrchestrationState.REEXECUTION,    # approved
        OrchestrationState.REGRESSION,     # reviewed, no reexecution authorized
        OrchestrationState.BLOCKED,
    },
    OrchestrationState.ACTION_ALLOWED: {OrchestrationState.REEXECUTION, OrchestrationState.BLOCKED},
    OrchestrationState.REEXECUTION: {OrchestrationState.REGRESSION, OrchestrationState.BLOCKED},
    OrchestrationState.REGRESSION: {OrchestrationState.FINAL_REPORT, OrchestrationState.BLOCKED},
    OrchestrationState.FINAL_REPORT: set(),
    OrchestrationState.BLOCKED: set(),  # terminal: requires Human + Di, not an automated transition
}


class InvalidTransitionError(RuntimeError):
    pass


class UnknownStateError(RuntimeError):
    pass


def validate_transition(current: str, target: str) -> None:
    """Raises deterministically for an unknown state or a transition not
    present in `VALID_TRANSITIONS` -- never allows a silent, undeclared
    jump."""
    if current not in ALL_STATES:
        raise UnknownStateError(f"Unknown orchestration state: {current!r}")
    if target not in ALL_STATES:
        raise UnknownStateError(f"Unknown orchestration state: {target!r}")
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidTransitionError(
            f"Invalid orchestration state transition: {current!r} -> {target!r}. "
            f"Allowed from {current!r}: {sorted(allowed) or '(terminal state)'}."
        )
