"""
CP-MVP2-CR-001 Batch 1 — Dependency/Reusability Matrix schema.

Explicitly NOT a risk-prioritization artifact (that is RBTP's concern,
`rbtp/schema.py`). This schema carries no priority/risk field at all —
it only records structural relationships: what a testcase shares with,
depends on, or might duplicate relative to another testcase.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


class DependencyKind:
    SHARED_JOURNEY = "SHARED_JOURNEY"
    SHARED_PRECONDITION = "SHARED_PRECONDITION"
    SHARED_REQUIREMENT = "SHARED_REQUIREMENT"
    POSSIBLE_DUPLICATE_TESTING = "POSSIBLE_DUPLICATE_TESTING"


ALL_DEPENDENCY_KINDS = {
    DependencyKind.SHARED_JOURNEY,
    DependencyKind.SHARED_PRECONDITION,
    DependencyKind.SHARED_REQUIREMENT,
    DependencyKind.POSSIBLE_DUPLICATE_TESTING,
}


@dataclass
class DependencyEdge:
    testcase_id: str
    related_testcase_id: str
    kind: str
    evidence: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DependencyMatrix:
    matrix_id: str
    testcase_ids: List[str]
    edges: List[DependencyEdge] = field(default_factory=list)
    reusable_component_candidates: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d
