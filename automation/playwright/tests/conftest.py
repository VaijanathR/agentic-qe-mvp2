"""
Post-MVP2 Enhancement 01 -- pytest fixtures for real, non-mocked Playwright
execution. Uses `playwright.sync_api.sync_playwright()` directly (matching
the frozen `execution/engine.py`'s own pattern), rather than introducing a
new `pytest-playwright` dependency.
"""
from __future__ import annotations

import os

import pytest
from playwright.sync_api import sync_playwright

from automation.playwright.config import DEFAULT_CONFIG


@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=DEFAULT_CONFIG.headless)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(DEFAULT_CONFIG.default_timeout_ms)
        yield page, browser.version
        context.close()
        browser.close()


@pytest.fixture
def worker_id() -> str:
    return os.environ.get("PYTEST_XDIST_WORKER", "main")
