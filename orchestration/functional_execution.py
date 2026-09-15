"""
Agentic QE Orchestration -- real Functional (Playwright) Execution
(governing instruction sec. 23, 56, 57).

Reuses the existing Enhancement-02 Page Object Model and
`automation.playwright.tests.enh02_helpers.real_execution` logging
helper verbatim -- this module authors no new locators, no new page
objects, and no competing execution framework. It drives real business
actions already evidenced for the requirement's real testcase.

Registered real drivers, one per requirement, each reusing the exact
real business action already established in the corresponding real
pytest test file (never a new locator, never a new page object):
  - REQ-BRW-01 <- `test_enh02_catalog.py::test_books_category_renders_product_grid`
  - REQ-SRCH-01 <- `test_enh02_catalog.py::test_search_returns_results_for_valid_keyword`
  - REQ-WISH-01/02/03 <- `test_enh02_wishlist.py::test_wishlist_add_view_and_shareable_url_chain`
    (a real, in-order chain -- WISH-02/03 require WISH-01's own real
    add-to-wishlist action to have already run in the SAME page session;
    the orchestrator's dependency planning, `dependency_planning.py`,
    independently discovers this same real ordering from the testcases'
    own precondition text).

Plus `execute_controlled_failure(...)`: a CLEARLY-MARKED controlled test
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

from typing import Callable, Dict, Tuple

from automation.playwright.components.navigation import start_at_home
from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.catalog_pages import CategoryPage, ProductPage
from automation.playwright.pages.search_page import SearchPage
from automation.playwright.pages.wishlist_page import WishlistPage
from automation.playwright.tests.enh02_helpers import real_execution

CONTROLLED_FAILURE_MARKER = "CONTROLLED TEST FAILURE"


def execute_real_srch01(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """Real, non-mocked execution of REQ-SRCH-01's own already-evidenced
    business action (search a real, known keyword, observe at least one
    rendered result)."""
    dataset = load_dataset("ENH02-TD-SRCH-01-01", required_fields=["search_term"])
    with real_execution(
        testcase_id="ENH02-TC-REQ-SRCH-01-VALID-KEYWORD",
        requirement_ids=["REQ-SRCH-01"],
        dataset_id=dataset.data_set_id,
        automation_id="ENH02-PW-TC-REQ-SRCH-01-VALID-KEYWORD",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
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
        assert has_results, "Real REQ-SRCH-01 execution did not render any results"

    return {"testcase_id": "ENH02-TC-REQ-SRCH-01-VALID-KEYWORD", "automation_id": "ENH02-PW-TC-REQ-SRCH-01-VALID-KEYWORD"}


def execute_real_wish01(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """Real, non-mocked execution of REQ-WISH-01's own already-evidenced
    business action (add a real, eligible product to the wishlist,
    observe the confirmation). Leaves the session's anonymous wishlist
    populated for REQ-WISH-02/03's own real, dependent actions."""
    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-01-ADD-TO-WISHLIST",
        requirement_ids=["REQ-WISH-01"],
        dataset_id="NO-DATASET",
        automation_id="ENH02-PW-TC-REQ-WISH-01-ADD-TO-WISHLIST",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
    ) as (steps, mark):
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/album-3")
        steps.append({"step_order": 1, "description": "Navigate to '3rd Album'", "status": "PASS"})
        resolution = product.add_to_wishlist()
        steps.append({"step_order": 2, "description": "Add to wishlist", "status": "PASS" if resolution["resolved_candidate"] else "FAIL", "locator_resolution": resolution})
        notification = product.notification_text()
        observed = "added to your wishlist" in notification
        steps.append({"step_order": 3, "description": "Observe wishlist-add confirmation", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"notification={notification!r}")
        assert observed, f"Real REQ-WISH-01 wishlist-add confirmation not observed (notification={notification!r})"

    return {"testcase_id": "ENH02-TC-REQ-WISH-01-ADD-TO-WISHLIST", "automation_id": "ENH02-PW-TC-REQ-WISH-01-ADD-TO-WISHLIST"}


def execute_real_wish02(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """Real REQ-WISH-02 -- requires REQ-WISH-01 to have already run in
    this same page session (its own real precondition; enforced by the
    orchestrator's dependency planning, never re-run here)."""
    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM",
        requirement_ids=["REQ-WISH-02"],
        dataset_id="NO-DATASET",
        automation_id="ENH02-PW-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
    ) as (steps, mark):
        wishlist = WishlistPage(page, DEFAULT_CONFIG)
        wishlist.open()
        steps.append({"step_order": 1, "description": "Navigate to wishlist page", "status": "PASS"})
        has_item = wishlist.has_item()
        has_price = bool(wishlist.item_price_text())
        has_remove = wishlist.has_remove_action()
        has_add_to_cart = wishlist.has_add_to_cart_action()
        observed = has_item and has_price and has_remove and has_add_to_cart
        steps.append({"step_order": 2, "description": "Observe item, price, and available actions", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"item={has_item} price={has_price} remove={has_remove} add_to_cart={has_add_to_cart}")
        assert observed, "Real REQ-WISH-02 execution: wishlist page did not reflect the added item with price and actions"

    return {"testcase_id": "ENH02-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM", "automation_id": "ENH02-PW-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM"}


def execute_real_wish03(page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    """Real REQ-WISH-03 -- requires REQ-WISH-01 to have already run in
    this same page session (its own real precondition)."""
    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-03-SHAREABLE-URL",
        requirement_ids=["REQ-WISH-03"],
        dataset_id="NO-DATASET",
        automation_id="ENH02-PW-TC-REQ-WISH-03-SHAREABLE-URL",
        page=page, browser_version=browser_version, worker_id=worker_id,
        run_label=orchestration_id,
    ) as (steps, mark):
        wishlist = WishlistPage(page, DEFAULT_CONFIG)
        wishlist.open()
        steps.append({"step_order": 1, "description": "Navigate to (anonymous) wishlist page", "status": "PASS"})
        has_url = wishlist.has_shareable_url()
        steps.append({"step_order": 2, "description": "Observe shareable URL displayed", "status": "PASS" if has_url else "FAIL"})
        mark(ExecutionStatus.PASS if has_url else ExecutionStatus.FAIL, None if has_url else "ASSERTION_FAILURE", None if has_url else "Shareable URL not observed")
        assert has_url, "Real REQ-WISH-03 execution: anonymous wishlist page did not display a shareable URL"

    return {"testcase_id": "ENH02-TC-REQ-WISH-03-SHAREABLE-URL", "automation_id": "ENH02-PW-TC-REQ-WISH-03-SHAREABLE-URL"}


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


#: Real driver registry -- the authoritative list of requirements this
#: orchestrator can actually drive against the real SUT. A requirement
#: absent from this dict has no real execution driver yet; the
#: orchestrator reports that honestly (BLOCKED for REAL_EXECUTION
#: purposes) rather than silently skipping or fabricating a result.
REAL_DRIVERS: Dict[str, Callable[..., Dict]] = {
    "REQ-BRW-01": execute_real_brw01,
    "REQ-SRCH-01": execute_real_srch01,
    "REQ-WISH-01": execute_real_wish01,
    "REQ-WISH-02": execute_real_wish02,
    "REQ-WISH-03": execute_real_wish03,
}


def has_real_driver(requirement_id: str) -> bool:
    return requirement_id in REAL_DRIVERS


def execute_real(requirement_id: str, page, browser_version: str, worker_id: str, orchestration_id: str) -> Dict:
    driver = REAL_DRIVERS.get(requirement_id)
    if driver is None:
        raise KeyError(f"No real execution driver registered for {requirement_id!r}. Registered: {sorted(REAL_DRIVERS)}")
    return driver(page, browser_version, worker_id, orchestration_id)
