"""Post-MVP2 Enhancement 01 -- Page Object Model base class."""
from __future__ import annotations

from automation.playwright.config import PlaywrightConfig


class BasePage:
    def __init__(self, page, config: PlaywrightConfig):
        self.page = page
        self.config = config

    def navigate(self, path: str = "/") -> None:
        self.page.goto(f"{self.config.base_url}{path}", timeout=self.config.navigation_timeout_ms)

    @property
    def title(self) -> str:
        return self.page.title()
