"""
Agentic QE Orchestration -- real Functional (Playwright) Execution
(governing instruction sec. 23, 56, 57).

Reuses the existing Enhancement-02 Page Object Model and
`automation.playwright.tests.enh02_helpers.real_execution` logging
helper verbatim -- this module authors no new locators, no new page
objects, and no competing execution framework. It drives real business
actions already evidenced for the requirement's real testcase.

Two entry points:
  - `execute_real(...)`: drives the real, demonstrated business action for
    a given requirement in REAL_EXECUTION mode -- a genuine, non-mocked
    Playwright Chromium session against the real SUT.
  - `execute_controlled_failure(...)`: a CLEARLY-MARKED controlled test
    failure fixture (sec. 57) -- still a real Playwright session against
    the real SUT, but asserting against a deliberately non-existent
    locator, so the resulting real FAIL/ERROR execution log feeds real
    RCA/Replanning/Governance without ever fabricating a production
    failure.

Only `browser_page`-shaped `(page, browser_version)` tuples are accepted
(the same fixture shape `automation/playwright/tests/conftest.py`
provides) -- callers (the orchestrator, or a real pytest test) own
browser lifecycle; this module never launches its own browser silently.
"""
from __future__ import annotations

from typing import Dict, Tuple

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.catalog_pages import CategoryPage
from automation.playwright.tests.enh02_helpers import real_execution

CONTROLLED_FAILURE_MARKER = "CONTROLLED TEST FAILURE"


def execute_real_brw01(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """Real, non-mocked execution of REQ-BRW-01's own already-evidenced
    business action (select the 'Books' top-level category, observe a
    rendered product grid) -- the same real action
    `test_enh02_catalog.py::test_books_category_renders_product_grid`
    already established; this call produces a *fresh*, orchestrator-
    attributed execution log/execution_id for this specific
    orchestration run, rather than reusing a stale historical one."""
    execution_id_holder: Dict = {}
    with real_execution(
        testcase_id="ENH02-TC-REQ-BRW-01-CATEGORY-GRID",
        requirement_ids=["REQ-BRW-01"],
        dataset_id="NO-DATASET",
        automation_id="ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
    ) as (steps, mark):
        category = CategoryPage(page, DEFAULT_CONFIG)
        category.open_books()
        steps.append({"step_order": 1, "description": "Navigate to the Books top-level category", "status": "PASS"})
        rendered = category.has_product_grid()
        steps.append({"step_order": 2, "description": "Observe the resulting page for a rendered product grid", "status": "PASS" if rendered else "FAIL"})
        mark(ExecutionStatus.PASS if rendered else ExecutionStatus.FAIL, None if rendered else "ASSERTION_FAILURE", None if rendered else "No product grid observed")
        execution_id_holder["execution_id"] = None  # set below via closure workaround
        assert rendered, "Real REQ-BRW-01 execution did not observe a rendered product grid"

    # real_execution's own execution_id is deterministic from these same
    # inputs (automation_id-run_label-worker_id-timestamp); recomputing it
    # here would risk a mismatch, so the caller instead looks it up via
    # `automation.playwright.logging_.list_execution_log_ids()` filtered
    # to this testcase_id -- see orchestrator.py's own real usage.
    return {"testcase_id": "ENH02-TC-REQ-BRW-01-CATEGORY-GRID", "automation_id": "ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID"}


def execute_controlled_failure(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """CONTROLLED TEST FAILURE (sec. 57): a real Playwright session
    against the real SUT, asserting against a deliberately non-existent
    CSS selector (`#this-locator-does-not-exist-controlled-fixture`) on
    a real, successfully-loaded page. The navigation itself is real and
    succeeds; only the final assertion is engineered to fail, so the
    resulting execution log is a genuine LOCATOR_FAILURE-shaped FAIL --
    never a fabricated production defect."""
    with real_execution(
        testcase_id="ORCH-CONTROLLED-TEST-FAILURE-FIXTURE",
        requirement_ids=["REQ-BRW-01"],
        dataset_id="NO-DATASET",
        automation_id="ORCH-PW-CONTROLLED-TEST-FAILURE-FIXTURE",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
    ) as (steps, mark):
        category = CategoryPage(page, DEFAULT_CONFIG)
        category.open_books()
        steps.append({"step_order": 1, "description": f"{CONTROLLED_FAILURE_MARKER}: Navigate to the Books category (real, expected to succeed)", "status": "PASS"})
        deliberately_missing = page.locator("#this-locator-does-not-exist-controlled-fixture").count() > 0
        steps.append({
            "step_order": 2,
            "description": f"{CONTROLLED_FAILURE_MARKER}: assert a deliberately non-existent locator is present (engineered to fail)",
            "status": "PASS" if deliberately_missing else "FAIL",
        })
        mark(
            ExecutionStatus.FAIL if not deliberately_missing else ExecutionStatus.PASS,
            None if deliberately_missing else "ASSERTION_FAILURE",
            None if deliberately_missing else f"{CONTROLLED_FAILURE_MARKER}: deliberately-missing locator, as designed",
        )
        assert deliberately_missing, f"{CONTROLLED_FAILURE_MARKER}: this assertion is DESIGNED to fail, to real-exercise RCA/Replanning/Governance"

    return {"testcase_id": "ORCH-CONTROLLED-TEST-FAILURE-FIXTURE", "automation_id": "ORCH-PW-CONTROLLED-TEST-FAILURE-FIXTURE"}
