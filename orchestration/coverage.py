"""
Agentic QE Orchestration -- Coverage (governing instruction sec. 47, 48).

Builds the 7 separately-reported coverage dimensions from real, already-
persisted evidence only (`reporting.gather`, `reporting.requirement_coverage`,
`automation.playwright.logging_`) -- never merges them into one misleading
overall number, and always preserves the Generated != Executable !=
Executed != Passed != Fully Covered distinctions (sec. 11/47):

  GENERATED   -- a testcase/dataset/automation artifact exists on disk.
  EXECUTABLE  -- the artifact is registered as real, runnable automation
                 (an automation_id is declared for it).
  EXECUTED    -- at least one real, persisted execution log exists for it.
  PASSED      -- the most recent real execution's final_status is PASS.
  FULLY_COVERED -- disposition is FUNCTIONAL_AUTOMATABLE /
                 FUNCTIONAL_AND_PERFORMANCE AND executed AND passed (a
                 requirement can be "executed" without being "fully
                 covered" if its most recent run failed).
"""
from __future__ import annotations

from typing import Dict, List

from automation.playwright.config import EXECUTIONS_ROOT
from automation.playwright.logging_ import list_execution_log_ids
from orchestration.safe_persistence import safe_load_latest
from reporting.requirement_coverage import Disposition, REQUIREMENT_COVERAGE, disposition_breakdown


def _latest_execution_status(execution_ids: List[str], all_logs_cache: Dict[str, Dict]) -> str:
    statuses = [all_logs_cache[eid]["final_status"] for eid in execution_ids if eid in all_logs_cache]
    if not statuses:
        return "NOT_EXECUTED"
    return statuses[-1]


def build_coverage_report() -> Dict:
    all_log_ids = list_execution_log_ids()
    all_logs_cache: Dict[str, Dict] = {}
    for eid in all_log_ids:
        record = safe_load_latest(EXECUTIONS_ROOT, eid)
        if record is not None:
            all_logs_cache[eid] = record

    requirement_rows = []
    for r in REQUIREMENT_COVERAGE:
        real_execution_ids = [eid for eid, log in all_logs_cache.items() if log["testcase_id"] in r.testcase_ids]
        generated = bool(r.testcase_ids)
        executable = bool(r.automation_ids) or any(
            log["automation_id"] for eid, log in all_logs_cache.items() if eid in real_execution_ids
        )
        executed = bool(real_execution_ids)
        latest_status = _latest_execution_status(real_execution_ids, all_logs_cache)
        passed = latest_status == "PASS"
        fully_covered = (
            r.disposition in (Disposition.FUNCTIONAL_AUTOMATABLE, Disposition.FUNCTIONAL_AND_PERFORMANCE)
            and executed and passed
        )
        requirement_rows.append(
            {
                "requirement_id": r.requirement_id,
                "disposition": r.disposition,
                "generated": generated,
                "executable": executable,
                "executed": executed,
                "passed": passed,
                "fully_covered": fully_covered,
                "real_execution_ids": real_execution_ids,
            }
        )

    n = len(requirement_rows)
    return {
        "requirement_coverage": {
            "total": n,
            "disposition_breakdown": disposition_breakdown(),
        },
        "testcase_coverage": {
            "total_requirements_with_testcase": sum(1 for r in requirement_rows if r["generated"]),
        },
        "automation_coverage": {
            "total_requirements_with_automation": sum(1 for r in requirement_rows if r["executable"]),
        },
        "execution_coverage": {
            "total_requirements_executed": sum(1 for r in requirement_rows if r["executed"]),
            "total_requirements_passed_latest": sum(1 for r in requirement_rows if r["passed"]),
        },
        "evidence_coverage": {
            "total_real_execution_logs": len(all_logs_cache),
        },
        "performance_coverage": {
            "total_requirements_performance_relevant": sum(1 for r in REQUIREMENT_COVERAGE if r.performance_testcase_ids),
        },
        "fully_covered_count": sum(1 for r in requirement_rows if r["fully_covered"]),
        "requirement_rows": requirement_rows,
        "distinction_note": (
            "Generated != Executable != Executed != Passed != Fully Covered -- each requirement row above "
            "reports all five independently; none is collapsed into a single misleading status."
        ),
    }
