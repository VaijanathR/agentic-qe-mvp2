"""
CP-MVP2-CR-001 Batch 1 — persisted Requirement <-> Testcase traceability.

Adds no new governance rule: reuses the existing, unmodified
`testcases.validate.calculate_coverage()` for the coverage arithmetic and
only reshapes/persists what CP-MVP2-03's own frozen governance already
decided (an unknown/orphan requirement ID is already rejected or
quarantined by `testcases.validate.govern_testcase`; this module surfaces
that fact for persisted, bidirectional navigation — it does not itself
decide traceability validity).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Set

from knowledge.lib.retrieval import KnowledgeBase
from persistence.envelope import REPO_ROOT, persist_artifact
from testcases.schema import GovernanceStatus, GovernedTestcase
from testcases.validate import calculate_coverage

BASE_DIR = REPO_ROOT / "traceability" / "req_to_testcase"


def build_req_testcase_traceability(
    governed_testcases: List[GovernedTestcase],
    kb: KnowledgeBase,
    applicable_requirement_ids: Optional[Set[str]] = None,
) -> Dict:
    coverage = calculate_coverage(kb, governed_testcases, applicable_requirement_ids)

    req_to_tc: Dict[str, List[str]] = defaultdict(list)
    tc_to_req: Dict[str, List[str]] = {}
    orphan_or_invalid: List[Dict] = []
    for g in governed_testcases:
        tc_to_req[g.testcase.testcase_id] = list(g.testcase.requirement_ids)
        for rid in g.testcase.requirement_ids:
            req_to_tc[rid].append(g.testcase.testcase_id)
        if g.governance_status in (GovernanceStatus.QUARANTINED, GovernanceStatus.REJECTED):
            if any("UNKNOWN_REQUIREMENT_ID" in r or "MISSING_OR_EMPTY_REQUIREMENT_ID" in r for r in g.reasons):
                orphan_or_invalid.append({"testcase_id": g.testcase.testcase_id, "reasons": list(g.reasons)})

    return {
        "coverage": coverage,
        "requirement_to_testcases": {rid: sorted(tcs) for rid, tcs in req_to_tc.items()},
        "testcase_to_requirements": tc_to_req,
        "orphan_or_invalid_references": orphan_or_invalid,
        "testcase_status": {g.testcase.testcase_id: g.governance_status for g in governed_testcases},
    }


def persist_req_testcase_traceability(payload: Dict, generator: str, batch_id: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=batch_id,
        payload=payload,
        generator=generator,
        provenance={"checkpoint": "CP-MVP2-03", "kind": "req_to_testcase_traceability"},
    )
