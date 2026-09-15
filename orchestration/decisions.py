"""
Agentic QE Orchestration -- the decision contract (governing instruction
sec. 43). Every major orchestration decision is recorded as one of these,
appended to the orchestration journal (`orchestration/journal.py`). This
is the "concise rationale + evidence references" the journal persists --
never a hidden chain-of-thought (sec. 37).
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from orchestration.ids import new_decision_id


@dataclass
class DecisionRecord:
    decision_id: str
    orchestration_id: str
    stage: str
    input_references: List[str]
    decision: str
    reason: str
    evidence_references: List[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"
    risk: str = "UNKNOWN"
    governance_state: str = "GREEN"
    proposed_action: Optional[str] = None
    approval_required: bool = False
    next_state: Optional[str] = None
    #: Wave 2 instruction sec. 12 additions -- which real agent/actor
    #: made this decision (see `orchestration/agents.py`), and what real
    #: alternative outcomes were genuinely available at this decision
    #: point (never fabricated -- an empty list is honest when only one
    #: outcome was ever possible).
    actor: str = "orchestrator"
    alternatives: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


def make_decision(
    *,
    orchestration_id: str,
    stage: str,
    input_references: List[str],
    decision: str,
    reason: str,
    evidence_references: Optional[List[str]] = None,
    confidence: str = "UNKNOWN",
    risk: str = "UNKNOWN",
    governance_state: str = "GREEN",
    proposed_action: Optional[str] = None,
    approval_required: bool = False,
    next_state: Optional[str] = None,
    actor: str = "orchestrator",
    alternatives: Optional[List[str]] = None,
) -> DecisionRecord:
    return DecisionRecord(
        decision_id=new_decision_id(orchestration_id, stage),
        orchestration_id=orchestration_id,
        stage=stage,
        input_references=list(input_references),
        decision=decision,
        reason=reason,
        evidence_references=list(evidence_references or []),
        confidence=confidence,
        risk=risk,
        governance_state=governance_state,
        proposed_action=proposed_action,
        approval_required=approval_required,
        next_state=next_state,
        actor=actor,
        alternatives=list(alternatives or []),
    )
