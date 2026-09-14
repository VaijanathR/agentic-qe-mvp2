"""
CP-MVP2-04 — deterministic test-data schema.

Implements the two-level TestDataSet/TestDataField model from the frozen
docs/CP-MVP2-04-SPECIFICATION-v1.0.md sec. 6 exactly as specified there,
for the same reason sec. 6.1 documents: a testcase like REQ-REG-01's
almost never needs a single independent field value — it needs a
coherent bundle (first_name, last_name, email, password,
confirm_password) together. Mirrors the fixed-vocabulary,
dataclass-plus-to_dict() convention already established in
knowledge/lib/schema.py (CP-MVP2-02) and testcases/schema.py (CP-MVP2-03).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class DataCategory:
    POSITIVE = "POSITIVE"
    ALTERNATE = "ALTERNATE"
    EXCEPTIONAL = "EXCEPTIONAL"
    BOUNDARY = "BOUNDARY"
    INVALID = "INVALID"


ALL_DATA_CATEGORIES = {
    DataCategory.POSITIVE,
    DataCategory.ALTERNATE,
    DataCategory.EXCEPTIONAL,
    DataCategory.BOUNDARY,
    DataCategory.INVALID,
}


class BoundaryClassification:
    NOMINAL = "NOMINAL"
    MIN_BOUNDARY = "MIN_BOUNDARY"
    MAX_BOUNDARY = "MAX_BOUNDARY"
    BELOW_MIN = "BELOW_MIN"
    ABOVE_MAX = "ABOVE_MAX"
    EMPTY = "EMPTY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class UniquenessRequirement:
    MUST_BE_UNIQUE = "MUST_BE_UNIQUE"
    MAY_REUSE = "MAY_REUSE"
    UNIQUENESS_UNKNOWN = "UNIQUENESS_UNKNOWN"


class ValueType:
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    EMAIL = "EMAIL"
    ENUM = "ENUM"


ALL_VALUE_TYPES = {
    ValueType.STRING, ValueType.INTEGER, ValueType.FLOAT,
    ValueType.BOOLEAN, ValueType.EMAIL, ValueType.ENUM,
}


class DataValidity:
    VALID = "VALID"
    INVALID = "INVALID"


class DataGovernanceStatus:
    """Deliberately the same vocabulary as testcases.schema.GovernanceStatus
    (spec sec. 6.4) — every downstream consumer already understands these
    states; inventing a parallel vocabulary would add no value."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    UNSUPPORTED_NEEDS_CLARIFICATION = "UNSUPPORTED_NEEDS_CLARIFICATION"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"


#: Statuses whose datasets legitimately count toward CP-MVP2-04 coverage
#: (spec sec. 14) — mirrors testcases.schema.COVERAGE_COUNTING_STATUSES.
COVERAGE_COUNTING_STATUSES = {
    DataGovernanceStatus.ACCEPTED,
    DataGovernanceStatus.POSSIBLE_DUPLICATE,
}


@dataclass
class TestDataField:
    __test__ = False  # not a pytest test class

    field_name: str
    field_value: Any
    value_type: str
    boundary_classification: str = BoundaryClassification.NOT_APPLICABLE
    uniqueness_requirement: str = UniquenessRequirement.UNIQUENESS_UNKNOWN
    dependency_reference: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TestDataSet:
    __test__ = False

    data_set_id: str
    testcase_id: str
    requirement_ids: List[str]
    data_category: str
    purpose: str
    validity: str
    fields: List[TestDataField] = field(default_factory=list)
    source_attribution: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class GovernedTestDataSet:
    """A TestDataSet plus the deterministic governance decision made
    about it — mirrors testcases.schema.GovernedTestcase. `reasons`
    explains any non-ACCEPTED status; empty for ACCEPTED."""

    dataset: TestDataSet
    governance_status: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"validation_status": self.governance_status, "notes": list(self.reasons)}
        d.update(self.dataset.to_dict())
        return d
