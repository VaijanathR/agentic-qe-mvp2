"""
Agentic QE Orchestration -- governance layer (governing instruction
sec. 9, 35, 58, 71).

Two responsibilities, kept deliberately separate:

1. `classify_governance_decision()` -- maps the *existing*, frozen
   `rca.schema.GovernanceDecision` vocabulary (CP-MVP2-07, reused
   unmodified) onto this orchestration's own GREEN/YELLOW/RED reporting
   vocabulary. This is presentation, not a new decision authority --
   CP-07's `rca.govern.decide_governance()` remains the actual decision
   maker for RCA-driven governance.

2. The `guard_*` functions -- new, orchestration-level prohibited-action
   checks (sec. 58) that exist independently of any one execution's RCA
   outcome: SRS immutability, expected-result immutability, permanent-
   state authorization, CR-002 non-implementation, evidence
   non-fabrication, human-approval presence, valid state transitions,
   and performance-threshold approval. Every guard is deterministic --
   no LLM anywhere in this module, per the frozen project-wide governance
   discipline. `enforce()` turns a failed guard into a hard
   `GovernanceViolation` for real pipeline use; the guard functions
   themselves always return a plain result dict so tests can assert on
   the outcome without needing to catch an exception.

The LLM is never the final authority here (sec. 9): every guard below is
plain, deterministic Python.
Wave 2 (instruction sec. 21, "Governance Stress Testing") adds four more
guards -- #9-12 below -- to close out the full 8-item prohibited-action
list that section enumerates explicitly (frozen requirement modification
and evidence fabrication are already covered by guards #1/#5 above;
unauthorized state mutation and invalid replan are already covered by
guards #3/#7 above). The four new guards give response-code mutation and
acceptance-criteria mutation their own explicitly-named guards (both are
otherwise instances of guard #2's expected-result-immutability pattern,
but sec. 21 lists them as distinct stress-test items so they get distinct,
directly-testable entry points), plus two genuinely new checks: the
Human-Review-boundary-cannot-be-overridden-by-a-replan rule (sec. 13-14),
and a real `git diff` based silent-baseline-change detector (sec. 21 item
7, sec. 26).
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT
from rca.govern import check_cr002_status
from rca.schema import GovernanceDecision


class GovernanceState:
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class GovernanceViolation(RuntimeError):
    """Raised by `enforce()` for a failed guard. Never caught and
    silently downgraded to a PASS anywhere in this package -- a
    governance conflict always surfaces (governing instruction sec. 3:
    'STOP -> REPORT -> HUMAN + DI DECIDE')."""


#: CP-07's own decision vocabulary never included a literal
#: "ACTION_AUTHORIZED" outcome in practice (rca/govern.py never assigns
#: it -- nothing in this project self-authorizes), but the enum value
#: exists for completeness, so it is mapped here too.
_RCA_GOVERNANCE_TO_STATE = {
    GovernanceDecision.NO_ACTION_REQUIRED: GovernanceState.GREEN,
    GovernanceDecision.ACTION_AUTHORIZED: GovernanceState.GREEN,
    GovernanceDecision.ACTION_DEFERRED_TO_HUMAN: GovernanceState.YELLOW,
    GovernanceDecision.GOVERNANCE_BLOCKED: GovernanceState.RED,
}


def classify_governance_decision(rca_governance_decision: str) -> str:
    return _RCA_GOVERNANCE_TO_STATE.get(rca_governance_decision, GovernanceState.RED)


def enforce(guard_result: Dict) -> Dict:
    """Raises GovernanceViolation if `guard_result["passed"]` is False;
    otherwise returns the result unchanged, so callers can chain
    `enforce(guard_x(...))`."""
    if not guard_result.get("passed", False):
        raise GovernanceViolation(guard_result.get("rationale", "Governance guard failed."))
    return guard_result


def _sha256(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- 1. Approved SRS immutability -------------------------------------------

SRS_PATH = REPO_ROOT / "requirements" / "MVP2_SRS_v1.0_APPROVED.md"


def snapshot_srs_hash() -> Optional[str]:
    return _sha256(SRS_PATH)


def guard_srs_immutable(baseline_hash: Optional[str]) -> Dict:
    """Prohibited action #1 (sec. 58): 'changing Approved SRS to make a
    test pass'. Compares a hash captured earlier in the run against the
    live file right now."""
    current_hash = snapshot_srs_hash()
    passed = baseline_hash is not None and current_hash == baseline_hash
    return {
        "guard": "srs_immutable",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            "Approved SRS content-hash unchanged since baseline snapshot."
            if passed
            else f"PROHIBITED: Approved SRS content-hash changed (baseline={baseline_hash!r}, current={current_hash!r}). "
                 "Rule 2: NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS."
        ),
    }


# --- 2. Expected-result immutability ----------------------------------------

def guard_no_expected_result_mutation(
    testcase_id: str, original_expected_result: str, proposed_expected_result: str
) -> Dict:
    """Prohibited action #2: 'changing expected result to make a test
    pass'. A proposed expected-result value that differs from the
    persisted/original one is always rejected here -- there is no
    legitimate in-scope reason for this orchestration layer to silently
    rewrite a testcase's expected result; any genuine correction is a
    separate, explicitly-authorized testcase-authoring change, never an
    automatic governance side effect."""
    passed = proposed_expected_result == original_expected_result
    return {
        "guard": "no_expected_result_mutation",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Expected result for {testcase_id} unchanged."
            if passed
            else f"PROHIBITED: an attempt was made to change {testcase_id}'s expected result "
                 f"from {original_expected_result!r} to {proposed_expected_result!r} -- rejected. "
                 "Rule 2: NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS."
        ),
    }


# --- 3. Unauthorized permanent SUT state ------------------------------------

def guard_permanent_state_authorization(
    action_description: str, authorized: bool, authorization_reference: Optional[str] = None
) -> Dict:
    """Prohibited action #3: 'creating unauthorized permanent SUT
    state'. `authorized` must be explicitly True, backed by a real
    `authorization_reference` (e.g. a Human + Di instruction, or an
    already-governed, previously-authorized real order this action
    merely reuses) -- defaulting to False, never inferred."""
    passed = bool(authorized) and bool(authorization_reference)
    return {
        "guard": "permanent_state_authorization",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Permanent SUT state change ({action_description!r}) is authorized: {authorization_reference}."
            if passed
            else f"PROHIBITED: permanent SUT state change ({action_description!r}) has no explicit "
                 "authorization reference. Rule 7: never create unauthorized permanent SUT state. "
                 "STOP -> REPORT -> HUMAN + DI DECIDE."
        ),
    }


# --- 4. CR-002 non-implementation -------------------------------------------

def guard_cr002_not_implemented() -> Dict:
    """Prohibited action #4: 'silently implementing CR-002'. Reuses
    CP-07's own, real, live-document check (never redefines it)."""
    status = check_cr002_status()
    passed = bool(status.get("still_unauthorized"))
    return {
        "guard": "cr002_not_implemented",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": status.get("detail", "CR-002 status could not be determined."),
    }


# --- 5. No fabricated evidence ----------------------------------------------

def _evidence_ref_exists(ref: str) -> bool:
    """A real evidence-reference string may have been recorded by a
    Windows-native process (this project's own real Windows-execution
    gate) and so may contain backslash separators -- normalized here so
    a genuinely real, existing file is never misreported as fabricated
    merely because this guard is running from a POSIX process (see
    `orchestration.safe_persistence`'s docstring for the same underlying
    cross-platform issue in the persistence-pointer format)."""
    if (REPO_ROOT / ref).exists():
        return True
    normalized = ref.replace("\\", "/")
    return (REPO_ROOT / normalized).exists()


def guard_evidence_not_fabricated(evidence_references: List[str]) -> Dict:
    """Prohibited action #5: 'fabricating evidence'. Every referenced
    evidence path must exist as a real file on disk (relative to the
    repository root) -- a reference to a path that does not exist is
    treated as fabricated evidence, never silently accepted."""
    missing = [ref for ref in evidence_references if not _evidence_ref_exists(ref)]
    passed = not missing
    return {
        "guard": "evidence_not_fabricated",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"All {len(evidence_references)} referenced evidence path(s) exist on disk."
            if passed
            else f"PROHIBITED: {len(missing)} referenced evidence path(s) do not exist on disk: {missing}. "
                 "Evidence must never be fabricated."
        ),
    }


# --- 6. Human approval not bypassed -----------------------------------------

def guard_approval_present(requires_approval: bool, approval_record: Optional[Dict]) -> Dict:
    """Prohibited action #6: 'bypassing human approval'. If
    `requires_approval` is True, a real, non-empty approval record
    (see `orchestration/approval.py::ApprovalRecord`) must be present."""
    if not requires_approval:
        return {
            "guard": "approval_present",
            "passed": True,
            "governance_state": GovernanceState.GREEN,
            "rationale": "No human approval was required for this action.",
        }
    passed = bool(approval_record) and bool(approval_record.get("approval_id"))
    return {
        "guard": "approval_present",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Human approval present: {approval_record.get('approval_id')}."
            if passed
            else "PROHIBITED: this action requires human approval, but no approval record was provided. "
                 "Rule 8: never bypass human approval."
        ),
    }


# --- 7. Valid state transition ----------------------------------------------

def guard_valid_state_transition(current_state: str, target_state: str) -> Dict:
    """Prohibited action #7: 'invalid state transition'. Delegates to
    `orchestration.state.validate_transition` -- this guard exists so
    callers get the same deterministic result/rationale shape as every
    other guard, without needing to catch `InvalidTransitionError`/
    `UnknownStateError` themselves."""
    from orchestration.state import InvalidTransitionError, UnknownStateError, validate_transition

    try:
        validate_transition(current_state, target_state)
        return {
            "guard": "valid_state_transition",
            "passed": True,
            "governance_state": GovernanceState.GREEN,
            "rationale": f"{current_state} -> {target_state} is a valid transition.",
        }
    except (InvalidTransitionError, UnknownStateError) as exc:
        return {
            "guard": "valid_state_transition",
            "passed": False,
            "governance_state": GovernanceState.RED,
            "rationale": f"PROHIBITED: {exc}",
        }


# --- 8. Approved performance threshold --------------------------------------

def guard_performance_threshold_approved(threshold_source: Optional[str], threshold_value: Optional[float] = None) -> Dict:
    """Prohibited action #8: 'using an unapproved performance
    threshold'. Per Approved MVP2 SRS v1.0 sec. 9.2, no numeric
    performance threshold is approved for this project -- so any
    non-None `threshold_value` MUST cite `threshold_source ==
    "SRS_APPROVED"`; anything else (an invented, assumed, or
    LLM-suggested number) is rejected. A `threshold_value` of None
    (i.e. the honest `SLA_STATUS = INCONCLUSIVE` disposition, governing
    instruction sec. 25) always passes -- there is no threshold to have
    fabricated."""
    if threshold_value is None:
        return {
            "guard": "performance_threshold_approved",
            "passed": True,
            "governance_state": GovernanceState.GREEN,
            "rationale": "No numeric threshold is asserted (SLA_STATUS=INCONCLUSIVE, per Approved SRS sec. 9.2) -- nothing to invent.",
        }
    passed = threshold_source == "SRS_APPROVED"
    return {
        "guard": "performance_threshold_approved",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Numeric threshold {threshold_value} is cited from an Approved-SRS source."
            if passed
            else f"PROHIBITED: a numeric performance threshold ({threshold_value}) was asserted with "
                 f"source {threshold_source!r}, not 'SRS_APPROVED'. Approved MVP2 SRS v1.0 sec. 9.2 "
                 "approves no numeric threshold -- never invent one."
        ),
    }


# --- 9. No response-code mutation (Wave 2 sec. 21 item 2) --------------------

def guard_no_response_code_mutation(
    testcase_id: str, original_expected_response_code, proposed_expected_response_code
) -> Dict:
    """Stress-test item #2: 'response-code modification'. An expected
    HTTP/application response code is a specific case of guard #2's
    expected-result immutability, given its own named entry point because
    sec. 21 lists it as a distinct attempted violation. Any proposed value
    that differs from the original, persisted one is rejected -- there is
    no legitimate in-scope reason for this orchestration layer to change
    what response code a frozen testcase expects."""
    passed = proposed_expected_response_code == original_expected_response_code
    return {
        "guard": "no_response_code_mutation",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Expected response code for {testcase_id} unchanged."
            if passed
            else f"PROHIBITED: an attempt was made to change {testcase_id}'s expected response code "
                 f"from {original_expected_response_code!r} to {proposed_expected_response_code!r} -- rejected. "
                 "Rule 2: NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS."
        ),
    }


# --- 10. No acceptance-criteria mutation (Wave 2 sec. 21 item 3) -------------

def guard_no_acceptance_criteria_mutation(
    requirement_id: str, original_acceptance_criteria: str, proposed_acceptance_criteria: str
) -> Dict:
    """Stress-test item #3: 'acceptance-criteria modification'. Approved
    acceptance criteria live inside the frozen Approved SRS text this
    module already hashes whole-file via `guard_srs_immutable` -- this
    guard gives the same immutability rule a requirement-scoped, directly
    testable entry point (sec. 14: 'A replan must NOT... alter approved
    acceptance criteria'), independent of whether the full-file hash guard
    also ran in a given call site."""
    passed = proposed_acceptance_criteria == original_acceptance_criteria
    return {
        "guard": "no_acceptance_criteria_mutation",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Acceptance criteria for {requirement_id} unchanged."
            if passed
            else f"PROHIBITED: an attempt was made to alter {requirement_id}'s approved acceptance criteria "
                 "-- rejected. Rule 2: NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS."
        ),
    }


# --- 11. Replan must not override an existing Human Review boundary ---------

def guard_replan_does_not_bypass_human_review(
    existing_human_review_boundary: bool, proposed_replan_action: str
) -> Dict:
    """Sec. 13: 'Do not allow a replan to override an existing Human
    Review boundary.' Sec. 14: 'A replan must NOT... bypass Human
    Review.' If a prior stage already produced a HUMAN_REVIEW_REQUIRED
    boundary for this failure, only HUMAN_REVIEW or ACTION_DEFERRED may
    follow it -- a replan that proposes RETRY/REPLAN/any auto-executing
    action instead is a silent override and is rejected, regardless of
    how confident the replanning logic claims to be."""
    ALLOWED_AFTER_HUMAN_REVIEW = {"HUMAN_REVIEW", "HUMAN_REVIEW_REQUIRED", "ACTION_DEFERRED", "ACTION_DEFERRED_TO_HUMAN"}
    if not existing_human_review_boundary:
        return {
            "guard": "replan_does_not_bypass_human_review",
            "passed": True,
            "governance_state": GovernanceState.GREEN,
            "rationale": "No existing Human Review boundary is in force -- nothing for a replan to override.",
        }
    passed = proposed_replan_action in ALLOWED_AFTER_HUMAN_REVIEW
    return {
        "guard": "replan_does_not_bypass_human_review",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"Existing Human Review boundary preserved -- proposed action {proposed_replan_action!r} "
            "still routes to a human."
            if passed
            else f"PROHIBITED: an existing Human Review boundary is in force, but the replan proposed "
                 f"{proposed_replan_action!r}, which would auto-execute past it. Sec. 13-14: a replan must "
                 "never override an existing Human Review boundary. STOP -> REPORT -> HUMAN + DI DECIDE."
        ),
    }


# --- 12. No silent baseline change (Wave 2 sec. 21 item 7, sec. 26) ---------

def guard_no_silent_baseline_change(baseline_commit: str, protected_paths: List[str]) -> Dict:
    """Stress-test item #7: 'silent baseline change'. Real, deterministic
    check: `git diff --quiet <baseline_commit> -- <protected_paths>`
    against the live working tree, run as a real subprocess against this
    repository. A nonzero exit code means at least one protected path has
    drifted from the named frozen baseline -- reported as a governance
    failure, never silently accepted. `git` itself is the source of
    truth here, not a hand-rolled hash comparison, so renamed/moved
    protected files are still caught."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--quiet", baseline_commit, "--", *protected_paths],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
    except FileNotFoundError as exc:
        return {
            "guard": "no_silent_baseline_change",
            "passed": False,
            "governance_state": GovernanceState.RED,
            "rationale": f"Could not run `git diff` to verify baseline integrity: {exc}",
        }
    passed = proc.returncode == 0
    return {
        "guard": "no_silent_baseline_change",
        "passed": passed,
        "governance_state": GovernanceState.GREEN if passed else GovernanceState.RED,
        "rationale": (
            f"`git diff --quiet {baseline_commit}` reports zero drift across {len(protected_paths)} "
            "protected path(s)."
            if passed
            else f"PROHIBITED: `git diff {baseline_commit}` reports real drift against a protected "
                 f"baseline across one or more of {protected_paths}. Sec. 26: report any drift explicitly, "
                 "never silently. STOP -> REPORT -> HUMAN + DI DECIDE."
        ),
    }
