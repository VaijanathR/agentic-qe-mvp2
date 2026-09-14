"""CP-MVP2-CR-001 Batch 1 — persisted RBTP artifacts."""
from __future__ import annotations

from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact
from rbtp.schema import GovernedRBTPRecord

BASE_DIR = REPO_ROOT / "rbtp" / "generated"


def persist_governed_record(g: GovernedRBTPRecord, generator: str, batch_id: str) -> Dict:
    payload = g.to_dict()
    return persist_artifact(
        BASE_DIR,
        artifact_id=g.record.rbtp_id,
        payload=payload,
        generator=generator,
        provenance={"batch_id": batch_id, "checkpoint": "RBTP"},
    )


def persist_batch(governed_records: List[GovernedRBTPRecord], generator: str, batch_id: str) -> List[Dict]:
    return [persist_governed_record(g, generator, batch_id) for g in governed_records]


def load_persisted_record(rbtp_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, rbtp_id)


def list_persisted_rbtp_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
