"""Multi-locator artifact pipeline — orchestration only, no new reasoning."""
from __future__ import annotations

from typing import Dict

from automation.multi_locator.generate import build_multi_locator_artifact
from automation.multi_locator.persist import persist_governed_multi_locator_artifact
from automation.multi_locator.validate import govern_multi_locator_artifact


def run_multi_locator_resolution(source_payload: Dict, ml_automation_id: str, generator: str = "deterministic-only") -> Dict:
    artifact = build_multi_locator_artifact(source_payload, ml_automation_id)
    governed = govern_multi_locator_artifact(artifact)
    persisted = persist_governed_multi_locator_artifact(governed, generator=generator)
    return {"governed": governed, "persisted": persisted}
