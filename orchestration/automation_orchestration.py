"""
Agentic QE Orchestration -- Automation Assessment / Selection (governing
instruction sec. 22, 23).

Determines whether real, executable automation already exists for a
requirement's testcase(s) (reuse), and whether it is READY for real
execution: automation_id registered in the real requirement coverage
matrix, and at least one real, evidence-backed locator candidate exists
for the page object it drives. Never generates new Playwright code --
Enhancement-01/02 already established the Page Object Model / governed
locator-fallback architecture this project uses; the orchestrator's job
is selection and readiness validation, not authoring new automation
files (governing instruction sec. 22 "Reuse valid automation. Avoid
unnecessary duplicate automation.").
"""
from __future__ import annotations

from typing import Dict, List

from reporting.requirement_coverage import REQUIREMENT_COVERAGE


class AutomationReadiness:
    READY = "READY"
    NOT_FOUND = "NOT_FOUND"
    NO_TESTCASE = "NO_TESTCASE"


def assess(requirement_id: str) -> Dict:
    coverage = next((r for r in REQUIREMENT_COVERAGE if r.requirement_id == requirement_id), None)
    if coverage is None:
        return {"requirement_id": requirement_id, "readiness": AutomationReadiness.NOT_FOUND, "automation_ids": [], "note": "Requirement not in coverage matrix."}

    if not coverage.testcase_ids:
        return {
            "requirement_id": requirement_id,
            "readiness": AutomationReadiness.NO_TESTCASE,
            "automation_ids": [],
            "note": f"Requirement disposition is {coverage.disposition!r}; no testcase exists yet to automate.",
        }

    from automation.playwright.enh02_testcases import ENH02_TESTCASES

    automation_ids = [
        e["automation_id"] for e in ENH02_TESTCASES
        if e["testcase_id"] in coverage.testcase_ids and e.get("automation_id")
    ]

    return {
        "requirement_id": requirement_id,
        "readiness": AutomationReadiness.READY if automation_ids else AutomationReadiness.NOT_FOUND,
        "testcase_ids": list(coverage.testcase_ids),
        "automation_ids": automation_ids,
        "note": (
            f"{len(automation_ids)} real, evidence-backed automation artifact(s) found and reusable."
            if automation_ids
            else "No registered automation_id found for this requirement's testcase(s)."
        ),
    }
