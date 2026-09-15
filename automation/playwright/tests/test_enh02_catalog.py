"""Post-MVP2 Enhancement 02 -- real execution of
ENH02-TC-REQ-SRCH-01-VALID-KEYWORD, ENH02-TC-REQ-SRCH-02-NO-RESULTS, and
ENH02-TC-REQ-BRW-01-CATEGORY-GRID. All safe, read-only GET traffic."""
from __future__ import annotations

from automation.playwright.components.navigation import start_at_home
from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.catalog_pages import CategoryPage
from automation.playwright.pages.search_page import SearchPage
from automation.playwright.tests.enh02_helpers import real_execution


def test_search_returns_results_for_valid_keyword(browser_page, worker_id):
    page, browser_version = browser_page
    dataset = load_dataset("ENH02-TD-SRCH-01-01", required_fields=["search_term"])
    with real_execution(
        testcase_id="ENH02-TC-REQ-SRCH-01-VALID-KEYWORD", requirement_ids=["REQ-SRCH-01"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-SRCH-01-VALID-KEYWORD",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})
        search = SearchPage(page, DEFAULT_CONFIG)
        resolution = search.search(dataset.fields["search_term"])
        steps.append({"step_order": 2, "description": f"Search for '{dataset.fields['search_term']}'", "status": "PASS", "locator_resolution": resolution})
        page.wait_for_timeout(500)
        has_results = search.has_results()
        steps.append({"step_order": 3, "description": "Observe at least one result renders", "status": "PASS" if has_results else "FAIL"})
        mark(ExecutionStatus.PASS if has_results else ExecutionStatus.FAIL, None if has_results else "ASSERTION_FAILURE", None if has_results else "No results rendered")
        assert has_results, "Real search did not render any results"


def test_search_shows_no_results_message(browser_page, worker_id):
    page, browser_version = browser_page
    dataset = load_dataset("ENH02-TD-SRCH-02-01", required_fields=["search_term"])
    with real_execution(
        testcase_id="ENH02-TC-REQ-SRCH-02-NO-RESULTS", requirement_ids=["REQ-SRCH-02"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-SRCH-02-NO-RESULTS",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        home = start_at_home(page, DEFAULT_CONFIG)
        steps.append({"step_order": 1, "description": "Navigate to home page", "status": "PASS"})
        search = SearchPage(page, DEFAULT_CONFIG)
        resolution = search.search(dataset.fields["search_term"])
        steps.append({"step_order": 2, "description": f"Search for nonsense keyword", "status": "PASS", "locator_resolution": resolution})
        page.wait_for_timeout(500)
        shows_message = search.shows_no_results_message()
        steps.append({"step_order": 3, "description": "Observe explicit no-results message", "status": "PASS" if shows_message else "FAIL"})
        mark(ExecutionStatus.PASS if shows_message else ExecutionStatus.FAIL, None if shows_message else "ASSERTION_FAILURE", None if shows_message else "No-results message not observed")
        assert shows_message, "Real search did not show the expected no-results message"


def test_books_category_renders_product_grid(browser_page, worker_id):
    page, browser_version = browser_page
    with real_execution(
        testcase_id="ENH02-TC-REQ-BRW-01-CATEGORY-GRID", requirement_ids=["REQ-BRW-01"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        category = CategoryPage(page, DEFAULT_CONFIG)
        category.open_books()
        steps.append({"step_order": 1, "description": "Navigate to Books category", "status": "PASS"})
        has_grid = category.has_product_grid()
        steps.append({"step_order": 2, "description": "Observe product grid renders", "status": "PASS" if has_grid else "FAIL"})
        mark(ExecutionStatus.PASS if has_grid else ExecutionStatus.FAIL, None if has_grid else "ASSERTION_FAILURE", None if has_grid else "Product grid not observed")
        assert has_grid, "Real category page did not render a product grid"
