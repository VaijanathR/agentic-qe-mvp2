"""
CP-MVP2-CR-001 Batch 1 — deterministic RBTP governance.

Mirrors the "LLM proposes (or here, elaborates), deterministic code
governs" boundary already established at every prior checkpoint. Every
function here is a plain equality/membership check.
"""
from __future__ import annotations

from typing import Dict, List

from rbtp.schema import (
    ALL_EXECUTION_RECOMMENDATIONS,
    ALL_PRIORITIES,
    ALL_RISK_LEVELS,
    RISK_FACTOR_FIELDS,
    GovernedRBTPRecord,
    RBTPGovernanceStatus,
    RBTPRecord,
)
from testcases.schema import GovernedTestcase


def govern_rbtp_record(record: RBTPRecord, accepted_testcases_by_id: Dict[str, GovernedTestcase]) -> GovernedRBTPRecord:
    if record.testcase_id not in accepted_testcases_by_id:
        return GovernedRBTPRecord(record, RBTPGovernanceStatus.REJECTED, ["TESTCASE_NOT_ACCEPTED_OR_UNKNOWN"])

    problems: List[str] = []
    for name in RISK_FACTOR_FIELDS:
        value = getattr(record, name)
        if value not in ALL_RISK_LEVELS:
            problems.append(f"INVALID_FACTOR:{name}={value!r}")
    if record.priority not in ALL_PRIORITIES:
        problems.append(f"INVALID_PRIORITY:{record.priority!r}")
    if record.execution_recommendation not in ALL_EXECUTION_RECOMMENDATIONS:
        problems.append(f"INVALID_EXECUTION_RECOMMENDATION:{record.execution_recommendation!r}")
    if not record.risk_rationale:
        problems.append("MISSING_RISK_RATIONALE")
    if not record.requirement_ids:
        problems.append("MISSING_REQUIREMENT_IDS")

    anchor = accepted_testcases_by_id[record.testcase_id]
    if set(record.requirement_ids) != set(anchor.testcase.requirement_ids):
        problems.append("REQUIREMENT_IDS_DO_NOT_MATCH_ANCHOR_TESTCASE")

    if problems:
        return GovernedRBTPRecord(record, RBTPGovernanceStatus.REJECTED, problems)
    return GovernedRBTPRecord(record, RBTPGovernanceStatus.ACCEPTED, [])


def govern_batch(records: List[RBTPRecord], accepted_testcases_by_id: Dict[str, GovernedTestcase]) -> List[GovernedRBTPRecord]:
    return [govern_rbtp_record(r, accepted_testcases_by_id) for r in records]
