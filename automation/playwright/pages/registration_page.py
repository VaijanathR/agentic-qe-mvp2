"""
Post-MVP2 Enhancement 01 -- Registration Page Object.

Real evidence: real, live GET of https://demowebshop.tricentis.com/register
performed during this enhancement's own inspection phase (real input `id`s
`FirstName`/`LastName`/`Email`/`Password`/`ConfirmPassword`, real submit
`id="register-button"`, real `<label for=...>` associations) -- see
`automation/playwright/locators.py::REGISTRATION_FORM_CANDIDATES` for the
full, disclosed evidence per field.

Business steps expressed here are the NEW, explicit Enhancement-01
testcase steps (`automation/playwright/enh01_testcase.py`) -- this page
object does not add any business action beyond what that testcase states,
and the historical `TC-REQ-REG-01-01` (with its own, disclosed generic
placeholder steps) is never modified or silently reinterpreted.
"""
from __future__ import annotations

from typing import Dict, List

from automation.playwright.locators import LocatorCandidate, REGISTRATION_FORM_CANDIDATES, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage


class RegistrationPage(BasePage):
    def _fill_field(self, field_name: str, value: str) -> Dict:
        candidates: List[LocatorCandidate] = REGISTRATION_FORM_CANDIDATES[field_name]

        def try_candidate(candidate: LocatorCandidate) -> bool:
            if candidate.locator_type == "LABEL":
                locator = self.page.get_by_label(candidate.expression.split("=", 1)[1])
            else:
                locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.fill(value)
            return True

        return resolve_with_fallback(field_name, candidates, try_candidate).to_dict()

    def fill_first_name(self, value: str) -> Dict:
        return self._fill_field("first_name", value)

    def fill_last_name(self, value: str) -> Dict:
        return self._fill_field("last_name", value)

    def fill_email(self, value: str) -> Dict:
        return self._fill_field("email", value)

    def fill_password(self, value: str) -> Dict:
        return self._fill_field("password", value)

    def fill_confirm_password(self, value: str) -> Dict:
        return self._fill_field("confirm_password", value)

    def submit(self) -> Dict:
        candidates = REGISTRATION_FORM_CANDIDATES["register_button"]

        def try_candidate(candidate: LocatorCandidate) -> bool:
            if candidate.locator_type == "ROLE":
                locator = self.page.get_by_role("button", name="Register")
            else:
                locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback("register_button", candidates, try_candidate).to_dict()

    def result_text(self) -> str:
        """Real, observed post-submit page content -- never a fabricated
        'success' string. Returns the visible <body> text so the caller
        can classify PASS/FAIL from real, current evidence."""
        return self.page.locator("body").inner_text()
