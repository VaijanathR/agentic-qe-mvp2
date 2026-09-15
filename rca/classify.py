"""
CP-MVP2-07 — deterministic failure classification.

Reuses `execution.schema.FailureCategory`/`FailureSubtype`/
`FAILURE_SUBTYPE_TO_CATEGORY` verbatim (frozen CP-MVP2-06 vocabulary,
imported, never redefined) -- per the frozen CP-MVP2-07 specification
sec. 5. The base category is trusted from the real, persisted
`ExecutionResult.failure_classification` field (already computed by the
frozen, unmodified `execution.pipeline.run_cp_mvp2_06()`); the SUBTYPE
is independently *re-derived* here from the same real step-level
evidence the frozen pipeline itself used (defense-in-depth re-
verification, mirroring this project's standing "never just trust
upstream blindly" precedent), never merely copied from a stored value
the frozen schema does not actually persist.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

from automation.schema import ActionType
from execution.schema import FAILURE_SUBTYPE_TO_CATEGORY, FailureSubtype, OverallStatus, StepStatus


def reclassify_from_evidence(execution_result: Dict) -> Tuple[Optional[str], Optional[str]]:
    """Returns (category, subtype). Both None for a genuine PASS/
    NOT_EXECUTED with no failure. Mirrors, independently, the exact
    subtype logic `execution/pipeline.py::run_cp_mvp2_06` already
    applies -- re-derived from real step_results, not merely trusted."""
    if execution_result["overall_status"] in (OverallStatus.PASS, OverallStatus.NOT_EXECUTED):
        return None, None

    step_results = execution_result.get("step_results", [])
    failed_steps = [s for s in step_results if s["status"] in (StepStatus.FAIL, StepStatus.ERROR)]

    if not failed_steps:
        # A FAIL/ERROR/BLOCKED with no failed step (e.g. a BUSINESS_REQUIRED
        # assertion that simply did not hold, or a design-time/governance
        # block) -- category is trusted from the real, stored field;
        # no step-level subtype applies.
        return execution_result.get("failure_classification"), None

    failed = failed_steps[0]
    error_info = failed.get("error_information") or ""
    if any(s["status"] == StepStatus.ERROR for s in failed_steps):
        errored = next(s for s in failed_steps if s["status"] == StepStatus.ERROR)
        subtype = (
            FailureSubtype.LOCATOR_FAILURE
            if errored["action_type"] in (ActionType.FILL, ActionType.CLICK, ActionType.SELECT)
            else FailureSubtype.BROWSER_LAUNCH_FAILURE
        )
    elif "TIMEOUT" in error_info:
        subtype = FailureSubtype.TIMEOUT
    elif failed["action_type"] == ActionType.NAVIGATE:
        subtype = FailureSubtype.NAVIGATION_FAILURE
    else:
        subtype = FailureSubtype.ASSERTION_FAILURE

    category = FAILURE_SUBTYPE_TO_CATEGORY.get(subtype, execution_result.get("failure_classification"))
    return category, subtype
