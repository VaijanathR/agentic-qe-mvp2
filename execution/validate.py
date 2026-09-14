"""
CP-MVP2-06 — deterministic eligibility and pre-execution validation.

Per the frozen specification secs. 4/17: execution eligibility is
derived SOLELY from the CP-MVP2-05 GovernanceStatus already assigned
upstream. There is no LLM component anywhere in CP-MVP2-06 — every
function here is a plain equality/membership/lookup check.
"""
from __future__ import annotations

from typing import Dict, List

from automation.schema import ActionType, LocatorStatus, PlaywrightArtifact
from automation.schema import GovernanceStatus as PlaywrightGovernanceStatus
from testdata.schema import GovernedTestDataSet

#: Spec sec. 4 table. ACCEPTED/POSSIBLE_DUPLICATE are eligible; every
#: other CP-MVP2-05 governance status is not.
ELIGIBLE_GOVERNANCE_STATUSES = {
    PlaywrightGovernanceStatus.ACCEPTED,
    PlaywrightGovernanceStatus.POSSIBLE_DUPLICATE,
}

REQUIRED_BROWSER_INTENT = "chromium-headless"


def _result(check: str, passed: bool, detail) -> dict:
    return {"check": check, "passed": bool(passed), "detail": detail}


def check_eligibility(governance_status: str) -> dict:
    """Spec sec. 4. Never re-derives or second-guesses the upstream
    CP-MVP2-05 decision -- purely a membership check."""
    return _result("eligibility", governance_status in ELIGIBLE_GOVERNANCE_STATUSES, {"governance_status": governance_status})


def validate_pre_execution(artifact: PlaywrightArtifact) -> dict:
    """Spec sec. 17: defensive re-verification of everything CP-MVP2-05
    already should have guaranteed, before any browser action is
    attempted. A failure here is a DESIGN-TIME integrity problem (spec
    sec. 18), never a runtime one."""
    problems: List[str] = []

    if artifact.browser_intent != REQUIRED_BROWSER_INTENT:
        problems.append(f"UNSUPPORTED_BROWSER_INTENT:{artifact.browser_intent}")

    if not artifact.steps:
        problems.append("NO_STEPS")

    business_assertions = [a for a in artifact.assertions if a.assertion_type == "BUSINESS_REQUIRED"]
    if not business_assertions:
        problems.append("NO_BUSINESS_REQUIRED_ASSERTION")

    for step in artifact.steps:
        if step.action_type in (ActionType.FILL, ActionType.CLICK, ActionType.SELECT):
            if step.locator is None or step.locator.status != LocatorStatus.EVIDENCED:
                problems.append(f"STEP_{step.step_order}_LOCATOR_NOT_EVIDENCED")
        if step.action_type in (ActionType.FILL, ActionType.SELECT) and not step.input_mapping:
            problems.append(f"STEP_{step.step_order}_MISSING_INPUT_MAPPING")

    if not artifact.requirement_ids or not artifact.testcase_id or not artifact.test_data_set_id:
        problems.append("MISSING_TRACEABILITY_KEYS")

    if not artifact.source_attribution:
        problems.append("MISSING_SOURCE_ATTRIBUTION")

    return _result("pre_execution", not problems, problems)


#: Precondition-text markers that imply a pre-existing authenticated
#: session/account is required. No reusable authenticated-session
#: fixture exists in this project (spec sec. 16, disclosed limitation)
#: -- an artifact whose precondition text names one of these cannot
#: have that precondition established today. This is a BLOCKED
#: (eligible artifact, unsatisfiable runtime precondition), never a
#: NOT_EXECUTED (design-time/ineligible) outcome -- the artifact itself
#: may be perfectly well-formed.
_AUTHENTICATED_PRECONDITION_MARKERS = ("authenticated", "existing account", "saved address", "logged in", "logged-in")


def check_authorization_precondition(artifact: PlaywrightArtifact) -> dict:
    flagged = [
        p for p in artifact.preconditions
        if any(marker in p.lower() for marker in _AUTHENTICATED_PRECONDITION_MARKERS)
    ]
    return _result("authorization_precondition", not flagged, {"unsatisfiable_preconditions": flagged})


#: Requirements whose governed intent is to create or mutate persistent
#: state on the shared, third-party Demo Web Shop instance (new
#: account, order placement). Cart/wishlist mutations are session-
#: scoped, not persistent across users, and are deliberately excluded.
#: This list is deterministic and evidence-cited (Approved SRS §6.1,
#: §6.9, §6.10, §6.13), never inferred by an LLM.
STATE_MUTATING_REQUIREMENT_IDS = {
    "REQ-REG-01",  # creates a new account
    "REQ-GCO-01", "REQ-GCO-02", "REQ-GCO-03",  # guest checkout culminates in an order
    "REQ-ACO-01",  # authenticated checkout culminates in an order
    "REQ-CONF-01", "REQ-CONF-02",  # order confirmation/total -- order already placed by this point
}


def assess_data_oq_01(artifact: PlaywrightArtifact) -> dict:
    """Spec sec. 10 (task instruction) / sec. 16/29 (frozen
    specification): DATA-OQ-01 (Approved SRS §13) -- the shared-instance
    data-reset/isolation policy -- remains genuinely unresolved. No
    constraint profile, dataset, or artifact anywhere in this project
    establishes a safe basis for repeated, uncontrolled state mutation
    against the shared public SUT. A state-mutating artifact is
    therefore never assumed safe merely because its field-level data is
    synthetic (CP-MVP2-04) -- synthetic values do not, by themselves,
    solve the isolation/reset problem."""
    mutating_ids = sorted(set(artifact.requirement_ids) & STATE_MUTATING_REQUIREMENT_IDS)
    if not mutating_ids:
        return _result("data_oq_01", True, {"state_mutating": False})
    return _result(
        "data_oq_01", False,
        {
            "state_mutating": True,
            "requirement_ids": mutating_ids,
            "reason": (
                "DATA-OQ-01 (Approved SRS §13: shared-instance data-reset/isolation policy) "
                "is unresolved. No established, evidenced basis exists for safely performing "
                "this state-mutating scenario repeatedly against the shared, third-party "
                "Demo Web Shop instance without uncontrolled data pollution."
            ),
        },
    )


def validate_data_field_availability(artifact: PlaywrightArtifact, dataset: GovernedTestDataSet) -> dict:
    """Every FILL/SELECT step's input_mapping must resolve to a real
    field on the linked, eligible CP-MVP2-04 dataset -- re-checked here
    defensively, mirroring the exact precedent already established in
    testdata.validate/automation.validate."""
    available = {f.field_name for f in dataset.dataset.fields}
    missing = [
        step.step_order
        for step in artifact.steps
        if step.action_type in (ActionType.FILL, ActionType.SELECT)
        and step.input_mapping not in available
    ]
    return _result("data_field_availability", not missing, {"missing_field_steps": missing})
