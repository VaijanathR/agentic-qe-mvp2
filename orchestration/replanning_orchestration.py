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

from typing import Dict, List

MAX_RETRIES = 1

_RETRYABLE_CATEGORIES = {"ENVIRONMENT_ISSUE", "TOOL_ISSUE"}


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
