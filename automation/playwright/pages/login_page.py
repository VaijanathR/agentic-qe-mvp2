"""Post-MVP2 Enhancement 02 -- Login Page Object.

Real evidence: real, live GET of https://demowebshop.tricentis.com/login
(real input id="Email"/id="Password", real submit class="login-button").
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import LOGIN_FORM_CANDIDATES, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage


class LoginPage(BasePage):
    def open(self) -> None:
        self.navigate("/login")

    def _fill(self, field_name: str, value: str) -> Dict:
        candidates = LOGIN_FORM_CANDIDATES[field_name]

        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.fill(value)
            return True

        return resolve_with_fallback(field_name, candidates, try_candidate).to_dict()

    def fill_email(self, value: str) -> Dict:
        return self._fill("email", value)

    def fill_password(self, value: str) -> Dict:
        return self._fill("password", value)

    def submit(self) -> Dict:
        candidates = LOGIN_FORM_CANDIDATES["login_button"]

        def try_candidate(candidate) -> bool:
            if candidate.locator_type == "ROLE":
                locator = self.page.get_by_role("button", name="Log in")
            else:
                locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback("login_button", candidates, try_candidate).to_dict()

    def is_authenticated(self) -> bool:
        """Real, observed evidence: the header shows a 'Log out' link
        only when authenticated -- never inferred, always checked live."""
        return self.page.locator("a.ico-logout").count() > 0

    def result_text(self) -> str:
        return self.page.locator("body").inner_text()
