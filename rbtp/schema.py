"""
CP-MVP2-CR-001 Batch 1 — RBTP (Risk-Based Test Prioritization) schema.

Per CR-001's correction: RBTP = **Risk-Based Test Prioritization**, a
persisted, explainable artifact answering "which testcases should be
executed first, and why" — NOT the earlier, superseded
"Requirement-Based Test Plan" reading (see
docs/CP-MVP2-CR-001-RBTP-CORRECTION.md).

RBTP is explicitly distinct from the Dependency/Reusability Matrix
(`dependencies/schema.py`): RBTP answers "what order/priority," the
Dependency Matrix answers "what depends on / can reuse what." Neither
schema below carries a field belonging to the other's concern.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


class RiskLevel:
    """A risk factor's value is HIGH/MEDIUM/LOW only when a real,
    citable evidence source exists to support that classification.
    UNKNOWN is used, by disclosed necessity, whenever no such source
    exists in this project — never invented to fill the gap."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


ALL_RISK_LEVELS = {RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW, RiskLevel.UNKNOWN}

RISK_FACTOR_FIELDS = (
    "business_criticality",
    "risk_likelihood",
    "change_impact",
    "defect_history",
    "dependency_impact",
    "security_impact",
    "customer_impact",
)


class Priority:
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


ALL_PRIORITIES = {Priority.P0, Priority.P1, Priority.P2, Priority.P3}


class ExecutionRecommendation:
    INCLUDE_IN_SMOKE_AND_REGRESSION = "INCLUDE_IN_SMOKE_AND_REGRESSION"
    INCLUDE_IN_REGRESSION = "INCLUDE_IN_REGRESSION"
    INCLUDE_IN_FULL_REGRESSION_ONLY = "INCLUDE_IN_FULL_REGRESSION_ONLY"


ALL_EXECUTION_RECOMMENDATIONS = {
    ExecutionRecommendation.INCLUDE_IN_SMOKE_AND_REGRESSION,
    ExecutionRecommendation.INCLUDE_IN_REGRESSION,
    ExecutionRecommendation.INCLUDE_IN_FULL_REGRESSION_ONLY,
}


class RBTPGovernanceStatus:
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass
class RBTPRecord:
    __test__ = False

    rbtp_id: str
    testcase_id: str
    requirement_ids: List[str]
    business_criticality: str
    risk_likelihood: str
    change_impact: str
    defect_history: str
    dependency_impact: str
    security_impact: str
    customer_impact: str
    priority: str
    execution_recommendation: str
    risk_rationale: str
    source_attribution: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernedRBTPRecord:
    record: RBTPRecord
    governance_status: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"validation_status": self.governance_status, "notes": list(self.reasons)}
        d.update(self.record.to_dict())
        return d
