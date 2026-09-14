"""
CP-MVP2-04 — deterministic test-data governance.

Per the frozen specification (secs. 8-14, 16): the LLM is never the
final governance authority for generated test data. Every function here
returns a decision computed from plain equality/membership/lookup logic
— never from an LLM judgment call — mirroring testcases/validate.py
(CP-MVP2-03) and knowledge/lib/validate.py (CP-MVP2-02).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set

from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase
from testdata.constraints import ConstraintProfile, get_constraint_profile
from testdata.schema import (
    COVERAGE_COUNTING_STATUSES,
    DataGovernanceStatus,
    DataValidity,
    GovernedTestDataSet,
    TestDataSet,
    UniquenessRequirement,
)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize(value) -> str:
    return _WHITESPACE_RE.sub(" ", str(value if value is not None else "").strip().lower())


def _result(check: str, passed: bool, detail) -> dict:
    return {"check": check, "passed": bool(passed), "detail": detail}


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(dataset: TestDataSet) -> dict:
    problems: List[str] = []
    if not dataset.data_set_id:
        problems.append("MISSING_DATA_SET_ID")
    if not dataset.testcase_id:
        problems.append("MISSING_TESTCASE_ID")
    if not dataset.requirement_ids:
        problems.append("MISSING_REQUIREMENT_IDS")
    if dataset.data_category not in {"POSITIVE", "ALTERNATE", "EXCEPTIONAL", "BOUNDARY", "INVALID"}:
        problems.append("INVALID_DATA_CATEGORY")
    if dataset.validity not in (DataValidity.VALID, DataValidity.INVALID):
        problems.append("INVALID_VALIDITY")
    if not dataset.fields:
        problems.append("NO_FIELDS")
    for f in dataset.fields:
        if not f.field_name:
            problems.append("FIELD_MISSING_NAME")
        if f.value_type not in {"STRING", "INTEGER", "FLOAT", "BOOLEAN", "EMAIL", "ENUM"}:
            problems.append(f"FIELD_INVALID_VALUE_TYPE:{f.field_name}")
    return _result("schema", not problems, problems)


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def validate_traceability(dataset: TestDataSet, accepted_testcases_by_id: Dict[str, GovernedTestcase]) -> dict:
    testcase = accepted_testcases_by_id.get(dataset.testcase_id)
    if testcase is None:
        return _result("traceability", False, {"status": "UNKNOWN_TESTCASE_ID"})
    if testcase.governance_status != TestcaseGovernanceStatus.ACCEPTED:
        return _result(
            "traceability", False,
            {"status": f"TESTCASE_NOT_ACCEPTED:{testcase.governance_status}"},
        )
    if sorted(dataset.requirement_ids) != sorted(testcase.testcase.requirement_ids):
        return _result(
            "traceability", False,
            {"status": "REQUIREMENT_IDS_DO_NOT_MATCH_TESTCASE", "expected": sorted(testcase.testcase.requirement_ids), "actual": sorted(dataset.requirement_ids)},
        )
    if not dataset.source_attribution:
        return _result("traceability", False, {"status": "MISSING_SOURCE_ATTRIBUTION"})
    return _result("traceability", True, {})


# ---------------------------------------------------------------------------
# Requirement-derived constraint validation (symmetric VALID/INVALID check)
# ---------------------------------------------------------------------------

def validate_constraints(dataset: TestDataSet, profile: ConstraintProfile) -> dict:
    field_map = {f.field_name: f.field_value for f in dataset.fields}
    mandatory_names = {s.field_name for s in profile.field_specs if s.mandatory}

    missing_mandatory = sorted(n for n in mandatory_names if n not in field_map)
    blank_mandatory = sorted(
        n for n in mandatory_names if n in field_map and (field_map[n] is None or field_map[n] == "")
    )

    dependency_violations = []
    for spec in profile.field_specs:
        if spec.dependency_reference and spec.field_name in field_map and spec.dependency_reference in field_map:
            if field_map[spec.field_name] != field_map[spec.dependency_reference]:
                dependency_violations.append(f"{spec.field_name}!={spec.dependency_reference}")

    enum_violations = [
        spec.field_name
        for spec in profile.field_specs
        if spec.allowed_values and spec.field_name in field_map and field_map[spec.field_name] not in spec.allowed_values
    ]

    email_format_violations = [
        spec.field_name
        for spec in profile.field_specs
        if spec.value_type == "EMAIL"
        and spec.field_name in field_map
        and not (isinstance(field_map[spec.field_name], str) and "@" in field_map[spec.field_name] and "." in field_map[spec.field_name].split("@")[-1])
    ]

    # A field the profile normally marks MUST_BE_UNIQUE, but which this
    # specific dataset explicitly carries as MAY_REUSE, is itself a
    # governed signal of an intentional documented-duplicate case (spec
    # sec. 10.1's "intentionally reused" example, e.g. NEG-04's reused
    # registration email) — the actual collision is confirmed later, at
    # batch level, by enforce_uniqueness against real accepted data; a
    # single dataset in isolation cannot detect a duplicate by itself.
    must_be_unique_names = {s.field_name for s in profile.field_specs if s.uniqueness_requirement == UniquenessRequirement.MUST_BE_UNIQUE}
    uniqueness_override_present = any(
        f.field_name in must_be_unique_names and f.uniqueness_requirement == UniquenessRequirement.MAY_REUSE
        for f in dataset.fields
    )

    any_violation = bool(
        missing_mandatory or blank_mandatory or dependency_violations
        or enum_violations or email_format_violations or uniqueness_override_present
    )
    detail = {
        "missing_mandatory": missing_mandatory,
        "blank_mandatory": blank_mandatory,
        "dependency_violations": dependency_violations,
        "enum_violations": enum_violations,
        "email_format_violations": email_format_violations,
        "uniqueness_override_present": uniqueness_override_present,
    }

    if dataset.validity == DataValidity.VALID:
        # A dataset claiming to be VALID must violate nothing.
        return _result("constraints", not any_violation, detail)
    # A dataset claiming to be INVALID must actually violate something
    # recognized — an "invalid" dataset that violates nothing is not a
    # legitimate documented negative case; it is rejected, not trusted.
    return _result("constraints", any_violation, detail)


# ---------------------------------------------------------------------------
# Per-dataset governance
# ---------------------------------------------------------------------------

def govern_dataset(dataset: TestDataSet, accepted_testcases_by_id: Dict[str, GovernedTestcase]) -> GovernedTestDataSet:
    schema_result = validate_schema(dataset)
    if not schema_result["passed"]:
        return GovernedTestDataSet(dataset, DataGovernanceStatus.REJECTED, [f"SCHEMA_INVALID:{p}" for p in schema_result["detail"]])

    trace_result = validate_traceability(dataset, accepted_testcases_by_id)
    if not trace_result["passed"]:
        status = trace_result["detail"]["status"]
        governance_status = DataGovernanceStatus.QUARANTINED if status == "UNKNOWN_TESTCASE_ID" else DataGovernanceStatus.REJECTED
        return GovernedTestDataSet(dataset, governance_status, [status])

    profile = get_constraint_profile(dataset.requirement_ids[0]) if dataset.requirement_ids else None
    if profile is None:
        return GovernedTestDataSet(dataset, DataGovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION, ["NO_CONSTRAINT_PROFILE"])

    constraint_result = validate_constraints(dataset, profile)
    if not constraint_result["passed"]:
        return GovernedTestDataSet(dataset, DataGovernanceStatus.REJECTED, [f"CONSTRAINT_VIOLATION:{constraint_result['detail']}"])

    return GovernedTestDataSet(dataset, DataGovernanceStatus.ACCEPTED, [])


# ---------------------------------------------------------------------------
# Duplicate detection (content-level)
# ---------------------------------------------------------------------------

def check_duplicate_dataset_ids(datasets: List[TestDataSet]) -> dict:
    counts = Counter(d.data_set_id for d in datasets)
    dupes = {did: n for did, n in counts.items() if n > 1}
    return _result("duplicate_data_set_ids", not dupes, dupes)


def _content_key(dataset: TestDataSet) -> tuple:
    field_tuple = tuple(sorted((f.field_name, _normalize(f.field_value)) for f in dataset.fields))
    return (dataset.testcase_id, dataset.data_category, field_tuple)


def _mapping_key(dataset: TestDataSet) -> tuple:
    return (dataset.testcase_id, dataset.data_category)


def detect_duplicates(governed: List[GovernedTestDataSet]) -> None:
    """Mutates governance_status in place for datasets that were
    ACCEPTED by govern_dataset. Exact repeats -> DUPLICATE; same
    (testcase, category) with different field content -> POSSIBLE_DUPLICATE
    (kept, never dropped) — mirrors testcases.validate.detect_duplicates."""
    first_seen_exact: Dict[tuple, str] = {}
    first_seen_mapping: Dict[tuple, str] = {}
    for g in governed:
        if g.governance_status != DataGovernanceStatus.ACCEPTED:
            continue
        exact_key = _content_key(g.dataset)
        mapping_key = _mapping_key(g.dataset)
        if exact_key in first_seen_exact:
            g.governance_status = DataGovernanceStatus.DUPLICATE
            g.reasons.append(f"DUPLICATE_OF:{first_seen_exact[exact_key]}")
            continue
        first_seen_exact[exact_key] = g.dataset.data_set_id
        if mapping_key in first_seen_mapping:
            g.governance_status = DataGovernanceStatus.POSSIBLE_DUPLICATE
            g.reasons.append(f"POSSIBLE_DUPLICATE_OF:{first_seen_mapping[mapping_key]}")
        else:
            first_seen_mapping[mapping_key] = g.dataset.data_set_id


# ---------------------------------------------------------------------------
# Uniqueness enforcement (spec sec. 10)
# ---------------------------------------------------------------------------

def enforce_uniqueness(governed: List[GovernedTestDataSet]) -> None:
    """Mutates governance_status for datasets carrying a MUST_BE_UNIQUE
    field whose value collides with an earlier ACCEPTED/POSSIBLE_DUPLICATE
    dataset's same-named field. The system never alters the colliding
    value to "fix" it — collision is a REJECTED outcome, not silently
    repaired (spec sec. 10.2)."""
    seen: Dict[str, Dict[str, str]] = defaultdict(dict)  # field_name -> {normalized_value: data_set_id}
    for g in governed:
        if g.governance_status not in (DataGovernanceStatus.ACCEPTED, DataGovernanceStatus.POSSIBLE_DUPLICATE):
            continue
        collided = False
        for f in g.dataset.fields:
            if f.uniqueness_requirement != UniquenessRequirement.MUST_BE_UNIQUE:
                continue
            key = _normalize(f.field_value)
            existing = seen[f.field_name].get(key)
            if existing and existing != g.dataset.data_set_id:
                g.governance_status = DataGovernanceStatus.REJECTED
                g.reasons.append(f"UNIQUENESS_COLLISION:{f.field_name}:{existing}")
                collided = True
                break
        if not collided:
            for f in g.dataset.fields:
                if f.uniqueness_requirement == UniquenessRequirement.MUST_BE_UNIQUE:
                    seen[f.field_name][_normalize(f.field_value)] = g.dataset.data_set_id


# ---------------------------------------------------------------------------
# Coverage (spec sec. 14)
# ---------------------------------------------------------------------------

def calculate_coverage(
    governed: List[GovernedTestDataSet],
    applicable_testcase_ids: Optional[Set[str]] = None,
) -> dict:
    if applicable_testcase_ids is None:
        applicable_testcase_ids = {g.dataset.testcase_id for g in governed}

    covered: Set[str] = set()
    for g in governed:
        if g.governance_status not in COVERAGE_COUNTING_STATUSES:
            continue
        if g.dataset.testcase_id in applicable_testcase_ids:
            covered.add(g.dataset.testcase_id)

    uncovered = applicable_testcase_ids - covered
    total = len(applicable_testcase_ids)
    percentage = round(100.0 * len(covered) / total, 2) if total else 0.0
    return {
        "total_applicable_testcases": total,
        "covered_testcases": sorted(covered),
        "uncovered_testcases": sorted(uncovered),
        "coverage_percentage": percentage,
    }


# ---------------------------------------------------------------------------
# Batch orchestration
# ---------------------------------------------------------------------------

def govern_batch(datasets: List[TestDataSet], accepted_testcases_by_id: Dict[str, GovernedTestcase]) -> List[GovernedTestDataSet]:
    governed = [govern_dataset(d, accepted_testcases_by_id) for d in datasets]
    detect_duplicates(governed)
    enforce_uniqueness(governed)
    return governed


def build_report(
    datasets: List[TestDataSet],
    accepted_testcases_by_id: Dict[str, GovernedTestcase],
    applicable_testcase_ids: Optional[Set[str]] = None,
) -> dict:
    id_check = check_duplicate_dataset_ids(datasets)
    governed = govern_batch(datasets, accepted_testcases_by_id)
    coverage = calculate_coverage(governed, applicable_testcase_ids)

    by_status: Dict[str, List[str]] = defaultdict(list)
    for g in governed:
        by_status[g.governance_status].append(g.dataset.data_set_id)

    return {
        "duplicate_data_set_id_check": id_check,
        "governed_datasets": [g.to_dict() for g in governed],
        "by_status": dict(by_status),
        "coverage": coverage,
    }
