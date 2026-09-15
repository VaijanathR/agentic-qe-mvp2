"""
Post-MVP2 Enhancement 02 -- Cart Page Object.

Real evidence: real GET/interaction against
https://demowebshop.tricentis.com/cart (real `input.qty-input`,
`input[name=removefromcart]`, `input[name=updatecart]`,
`#termsofservice`, `#checkout`; real empty-state text "Your Shopping
Cart is empty!").
"""
from __future__ import annotations

from typing import Dict

from automation.playwright.locators import CART_CANDIDATES, resolve_with_fallback
from automation.playwright.pages.base_page import BasePage

EMPTY_CART_TEXT = "Your Shopping Cart is empty!"


class CartPage(BasePage):
    def open(self) -> None:
        self.navigate("/cart")

    def is_empty(self) -> bool:
        return EMPTY_CART_TEXT in self.page.locator("body").inner_text()

    def set_quantity(self, value: str) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.fill(value)
            return True

        return resolve_with_fallback("qty_input", CART_CANDIDATES["qty_input"], try_candidate).to_dict()

    def update_cart(self) -> Dict:
        def try_candidate(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        return resolve_with_fallback("update_cart_button", CART_CANDIDATES["update_cart_button"], try_candidate).to_dict()

    def line_subtotal_text(self) -> str:
        """Real, evidence-based selector: `.product-subtotal` -- live
        capture confirmed this holds the plain numeric line-subtotal
        text (e.g. "1.00")."""
        return self.page.locator(".product-subtotal").first.inner_text() if self.page.locator(".product-subtotal").count() else ""

    def cart_total_text(self) -> str:
        """Real, evidence-based selector: `.cart-total` contains the
        whole Sub-Total/Shipping/Tax/Total block as plain text; the
        caller parses out the "Total:" line."""
        return self.page.locator(".cart-total").inner_text() if self.page.locator(".cart-total").count() else ""

    def accept_terms_and_checkout(self) -> Dict:
        def try_terms(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.check()
            return True

        terms_result = resolve_with_fallback("terms_of_service", CART_CANDIDATES["terms_of_service"], try_terms)

        def try_checkout(candidate) -> bool:
            locator = self.page.locator(candidate.expression)
            if locator.count() == 0:
                return False
            locator.first.click()
            return True

        checkout_result = resolve_with_fallback("checkout_button", CART_CANDIDATES["checkout_button"], try_checkout)
        return {"terms_of_service": terms_result.to_dict(), "checkout_button": checkout_result.to_dict()}
