"""
CP-MVP2-CR-001 Batch 1 — persisted Execution Summary.

Additive: consumes real `ExecutionResult` objects already produced by
the unmodified, frozen `run_cp_mvp2_06()`. Does not modify
`execution/schema.py`, `pipeline.py`, `engine.py`, or `evidence.py`.

Explicitly distinguishes (CR-001 sec. 14):
  - **execution coverage** — how many planned executions actually ran to
    a real, non-`NOT_EXECUTED` outcome;
  - **testcase coverage** — how many distinct `testcase_id`s appear in
    this batch, regardless of outcome;
  - **requirement coverage** — how many distinct `requirement_id`s are
    represented by at least one **passing** execution. A testcase or
    automation artifact merely *existing* for a requirement never counts
    toward requirement coverage here.
"""
from __future__ import annotations

import datetime
from typing import Dict, List

from execution.schema import ExecutionResult, OverallStatus
from persistence.envelope import REPO_ROOT, persist_artifact

BASE_DIR = REPO_ROOT / "reports" / "execution_summaries"

_ALL_STATUSES = (
    OverallStatus.PASS, OverallStatus.FAIL, OverallStatus.BLOCKED,
    OverallStatus.NOT_EXECUTED, OverallStatus.ERROR,
)


def build_execution_summary(results: List[ExecutionResult], batch_id: str) -> Dict:
    counts = {status: 0 for status in _ALL_STATUSES}
    for r in results:
        counts[r.overall_status] = counts.get(r.overall_status, 0) + 1

    executed = sum(1 for r in results if r.overall_status != OverallStatus.NOT_EXECUTED)
    testcase_ids = sorted({r.testcase_id for r in results})
    automation_ids = sorted({r.automation_id for r in results})
    all_requirement_ids = sorted({rid for r in results for rid in r.requirement_ids})
    passed_requirement_ids = sorted({rid for r in results if r.overall_status == OverallStatus.PASS for rid in r.requirement_ids})

    return {
        "batch_id": batch_id,
        "execution_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": {"testcases_planned": len(testcase_ids), "automation_count": len(automation_ids)},
        "executed_count": executed,
        "counts_by_status": counts,
        "testcase_coverage": {"total": len(testcase_ids), "testcase_ids": testcase_ids},
        "requirement_coverage": {
            "total_requirements_represented": len(all_requirement_ids),
            "requirements_with_a_passing_execution": passed_requirement_ids,
            "note": (
                "A requirement counts toward coverage here ONLY via a PASS "
                "execution result -- never merely because a testcase or "
                "automation artifact exists for it."
            ),
        },
        "evidence_locations": sorted({loc for r in results for loc in r.evidence_references}),
        "major_failures": [
            {
                "execution_id": r.execution_id,
                "failure_classification": r.failure_classification,
                "failure_summary": r.failure_summary,
            }
            for r in results if r.overall_status in (OverallStatus.FAIL, OverallStatus.ERROR)
        ],
        "limitations": sorted({note for r in results for note in r.notes}),
    }


def persist_execution_summary(summary: Dict, generator: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=summary["batch_id"],
        payload=summary,
        generator=generator,
        provenance={"kind": "execution_summary"},
    )
