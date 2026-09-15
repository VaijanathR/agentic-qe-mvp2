"""
CP-MVP2-07 — persistence for RCARecord / ReplanningRecord / GovernanceRecord.

Purely additive; delegates all on-disk version/pointer logic to the
unmodified, shared `persistence/envelope.py` (per this project's
standing "new capability = new package, reuse the shared envelope"
pattern, established at CR-001 Batch 1).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact
from rca.schema import GovernanceRecord, RCARecord, ReplanningRecord

RCA_BASE_DIR = REPO_ROOT / "rca" / "generated" / "rca"
REPLANNING_BASE_DIR = REPO_ROOT / "rca" / "generated" / "replanning"
GOVERNANCE_BASE_DIR = REPO_ROOT / "rca" / "generated" / "governance"

GENERATOR = "rca.pipeline.run_cp07_rca (deterministic-only, no LLM)"


def persist_rca(rca: RCARecord) -> Dict:
    return persist_artifact(RCA_BASE_DIR, artifact_id=rca.rca_id, payload=rca.to_dict(), generator=GENERATOR, provenance={"execution_id": rca.execution_id, "checkpoint": "CP-MVP2-07"})


def persist_replanning(replanning: ReplanningRecord) -> Dict:
    return persist_artifact(REPLANNING_BASE_DIR, artifact_id=replanning.replanning_id, payload=replanning.to_dict(), generator=GENERATOR, provenance={"rca_id": replanning.rca_id, "checkpoint": "CP-MVP2-07"})


def persist_governance(governance: GovernanceRecord) -> Dict:
    return persist_artifact(GOVERNANCE_BASE_DIR, artifact_id=governance.governance_id, payload=governance.to_dict(), generator=GENERATOR, provenance={"replanning_id": governance.replanning_id, "checkpoint": "CP-MVP2-07"})


def load_persisted_rca(rca_id: str) -> Optional[Dict]:
    return load_latest(RCA_BASE_DIR, rca_id)


def load_persisted_replanning(replanning_id: str) -> Optional[Dict]:
    return load_latest(REPLANNING_BASE_DIR, replanning_id)


def load_persisted_governance(governance_id: str) -> Optional[Dict]:
    return load_latest(GOVERNANCE_BASE_DIR, governance_id)


def list_persisted_rca_ids() -> List[str]:
    return list_artifact_ids(RCA_BASE_DIR)
