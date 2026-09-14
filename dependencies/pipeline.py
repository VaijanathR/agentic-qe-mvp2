"""CP-MVP2-CR-001 Batch 1 — Dependency/Reusability Matrix batch pipeline."""
from __future__ import annotations

from typing import Dict, List

from dependencies.generate import build_dependency_matrix
from dependencies.persist import persist_dependency_matrix
from dependencies.validate import validate_dependency_matrix
from testcases.schema import GovernedTestcase


def run_dependency_matrix(governed_testcases: List[GovernedTestcase], matrix_id: str) -> Dict:
    matrix = build_dependency_matrix(governed_testcases, matrix_id)
    validation = validate_dependency_matrix(matrix)
    persisted = persist_dependency_matrix(matrix, generator="deterministic-only")
    return {
        "matrix": matrix.to_dict(),
        "validation": validation,
        "persisted": persisted,
    }
