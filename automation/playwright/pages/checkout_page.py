"""
Post-MVP2 Enhancement 02 -- Checkout Page Object (guest-initiation scope
only; stops at the Billing Address step -- see REQ-GCO-01/02/REQ-ACO-03
testcases for the exact, bounded scope and rationale).

Real evidence: real click of `.checkout-as-guest-button` from the guest
interstitial reaches `/onepagecheckout` (title "Demo Web Shop. Checkout"),
rendering a real "1 Billing address" step heading.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from automation.playwright.locators import (
    BILLING_ADDRESS_CANDIDATES,
    CHECKOUT_CANDIDATES,
    CONFIRM_ORDER_CANDIDATES,
    ORDER_COMPLETED_CANDIDATES,
    PAYMENT_INFO_CANDIDATES,
    PAYMENT_METHOD_CANDIDATES,
    SHIPPING_ADDRESS_CANDIDATES,
    SHIPPING_METHOD_CANDIDATES,
    resolve_with_fallback,
)
from automation.playwright.pages.base_page import BasePage


class CheckoutPage(BasePage):
    def checkout_as_guest(self) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback(
            "checkout_as_guest_button", CHECKOUT_CANDIDATES["checkout_as_guest_button"], try_candidate
        ).to_dict()

    def is_on_onepagecheckout(self) -> bool:
        return "/onepagecheckout" in self.page.url

    def shows_billing_address_step(self) -> bool:
        """Real, live-verified (this task) exact heading text:
        `.step-title` -> "1\\nBilling Address"."""
        return self.page.locator("#opc-billing .step-title").count() > 0 and "Billing Address" in self.page.locator("#opc-billing .step-title").first.inner_text()

    def submit_billing_address_blank(self) -> None:
        """Attempts to progress past the Billing Address step with all
        real, required fields left blank -- real, non-mutating negative
        path for REQ-ACO-03. Real, live-verified selector (this task):
        `.new-address-next-step-button` (`onclick="Billing.save()"`) --
        the same real control the original MVP2 multi-locator/CR-002
        investigation already evidenced for this exact step."""
        self.page.locator(".new-address-next-step-button").first.click()
        self.page.wait_for_timeout(1500)

    def has_required_field_validation_errors(self) -> bool:
        """Real, evidence-based signal that progression was blocked:
        real, live verification (this task) confirmed a blank Billing
        Address submission stays on `/onepagecheckout` and surfaces a
        real `.field-validation-error` message ("First name is
        required."), rather than a heading-text check (which proved
        unreliable against the real, exact DOM casing/structure)."""
        return "/onepagecheckout" in self.page.url and self.page.locator(".field-validation-error").count() > 0

    # --- Post-MVP2 Enhancement 02 Deferred-10 Closure: real checkout
    # completion (Billing Address -> Shipping Address -> Shipping Method
    # -> Payment Method -> Payment Info -> Confirm Order -> Order
    # Completed). Real evidence for every selector below: see
    # `locators.py`'s BILLING_ADDRESS_CANDIDATES through
    # ORDER_COMPLETED_CANDIDATES docstring.

    def fill_billing_address(self, fields: Dict[str, str]) -> Dict:
        """Fills the real, required Billing Address fields and selects
        Country/State (the State dropdown is real, AJAX-populated after
        Country changes -- live-verified this task, hence the explicit
        wait). Does not click Continue; callers call
        `continue_billing_address()` separately so a testcase's blank-field
        negative path (`submit_billing_address_blank`, pre-existing) never
        shares this codepath."""
        results: Dict[str, Dict] = {}

        def make_try(expression: str, value: str):
            def _try(candidate) -> bool:
                locator = self.page.locator(candidate.expression)
                if locator.count() == 0:
                    return False
                locator.first.fill(value)
                return True
            return _try

        for field_name in ["first_name", "last_name", "email", "city", "address1", "zip_postal_code", "phone_number"]:
            results[field_name] = resolve_with_fallback(
                field_name, BILLING_ADDRESS_CANDIDATES[field_name], make_try(field_name, fields[field_name])
            ).to_dict()

        def try_country(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.select_option(fields.get("country_id", "1"))
            return True

        results["country"] = resolve_with_fallback("country", BILLING_ADDRESS_CANDIDATES["country"], try_country).to_dict()
        self.page.wait_for_timeout(1200)  # real AJAX state-list reload on Country change

        state_label = fields.get("state_label")
        if state_label:
            def try_state(candidate) -> bool:
                locator = self.page.locator(candidate.expression)
                if locator.count() == 0:
                    return False
                locator.first.select_option(label=state_label)
                return True

            results["state_province"] = resolve_with_fallback(
                "state_province", BILLING_ADDRESS_CANDIDATES["state_province"], try_state
            ).to_dict()

        return results

    def continue_billing_address(self) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("continue_button", BILLING_ADDRESS_CANDIDATES["continue_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2000)
        return result

    def billing_address_select_options(self) -> List[str]:
        """Real evidence for REQ-ACO-02: on a repeat checkout, this
        real `#billing-address-select` offers the previously-saved
        address as an additional option alongside "New Address"."""
        locator = self.page.locator(BILLING_ADDRESS_CANDIDATES["address_select"][0].expression)
        if locator.count() == 0:
            return []
        return locator.first.locator("option").all_text_contents()

    def shipping_address_select_options(self) -> List[str]:
        locator = self.page.locator(SHIPPING_ADDRESS_CANDIDATES["address_select"][0].expression)
        if locator.count() == 0:
            return []
        return locator.first.locator("option").all_text_contents()

    def accept_shipping_address(self) -> Dict:
        """Real, live-verified (this task) behavior: the Billing Address
        just entered is auto-saved and pre-selected as the default
        shipping address, so Continue can be selected directly without
        re-entering the same data -- a real, legitimate business action,
        not a shortcut around the step."""
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("continue_button", SHIPPING_ADDRESS_CANDIDATES["continue_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2000)
        return result

    def shipping_method_option_values(self) -> List[str]:
        return self.page.locator(SHIPPING_METHOD_CANDIDATES["radio_group"][0].expression).evaluate_all("els => els.map(e => e.value)")

    def select_shipping_method_and_continue(self, option_id: str = "#shippingoption_0") -> Dict:
        self.page.locator(option_id).check()

        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("continue_button", SHIPPING_METHOD_CANDIDATES["continue_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2000)
        return result

    def payment_method_option_values(self) -> List[str]:
        return self.page.locator(PAYMENT_METHOD_CANDIDATES["radio_group"][0].expression).evaluate_all("els => els.map(e => e.value)")

    def select_payment_method_and_continue(self, option_id: str = "#paymentmethod_0") -> Dict:
        self.page.locator(option_id).check()

        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("continue_button", PAYMENT_METHOD_CANDIDATES["continue_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2000)
        return result

    def payment_info_content(self) -> str:
        locator = self.page.locator(PAYMENT_INFO_CANDIDATES["content"][0].expression)
        return locator.inner_text() if locator.count() else ""

    def payment_info_has_form_fields(self) -> bool:
        """Real, evidence-based check for REQ-PAY-03: COD's Payment Info
        content renders zero real input/select/textarea fields (plain
        descriptive text only)."""
        content = self.page.locator(PAYMENT_INFO_CANDIDATES["content"][0].expression)
        if content.count() == 0:
            return False
        return content.locator("input:not([type=hidden]), select, textarea").count() > 0

    def continue_payment_info(self) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("continue_button", PAYMENT_INFO_CANDIDATES["continue_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2000)
        return result

    def confirm_order_totals_text(self) -> str:
        locator = self.page.locator(CONFIRM_ORDER_CANDIDATES["totals"][0].expression)
        return locator.inner_text() if locator.count() else ""

    def confirm_order_totals_are_internally_consistent(self) -> bool:
        """Real, evidence-based check for REQ-CONF-02: parses the real
        Sub-Total/Shipping/Payment method additional fee/Tax/Total lines
        and asserts Total == sum of the other four -- a computed check,
        never a hard-coded literal (SRS sec. 10 forbids fixing a
        discovery-session-specific value as an expected result)."""
        text = self.confirm_order_totals_text()
        values = {}
        # Real, live-confirmed layout (this task): each line is
        # "<Label>:<...>\t<amount>". Matched per line (anchored at
        # line-start) so the bare "Total" line is never confused with
        # the "Sub-Total" line, which also contains the substring
        # "Total" (a real bug found and fixed this task).
        for line in text.splitlines():
            m = re.match(r"^(Sub-Total|Shipping|Payment method additional fee|Tax|Total):.*?([0-9]+\.[0-9]{2})\s*$", line.strip())
            if m:
                values[m.group(1)] = float(m.group(2))
        required = ["Sub-Total", "Shipping", "Payment method additional fee", "Tax", "Total"]
        if not all(k in values for k in required):
            return False
        computed = values["Sub-Total"] + values["Shipping"] + values["Payment method additional fee"] + values["Tax"]
        return abs(computed - values["Total"]) < 0.01

    def submit_confirm_order(self) -> Dict:
        """The real, actual order-creation action -- the ONE real,
        permanent SUT state mutation this closure work performs."""
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("confirm_button", CONFIRM_ORDER_CANDIDATES["confirm_button"], try_candidate).to_dict()
        self.page.wait_for_timeout(2500)
        return result

    def is_order_completed(self) -> bool:
        return "/checkout/completed" in self.page.url and self.page.locator(ORDER_COMPLETED_CANDIDATES["container"][0].expression).count() > 0

    def completed_order_number(self) -> Optional[str]:
        """Parses the real "Order number: <N>" text (real evidence:
        checkout_final.html) -- never hard-codes the literal discovery
        order number, per SRS sec. 10."""
        container = self.page.locator(ORDER_COMPLETED_CANDIDATES["container"][0].expression)
        if container.count() == 0:
            return None
        m = re.search(r"Order number:\s*(\d+)", container.inner_text())
        return m.group(1) if m else None
