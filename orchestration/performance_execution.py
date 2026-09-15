"""
Agentic QE Orchestration -- Performance Orchestration (governing
instruction sec. 25, 26).

Wraps CP-MVP2-08's real, unmodified JMeter execution pipeline
(`performance.pipeline.run_cp08_performance_scenario`). That pipeline is
scoped to exactly one, already-committed scenario
(`PERF-REQ-BRW-01-catalog-browse.jmx`, REQ-BRW-01) -- this module does
not generalize or modify it (governing instruction sec. 4 "existing
performance implementation" is a protected historical asset); it
determines performance relevance from the real requirement coverage
matrix and, for REQ-BRW-01 specifically, invokes the real pipeline
unchanged. Never invents a numeric threshold -- `SLA_STATUS` is always
read straight from the real `NumericSLAResult`/`numeric_sla_result`
field the pipeline itself produces (always INCONCLUSIVE, per Approved
SRS sec. 9.2 -- no numeric threshold is approved for this project).
"""
from __future__ import annotations

from typing import Dict, Optional

from performance.pipeline import run_cp08_performance_scenario
from reporting.requirement_coverage import REQUIREMENT_COVERAGE


def is_performance_relevant(requirement_id: str) -> bool:
    coverage = next((r for r in REQUIREMENT_COVERAGE if r.requirement_id == requirement_id), None)
    return bool(coverage and coverage.performance_testcase_ids)


def execute_real(requirement_id: str, run_id: Optional[str] = None) -> Dict:
    if requirement_id != "REQ-BRW-01":
        return {
            "requirement_id": requirement_id,
            "status": "NOT_APPLICABLE",
            "note": "The real CP-MVP2-08 JMeter pipeline is scoped to REQ-BRW-01's own committed "
                    ".jmx scenario only (governing instruction sec. 4: protected historical asset, "
                    "never generalized/modified by this orchestration layer).",
        }
    result = run_cp08_performance_scenario(run_id=run_id)
    result["requirement_id"] = requirement_id
    result["sla_status"] = result["record"]["numeric_sla_result"]
    result["sla_status_detail"] = result["record"]["numeric_sla_result_detail"]
    return result
