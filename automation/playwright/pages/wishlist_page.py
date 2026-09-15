"""
Post-MVP2 Enhancement 02 -- Wishlist Page Object.

Real evidence: real click of `.add-to-wishlist-button` on
https://demowebshop.tricentis.com/album-3 shows notification "The
product has been added to your wishlist"; the real `/wishlist` page
shows a real item row, `.product-unit-price`, a real
`input[name=removefromcart]`, and a real `.share-info` block containing
"Your wishlist URL for sharing:" plus a real, live URL.
"""
from __future__ import annotations

from automation.playwright.pages.base_page import BasePage


class WishlistPage(BasePage):
    def open(self) -> None:
        self.navigate("/wishlist")

    def has_item(self) -> bool:
        return self.page.locator(".cart tbody tr").count() > 0

    def item_price_text(self) -> str:
        return self.page.locator(".product-unit-price").first.inner_text() if self.page.locator(".product-unit-price").count() else ""

    def has_remove_action(self) -> bool:
        return self.page.locator("input[name=removefromcart]").count() > 0

    def has_add_to_cart_action(self) -> bool:
        return self.page.locator("input.button-1").count() > 0

    def shareable_url_text(self) -> str:
        return self.page.locator(".share-info").inner_text() if self.page.locator(".share-info").count() else ""

    def has_shareable_url(self) -> bool:
        text = self.shareable_url_text()
        return "wishlist URL for sharing" in text and "http" in text
