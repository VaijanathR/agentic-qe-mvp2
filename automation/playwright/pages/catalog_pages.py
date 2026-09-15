"""
Post-MVP2 Enhancement 02 -- Category and Product Page Objects.

Real evidence: real GETs of https://demowebshop.tricentis.com/books (real
`.product-grid`), https://demowebshop.tricentis.com/album-3 (real
add-to-cart/add-to-wishlist controls), and
https://demowebshop.tricentis.com/build-your-own-computer (real,
live-discovered mandatory HDD attribute -- see the Enhancement-02
report's "Live discovery" section for the exact interactive session that
found this, not merely static HTML inspection).
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import (
    CART_CANDIDATES,
    CONFIGURABLE_ATTRIBUTE_CANDIDATES,
    WISHLIST_CANDIDATES,
    resolve_with_fallback,
)
from automation.playwright.pages.base_page import BasePage


class CategoryPage(BasePage):
    def open_books(self) -> None:
        self.navigate("/books")

    def has_product_grid(self) -> bool:
        return self.page.locator(".product-grid").count() > 0


class ProductPage(BasePage):
    """Generic product-detail-page actions, parameterized by the real,
    product-specific control IDs (Enhancement-01/02 both disclose that
    this SUT's IDs embed the product's own numeric ID, so a single,
    reusable ID candidate cannot be shared across products -- callers
    pass the concrete, real, evidence-backed selector)."""

    def open(self, path: str) -> None:
        self.navigate(path)

    def add_to_cart(self, button_selector: str) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        from automation.playwright.locators import LocatorCandidate

        candidates = [LocatorCandidate("ID", button_selector, f"live capture: real add-to-cart id for this product", 1)]
        return resolve_with_fallback("add_to_cart_button", candidates, try_candidate).to_dict()

    def add_to_wishlist(self) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback("add_to_wishlist_button", WISHLIST_CANDIDATES["add_to_wishlist_button"], try_candidate).to_dict()

    def notification_text(self) -> str:
        self.page.wait_for_timeout(1000)
        return self.page.locator("#bar-notification").inner_text() if self.page.locator("#bar-notification").count() else ""

    def leave_hdd_attribute_unselected_and_add_to_cart(self) -> Dict:
        """Real, evidence-based negative-path action for REQ-CFG-01:
        deliberately does NOT select the mandatory HDD radio group
        (product_attribute_16_3_6), then clicks the real add-to-cart
        button for 'Build your own computer' (id=add-to-cart-button-16)."""
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback(
            "add_to_cart_button_byoc", CONFIGURABLE_ATTRIBUTE_CANDIDATES["add_to_cart_button_byoc"], try_candidate
        ).to_dict()

    def cart_quantity_indicator(self) -> str:
        return self.page.locator("#topcartlink .cart-qty").inner_text() if self.page.locator("#topcartlink .cart-qty").count() else ""
