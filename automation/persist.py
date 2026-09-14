"""
CP-MVP2-CR-001 Batch 1 — persisted CP-MVP2-05 Playwright automation
artifacts.

Additive only: `automation/schema.py`, `generate.py`, `validate.py`, and
`pipeline.py` (the frozen CP-MVP2-05 implementation) are not modified.
Wraps the existing, unmodified `GovernedPlaywrightArtifact.to_dict()`
output; versioning/collision handling delegated to `persistence.envelope`.
The persisted artifact is what makes CP-06 able to load a specific,
previously-governed automation without it having to still exist in the
same process that generated it.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from automation.schema import GovernedPlaywrightArtifact
from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact

BASE_DIR = REPO_ROOT / "automation" / "generated"


def persist_governed_artifact(gpa: GovernedPlaywrightArtifact, generator: str, batch_id: str) -> Dict:
    payload = gpa.to_dict()
    return persist_artifact(
        BASE_DIR,
        artifact_id=gpa.artifact.automation_id,
        payload=payload,
        generator=generator,
        provenance={"batch_id": batch_id, "checkpoint": "CP-MVP2-05"},
    )


def persist_batch(governed_artifacts: List[GovernedPlaywrightArtifact], generator: str, batch_id: str) -> List[Dict]:
    return [persist_governed_artifact(g, generator, batch_id) for g in governed_artifacts]


def load_persisted_artifact(automation_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, automation_id)


def list_persisted_automation_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
