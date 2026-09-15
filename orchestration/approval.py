"""
Agentic QE Orchestration -- structured human approval (governing
instruction sec. 34).

A plain, persisted record. Nothing in this module can mark itself
approved -- `record_approval()` requires the caller to supply
`approved_by` and `decision`, i.e. a real human input; there is no
code path that synthesizes an approval.
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from orchestration.ids import new_approval_id


class ApprovalDecision:
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


@dataclass
class ApprovalRecord:
    approval_id: str
    orchestration_id: str
    reason: str
    evidence_references: List[str]
    proposed_action: str
    risk: str
    affected_requirements: List[str]
    affected_artifacts: List[str]
    impact: str
    requested_decision: str
    decision: str = ApprovalDecision.PENDING
    approved_by: Optional[str] = None
    decided_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def request_approval(
    *,
    orchestration_id: str,
    reason: str,
    evidence_references: List[str],
    proposed_action: str,
    risk: str,
    affected_requirements: List[str],
    affected_artifacts: List[str],
    impact: str,
    requested_decision: str,
) -> ApprovalRecord:
    return ApprovalRecord(
        approval_id=new_approval_id(orchestration_id),
        orchestration_id=orchestration_id,
        reason=reason,
        evidence_references=list(evidence_references),
        proposed_action=proposed_action,
        risk=risk,
        affected_requirements=list(affected_requirements),
        affected_artifacts=list(affected_artifacts),
        impact=impact,
        requested_decision=requested_decision,
    )


def record_decision(record: ApprovalRecord, decision: str, approved_by: str) -> ApprovalRecord:
    """Requires a real `approved_by` identity string -- never defaults
    to a synthetic/anonymous approver."""
    if not approved_by:
        raise ValueError("record_decision() requires a real approved_by identity -- approval cannot be anonymous.")
    if decision not in (ApprovalDecision.APPROVED, ApprovalDecision.REJECTED):
        raise ValueError(f"decision must be APPROVED or REJECTED, got {decision!r}")
    record.decision = decision
    record.approved_by = approved_by
    record.decided_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return record
