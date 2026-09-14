"""
CP-MVP2-CR-001 Batch 1 — end-to-end RBTP batch pipeline.

Operates only on already-persisted, ACCEPTED CP-MVP2-03 testcases,
exactly as required ("RBTP must operate on persisted testcases").
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.rbtp_client import RBTPLLMClient
from rbtp.generate import generate_rbtp_for_testcase
from rbtp.persist import persist_batch
from rbtp.validate import govern_batch
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase


def run_rbtp_batch(
    kb: KnowledgeBase,
    governed_testcases: List[GovernedTestcase],
    llm: Optional[RBTPLLMClient] = None,
    batch_id: str = "default",
) -> Dict:
    accepted = [g for g in governed_testcases if g.governance_status == TestcaseGovernanceStatus.ACCEPTED]
    accepted_by_id = {g.testcase.testcase_id: g for g in accepted}

    records = [generate_rbtp_for_testcase(kb, g, llm) for g in accepted]
    governed_records = govern_batch(records, accepted_by_id)

    generator_name = llm.model_name if llm is not None else "deterministic-only"
    persisted = persist_batch(governed_records, generator_name, batch_id)

    by_status: Dict[str, List[str]] = {}
    for g in governed_records:
        by_status.setdefault(g.governance_status, []).append(g.record.rbtp_id)

    return {
        "governed_records": [g.to_dict() for g in governed_records],
        "by_status": by_status,
        "persisted": persisted,
        "testcase_ids_processed": sorted(accepted_by_id),
        "generator": generator_name,
    }
