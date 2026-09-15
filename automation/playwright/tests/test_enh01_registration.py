"""
Post-MVP2 Enhancement 01 -- real, non-mocked Playwright execution of
`ENH01_TC_REQ_REG_01_BLANK_VALIDATION` against the real SUT
(https://demowebshop.tricentis.com/).

Parametrized over TWO real, persisted, `ACCEPTED` datasets
(`TD-TC-REQ-REG-01-01-02`, `TD-TC-REQ-REG-01-01-06`), demonstrating
"one testcase -> multiple datasets" (governing instruction sec. 10) with
real evidence, not a synthetic fixture. Both datasets are the real,
already-governed "all fields blank" case -- deliberately non-mutating, so
running this test repeatedly (including in parallel, via `pytest -n`)
never creates a duplicate account on the shared, public, third-party SUT.

Every real run logs a full `ExecutionLogRecord` (sec. 23) and captures a
real screenshot (sec. 24), regardless of PASS/FAIL -- never fabricated.
"""
from __future__ import annotations

import time

import pytest

from automation.playwright.components.navigation import start_at_home
from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.enh01_testcase import ENH01_TC_REQ_REG_01_BLANK_VALIDATION as TC
from automation.playwright.evidence import relative_evidence_refs, screenshot_path
from automation.playwright.logging_ import ExecutionLogRecord, ExecutionStatus, now_iso, persist_execution_log

AUTOMATION_ID = "ENH01-PW-TC-REQ-REG-01-BLANK-VALIDATION"

REQUIRED_FIELD_MESSAGE_FRAGMENTS = [
    "First name is required",
    "Last name is required",
    "Email is required",
    "Password is required",
]


@pytest.mark.parametrize("dataset_id", TC["dataset_references"])
def test_registration_rejects_all_fields_blank(browser_page, worker_id, dataset_id):
    page, browser_version = browser_page
    execution_id = f"ENH01-REG-BLANK-{dataset_id}-{worker_id}-{int(time.time() * 1000)}"
    start_time = now_iso()
    steps = []
    final_status = ExecutionStatus.NOT_EXECUTED
    failure_category = None
    error_detail = None

    try:
        dataset = load_dataset(dataset_id, required_fields=["first_name", "last_name", "email", "password", "confirm_password"])

        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})

        registration, nav_resolution = home.go_to_registration()
        steps.append({"step_order": 2, "description": "Select 'Register' link", "status": "PASS", "locator_resolution": nav_resolution.to_dict()})

        fill_results = []
        for field, method in [
            ("first_name", registration.fill_first_name),
            ("last_name", registration.fill_last_name),
            ("email", registration.fill_email),
            ("password", registration.fill_password),
            ("confirm_password", registration.fill_confirm_password),
        ]:
            resolution = method(dataset.fields[field])
            fill_results.append(resolution)
            steps.append({
                "step_order": len(steps) + 1,
                "description": f"Fill {field} (value from {dataset_id})",
                "status": "PASS" if resolution["resolved_candidate"] else "FAIL",
                "locator_resolution": resolution,
            })

        submit_resolution = registration.submit()
        steps.append({"step_order": len(steps) + 1, "description": "Submit registration form", "status": "PASS" if submit_resolution["resolved_candidate"] else "FAIL", "locator_resolution": submit_resolution})

        page.wait_for_timeout(500)
        result_text = registration.result_text()

        observed_messages = [frag for frag in REQUIRED_FIELD_MESSAGE_FRAGMENTS if frag in result_text]
        assertion_passed = len(observed_messages) == len(REQUIRED_FIELD_MESSAGE_FRAGMENTS)
        steps.append({
            "step_order": len(steps) + 1,
            "description": "Observe required-field validation messages",
            "status": "PASS" if assertion_passed else "FAIL",
            "error_detail": None if assertion_passed else f"Observed only {observed_messages} of {REQUIRED_FIELD_MESSAGE_FRAGMENTS}",
        })

        final_status = ExecutionStatus.PASS if assertion_passed else ExecutionStatus.FAIL
        if not assertion_passed:
            failure_category = "ASSERTION_FAILURE"
            error_detail = f"Expected all of {REQUIRED_FIELD_MESSAGE_FRAGMENTS}; observed {observed_messages}"

    except Exception as exc:  # real, unexpected failure -- never swallowed
        final_status = ExecutionStatus.ERROR
        failure_category = "TOOL_ISSUE"
        error_detail = repr(exc)
        steps.append({"step_order": len(steps) + 1, "description": "Unhandled exception", "status": "ERROR", "error_detail": repr(exc)})

    finally:
        try:
            page.screenshot(path=str(screenshot_path(execution_id, "final_state")))
        except Exception:
            pass

    end_time = now_iso()
    import datetime as _dt

    duration_seconds = (
        _dt.datetime.fromisoformat(end_time) - _dt.datetime.fromisoformat(start_time)
    ).total_seconds()
    record = ExecutionLogRecord(
        execution_id=execution_id,
        requirement_ids=TC["requirement_ids"],
        testcase_id=TC["testcase_id"],
        dataset_id=dataset_id,
        automation_id=AUTOMATION_ID,
        browser="chromium",
        browser_version=browser_version,
        environment="Windows",
        worker_id=worker_id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        steps=steps,
        final_status=final_status,
        failure_category=failure_category,
        error_detail=error_detail,
        evidence_references=relative_evidence_refs(execution_id),
        generation_metadata={"generator": "automation.playwright (Post-MVP2 Enhancement 01)"},
    )
    persist_execution_log(record)

    assert final_status == ExecutionStatus.PASS, f"Real execution {execution_id} did not PASS: {error_detail}"
