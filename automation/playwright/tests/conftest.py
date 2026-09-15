"""
Post-MVP2 Enhancement 01/02 -- pytest fixtures for real, non-mocked
Playwright execution. Uses `playwright.sync_api.sync_playwright()`
directly (matching the frozen `execution/engine.py`'s own pattern),
rather than introducing a new `pytest-playwright` dependency.
"""
from __future__ import annotations

import os

import pytest
from playwright.sync_api import sync_playwright

from automation.playwright.config import DEFAULT_CONFIG
from automation.playwright.enh02_testdata import persist_all as _persist_enh02_testdata


def pytest_configure(config):
    """Persists the Enhancement-02 dataset corpus (governed, real JSON
    artifacts) exactly once, before test collection/execution begins, so
    `data_access.load_dataset()` can find them -- see that module's own
    docstring for the two-source lookup rule.

    Deliberately NOT a session-scoped autouse fixture: under
    `pytest-xdist`, each worker process has its own "session," so an
    autouse fixture calling this concurrently from multiple worker
    processes raced to read/write the same underlying
    `persistence/envelope.py` pointer files -- a real concurrency bug
    found and fixed this task (`JSONDecodeError` from a half-written
    pointer file). `pytest_configure` runs once, on the master process,
    before any worker is spawned, avoiding the race entirely."""
    if getattr(config, "workerinput", None) is None:
        _persist_enh02_testdata()


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
