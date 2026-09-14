"""
CP-MVP2-03 — deterministic governance and validation.

Per the frozen specification (secs. 8-14, 16-17), the LLM is never the
final governance authority. Every function in this module returns a
decision computed from plain equality/membership/lookup logic — never
from an LLM judgment call — mirroring the convention already established
in knowledge/lib/validate.py for CP-MVP2-02.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set

from knowledge.lib.retrieval import KnowledgeBase
from knowledge.lib.schema import ApprovalStatus
from testcases.schema import (
    ALL_SCENARIO_TYPES,
    COVERAGE_COUNTING_STATUSES,
    GovernanceStatus,
    GovernedTestcase,
    Testcase,
)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", (text or "").strip().lower())


def _result(check: str, passed: bool, detail) -> dict:
    return {"check": check, "passed": bool(passed), "detail": detail}


# ---------------------------------------------------------------------------
# Schema validation (spec sec. 14 "Schema")
# ---------------------------------------------------------------------------

def validate_schema(tc: Testcase) -> dict:
    problems: List[str] = []
    if not tc.testcase_id:
        problems.append("MISSING_TESTCASE_ID")
    if not tc.title:
        problems.append("MISSING_TITLE")
    if not tc.requirement_ids or not all(tc.requirement_ids):
        problems.append("MISSING_REQUIREMENT_IDS")
    if tc.scenario_type not in ALL_SCENARIO_TYPES:
        problems.append("INVALID_SCENARIO_TYPE")
    if not tc.test_steps:
        problems.append("MISSING_TEST_STEPS")
    if not tc.expected_result:
        problems.append("MISSING_EXPECTED_RESULT")
    return _result("schema", not problems, problems)


# ---------------------------------------------------------------------------
# Traceability + governance (spec secs. 8-11)
# ---------------------------------------------------------------------------

def _canonical_requirement_chunk(kb: KnowledgeBase, requirement_id: str) -> Optional[dict]:
    """The canonical record for a requirement ID: the highest-authority
    (lowest authority_tier) chunk carrying it, matching the same authority
    ranking CP-MVP2-02's retrieval already enforces. Restricted to
    content_type == "requirement" so a testcase cannot claim traceability
    to e.g. a business_rule or negative_case chunk that merely mentions
    the ID."""
    hits = [h for h in kb.by_id(requirement_id, include_non_current=True) if h["content_type"] == "requirement"]
    if not hits:
        return None
    return sorted(hits, key=lambda h: h["authority_tier"])[0]


def validate_traceability(tc: Testcase, kb: KnowledgeBase) -> dict:
    """Enforces spec sec. 9: missing/empty -> caller rejects; unknown ->
    caller quarantines; approved-but-not-current is treated the same as
    not-approved (never eligible)."""
    if not tc.requirement_ids or not all(tc.requirement_ids):
        return _result("traceability", False, {"status": "MISSING_OR_EMPTY_REQUIREMENT_ID"})

    problems: Dict[str, str] = {}
    for rid in tc.requirement_ids:
        canonical = _canonical_requirement_chunk(kb, rid)
        if canonical is None:
            problems[rid] = "UNKNOWN_REQUIREMENT_ID"
        elif not (canonical["source_type"] == "approved_srs" and canonical["approval_status"] == ApprovalStatus.APPROVED):
            problems[rid] = f"NOT_APPROVED:{canonical['source_type']}/{canonical['approval_status']}"
    return _result("traceability", not problems, problems)


def govern_testcase(tc: Testcase, kb: KnowledgeBase) -> GovernedTestcase:
    """Single-testcase deterministic governance decision. Duplicate
    classification is NOT decided here — it requires the full batch and
    is applied afterward by `detect_duplicates`."""
    schema_result = validate_schema(tc)
    if not schema_result["passed"]:
        return GovernedTestcase(tc, GovernanceStatus.REJECTED, [f"SCHEMA_INVALID:{p}" for p in schema_result["detail"]])

    trace_result = validate_traceability(tc, kb)
    if not trace_result["passed"]:
        detail = trace_result["detail"]
        if "status" in detail and detail["status"] == "MISSING_OR_EMPTY_REQUIREMENT_ID":
            return GovernedTestcase(tc, GovernanceStatus.REJECTED, ["MISSING_OR_EMPTY_REQUIREMENT_ID"])
        # Any draft/not-approved leakage anywhere in the mapping is a hard
        # reject (spec sec. 11 — draft leakage must never become
        # accepted). A mapping whose only problem is an unknown ID (no
        # leakage risk, just an unresolved reference) is quarantined
        # instead, pending human/Di clarification.
        reasons = [f"{rid}:{problem}" for rid, problem in detail.items()]
        has_leakage = any(str(problem).startswith("NOT_APPROVED") for problem in detail.values())
        status = GovernanceStatus.REJECTED if has_leakage else GovernanceStatus.QUARANTINED
        return GovernedTestcase(tc, status, reasons)

    if not tc.source_attribution:
        return GovernedTestcase(tc, GovernanceStatus.REJECTED, ["MISSING_SOURCE_ATTRIBUTION"])

    return GovernedTestcase(tc, GovernanceStatus.ACCEPTED, [])


# ---------------------------------------------------------------------------
# Duplicate detection (spec sec. 13)
# ---------------------------------------------------------------------------

def check_duplicate_testcase_ids(testcases: List[Testcase]) -> dict:
    counts = Counter(tc.testcase_id for tc in testcases)
    dupes = {tid: n for tid, n in counts.items() if n > 1}
    return _result("duplicate_testcase_ids", not dupes, dupes)


def _content_key(tc: Testcase) -> tuple:
    return (tuple(sorted(tc.requirement_ids)), tc.scenario_type, _normalize(tc.expected_result))


def _mapping_key(tc: Testcase) -> tuple:
    return (tuple(sorted(tc.requirement_ids)), tc.scenario_type)


def detect_duplicates(governed: List[GovernedTestcase]) -> None:
    """Mutates governance_status in place for testcases that were
    ACCEPTED by govern_testcase. Rejected/quarantined items are left
    untouched — duplicate classification only ever applies to items that
    already passed schema+traceability.

    Rule (spec sec. 13): the SAME requirement(s) + SAME scenario_type +
    SAME expected_result (normalized) is a true DUPLICATE of the first
    accepted occurrence. The SAME requirement(s) + SAME scenario_type but
    a DIFFERENT expected_result is only a POSSIBLE_DUPLICATE — flagged
    for review, but deliberately NOT removed or downgraded further, per
    the explicit safeguard against collapsing legitimately distinct
    scenarios that merely share a requirement and scenario type.
    """
    first_seen_exact: Dict[tuple, str] = {}
    first_seen_mapping: Dict[tuple, str] = {}
    for g in governed:
        if g.governance_status != GovernanceStatus.ACCEPTED:
            continue
        exact_key = _content_key(g.testcase)
        mapping_key = _mapping_key(g.testcase)
        if exact_key in first_seen_exact:
            g.governance_status = GovernanceStatus.DUPLICATE
            g.reasons.append(f"DUPLICATE_OF:{first_seen_exact[exact_key]}")
            continue
        first_seen_exact[exact_key] = g.testcase.testcase_id
        if mapping_key in first_seen_mapping:
            g.governance_status = GovernanceStatus.POSSIBLE_DUPLICATE
            g.reasons.append(f"POSSIBLE_DUPLICATE_OF:{first_seen_mapping[mapping_key]}")
        else:
            first_seen_mapping[mapping_key] = g.testcase.testcase_id


# ---------------------------------------------------------------------------
# Coverage (spec sec. 10)
# ---------------------------------------------------------------------------

def calculate_coverage(
    kb: KnowledgeBase,
    governed: List[GovernedTestcase],
    applicable_requirement_ids: Optional[Set[str]] = None,
) -> dict:
    if applicable_requirement_ids is None:
        applicable_requirement_ids = set(kb.manifests["approved_srs"]["ids"]["requirements"])

    covered: Set[str] = set()
    for g in governed:
        if g.governance_status not in COVERAGE_COUNTING_STATUSES:
            continue
        for rid in g.testcase.requirement_ids:
            # Deterministic guard: even a status that counts toward
            # coverage can never inflate coverage with an ID outside the
            # applicable universe (unknown/fabricated IDs cannot reach
            # ACCEPTED via govern_testcase, but this filter defends the
            # invariant unconditionally rather than trusting that alone).
            if rid in applicable_requirement_ids:
                covered.add(rid)

    uncovered = applicable_requirement_ids - covered
    total = len(applicable_requirement_ids)
    percentage = round(100.0 * len(covered) / total, 2) if total else 0.0
    return {
        "total_applicable_requirements": total,
        "covered_requirements": sorted(covered),
        "uncovered_requirements": sorted(uncovered),
        "coverage_percentage": percentage,
    }


# ---------------------------------------------------------------------------
# Batch orchestration
# ---------------------------------------------------------------------------

def govern_batch(testcases: List[Testcase], kb: KnowledgeBase) -> List[GovernedTestcase]:
    governed = [govern_testcase(tc, kb) for tc in testcases]
    detect_duplicates(governed)
    return governed


def build_report(
    testcases: List[Testcase],
    kb: KnowledgeBase,
    applicable_requirement_ids: Optional[Set[str]] = None,
) -> dict:
    id_check = check_duplicate_testcase_ids(testcases)
    governed = govern_batch(testcases, kb)
    coverage = calculate_coverage(kb, governed, applicable_requirement_ids)

    by_status: Dict[str, List[str]] = defaultdict(list)
    for g in governed:
        by_status[g.governance_status].append(g.testcase.testcase_id)

    return {
        "duplicate_testcase_id_check": id_check,
        "governed_testcases": [g.to_dict() for g in governed],
        "by_status": dict(by_status),
        "coverage": coverage,
    }
