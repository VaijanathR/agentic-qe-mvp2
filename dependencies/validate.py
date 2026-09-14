"""CP-MVP2-CR-001 Batch 1 — deterministic Dependency Matrix validation."""
from __future__ import annotations

from typing import List

from dependencies.schema import ALL_DEPENDENCY_KINDS, DependencyMatrix


def validate_dependency_matrix(matrix: DependencyMatrix) -> dict:
    problems: List[str] = []
    known_ids = set(matrix.testcase_ids)
    for edge in matrix.edges:
        if edge.kind not in ALL_DEPENDENCY_KINDS:
            problems.append(f"INVALID_KIND:{edge.kind!r}")
        if edge.testcase_id not in known_ids:
            problems.append(f"EDGE_REFERENCES_UNKNOWN_TESTCASE:{edge.testcase_id}")
        # related_testcase_id may reference a testcase outside this
        # matrix's own eligible set (e.g. a POSSIBLE_DUPLICATE_OF
        # target that was itself REJECTED/QUARANTINED) -- that is
        # expected and not itself a validation problem, since it is
        # exactly the kind of fact this matrix exists to surface.
    return {"check": "dependency_matrix_schema", "passed": not problems, "detail": problems}
