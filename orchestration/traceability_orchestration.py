"""
Agentic QE Orchestration -- Traceability (governing instruction sec. 21).

Assembles the full Requirement -> Testcase -> Dataset -> Automation ->
Execution -> Evidence chain for one requirement from real, persisted
sources only:
  - `reporting.requirement_coverage` (Enhancement-02's real coverage
    matrix, already carrying testcase/dataset/automation/execution IDs
    for most of this project's requirements);
  - `automation.playwright.logging_` (real, persisted execution logs,
    re-verified live rather than trusted from the coverage matrix's own
    possibly-stale `execution_ids` list).

`validate()` checks for orphaned automation (an automation_id with no
real, persisted execution log) and reports it explicitly -- never
silently drops it.
"""
from __future__ import annotations

from typing import Dict, List

from automation.playwright.config import EXECUTIONS_ROOT
from automation.playwright.logging_ import list_execution_log_ids
from orchestration.safe_persistence import safe_load_latest
from reporting.requirement_coverage import REQUIREMENT_COVERAGE


def build_chain(requirement_id: str) -> Dict:
    coverage = next((r for r in REQUIREMENT_COVERAGE if r.requirement_id == requirement_id), None)
    if coverage is None:
        return {
            "requirement_id": requirement_id,
            "found": False,
            "chain": [],
            "note": "Requirement not present in the real requirement coverage matrix.",
        }

    all_logs = list_execution_log_ids()
    execution_entries = []
    for eid in all_logs:
        record = safe_load_latest(EXECUTIONS_ROOT, eid)
        if record and record.get("testcase_id") in coverage.testcase_ids:
            execution_entries.append(
                {
                    "execution_id": eid,
                    "testcase_id": record["testcase_id"],
                    "dataset_id": record["dataset_id"],
                    "automation_id": record["automation_id"],
                    "final_status": record["final_status"],
                    "evidence_references": record.get("evidence_references", []),
                }
            )

    return {
        "requirement_id": requirement_id,
        "found": True,
        "disposition": coverage.disposition,
        "testcase_ids": list(coverage.testcase_ids),
        "dataset_ids": list(coverage.dataset_ids),
        "declared_automation_ids": list(coverage.automation_ids),
        "declared_execution_ids": list(coverage.execution_ids),
        "real_executions": execution_entries,
        "performance_testcase_ids": list(coverage.performance_testcase_ids),
    }


def validate(chain: Dict) -> Dict:
    if not chain.get("found"):
        return {"valid": False, "orphans": [], "note": chain.get("note", "Requirement not found.")}

    real_automation_ids = {e["automation_id"] for e in chain["real_executions"]}
    orphaned_automation = [
        aid for aid in chain["declared_automation_ids"] if aid and aid not in real_automation_ids
    ]
    no_execution_testcases = [
        tc for tc in chain["testcase_ids"]
        if tc not in {e["testcase_id"] for e in chain["real_executions"]}
    ]

    valid = not orphaned_automation
    return {
        "valid": valid,
        "orphaned_automation_ids": orphaned_automation,
        "testcases_without_real_execution": no_execution_testcases,
        "note": (
            "Full chain intact: every declared automation_id has at least one real, persisted execution log."
            if valid
            else f"Orphaned automation detected (declared but no real execution log found): {orphaned_automation}."
        ),
    }
