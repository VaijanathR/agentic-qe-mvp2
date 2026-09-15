"""
Agentic QE Orchestration -- adapter from Enhancement-01/02's real
`automation.playwright.logging_.ExecutionLogRecord` to CP-MVP2-06/07's
`execution.schema.ExecutionResult` shape.

Why this exists: CP-MVP2-07's real RCA/Replanning/Governance pipeline
(`rca.pipeline.run_cp07_rca`) is real and fully reusable, but it reads
`ExecutionResult` JSON from `runs/YYYY/MM/DD/<execution_id>/final_result.json`
(via `execution.persist.persist_execution_result`, unmodified) -- the
schema CP-MVP2-06's own execution engine produces. Enhancement-01/02's
real Playwright executions use a different, later, Page-Object-based
architecture with its own `ExecutionLogRecord` schema, persisted
separately under `automation/playwright/generated/executions/`.

This module performs a structural, field-preserving translation --
never inventing a step, a status, or an outcome that the real
`ExecutionLogRecord` did not already contain -- so this orchestration
package can reuse CP-07's real RCA logic unmodified, rather than
reimplementing it (governing instruction sec. 7 "Reuse existing
components. Do not reinvent working infrastructure."). Both the source
`ExecutionLogRecord` and the adapted `ExecutionResult` remain real,
persisted, and independently inspectable.

`action_type` inference: `ExecutionLogRecord.steps[].description` is a
free-text business-step description with no structured action_type
field. This adapter classifies it with a small, disclosed keyword
heuristic (Navigate.../Fill.../Select|click.../Observe... -> NAVIGATE/
FILL/CLICK/ASSERT) -- genuinely derived from the real description text,
never fabricated, and disclosed here rather than silently assumed.
"""
from __future__ import annotations

import re
from typing import Dict, Optional

from automation.schema import ActionType
from execution.persist import persist_execution_result
from execution.schema import AssertionResult, ExecutionResult, OverallStatus, StepResult, StepStatus

_STATUS_MAP = {
    "PASS": StepStatus.PASS,
    "FAIL": StepStatus.FAIL,
    "ERROR": StepStatus.ERROR,
    "NOT_EXECUTED": StepStatus.NOT_EXECUTED,
}

_OVERALL_STATUS_MAP = {
    "PASS": OverallStatus.PASS,
    "FAIL": OverallStatus.FAIL,
    "ERROR": OverallStatus.ERROR,
    "NOT_EXECUTED": OverallStatus.NOT_EXECUTED,
}

_NAV_RE = re.compile(r"^(navigate|as an anonymous session, )", re.IGNORECASE)
_FILL_RE = re.compile(r"\bfill\b", re.IGNORECASE)
_SELECT_RE = re.compile(r"\b(select|check|click|accept|submit|confirm)\b", re.IGNORECASE)
_OBSERVE_RE = re.compile(r"\bobserve\b", re.IGNORECASE)


def _infer_action_type(description: str) -> str:
    if _NAV_RE.search(description):
        return ActionType.NAVIGATE
    if _FILL_RE.search(description):
        return ActionType.FILL
    if _OBSERVE_RE.search(description):
        return ActionType.ASSERT
    if _SELECT_RE.search(description):
        return ActionType.CLICK
    return ActionType.ASSERT


def adapt_and_persist(execution_log: Dict) -> Dict:
    """Translates one real, persisted `ExecutionLogRecord` dict into a
    CP-06-shaped `ExecutionResult` and persists it via the unmodified
    `execution.persist.persist_execution_result`, so
    `rca.pipeline.run_cp07_rca(execution_id)` can ingest it. Returns the
    persist result dict (`{"execution_id": ..., "path": ...}`)."""
    step_results = []
    for s in execution_log.get("steps", []):
        step_results.append(
            StepResult(
                step_order=s["step_order"],
                action_type=_infer_action_type(s.get("description", "")),
                target_locator_reference=(
                    (s.get("locator_resolution") or {}).get("resolved_candidate", {}) or {}
                ).get("expression"),
                status=_STATUS_MAP.get(s.get("status"), StepStatus.NOT_EXECUTED),
                observed_result=s.get("description"),
                error_information=s.get("error_detail"),
            )
        )

    overall_status = _OVERALL_STATUS_MAP.get(execution_log.get("final_status"), OverallStatus.NOT_EXECUTED)
    assertion_results = [
        AssertionResult(
            assertion_type="BUSINESS_REQUIRED",
            condition=f"execution final_status == PASS (adapted from ExecutionLogRecord {execution_log['execution_id']})",
            source="orchestration.execution_result_adapter",
            counts_toward_coverage=True,
            passed=(overall_status == OverallStatus.PASS),
            observed=execution_log.get("final_status"),
        )
    ]

    result = ExecutionResult(
        execution_id=execution_log["execution_id"],
        automation_id=execution_log["automation_id"],
        testcase_id=execution_log["testcase_id"],
        requirement_ids=list(execution_log.get("requirement_ids", [])),
        test_data_set_id=execution_log.get("dataset_id"),
        journey_id=None,
        scenario_type="ADAPTED_FROM_PLAYWRIGHT_EXECUTION_LOG",
        browser=execution_log.get("browser"),
        execution_start=execution_log.get("start_time"),
        execution_end=execution_log.get("end_time"),
        duration_seconds=execution_log.get("duration_seconds"),
        overall_status=overall_status,
        step_results=step_results,
        assertion_results=assertion_results,
        evidence_references=list(execution_log.get("evidence_references", [])),
        failure_classification=execution_log.get("failure_category"),
        failure_summary=execution_log.get("error_detail"),
        source_attribution=[{"source": "automation/playwright/generated/executions", "execution_id": execution_log["execution_id"]}],
        environment_metadata={"environment": execution_log.get("environment"), "worker_id": execution_log.get("worker_id"), "browser_version": execution_log.get("browser_version")},
        governance_status="ADAPTED",
        notes=["Adapted by orchestration.execution_result_adapter from a real Enhancement-01/02 ExecutionLogRecord -- never a fabricated ExecutionResult."],
    )
    return persist_execution_result(result)
