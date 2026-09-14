"""
CP-MVP2-05 — deterministic Playwright-artifact governance.

Per the frozen specification (secs. 3/9/11/12/17): the LLM is never the
final governance authority. Every function here returns a decision
computed from plain equality/membership/lookup logic — never from an
LLM judgment call — mirroring testcases/validate.py and
testdata/validate.py exactly, one layer further downstream.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set

from automation.schema import (
    ALL_ACTION_TYPES,
    COVERAGE_COUNTING_STATUSES,
    ELEMENT_TARGETING_ACTION_TYPES,
    ActionType,
    AssertionType,
    GovernanceStatus,
    GovernedPlaywrightArtifact,
    LocatorStatus,
    PlaywrightArtifact,
)
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase
from testdata.schema import DataGovernanceStatus, GovernedTestDataSet

ELIGIBLE_DATASET_STATUSES = {DataGovernanceStatus.ACCEPTED, DataGovernanceStatus.POSSIBLE_DUPLICATE}


def _result(check: str, passed: bool, detail) -> dict:
    return {"check": check, "passed": bool(passed), "detail": detail}


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(artifact: PlaywrightArtifact) -> dict:
    problems: List[str] = []
    if not artifact.automation_id:
        problems.append("MISSING_AUTOMATION_ID")
    if not artifact.testcase_id:
        problems.append("MISSING_TESTCASE_ID")
    if not artifact.requirement_ids:
        problems.append("MISSING_REQUIREMENT_IDS")
    if not artifact.test_data_set_id:
        problems.append("MISSING_TEST_DATA_SET_ID")
    if not artifact.steps:
        problems.append("NO_STEPS")
    if not artifact.assertions:
        problems.append("NO_ASSERTIONS")
    for step in artifact.steps:
        if step.action_type not in ALL_ACTION_TYPES:
            problems.append(f"STEP_INVALID_ACTION_TYPE:{step.step_order}")
    return _result("schema", not problems, problems)


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def validate_traceability(
    artifact: PlaywrightArtifact,
    accepted_testcases_by_id: Dict[str, GovernedTestcase],
    eligible_datasets_by_id: Dict[str, GovernedTestDataSet],
) -> dict:
    testcase = accepted_testcases_by_id.get(artifact.testcase_id)
    if testcase is None:
        return _result("traceability", False, {"status": "UNKNOWN_TESTCASE_ID"})
    if testcase.governance_status != TestcaseGovernanceStatus.ACCEPTED:
        return _result("traceability", False, {"status": f"TESTCASE_NOT_ACCEPTED:{testcase.governance_status}"})
    if sorted(artifact.requirement_ids) != sorted(testcase.testcase.requirement_ids):
        return _result("traceability", False, {"status": "REQUIREMENT_IDS_DO_NOT_MATCH_TESTCASE"})

    dataset = eligible_datasets_by_id.get(artifact.test_data_set_id)
    if dataset is None:
        return _result("traceability", False, {"status": "UNKNOWN_TEST_DATA_SET_ID"})
    if dataset.governance_status not in ELIGIBLE_DATASET_STATUSES:
        return _result("traceability", False, {"status": f"DATASET_NOT_ELIGIBLE:{dataset.governance_status}"})
    if dataset.dataset.testcase_id != artifact.testcase_id:
        return _result("traceability", False, {"status": "DATASET_TESTCASE_MISMATCH"})

    if not artifact.source_attribution:
        return _result("traceability", False, {"status": "MISSING_SOURCE_ATTRIBUTION"})

    return _result("traceability", True, {})


# ---------------------------------------------------------------------------
# Data-mapping integrity (spec sec. 9/17)
# ---------------------------------------------------------------------------

def validate_data_mapping(artifact: PlaywrightArtifact, dataset: GovernedTestDataSet) -> dict:
    available_field_names = {f.field_name for f in dataset.dataset.fields}
    unmapped = []
    for step in artifact.steps:
        if step.action_type in (ActionType.FILL, ActionType.SELECT):
            if step.input_mapping is None or step.input_mapping not in available_field_names:
                unmapped.append(step.step_order)
    return _result("data_mapping", not unmapped, {"unmapped_steps": unmapped})


# ---------------------------------------------------------------------------
# Assertion integrity (spec sec. 10/17)
# ---------------------------------------------------------------------------

def validate_assertions(artifact: PlaywrightArtifact) -> dict:
    business_required = [a for a in artifact.assertions if a.assertion_type == AssertionType.BUSINESS_REQUIRED]
    problems = []
    if not business_required:
        problems.append("NO_BUSINESS_REQUIRED_ASSERTION")
    for a in business_required:
        if not a.source or not a.condition:
            problems.append("BUSINESS_REQUIRED_ASSERTION_MISSING_SOURCE_OR_CONDITION")
    # Coverage-eligibility invariant: only BUSINESS_REQUIRED may count.
    for a in artifact.assertions:
        if a.assertion_type != AssertionType.BUSINESS_REQUIRED and a.counts_toward_coverage:
            problems.append(f"NON_BUSINESS_ASSERTION_FALSELY_COUNTS:{a.assertion_type}")
    return _result("assertions", not problems, problems)


# ---------------------------------------------------------------------------
# Locator integrity / load-bearing rule (spec sec. 6.4/12.1/13)
# ---------------------------------------------------------------------------

def validate_locators(artifact: PlaywrightArtifact) -> dict:
    unsupported_steps = [
        step.step_order
        for step in artifact.steps
        if step.action_type in ELEMENT_TARGETING_ACTION_TYPES
        and step.locator is not None
        and step.locator.status == LocatorStatus.UNSUPPORTED
    ]
    # Every element-targeting step is treated as load-bearing (spec sec.
    # 12.1: "any step required to reach or verify the core expected
    # result" -- this implementation conservatively treats every
    # FILL/CLICK/SELECT as load-bearing, since CP-MVP2-05 has no
    # deterministic way to prove a given UI action is safely skippable
    # without inventing that judgment itself).
    return _result("locators", not unsupported_steps, {"unsupported_steps": unsupported_steps})


# ---------------------------------------------------------------------------
# Per-artifact governance
# ---------------------------------------------------------------------------

def govern_artifact(
    artifact: PlaywrightArtifact,
    accepted_testcases_by_id: Dict[str, GovernedTestcase],
    eligible_datasets_by_id: Dict[str, GovernedTestDataSet],
) -> GovernedPlaywrightArtifact:
    schema_result = validate_schema(artifact)
    if not schema_result["passed"]:
        return GovernedPlaywrightArtifact(artifact, GovernanceStatus.REJECTED, [f"SCHEMA_INVALID:{p}" for p in schema_result["detail"]])

    trace_result = validate_traceability(artifact, accepted_testcases_by_id, eligible_datasets_by_id)
    if not trace_result["passed"]:
        status = trace_result["detail"]["status"]
        governance_status = (
            GovernanceStatus.QUARANTINED
            if status in ("UNKNOWN_TESTCASE_ID", "UNKNOWN_TEST_DATA_SET_ID")
            else GovernanceStatus.REJECTED
        )
        return GovernedPlaywrightArtifact(artifact, governance_status, [status])

    dataset = eligible_datasets_by_id[artifact.test_data_set_id]

    mapping_result = validate_data_mapping(artifact, dataset)
    if not mapping_result["passed"]:
        return GovernedPlaywrightArtifact(artifact, GovernanceStatus.REJECTED, [f"UNMAPPED_FIELD:{mapping_result['detail']}"])

    assertion_result = validate_assertions(artifact)
    if not assertion_result["passed"]:
        return GovernedPlaywrightArtifact(artifact, GovernanceStatus.REJECTED, [f"ASSERTION_INVALID:{p}" for p in assertion_result["detail"]])

    locator_result = validate_locators(artifact)
    if not locator_result["passed"]:
        return GovernedPlaywrightArtifact(
            artifact, GovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION,
            [f"LOCATOR_UNSUPPORTED:step_{s}" for s in locator_result["detail"]["unsupported_steps"]],
        )

    return GovernedPlaywrightArtifact(artifact, GovernanceStatus.ACCEPTED, [])


# ---------------------------------------------------------------------------
# Duplicate detection (content-level)
# ---------------------------------------------------------------------------

def check_duplicate_automation_ids(artifacts: List[PlaywrightArtifact]) -> dict:
    counts = Counter(a.automation_id for a in artifacts)
    dupes = {aid: n for aid, n in counts.items() if n > 1}
    return _result("duplicate_automation_ids", not dupes, dupes)


def _content_key(artifact: PlaywrightArtifact) -> tuple:
    step_tuple = tuple((s.action_type, s.input_mapping) for s in artifact.steps)
    return (artifact.testcase_id, artifact.test_data_set_id, step_tuple)


def _mapping_key(artifact: PlaywrightArtifact) -> tuple:
    return (artifact.testcase_id,)


def detect_duplicates(governed: List[GovernedPlaywrightArtifact]) -> None:
    first_seen_exact: Dict[tuple, str] = {}
    first_seen_mapping: Dict[tuple, str] = {}
    for g in governed:
        if g.governance_status != GovernanceStatus.ACCEPTED:
            continue
        exact_key = _content_key(g.artifact)
        mapping_key = _mapping_key(g.artifact)
        if exact_key in first_seen_exact:
            g.governance_status = GovernanceStatus.DUPLICATE
            g.reasons.append(f"DUPLICATE_OF:{first_seen_exact[exact_key]}")
            continue
        first_seen_exact[exact_key] = g.artifact.automation_id
        if mapping_key in first_seen_mapping:
            g.governance_status = GovernanceStatus.POSSIBLE_DUPLICATE
            g.reasons.append(f"POSSIBLE_DUPLICATE_OF:{first_seen_mapping[mapping_key]}")
        else:
            first_seen_mapping[mapping_key] = g.artifact.automation_id


# ---------------------------------------------------------------------------
# Coverage (spec sec. 18)
# ---------------------------------------------------------------------------

def calculate_coverage(governed: List[GovernedPlaywrightArtifact], applicable_testcase_ids: Optional[Set[str]] = None) -> dict:
    if applicable_testcase_ids is None:
        applicable_testcase_ids = {g.artifact.testcase_id for g in governed}

    covered: Set[str] = set()
    for g in governed:
        if g.governance_status not in COVERAGE_COUNTING_STATUSES:
            continue
        if g.artifact.testcase_id in applicable_testcase_ids:
            covered.add(g.artifact.testcase_id)

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

def govern_batch(
    artifacts: List[PlaywrightArtifact],
    accepted_testcases_by_id: Dict[str, GovernedTestcase],
    eligible_datasets_by_id: Dict[str, GovernedTestDataSet],
) -> List[GovernedPlaywrightArtifact]:
    governed = [govern_artifact(a, accepted_testcases_by_id, eligible_datasets_by_id) for a in artifacts]
    detect_duplicates(governed)
    return governed


def build_report(
    artifacts: List[PlaywrightArtifact],
    accepted_testcases_by_id: Dict[str, GovernedTestcase],
    eligible_datasets_by_id: Dict[str, GovernedTestDataSet],
    applicable_testcase_ids: Optional[Set[str]] = None,
) -> dict:
    id_check = check_duplicate_automation_ids(artifacts)
    governed = govern_batch(artifacts, accepted_testcases_by_id, eligible_datasets_by_id)
    coverage = calculate_coverage(governed, applicable_testcase_ids)

    by_status: Dict[str, List[str]] = defaultdict(list)
    for g in governed:
        by_status[g.governance_status].append(g.artifact.automation_id)

    return {
        "duplicate_automation_id_check": id_check,
        "governed_artifacts": [g.to_dict() for g in governed],
        "by_status": dict(by_status),
        "coverage": coverage,
    }
