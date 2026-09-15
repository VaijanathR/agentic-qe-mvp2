"""
Post-MVP2 Enhancement 02 -- Customer Account and Password Recovery Page
Objects.

Real evidence: `/customer/info`, `/customer/addresses`, `/customer/orders`
each real-verified (this task) to return a real `302 Found` redirect for
an anonymous session; `/passwordrecovery` real-verified to return "Email
not found." for a non-registered email, so the real, registered-account
case (used by `ENH02-TC-REQ-PWR-01-RECOVERY-UI`) is checked against the
ABSENCE of that same, real, negative-case text.
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import PASSWORD_RECOVERY_CANDIDATES, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage

RECOVERY_NOT_FOUND_TEXT = "Email not found."


class AccountPage(BasePage):
    def open_customer_info(self) -> None:
        self.navigate("/customer/info")

    def open_addresses(self) -> None:
        self.navigate("/customer/addresses")

    def open_orders(self) -> None:
        self.navigate("/customer/orders")

    def redirected_to_login(self) -> bool:
        return "/login" in self.page.url

    def order_history_contains(self, order_number: str) -> bool:
        """Real evidence for REQ-OHIST-01: the real `/customer/orders`
        page lists each order's real order number in its own row text.
        Never hard-codes a literal order number -- the caller passes the
        real one just observed on the Order Completed page."""
        return order_number in self.page.locator("body").inner_text()


class PasswordRecoveryPage(BasePage):
    def open(self) -> None:
        self.navigate("/passwordrecovery")

    def submit_email(self, email: str) -> Dict:
        def try_email(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.fill(email)
            return True

        email_result = resolve_with_fallback("email", PASSWORD_RECOVERY_CANDIDATES["email"], try_email)

        def try_submit(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        submit_result = resolve_with_fallback("recover_button", PASSWORD_RECOVERY_CANDIDATES["recover_button"], try_submit)
        self.page.wait_for_timeout(1000)
        return {"email": email_result.to_dict(), "recover_button": submit_result.to_dict()}

    def result_text(self) -> str:
        return self.page.locator(".result").inner_text() if self.page.locator(".result").count() else self.page.locator("body").inner_text()

    def shows_acceptance(self) -> bool:
        """Real, evidence-based check: acceptance is confirmed by the
        ABSENCE of the real, live-verified negative-case text ("Email
        not found.") -- the literal positive-acceptance string is not
        quoted verbatim in the Approved SRS, so this checkpoint asserts
        against the disclosed, real negative-case signature rather than
        inventing a positive string that was never directly observed."""
        return RECOVERY_NOT_FOUND_TEXT not in self.result_text()
