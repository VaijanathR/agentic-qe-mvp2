"""Post-MVP2 Enhancement 02 -- real execution of
ENH02-TC-REQ-CFG-01-MANDATORY-ATTRIBUTE (independent) and the chained
CART-01 -> CART-02 -> CART-03 -> CART-04 sequence (each depends on the
real cart state left by the previous step, so all four real, per-testcase
execution logs are produced within one real browser session)."""
from __future__ import annotations

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.cart_page import CartPage
from automation.playwright.pages.catalog_pages import ProductPage
from automation.playwright.tests.enh02_helpers import real_execution


def test_add_to_cart_blocked_without_mandatory_attribute(browser_page, worker_id):
    page, browser_version = browser_page
    with real_execution(
        testcase_id="ENH02-TC-REQ-CFG-01-MANDATORY-ATTRIBUTE", requirement_ids=["REQ-CFG-01"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-CFG-01-MANDATORY-ATTRIBUTE",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/build-your-own-computer")
        steps.append({"step_order": 1, "description": "Navigate to 'Build your own computer'", "status": "PASS"})
        resolution = product.leave_hdd_attribute_unselected_and_add_to_cart()
        steps.append({"step_order": 2, "description": "Add to Cart with mandatory HDD attribute left unselected", "status": "PASS" if resolution["resolved_candidate"] else "FAIL", "locator_resolution": resolution})
        notification = product.notification_text()
        expected = "Please select HDD"
        observed = expected in notification
        cart_qty = product.cart_quantity_indicator()
        cart_unchanged = cart_qty in ("", "(0)")
        steps.append({"step_order": 3, "description": "Observe blocking message names HDD; cart unchanged", "status": "PASS" if (observed and cart_unchanged) else "FAIL"})
        success = observed and cart_unchanged
        mark(ExecutionStatus.PASS if success else ExecutionStatus.FAIL, None if success else "ASSERTION_FAILURE", None if success else f"notification={notification!r} cart_qty={cart_qty!r}")
        assert success, f"Real execution did not observe the expected block (notification={notification!r}, cart_qty={cart_qty!r})"


def test_cart_add_update_zero_and_empty_state_chain(browser_page, worker_id):
    page, browser_version = browser_page

    # --- REQ-CART-01: Add to Cart confirms addition ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-CART-01-ADD-CONFIRMATION", requirement_ids=["REQ-CART-01"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-CART-01-ADD-CONFIRMATION",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/album-3")
        steps.append({"step_order": 1, "description": "Navigate to '3rd Album'", "status": "PASS"})
        resolution = product.add_to_cart("#add-to-cart-button-53")
        steps.append({"step_order": 2, "description": "Add to Cart", "status": "PASS" if resolution["resolved_candidate"] else "FAIL", "locator_resolution": resolution})
        notification = product.notification_text()
        cart_qty = product.cart_quantity_indicator()
        observed = "added to your shopping cart" in notification and "(1)" in cart_qty
        steps.append({"step_order": 3, "description": "Observe success notice and incremented cart count", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"notification={notification!r} cart_qty={cart_qty!r}")
        assert observed, f"Real add-to-cart confirmation not observed (notification={notification!r}, cart_qty={cart_qty!r})"

    # --- REQ-CART-02: quantity update recalculates subtotal/total ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-CART-02-QUANTITY-UPDATE", requirement_ids=["REQ-CART-02"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-CART-02-QUANTITY-UPDATE",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        steps.append({"step_order": 1, "description": "Navigate to cart page", "status": "PASS"})
        unit_price = float(cart.line_subtotal_text() or "0")
        qty_resolution = cart.set_quantity("3")
        steps.append({"step_order": 2, "description": "Set quantity to 3", "status": "PASS" if qty_resolution["resolved_candidate"] else "FAIL", "locator_resolution": qty_resolution})
        update_resolution = cart.update_cart()
        steps.append({"step_order": 3, "description": "Update shopping cart", "status": "PASS" if update_resolution["resolved_candidate"] else "FAIL", "locator_resolution": update_resolution})
        page.wait_for_timeout(1000)
        new_subtotal = float(cart.line_subtotal_text() or "0")
        expected_subtotal = round(unit_price * 3, 2)
        observed = abs(new_subtotal - expected_subtotal) < 0.01
        steps.append({"step_order": 4, "description": f"Observe subtotal recalculated to {expected_subtotal}", "status": "PASS" if observed else "FAIL"})
        mark(ExecutionStatus.PASS if observed else ExecutionStatus.FAIL, None if observed else "ASSERTION_FAILURE", None if observed else f"expected={expected_subtotal} observed={new_subtotal}")
        assert observed, f"Real cart subtotal did not recalculate as expected (expected={expected_subtotal}, observed={new_subtotal})"

    # --- REQ-CART-03: quantity 0 removes the line item ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-CART-03-ZERO-QUANTITY-REMOVES", requirement_ids=["REQ-CART-03"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-CART-03-ZERO-QUANTITY-REMOVES",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        steps.append({"step_order": 1, "description": "Navigate to cart page", "status": "PASS"})
        qty_resolution = cart.set_quantity("0")
        steps.append({"step_order": 2, "description": "Set quantity to 0", "status": "PASS" if qty_resolution["resolved_candidate"] else "FAIL", "locator_resolution": qty_resolution})
        update_resolution = cart.update_cart()
        steps.append({"step_order": 3, "description": "Update shopping cart", "status": "PASS" if update_resolution["resolved_candidate"] else "FAIL", "locator_resolution": update_resolution})
        page.wait_for_timeout(1000)
        now_empty = cart.is_empty()
        steps.append({"step_order": 4, "description": "Observe line item removed, no prompt", "status": "PASS" if now_empty else "FAIL"})
        mark(ExecutionStatus.PASS if now_empty else ExecutionStatus.FAIL, None if now_empty else "ASSERTION_FAILURE", None if now_empty else "Cart not empty after zero-quantity update")
        assert now_empty, "Real cart was not emptied by the zero-quantity update"

    # --- REQ-CART-04: empty-cart state blocks checkout ---
    with real_execution(
        testcase_id="ENH02-TC-REQ-CART-04-EMPTY-CART-STATE", requirement_ids=["REQ-CART-04"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-CART-04-EMPTY-CART-STATE",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        steps.append({"step_order": 1, "description": "Navigate to (empty) cart page", "status": "PASS"})
        is_empty = cart.is_empty()
        steps.append({"step_order": 2, "description": "Observe empty-state message", "status": "PASS" if is_empty else "FAIL"})
        mark(ExecutionStatus.PASS if is_empty else ExecutionStatus.FAIL, None if is_empty else "ASSERTION_FAILURE", None if is_empty else "Empty-state message not observed")
        assert is_empty, "Real cart page did not show the expected empty-state message"
