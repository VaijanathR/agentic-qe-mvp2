"""
CONTROLLED REQ-GCO-03 POST-FREEZE VALIDATION.

Separate, clearly-dated real Playwright execution created AFTER the
Enhancement-02 frozen baseline (`521b155`), under explicit Human + Di
authorization, to supply the one piece of DIRECT SYSTEM EVIDENCE the
Approved SRS itself discloses as missing for REQ-GCO-03 (its Evidence
Basis is "AGENT INFERENCE, bridging from DIRECT SYSTEM EVIDENCE on the
authenticated path" -- see `requirements/MVP2_SRS_v1.0_APPROVED.md` line
176).

This file is deliberately NOT folded into the historical
`test_enh02_guest_checkout.py` (which intentionally stops at the Billing
Address step and is frozen Enhancement-02 evidence). This is the ONE real,
permanent, guest-path order this validation is authorized to create --
never repeated, never parallelized, and run standalone (a real
registration/checkout-heavy sequential test must not be combined with
other files under real `pytest -n 4`, per the real, reproducible
concurrency finding already disclosed in the Enhancement-02 final freeze
report).

The session remains genuinely anonymous throughout: no login, no
registration, no reuse of the existing shared authenticated account or its
saved address.
"""
from __future__ import annotations

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.data_access import load_dataset
from automation.playwright.logging_ import ExecutionStatus
from automation.playwright.pages.cart_page import CartPage
from automation.playwright.pages.catalog_pages import ProductPage
from automation.playwright.pages.checkout_page import CheckoutPage
from automation.playwright.tests.enh02_helpers import real_execution


def test_gco03_guest_checkout_completion(browser_page, worker_id):
    page, browser_version = browser_page

    dataset = load_dataset(
        "ENH02-TD-GCO-03-01",
        required_fields=["first_name", "last_name", "email", "country_id", "state_label", "city", "address1", "zip_postal_code", "phone_number"],
    )

    with real_execution(
        testcase_id="ENH02-TC-REQ-GCO-03-GUEST-CHECKOUT-COMPLETION",
        requirement_ids=["REQ-GCO-03"],
        dataset_id=dataset.data_set_id, automation_id="ENH02-PW-TC-REQ-GCO-03-GUEST-CHECKOUT-COMPLETION",
        page=page, browser_version=browser_version, worker_id=worker_id,
    ) as (steps, mark):
        # --- Step 1: anonymous session adds a real, physical product ---
        product = ProductPage(page, DEFAULT_CONFIG)
        product.open("/computing-and-internet")
        add_resolution = product.add_to_cart("#add-to-cart-button-13")
        page.wait_for_timeout(1500)
        steps.append({"step_order": 1, "description": "As an anonymous session, add the real 'Computing and Internet' physical product to the cart", "status": "PASS" if add_resolution["resolved_candidate"] else "FAIL", "locator_resolution": add_resolution})

        # --- Step 2: Terms of Service + Checkout ---
        cart = CartPage(page, DEFAULT_CONFIG)
        cart.open()
        checkout_resolution = cart.accept_terms_and_checkout()
        page.wait_for_timeout(1000)
        steps.append({"step_order": 2, "description": "Accept Terms of Service and select Checkout", "status": "PASS", "locator_resolution": checkout_resolution})

        # --- Step 3: explicit 'Checkout as Guest' -- session stays anonymous ---
        checkout = CheckoutPage(page, DEFAULT_CONFIG)
        guest_resolution = checkout.checkout_as_guest()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        reached_checkout = checkout.is_on_onepagecheckout()
        steps.append({"step_order": 3, "description": "Select 'Checkout as Guest' (remain anonymous)", "status": "PASS" if (guest_resolution["resolved_candidate"] and reached_checkout) else "FAIL", "locator_resolution": guest_resolution})

        # --- Step 4: Billing Address ---
        billing_resolution = checkout.fill_billing_address(dataset.fields)
        checkout.continue_billing_address()
        steps.append({"step_order": 4, "description": "Fill the real, required Billing Address fields and Continue", "status": "PASS", "locator_resolution": billing_resolution})

        # --- Step 5: Shipping Address (accept auto-saved default) ---
        checkout.accept_shipping_address()
        steps.append({"step_order": 5, "description": "Accept the pre-selected (auto-saved) shipping address and Continue", "status": "PASS"})

        # --- Step 6: Shipping Method ---
        shipping_options = checkout.shipping_method_option_values()
        multiple_shipping_options = len(shipping_options) > 1
        checkout.select_shipping_method_and_continue()
        steps.append({"step_order": 6, "description": "Observe multiple real Shipping Method options; select default and Continue", "status": "PASS" if multiple_shipping_options else "FAIL", "shipping_options": shipping_options})

        # --- Step 7: Payment Method ---
        payment_options = checkout.payment_method_option_values()
        multiple_payment_options = len(payment_options) > 1
        checkout.select_payment_method_and_continue()
        steps.append({"step_order": 7, "description": "Observe multiple real Payment Method options; select Cash On Delivery and Continue", "status": "PASS" if multiple_payment_options else "FAIL", "payment_options": payment_options})

        # --- Step 8: Payment Info (COD -- no form) ---
        cod_has_no_form = not checkout.payment_info_has_form_fields()
        payment_info_text = checkout.payment_info_content()
        checkout.continue_payment_info()
        steps.append({"step_order": 8, "description": "Observe Cash On Delivery Payment Info renders no payment-detail form; Continue", "status": "PASS" if cod_has_no_form else "FAIL", "payment_info_text": payment_info_text})

        # --- Step 9: Confirm Order totals ---
        totals_consistent = checkout.confirm_order_totals_are_internally_consistent()
        totals_text = checkout.confirm_order_totals_text()
        steps.append({"step_order": 9, "description": "Observe Confirm Order totals; verify Total equals the sum of its components", "status": "PASS" if totals_consistent else "FAIL", "totals_text": totals_text})

        # --- Step 10: Submit the real order (the ONE authorized permanent state change) ---
        checkout.submit_confirm_order()
        steps.append({"step_order": 10, "description": "Select Confirm to submit the real guest-path order", "status": "PASS"})

        # --- Step 11: Order Completed + real order number ---
        order_completed = checkout.is_order_completed()
        completed_order_number = checkout.completed_order_number()
        order_number_present = bool(completed_order_number)
        still_anonymous = page.locator("a.ico-logout").count() == 0
        steps.append({
            "step_order": 11,
            "description": "Observe the Order Completed page for success and a real order number, while remaining genuinely anonymous",
            "status": "PASS" if (order_completed and order_number_present and still_anonymous) else "FAIL",
            "order_number": completed_order_number,
            "still_anonymous": still_anonymous,
        })

        success = (
            guest_resolution["resolved_candidate"] and reached_checkout
            and multiple_shipping_options and multiple_payment_options
            and cod_has_no_form and totals_consistent
            and order_completed and order_number_present and still_anonymous
        )
        mark(
            ExecutionStatus.PASS if success else ExecutionStatus.FAIL,
            None if success else "ASSERTION_FAILURE",
            None if success else (
                f"reached_checkout={reached_checkout} multiple_shipping_options={multiple_shipping_options} "
                f"multiple_payment_options={multiple_payment_options} cod_has_no_form={cod_has_no_form} "
                f"totals_consistent={totals_consistent} order_completed={order_completed} "
                f"order_number_present={order_number_present} still_anonymous={still_anonymous}"
            ),
        )
        assert success, (
            f"Real guest checkout completion did not satisfy every REQ-GCO-03 checkpoint: "
            f"reached_checkout={reached_checkout} multiple_shipping_options={multiple_shipping_options} "
            f"multiple_payment_options={multiple_payment_options} cod_has_no_form={cod_has_no_form} "
            f"totals_consistent={totals_consistent} order_completed={order_completed} "
            f"order_number_present={order_number_present} still_anonymous={still_anonymous} "
            f"totals_text={totals_text!r} order_number={completed_order_number!r}"
        )
