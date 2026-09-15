"""
Agentic QE Orchestration -- RCA (governing instruction sec. 30).

Thin wrapper: adapts a real Enhancement-01/02 `ExecutionLogRecord` into
CP-MVP2-06's `ExecutionResult` shape (`execution_result_adapter.py`),
then invokes CP-MVP2-07's real, unmodified, fully deterministic RCA
pipeline (`rca.pipeline.run_cp07_rca`). No RCA logic is reimplemented
here -- `Observed Evidence -> Candidate Causes -> Evidence Comparison ->
Most Supported Cause -> Confidence -> Recommended Action` is exactly
CP-07's own real, frozen pipeline (`rca/analyze.py::build_rca_record`).
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.config import EXECUTIONS_ROOT
from orchestration.execution_result_adapter import adapt_and_persist
from orchestration.safe_persistence import safe_load_latest
from rca.pipeline import run_cp07_rca


def run_rca_for_execution(execution_id: str) -> Dict:
    execution_log = safe_load_latest(EXECUTIONS_ROOT, execution_id)
    if execution_log is None:
        return {"status": "BLOCKED", "reason": f"No real, persisted ExecutionLogRecord found for execution_id={execution_id!r}."}

    adapt_and_persist(execution_log)
    return run_cp07_rca(execution_id)
