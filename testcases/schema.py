"""
CP-MVP2-03 — deterministic testcase schema.

Mirrors the conventions established in knowledge/lib/schema.py (CP-MVP2-02):
a fixed, deterministic vocabulary (plain string constants, not an LLM
decision) plus a dataclass with a to_dict() for JSON-friendly evidence
output. Field names follow the CP-MVP2-03 Specification v1.0, section 6
("Testcase Output Contract"), exactly — nothing added, nothing removed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


class ScenarioType:
    POSITIVE = "POSITIVE"
    ALTERNATE = "ALTERNATE"
    EXCEPTIONAL = "EXCEPTIONAL"


ALL_SCENARIO_TYPES = {ScenarioType.POSITIVE, ScenarioType.ALTERNATE, ScenarioType.EXCEPTIONAL}


class Priority:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GovernanceStatus:
    """Outcomes from the CP-MVP2-03 specification, section 17
    ("Governance Outcomes"). Decided exclusively by testcases/validate.py
    — never by the LLM (spec sec. 16)."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"


#: Statuses whose testcases legitimately cover their requirement(s).
#: DUPLICATE is deliberately excluded (it is represented by the first
#: ACCEPTED occurrence already); REJECTED/QUARANTINED never count.
COVERAGE_COUNTING_STATUSES = {GovernanceStatus.ACCEPTED, GovernanceStatus.POSSIBLE_DUPLICATE}

REQUIRED_NON_EMPTY_FIELDS = (
    "testcase_id",
    "title",
    "requirement_ids",
    "test_steps",
    "expected_result",
)


@dataclass
class Testcase:
    __test__ = False  # not a pytest test class; name follows the spec's "testcase" vocabulary

    testcase_id: str
    title: str
    requirement_ids: List[str]
    scenario_type: str
    preconditions: List[str]
    test_steps: List[str]
    expected_result: str
    priority: str = Priority.MEDIUM
    journey_id: Optional[str] = None
    test_data_reference: Optional[str] = None
    source_attribution: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernedTestcase:
    """A Testcase plus the deterministic governance decision made about
    it. `reasons` always explains a non-ACCEPTED status; it is empty for
    ACCEPTED testcases."""

    testcase: Testcase
    governance_status: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"governance_status": self.governance_status, "reasons": list(self.reasons)}
        d.update(self.testcase.to_dict())
        return d
