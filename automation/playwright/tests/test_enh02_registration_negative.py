"""Post-MVP2 Enhancement 02 -- real, non-mocked execution of
ENH02-TC-REQ-REG-02-MISMATCH and ENH02-TC-REQ-REG-03-MALFORMED-EMAIL
against the real SUT. Both non-mutating: real form submissions that the
SUT rejects, so no account is ever created."""
from __future__ import annotations

from automation.playwright.components.navigation import start_at_home
from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.tests.enh02_helpers import real_execution
from automation.playwright.logging_ import ExecutionStatus

REQUIRED_FIELDS = ["first_name", "last_name", "email", "password", "confirm_password"]


def _fill_and_submit(registration, dataset):
    steps = []
    for field, method in [
        ("first_name", registration.fill_first_name), ("last_name", registration.fill_last_name),
        ("email", registration.fill_email), ("password", registration.fill_password),
        ("confirm_password", registration.fill_confirm_password),
    ]:
        resolution = method(dataset.fields[field])
        steps.append({"step_order": len(steps) + 1, "description": f"Fill {field}", "status": "PASS" if resolution["resolved_candidate"] else "FAIL", "locator_resolution": resolution})
    submit_resolution = registration.submit()
    steps.append({"step_order": len(steps) + 1, "description": "Submit registration form", "status": "PASS" if submit_resolution["resolved_candidate"] else "FAIL", "locator_resolution": submit_resolution})
    return steps


def test_registration_rejects_mismatched_password(browser_page, worker_id):
    page, browser_version = browser_page
    dataset = load_dataset("ENH02-TD-REG-02-01", required_fields=REQUIRED_FIELDS)
    with real_execution(
        testcase_id="ENH02-TC-REQ-REG-02-MISMATCH", requirement_ids=["REQ-REG-02"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-REG-02-MISMATCH",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})
        registration, nav_resolution = home.go_to_registration()
        steps.append({"step_order": 2, "description": "Select 'Register' link", "status": "PASS", "locator_resolution": nav_resolution.to_dict()})
        steps.extend(_fill_and_submit(registration, dataset))
        page.wait_for_timeout(500)
        result_text = registration.result_text()
        expected = "The password and confirmation password do not match."
        observed = expected in result_text
        steps.append({"step_order": len(steps) + 1, "description": "Observe password-mismatch message", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"Expected '{expected}' not found")
        assert observed, f"Real execution did not observe the expected mismatch message"


def test_registration_rejects_malformed_email(browser_page, worker_id):
    page, browser_version = browser_page
    dataset = load_dataset("ENH02-TD-REG-03-01", required_fields=REQUIRED_FIELDS)
    with real_execution(
        testcase_id="ENH02-TC-REQ-REG-03-MALFORMED-EMAIL", requirement_ids=["REQ-REG-03"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-REG-03-MALFORMED-EMAIL",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})
        registration, nav_resolution = home.go_to_registration()
        steps.append({"step_order": 2, "description": "Select 'Register' link", "status": "PASS", "locator_resolution": nav_resolution.to_dict()})
        steps.extend(_fill_and_submit(registration, dataset))
        page.wait_for_timeout(500)
        result_text = registration.result_text()
        expected = "Wrong email"
        observed = expected in result_text
        steps.append({"step_order": len(steps) + 1, "description": "Observe email-format message", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"Expected '{expected}' not found")
        assert observed, "Real execution did not observe the expected malformed-email message"
