"""CP-MVP2-CR-001 Batch 1 — persisted Dependency/Reusability Matrix."""
from __future__ import annotations

from typing import Dict, Optional

from dependencies.schema import DependencyMatrix
from persistence.envelope import REPO_ROOT, load_latest, persist_artifact

BASE_DIR = REPO_ROOT / "dependencies" / "generated"


def persist_dependency_matrix(matrix: DependencyMatrix, generator: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=matrix.matrix_id,
        payload=matrix.to_dict(),
        generator=generator,
        provenance={"kind": "dependency_reusability_matrix"},
    )


def load_persisted_matrix(matrix_id: str) -> Optional[Dict]:
    return load_latest(BASE_DIR, matrix_id)
