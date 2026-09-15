"""
Post-MVP2 Enhancement 02 -- shared real-execution logging helper, factored
out of the per-test boilerplate `automation/playwright/tests/
test_enh01_registration.py` first established, to avoid copy-pasting it
into every one of this enhancement's many new tests (governing
instruction sec. 10: "avoid copy/paste implementations").
"""
from __future__ import annotations

import datetime
import time
from contextlib import contextmanager
from typing import Callable, Dict, List, Optional

from automation.playwright.evidence import relative_evidence_refs, screenshot_path
from automation.playwright.logging_ import ExecutionLogRecord, ExecutionStatus, now_iso, persist_execution_log


@contextmanager
def real_execution(
    *,
    testcase_id: str,
    requirement_ids: List[str],
    dataset_id: str,
    automation_id: str,
    page,
    browser_version: str,
    worker_id: str,
    run_label: str = "",
):
    """Context manager that yields a mutable `steps` list the caller
    appends real StepLogEntry-shaped dicts to, and a `mark(status,
    failure_category=None, error_detail=None)` callback the caller must
    call exactly once with the real, observed final outcome. Always
    persists a full ExecutionLogRecord and a real screenshot on exit --
    PASS, FAIL, or a genuine unhandled exception (never silently
    swallowed; re-raised after logging as ERROR)."""
    execution_id = f"{automation_id}-{run_label or dataset_id}-{worker_id}-{int(time.time() * 1000)}"
    start_time = now_iso()
    steps: List[Dict] = []
    outcome = {"status": ExecutionStatus.NOT_EXECUTED, "failure_category": None, "error_detail": None}

    def mark(status: str, failure_category: Optional[str] = None, error_detail: Optional[str] = None) -> None:
        outcome["status"] = status
        outcome["failure_category"] = failure_category
        outcome["error_detail"] = error_detail

    try:
        yield steps, mark
    except Exception as exc:
        outcome["status"] = ExecutionStatus.ERROR
        outcome["failure_category"] = "TOOL_ISSUE"
        outcome["error_detail"] = repr(exc)
        steps.append({"step_order": len(steps) + 1, "description": "Unhandled exception", "status": "ERROR", "error_detail": repr(exc)})
        raise
    finally:
        try:
            page.screenshot(path=str(screenshot_path(execution_id, "final_state")))
        except Exception:
            pass
        end_time = now_iso()
        duration_seconds = (datetime.datetime.fromisoformat(end_time) - datetime.datetime.fromisoformat(start_time)).total_seconds()
        record = ExecutionLogRecord(
            execution_id=execution_id,
            requirement_ids=requirement_ids,
            testcase_id=testcase_id,
            dataset_id=dataset_id,
            automation_id=automation_id,
            browser="chromium",
            browser_version=browser_version,
            environment="Windows",
            worker_id=worker_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            steps=steps,
            final_status=outcome["status"],
            failure_category=outcome["failure_category"],
            error_detail=outcome["error_detail"],
            evidence_references=relative_evidence_refs(execution_id),
            generation_metadata={"generator": "automation.playwright (Post-MVP2 Enhancement 02)"},
        )
        persist_execution_log(record)
