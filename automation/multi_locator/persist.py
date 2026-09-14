"""Multi-locator artifact persistence — reuses persistence/envelope.py
(Batch 1, additive, unmodified) exactly like every other artifact family."""
from __future__ import annotations

from typing import Dict, List, Optional

from automation.multi_locator.schema import GovernedMultiLocatorArtifact
from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact

BASE_DIR = REPO_ROOT / "automation" / "multi_locator" / "generated"


def persist_governed_multi_locator_artifact(g: GovernedMultiLocatorArtifact, generator: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=g.artifact.ml_automation_id,
        payload=g.to_dict(),
        generator=generator,
        provenance={"kind": "multi_locator_artifact", "source_automation_id": g.artifact.source_automation_id},
    )


def load_persisted_multi_locator_artifact(ml_automation_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, ml_automation_id)


def list_persisted_multi_locator_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
