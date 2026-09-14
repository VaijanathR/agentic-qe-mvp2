"""
CP-MVP2-CR-001 Batch 1 — persisted CP-MVP2-04 test-data artifacts.

Additive only: `testdata/schema.py`, `generate.py`, `validate.py`, and
`pipeline.py` (the frozen CP-MVP2-04 implementation) are not modified.
Wraps the existing, unmodified `GovernedTestDataSet.to_dict()` output;
versioning/collision handling delegated to `persistence.envelope`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact
from testdata.schema import GovernedTestDataSet

BASE_DIR = REPO_ROOT / "testdata" / "generated"


def persist_governed_dataset(gds: GovernedTestDataSet, generator: str, batch_id: str) -> Dict:
    payload = gds.to_dict()
    return persist_artifact(
        BASE_DIR,
        artifact_id=gds.dataset.data_set_id,
        payload=payload,
        generator=generator,
        provenance={"batch_id": batch_id, "checkpoint": "CP-MVP2-04"},
    )


def persist_batch(governed_datasets: List[GovernedTestDataSet], generator: str, batch_id: str) -> List[Dict]:
    return [persist_governed_dataset(g, generator, batch_id) for g in governed_datasets]


def load_persisted_dataset(data_set_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, data_set_id)


def list_persisted_dataset_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
