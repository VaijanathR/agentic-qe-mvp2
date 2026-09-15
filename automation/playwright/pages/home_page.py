"""
Post-MVP2 Enhancement 01 -- Home Page Object.

Real evidence: `<a href="/register" class="ico-register">Register</a>`,
captured live from https://demowebshop.tricentis.com/ during this
enhancement's own inspection phase.
"""
from __future__ import annotations

from automation.playwright.locators import LocatorCandidate, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage

REGISTER_LINK_CANDIDATES = [
    LocatorCandidate("HREF", "a[href='/register']", "live capture: <a href=\"/register\" class=\"ico-register\">", 1),
    LocatorCandidate("TEXT", "text=Register", "live capture: link text 'Register'", 2),
]


class HomePage(BasePage):
    def open(self) -> None:
        self.navigate("/")

    def go_to_registration(self):
        """Navigates to the registration page, trying each real,
        evidence-backed candidate in priority order. Returns the
        LocatorResolutionResult (never silent about which candidate was
        actually used)."""
        def try_candidate(candidate: LocatorCandidate) -> bool:
            locator = self.page.locator(candidate.expression) if candidate.locator_type != "TEXT" else self.page.get_by_text(candidate.expression.split("=", 1)[1], exact=True)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        result = resolve_with_fallback("register_link", REGISTER_LINK_CANDIDATES, try_candidate)
        from automation.playwright.pages.registration_page import RegistrationPage

        return RegistrationPage(self.page, self.config), result
