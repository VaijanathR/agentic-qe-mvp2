"""Post-MVP2 Enhancement 02 -- real, chained execution of
ENH02-TC-REQ-WISH-01/02/03 (anonymous, session-scoped; a real, eligible
Digital Downloads product per SRS sec. 6.8's own disclosed evidence)."""
from __future__ import annotations

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.catalog_pages import ProductPage
from automation.playwright.pages.wishlist_page import WishlistPage
from automation.playwright.tests.enh02_helpers import real_execution


def test_wishlist_add_view_and_shareable_url_chain(browser_page, worker_id):
    page, browser_version = browser_page

    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-01-ADD-TO-WISHLIST", requirement_ids=["REQ-WISH-01"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-WISH-01-ADD-TO-WISHLIST",
        page=page, browser_version=browser_version, worker_id=worker_id,
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
        assert observed, f"Real wishlist-add confirmation not observed (notification={notification!r})"

    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM", requirement_ids=["REQ-WISH-02"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-WISH-02-WISHLIST-PAGE-REFLECTS-ITEM",
        page=page, browser_version=browser_version, worker_id=worker_id,
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
        assert observed, "Real wishlist page did not reflect the added item with price and actions"

    with real_execution(
        testcase_id="ENH02-TC-REQ-WISH-03-SHAREABLE-URL", requirement_ids=["REQ-WISH-03"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-WISH-03-SHAREABLE-URL",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        wishlist = WishlistPage(page, DEFAULT_CONFIG)
        wishlist.open()
        steps.append({"step_order": 1, "description": "Navigate to (anonymous) wishlist page", "status": "PASS"})
        has_url = wishlist.has_shareable_url()
        steps.append({"step_order": 2, "description": "Observe shareable URL displayed", "status": "PASS" if has_url else "FAIL"})
        mark(ExecutionStatus.PASS if has_url else ExecutionStatus.FAIL, None if has_url else "ASSERTION_FAILURE", None if has_url else "Shareable URL not observed")
        assert has_url, "Real anonymous wishlist page did not display a shareable URL"
