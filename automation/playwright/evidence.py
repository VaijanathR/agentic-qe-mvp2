"""
Post-MVP2 Enhancement 01 -- Playwright evidence capture (screenshots,
traces). Additive; writes only under `automation/playwright/generated/`.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from automation.playwright.config import EVIDENCE_ROOT


def evidence_dir_for(execution_id: str) -> Path:
    d = EVIDENCE_ROOT / execution_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def screenshot_path(execution_id: str, name: str) -> Path:
    return evidence_dir_for(execution_id) / f"{name}.png"


def trace_path(execution_id: str) -> Path:
    return evidence_dir_for(execution_id) / "trace.zip"


def relative_evidence_refs(execution_id: str) -> List[str]:
    from persistence.envelope import REPO_ROOT

    d = evidence_dir_for(execution_id)
    if not d.exists():
        return []
    return [str(p.relative_to(REPO_ROOT)) for p in sorted(d.iterdir()) if p.is_file()]
