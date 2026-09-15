"""
Post-MVP2 Enhancement 01 -- reusable navigation component (backlog item
E-07). Wraps the common "start at the home page" entry sequence every
automated testcase in this framework needs, so it is written once rather
than copy-pasted into every test.
"""
from __future__ import annotations

from automation.playwright.config import PlaywrightConfig
from automation.playwright.pages.home_page import HomePage


def start_at_home(page, config: PlaywrightConfig) -> HomePage:
    home = HomePage(page, config)
    home.open()
    return home
