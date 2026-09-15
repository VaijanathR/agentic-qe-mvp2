"""
Agentic QE Orchestration -- Replanning + bounded Retry Policy (governing
instruction sec. 31, 32, 33).

CP-MVP2-07's real, deterministic replanning decision
(`rca.replan.decide_replanning`, reused unmodified via
`rca_orchestration.run_rca_for_execution`) is the actual decision
authority -- this module only adds a bounded RETRY POLICY on top of it
(sec. 33), and enforces the replanning prohibitions (sec. 32) as an
explicit guard, never silently.

Retry policy (sec. 33, applied to the real failure_classification the
adapted ExecutionResult carries):
  ENVIRONMENT_ISSUE / TOOL_ISSUE        -> retry allowed, bounded to
                                            MAX_RETRIES (transient
                                            infrastructure)
  everything else (APPLICATION_DEFECT-
  shaped, REQUIREMENT_MISMATCH, TEST_DATA_ISSUE, CONSTRAINT_VIOLATION,
  AUTHORIZATION_ISSUE, THIRD_PARTY_DEPENDENCY_ISSUE)
                                        -> retry NOT allowed (sec. 33's
                                            own explicit examples)
Every retry decision, taken or not, is recorded (sec. 33 "Record every
retry").
"""
from __future__ import annotations

from typing import Dict, List, Optional

MAX_RETRIES = 1

_RETRYABLE_CATEGORIES = {"ENVIRONMENT_ISSUE", "TOOL_ISSUE"}


class ReplanAction:
    """Orchestration Expansion instruction, Phase K's own vocabulary --
    a real, disclosed refinement layered on top of CP-07's real
    `rca.schema.ReplanningDecision` (REPLAN_ALLOWED/REPLAN_NOT_ALLOWED/
    HUMAN_REVIEW_REQUIRED/GOVERNANCE_BLOCKED), never a second,
    conflicting authority -- `determine_replan_action()` below always
    derives the action FROM CP-07's own real decision plus this
    orchestrator's own bounded retry/dependency evidence, never
    independently of it."""

    RETRY = "RETRY"
    ALTERNATE_TESTCASE = "ALTERNATE_TESTCASE"
    ALTERNATE_DATASET = "ALTERNATE_DATASET"
    PREREQUISITE_ESTABLISHMENT = "PREREQUISITE_ESTABLISHMENT"
    ENVIRONMENT_RETRY = "ENVIRONMENT_RETRY"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    ACTION_DEFERRED = "ACTION_DEFERRED"
    TERMINAL_FAILURE = "TERMINAL_FAILURE"


def retry_decision(failure_classification: str, retry_count_so_far: int) -> Dict:
    if failure_classification not in _RETRYABLE_CATEGORIES:
        return {
            "retry_allowed": False,
            "reason": f"failure_classification={failure_classification!r} is not in the retryable set "
                      f"{sorted(_RETRYABLE_CATEGORIES)} -- per governing instruction sec. 33, retry is "
                      "not an appropriate resolution for this failure class.",
        }
    if retry_count_so_far >= MAX_RETRIES:
        return {
            "retry_allowed": False,
            "reason": f"Retry budget exhausted ({retry_count_so_far}/{MAX_RETRIES} already attempted).",
        }
    return {
        "retry_allowed": True,
        "reason": f"failure_classification={failure_classification!r} is a transient-infrastructure class; "
                  f"retry {retry_count_so_far + 1}/{MAX_RETRIES} authorized.",
    }


def determine_replan_action(
    *,
    rca_replanning_decision: str,
    rca_confidence: str,
    failure_classification: Optional[str],
    retry_count_so_far: int = 0,
    prerequisite_missing: bool = False,
    alternate_dataset_available: bool = False,
) -> Dict:
    """Derives one real `ReplanAction` from CP-07's own real replanning
    decision (`rca.schema.ReplanningDecision`) plus this orchestrator's
    own bounded retry policy and dependency evidence -- never overrides
    CP-07's decision, only refines its presentation into the Phase K
    vocabulary. Every result states why, what changes, what remains
    unchanged, and whether approval is required (Phase K's own
    requirement)."""
    from rca.schema import ReplanningDecision

    if rca_replanning_decision == ReplanningDecision.GOVERNANCE_BLOCKED:
        return {
            "action": ReplanAction.TERMINAL_FAILURE,
            "why": "CP-07 governance itself is BLOCKED for this failure (e.g. a LOCATOR_FAILURE, whose only "
                   "automated remedy is the still-unauthorized CR-002) -- no automated recovery path exists.",
            "what_changes": "Nothing -- no automated action is taken.",
            "what_remains_unchanged": "Requirement, expected result, testcase, test data, automation.",
            "approval_required": True,
        }

    if rca_replanning_decision == ReplanningDecision.REPLAN_NOT_ALLOWED:
        return {
            "action": ReplanAction.TERMINAL_FAILURE if failure_classification not in (None,) and failure_classification not in _RETRYABLE_CATEGORIES else ReplanAction.ACTION_DEFERRED,
            "why": "Execution PASSED (REPLAN_NOT_ALLOWED) -- there is nothing to replan." if failure_classification is None else "Real failure exists but CP-07 found nothing to replan for it.",
            "what_changes": "Nothing.",
            "what_remains_unchanged": "Everything.",
            "approval_required": False,
        }

    if prerequisite_missing:
        return {
            "action": ReplanAction.PREREQUISITE_ESTABLISHMENT,
            "why": "Dependency planning (orchestration.dependency_planning) found a real, disclosed prerequisite "
                   "requirement that has not yet run in this orchestration.",
            "what_changes": "Execution order -- the prerequisite requirement is scheduled first.",
            "what_remains_unchanged": "Requirement, expected result, testcase, test data, automation.",
            "approval_required": False,
        }

    retry = retry_decision(failure_classification or "", retry_count_so_far)
    if retry["retry_allowed"]:
        action = ReplanAction.ENVIRONMENT_RETRY if failure_classification == "ENVIRONMENT_ISSUE" else ReplanAction.RETRY
        return {
            "action": action,
            "why": retry["reason"],
            "what_changes": "The same real testcase/dataset/automation is re-executed once more.",
            "what_remains_unchanged": "Requirement, expected result, testcase content, test data, automation code.",
            "approval_required": False,
        }

    if alternate_dataset_available:
        return {
            "action": ReplanAction.ALTERNATE_DATASET,
            "why": "A real, alternate governed dataset exists for the same testcase (One Testcase -> Multiple "
                   "Datasets); the failure may be dataset-specific.",
            "what_changes": "The dataset used for re-execution.",
            "what_remains_unchanged": "Requirement, expected result, testcase, automation.",
            "approval_required": True,
        }

    if rca_confidence != "HIGH" or rca_replanning_decision == ReplanningDecision.HUMAN_REVIEW_REQUIRED:
        return {
            "action": ReplanAction.HUMAN_REVIEW,
            "why": f"RCA confidence is {rca_confidence!r} and/or CP-07 itself returned HUMAN_REVIEW_REQUIRED -- "
                   "insufficient certainty for any automated action.",
            "what_changes": "Nothing automatically -- a human decision is requested.",
            "what_remains_unchanged": "Everything, pending that decision.",
            "approval_required": True,
        }

    return {
        "action": ReplanAction.ACTION_DEFERRED,
        "why": "A high-confidence root cause exists but the only real corrective action (e.g. authoring richer "
               "testcase content) requires content this orchestrator has no authority to invent.",
        "what_changes": "Nothing in this run.",
        "what_remains_unchanged": "Everything -- deferred to a future, separately-authorized task.",
        "approval_required": True,
    }


def check_replanning_prohibitions(proposed_change: str) -> Dict:
    """Prohibited-replanning guard (sec. 32): a real proposed_change
    string is scanned for the exact prohibited-action phrases CP-07's
    own replanning module is designed to never produce (it only ever
    emits RECOMMENDATION-ONLY / NOT APPLIED text, per `rca/replan.py`).
    This is a defense-in-depth re-check of that text, not the primary
    control -- the primary control is that CP-07 never self-executes
    any change at all."""
    prohibited_phrases = [
        "change the approved requirement", "change approved requirement",
        "change the expected result", "modify the expected result",
        "change the acceptance criteria", "change the business rule",
        "change the response code", "alter the valid test data merely to pass",
        "remove a required business step", "skip a required business step",
    ]
    lowered = proposed_change.lower()
    hits = [p for p in prohibited_phrases if p in lowered]
    return {
        "passed": not hits,
        "rationale": (
            "Proposed change contains no prohibited replanning phrase."
            if not hits
            else f"PROHIBITED: proposed change text matched prohibited replanning phrase(s): {hits}. "
                 "Rule 2 / sec. 32: never change the contract to force a PASS."
        ),
    }
