"""Post-MVP2 Enhancement 02 -- Search Page Object.

Real evidence: real GET of https://demowebshop.tricentis.com/ (search box
id="small-searchterms", name="q"; button class="search-box-button") and
https://demowebshop.tricentis.com/search?q=... (real result/no-result text).
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import SEARCH_CANDIDATES, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage

NO_RESULTS_TEXT = "No products were found that matched your criteria."


class SearchPage(BasePage):
    def search(self, term: str) -> Dict:
        box_candidates = SEARCH_CANDIDATES["search_box"]

        def try_box(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.fill(term)
            return True

        box_result = resolve_with_fallback("search_box", box_candidates, try_box)

        button_candidates = SEARCH_CANDIDATES["search_button"]

        def try_button(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        button_result = resolve_with_fallback("search_button", button_candidates, try_button)
        return {"search_box": box_result.to_dict(), "search_button": button_result.to_dict()}

    def has_results(self) -> bool:
        return self.page.locator(".product-grid .item-box").count() > 0

    def shows_no_results_message(self) -> bool:
        return NO_RESULTS_TEXT in self.page.locator("body").inner_text()
