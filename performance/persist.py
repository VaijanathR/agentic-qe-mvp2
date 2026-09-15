"""CP-MVP2-08 — persistence for PerformanceRunRecord, via the unmodified,
shared `persistence/envelope.py` (same pattern as every other new capability
this project has added since CR-001 Batch 1)."""
from __future__ import annotations

from typing import Dict, List, Optional

from performance.schema import PerformanceRunRecord
from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact

BASE_DIR = REPO_ROOT / "performance" / "generated" / "records"

GENERATOR = "performance.pipeline.run_cp08_performance_scenario (real JMeter execution, deterministic parse)"


def persist_run(record: PerformanceRunRecord) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=record.run_id,
        payload=record.to_dict(),
        generator=GENERATOR,
        provenance={"scenario_id": record.scenario_id, "checkpoint": "CP-MVP2-08"},
    )


def load_persisted_run(run_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, run_id)


def list_persisted_run_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
