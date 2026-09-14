"""
CP-MVP2-CR-001 Batch 1 — deterministic Dependency/Reusability Matrix
generation.

Fully deterministic, no LLM: every edge is a plain set-overlap/equality
check over already-governed CP-MVP2-03 testcase fields (journey_id,
preconditions text, requirement_ids) plus CP-MVP2-03's own existing
duplicate-detection reasons. Per CR-001 sec. 7: "Do not create
abstractions merely for architectural appearance. Only identify reuse
where there is actual repetition or evidence-backed commonality" —
`reusable_component_candidates` is populated only from precondition text
that is literally, exactly shared by 2+ real testcases, never inferred.
"""
from __future__ import annotations

import datetime
import re
from collections import defaultdict
from typing import Dict, List

from dependencies.schema import DependencyEdge, DependencyKind, DependencyMatrix
from testcases.schema import GovernanceStatus, GovernedTestcase

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", (text or "").strip().lower())


#: Matrix input is every testcase whose CP-03 governance status counts
#: toward coverage (ACCEPTED/POSSIBLE_DUPLICATE) — mirrors
#: `testcases.schema.COVERAGE_COUNTING_STATUSES` exactly, reused rather
#: than reinvented.
_ELIGIBLE_STATUSES = {GovernanceStatus.ACCEPTED, GovernanceStatus.POSSIBLE_DUPLICATE}


def build_dependency_matrix(governed_testcases: List[GovernedTestcase], matrix_id: str) -> DependencyMatrix:
    eligible = [g for g in governed_testcases if g.governance_status in _ELIGIBLE_STATUSES]
    edges: List[DependencyEdge] = []

    by_journey: Dict[str, List[str]] = defaultdict(list)
    by_precondition: Dict[str, List[str]] = defaultdict(list)
    by_requirement: Dict[str, List[str]] = defaultdict(list)
    for g in eligible:
        tc = g.testcase
        if tc.journey_id:
            by_journey[tc.journey_id].append(tc.testcase_id)
        for p in tc.preconditions:
            by_precondition[_normalize(p)].append(tc.testcase_id)
        for rid in tc.requirement_ids:
            by_requirement[rid].append(tc.testcase_id)

    def _pairwise_edges(groups: Dict[str, List[str]], kind: str, evidence_fmt) -> None:
        for key, tcids in groups.items():
            unique = sorted(set(tcids))
            if len(unique) < 2:
                continue
            for i in range(len(unique)):
                for j in range(i + 1, len(unique)):
                    edges.append(DependencyEdge(unique[i], unique[j], kind, evidence_fmt(key)))

    _pairwise_edges(by_journey, DependencyKind.SHARED_JOURNEY, lambda jid: f"both belong to journey {jid}")
    _pairwise_edges(by_precondition, DependencyKind.SHARED_PRECONDITION, lambda key: f"identical precondition text: {key!r}")
    _pairwise_edges(by_requirement, DependencyKind.SHARED_REQUIREMENT, lambda rid: f"both trace to requirement {rid}")

    for g in governed_testcases:
        if g.governance_status == GovernanceStatus.POSSIBLE_DUPLICATE:
            for r in g.reasons:
                if r.startswith("POSSIBLE_DUPLICATE_OF:"):
                    other = r.split(":", 1)[1]
                    edges.append(DependencyEdge(g.testcase.testcase_id, other, DependencyKind.POSSIBLE_DUPLICATE_TESTING, r))

    reusable_candidates = [
        {
            "candidate_kind": "SHARED_SETUP_PRECONDITION",
            "precondition": key,
            "testcase_ids": sorted(set(tcids)),
        }
        for key, tcids in by_precondition.items()
        if len(set(tcids)) > 1
    ]

    return DependencyMatrix(
        matrix_id=matrix_id,
        testcase_ids=sorted(g.testcase.testcase_id for g in eligible),
        edges=edges,
        reusable_component_candidates=reusable_candidates,
        generation_metadata={
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "generator": "deterministic-only (no LLM used anywhere in dependency-matrix generation)",
            "eligible_testcase_count": len(eligible),
        },
    )
