"""
Agentic QE Orchestration -- Regression Selection (governing instruction
sec. 46).

Deterministic selection built on real, already-computed impact-analysis
output (`orchestration.impact.analyze`). Actual execution of the selected
scope is left to the caller (typically the orchestrator invoking the
project's own established `pytest` invocation conventions -- this module
never spawns a subprocess itself, so it can be unit-tested without a
real SUT/browser).
"""
from __future__ import annotations

from typing import Dict, List


class RegressionScope:
    TARGETED_REGRESSION = "TARGETED_REGRESSION"
    DEPENDENCY_REGRESSION = "DEPENDENCY_REGRESSION"
    RISK_REGRESSION = "RISK_REGRESSION"
    FULL_REGRESSION = "FULL_REGRESSION"


def select_scope(impact_result: Dict, risk_result: Dict, force_full: bool = False) -> Dict:
    if force_full:
        return {
            "scope": RegressionScope.FULL_REGRESSION,
            "testcase_ids": None,
            "explanation": "Full regression explicitly requested (e.g. pre-freeze gate).",
        }

    direct = impact_result.get("directly_impacted_testcase_ids", [])
    indirect = impact_result.get("indirectly_impacted_testcase_ids", [])

    high_risk_ids = [
        r["testcase_id"] for r in risk_result.get("records", [])
        if r.get("priority") in ("P0", "P1")
    ]

    if high_risk_ids:
        scope = RegressionScope.RISK_REGRESSION
        testcase_ids = sorted(set(direct) | set(indirect) | set(high_risk_ids))
        explanation = (
            f"{len(high_risk_ids)} high-priority (P0/P1) testcase(s) identified by RBTP risk assessment "
            "-- included alongside directly/indirectly impacted testcases."
        )
    elif indirect:
        scope = RegressionScope.DEPENDENCY_REGRESSION
        testcase_ids = sorted(set(direct) | set(indirect))
        explanation = f"{len(indirect)} indirectly-impacted testcase(s) found via the dependency matrix -- included."
    elif direct:
        scope = RegressionScope.TARGETED_REGRESSION
        testcase_ids = sorted(set(direct))
        explanation = f"Only {len(direct)} directly-impacted testcase(s) -- no dependency/risk expansion needed."
    else:
        scope = RegressionScope.FULL_REGRESSION
        testcase_ids = None
        explanation = "No impact data available -- falling back to full regression rather than risking an under-scoped run."

    return {"scope": scope, "testcase_ids": testcase_ids, "explanation": explanation}
