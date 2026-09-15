"""
Post-MVP2 Enhancement 01 -- centralized Playwright configuration.

Additive, new package (`automation/playwright/`). Does not modify, import
for write, or otherwise touch the frozen `automation/schema.py`,
`generate.py`, `validate.py`, `pipeline.py`, `evidence.py`, or
`automation/multi_locator/` (CR-002 investigation package) -- those remain
exactly as closed at the MVP2 baseline `33b9946`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from persistence.envelope import REPO_ROOT

GENERATED_ROOT = REPO_ROOT / "automation" / "playwright" / "generated"
EVIDENCE_ROOT = GENERATED_ROOT / "evidence"
LOGS_ROOT = GENERATED_ROOT / "logs"
EXECUTIONS_ROOT = GENERATED_ROOT / "executions"


@dataclass(frozen=True)
class PlaywrightConfig:
    base_url: str = "https://demowebshop.tricentis.com"
    browser: str = "chromium"
    headless: bool = True
    default_timeout_ms: int = 30000
    navigation_timeout_ms: int = 30000
    screenshot_on_failure: bool = True
    trace_on_failure: bool = True
    evidence_dir: Path = EVIDENCE_ROOT
    logs_dir: Path = LOGS_ROOT

    @staticmethod
    def from_environment() -> "PlaywrightConfig":
        """Environment-variable overrides (ENH01_* prefix, to avoid any
        collision with this project's existing JAVA_HOME/JMETER_EXECUTABLE
        convention). Defaults match the values verified during this
        enhancement's real Windows execution."""
        return PlaywrightConfig(
            base_url=os.environ.get("ENH01_BASE_URL", "https://demowebshop.tricentis.com"),
            headless=os.environ.get("ENH01_HEADLESS", "true").lower() != "false",
        )


DEFAULT_CONFIG = PlaywrightConfig.from_environment()
