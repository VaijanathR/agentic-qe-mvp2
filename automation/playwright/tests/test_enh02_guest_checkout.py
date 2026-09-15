"""Post-MVP2 Enhancement 02 -- real, chained execution of
ENH02-TC-REQ-GCO-01/02 and ENH02-TC-REQ-ACO-03. Stops at the Billing
Address step; never submits real billing/shipping/payment data and never
completes an order (see REQ-GCO-03/ACO-01's own DEFERRED disposition in
the coverage matrix for why)."""
from __future__ import annotations

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.cart_page import CartPage
from automation.playwright.pages.catalog_pages import ProductPage
from automation.playwright.pages.checkout_page import CheckoutPage
from automation.playwright.tests.enh02_helpers import real_execution


def test_guest_checkout_init_step_sequence_and_address_validation_chain(browser_page, worker_id):
    page, browser_version = browser_page

    with real_execution(
        testcase_id="ENH02-TC-REQ-GCO-01-GUEST-CHECKOUT-INIT", requirement_ids=["REQ-GCO-01"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-GCO-01-GUEST-CHECKOUT-INIT",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/album-3")
        steps.append({"step_order": 1, "description": "Navigate to '3rd Album'", "status": "PASS"})
        add_resolution = product.add_to_cart("#add-to-cart-button-53")
        page.wait_for_timeout(1500)  # real, AJAX add-to-cart; without this wait the cart page can load before the item is actually added (a real timing bug found and fixed this task)
        steps.append({"step_order": 2, "description": "Add to Cart", "status": "PASS" if add_resolution["resolved_candidate"] else "FAIL", "locator_resolution": add_resolution})
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        steps.append({"step_order": 3, "description": "Navigate to cart page", "status": "PASS"})
        checkout_resolution = cart.accept_terms_and_checkout()
        steps.append({"step_order": 4, "description": "Accept Terms of Service and select Checkout", "status": "PASS", "locator_resolution": checkout_resolution})
        page.wait_for_timeout(1000)
        checkout = CheckoutPage(page, DEFAULT_CONFIG)
        guest_resolution = checkout.checkout_as_guest()
        steps.append({"step_order": 5, "description": "Select 'Checkout as Guest'", "status": "PASS" if guest_resolution["resolved_candidate"] else "FAIL", "locator_resolution": guest_resolution})
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        reached = checkout.is_on_onepagecheckout()
        steps.append({"step_order": 6, "description": "Observe checkout page loads, still anonymous", "status": "PASS" if reached else "FAIL"})
        mark(ExecutionStatus.PASS if reached else ExecutionStatus.FAIL, None if reached else "ASSERTION_FAILURE", None if reached else f"url={page.url}")
        assert reached, f"Real guest checkout did not reach /onepagecheckout (actual url={page.url})"

    with real_execution(
        testcase_id="ENH02-TC-REQ-GCO-02-GUEST-STEP-SEQUENCE", requirement_ids=["REQ-GCO-02"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-GCO-02-GUEST-STEP-SEQUENCE",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        checkout = CheckoutPage(page, DEFAULT_CONFIG)
        shown = checkout.shows_billing_address_step()
        steps.append({"step_order": 1, "description": "Observe Billing Address step heading", "status": "PASS" if shown else "FAIL"})
        mark(ExecutionStatus.PASS if shown else ExecutionStatus.FAIL, None if shown else "ASSERTION_FAILURE", None if shown else "Billing Address step heading not observed")
        assert shown, "Real guest checkout session did not show the Billing Address step"

    with real_execution(
        testcase_id="ENH02-TC-REQ-ACO-03-ADDRESS-FORM-VALIDATION", requirement_ids=["REQ-ACO-03"],
        dataset_id="NO-DATASET", automation_id="ENH02-PW-TC-REQ-ACO-03-ADDRESS-FORM-VALIDATION",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        checkout = CheckoutPage(page, DEFAULT_CONFIG)
        checkout.submit_billing_address_blank()
        steps.append({"step_order": 1, "description": "Submit Billing Address step with all required fields blank", "status": "PASS"})
        blocked = checkout.has_required_field_validation_errors()
        steps.append({"step_order": 2, "description": "Observe progression is blocked with validation errors", "status": "PASS" if blocked else "FAIL"})
        mark(ExecutionStatus.PASS if blocked else ExecutionStatus.FAIL, None if blocked else "ASSERTION_FAILURE", None if blocked else "Blank-field block not observed")
        assert blocked, "Real blank Billing Address submission was not blocked as expected"
