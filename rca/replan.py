"""
CP-MVP2-07 — governed replanning decision.

Fully deterministic, rule-based. Never proposes an action that would
require modifying a frozen testcase/requirement/spec, inventing a
missing business step, or implementing runtime locator fallback
(CR-002 remains unauthorized -- frozen CP-07 spec sec. 8/10). A
`REPLAN_NOT_ALLOWED`/`HUMAN_REVIEW_REQUIRED` outcome is a valid,
complete result -- never converted into a manufactured `REPLAN_ALLOWED`
merely to exercise the feature.
"""
from __future__ import annotations

from typing import Optional

from execution.schema import FailureSubtype, OverallStatus
from rca.schema import Confidence, RCARecord, ReplanningDecision, ReplanningRecord


def decide_replanning(rca: RCARecord, execution_result_overall_status: str) -> ReplanningRecord:
    if execution_result_overall_status == OverallStatus.PASS:
        decision = ReplanningDecision.REPLAN_NOT_ALLOWED
        reason = "Execution PASSED; there is nothing to replan."
        proposed_change = None
        governance_impact = "None."
        human_approval_required = False
        affected: list = []
        benefit: Optional[str] = None

    elif rca.final_rca_subtype == FailureSubtype.LOCATOR_FAILURE:
        # The only automated corrective action for a genuine locator
        # failure would be runtime locator fallback -- CR-002's exclusive,
        # currently-unauthorized scope. CP-07 never implements it.
        decision = ReplanningDecision.GOVERNANCE_BLOCKED
        reason = (
            "The only automated corrective action for a LOCATOR_FAILURE is runtime locator "
            "fallback, which is CR-002's exclusive scope. CR-002 is PROPOSED -- NOT AUTHORIZED "
            "(docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md). No automated action is "
            "governed for this failure class."
        )
        proposed_change = "RECOMMENDATION ONLY: authorize and implement CR-002."
        governance_impact = "Would require amending frozen CP-MVP2-06 sec. 14/15 via a real, separately-authorized Change Request."
        human_approval_required = True
        affected = [rca.automation_id]
        benefit = "Would allow this specific locator failure class to self-recover using already-evidenced fallback candidates."

    elif rca.confidence != Confidence.HIGH:
        decision = ReplanningDecision.HUMAN_REVIEW_REQUIRED
        reason = f"RCA confidence is {rca.confidence}, not HIGH -- insufficient certainty for any automated recommendation to be acted on without Human + Di review."
        proposed_change = None
        governance_impact = "None -- no action proposed."
        human_approval_required = True
        affected = [rca.testcase_id]
        benefit = None

    else:
        # High-confidence, non-locator failure (this project's real,
        # current case: a testcase-content/precondition limitation).
        # The only real corrective action (authoring richer testcase
        # content) requires content CP-07 has no authority to invent.
        decision = ReplanningDecision.HUMAN_REVIEW_REQUIRED
        reason = (
            "A high-confidence root cause was established, but the only real corrective action "
            "(authoring richer, specific testcase content establishing the missing precondition) "
            "requires inventing business-step content this checkpoint has no authority to invent "
            "(frozen CP-MVP2-07 spec sec. 9 / governing instruction sec. 9). Selecting and "
            "authorizing that future work is a Human + Di decision."
        )
        proposed_change = (
            "RECOMMENDATION ONLY, NOT APPLIED: a future, separately-authorized task should author "
            "a specific testcase (e.g. via real, non-stub testcase generation) that includes the "
            "precondition-establishing business steps this scenario requires."
        )
        governance_impact = "None to CP-06/CP-07 themselves; would require a new, separately-authorized testcase-generation task, not a specification change."
        human_approval_required = True
        affected = [rca.testcase_id, rca.automation_id]
        benefit = "Would allow this scenario to reach a genuine, meaningful business-level PASS/FAIL instead of an environment-level TIMEOUT."

    return ReplanningRecord(
        replanning_id=f"REPLAN-{rca.rca_id}",
        rca_id=rca.rca_id,
        execution_id=rca.execution_id,
        decision=decision,
        reason=reason,
        evidence_refs=[rca.rca_id, rca.execution_id],
        proposed_change=proposed_change,
        affected_artifacts=affected,
        expected_benefit=benefit,
        governance_impact=governance_impact,
        human_approval_required=human_approval_required,
        generation_metadata={"generator": "deterministic-only (no LLM anywhere in CP-MVP2-07 replanning)"},
    )
