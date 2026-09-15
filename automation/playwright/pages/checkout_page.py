"""
Post-MVP2 Enhancement 02 -- Checkout Page Object (guest-initiation scope
only; stops at the Billing Address step -- see REQ-GCO-01/02/REQ-ACO-03
testcases for the exact, bounded scope and rationale).

Real evidence: real click of `.checkout-as-guest-button` from the guest
interstitial reaches `/onepagecheckout` (title "Demo Web Shop. Checkout"),
rendering a real "1 Billing address" step heading.
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import CHECKOUT_CANDIDATES, resolve_with_fallback
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
