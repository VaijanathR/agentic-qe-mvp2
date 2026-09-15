"""
CP-MVP2-07 — RCA / Replanning / Governance schema.

Additive, new package. Reuses `execution.schema.FailureCategory`/
`FailureSubtype` by value (imported, never redefined) for
`final_rca_classification`/`final_rca_subtype` — per the frozen
`docs/CP-MVP2-07-SPECIFICATION-v1.0.md` sec. 5 ("reuse, never
reinvention"). Every RCA record structurally separates FACT/EVIDENCE
(`failure_symptom`, `observed_evidence`, `requirement_testcase_data_context`,
`historical_evidence`) from INFERENCE/CONCLUSION (`agent_inference`,
`root_cause_hypothesis`) — never conflated into one free-text field.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


class Confidence:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


ALL_CONFIDENCE_LEVELS = {Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW}


class ReplanningDecision:
    REPLAN_ALLOWED = "REPLAN_ALLOWED"
    REPLAN_NOT_ALLOWED = "REPLAN_NOT_ALLOWED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"


ALL_REPLANNING_DECISIONS = {
    ReplanningDecision.REPLAN_ALLOWED,
    ReplanningDecision.REPLAN_NOT_ALLOWED,
    ReplanningDecision.HUMAN_REVIEW_REQUIRED,
    ReplanningDecision.GOVERNANCE_BLOCKED,
}


class GovernanceDecision:
    ACTION_AUTHORIZED = "ACTION_AUTHORIZED"
    ACTION_DEFERRED_TO_HUMAN = "ACTION_DEFERRED_TO_HUMAN"
    NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"
    GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"


ALL_GOVERNANCE_DECISIONS = {
    GovernanceDecision.ACTION_AUTHORIZED,
    GovernanceDecision.ACTION_DEFERRED_TO_HUMAN,
    GovernanceDecision.NO_ACTION_REQUIRED,
    GovernanceDecision.GOVERNANCE_BLOCKED,
}


@dataclass
class RCARecord:
    __test__ = False

    rca_id: str
    execution_id: str
    automation_id: str
    testcase_id: str
    requirement_ids: List[str]
    test_data_set_id: str
    # --- FACT ---
    failure_symptom: str
    # --- EVIDENCE ---
    observed_evidence: Dict
    requirement_testcase_data_context: Dict
    historical_evidence: List[Dict] = field(default_factory=list)
    # --- INFERENCE (explicitly labeled, never presented as fact) ---
    agent_inference: str = ""
    # --- CONCLUSION ---
    root_cause_hypothesis: str = ""
    confidence: str = Confidence.LOW
    final_rca_classification: Optional[str] = None
    final_rca_subtype: Optional[str] = None
    # --- RECOMMENDATION (never self-executed) ---
    recommended_next_action: str = ""
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReplanningRecord:
    __test__ = False

    replanning_id: str
    rca_id: str
    execution_id: str
    decision: str
    reason: str
    evidence_refs: List[str] = field(default_factory=list)
    proposed_change: Optional[str] = None
    affected_artifacts: List[str] = field(default_factory=list)
    expected_benefit: Optional[str] = None
    governance_impact: str = ""
    human_approval_required: bool = True
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernanceRecord:
    governance_id: str
    rca_id: str
    replanning_id: str
    execution_id: str
    decision: str
    cr002_status: str
    prohibited_change_guard_passed: bool
    prohibited_change_guard_detail: Dict
    rationale: str
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
