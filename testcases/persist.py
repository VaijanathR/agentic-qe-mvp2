"""
CP-MVP2-CR-001 Batch 1 — persisted CP-MVP2-03 testcase artifacts.

Additive only: `testcases/schema.py`, `generate.py`, `validate.py`, and
`pipeline.py` (the frozen CP-MVP2-03 implementation) are not modified by
this module. `persist_governed_testcase` wraps the existing, unmodified
`GovernedTestcase.to_dict()` output; versioning/collision handling is
delegated entirely to `persistence.envelope` (CR-001 sec. 16).

Closes the RED finding from
docs/claude-execution-reports/CP-MVP2-03/CP-MVP2-03-TESTCASE-PERSISTENCE-INVESTIGATION-*.md:
an accepted testcase is now independently readable from disk, in a fresh
process, without rerunning the LLM.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT, list_artifact_ids, load_latest, persist_artifact
from testcases.schema import GovernedTestcase

BASE_DIR = REPO_ROOT / "testcases" / "generated"


def persist_governed_testcase(gtc: GovernedTestcase, generator: str, batch_id: str) -> Dict:
    """Persists one governed testcase (any governance status — a
    REJECTED/QUARANTINED testcase is itself real evidence and must
    remain inspectable, not only ACCEPTED ones) as an immutable,
    ID-addressed artifact version."""
    payload = gtc.to_dict()
    return persist_artifact(
        BASE_DIR,
        artifact_id=gtc.testcase.testcase_id,
        payload=payload,
        generator=generator,
        provenance={"batch_id": batch_id, "checkpoint": "CP-MVP2-03"},
    )


def persist_batch(governed_testcases: List[GovernedTestcase], generator: str, batch_id: str) -> List[Dict]:
    return [persist_governed_testcase(g, generator, batch_id) for g in governed_testcases]


def load_persisted_testcase(testcase_id: str) -> Optional[Dict]:
    """Loads the latest persisted version of `testcase_id` from disk —
    the mechanism that makes a testcase independently consumable by
    CP-04/CP-05 without it having to still exist in Python memory."""
    return load_latest(BASE_DIR, testcase_id)


def list_persisted_testcase_ids() -> List[str]:
    return list_artifact_ids(BASE_DIR)
