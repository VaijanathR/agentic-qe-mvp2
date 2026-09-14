"""
CP-MVP2-CR-001 Batch 1 — Dependency/Reusability Matrix tests.

Fully deterministic, no LLM. Verifies real set-overlap edges (shared
journey / precondition / requirement), surfacing of CP-03's own
POSSIBLE_DUPLICATE reasons, and the "no premature abstraction" rule
(a reusable-component candidate requires 2+ DISTINCT testcases, never 1).
"""
from __future__ import annotations

from dependencies.generate import build_dependency_matrix
from dependencies.schema import DependencyKind
from dependencies.validate import validate_dependency_matrix
from testcases.schema import GovernanceStatus, Testcase
from testcases.validate import govern_batch
from knowledge.lib.retrieval import KnowledgeBase


def _tc(**overrides) -> Testcase:
    base = dict(
        testcase_id="TC-X-01",
        title="t",
        requirement_ids=["REQ-REG-01"],
        scenario_type="POSITIVE",
        preconditions=["User is a Guest with no existing account"],
        test_steps=["step"],
        expected_result="result",
        journey_id="J-01",
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    return Testcase(**base)


def test_two_testcases_sharing_a_precondition_and_journey_produce_edges():
    kb = KnowledgeBase.load()
    tc1 = _tc(testcase_id="TC-X-01")
    tc2 = _tc(testcase_id="TC-X-02", scenario_type="ALTERNATE")
    governed = govern_batch([tc1, tc2], kb)
    assert all(g.governance_status == GovernanceStatus.ACCEPTED for g in governed)

    matrix = build_dependency_matrix(governed, matrix_id="M1")
    kinds = {(e.kind, tuple(sorted((e.testcase_id, e.related_testcase_id)))) for e in matrix.edges}
    assert (DependencyKind.SHARED_JOURNEY, ("TC-X-01", "TC-X-02")) in kinds
    assert (DependencyKind.SHARED_PRECONDITION, ("TC-X-01", "TC-X-02")) in kinds
    assert (DependencyKind.SHARED_REQUIREMENT, ("TC-X-01", "TC-X-02")) in kinds


def test_reusable_candidate_requires_two_distinct_testcases_not_one():
    kb = KnowledgeBase.load()
    tc1 = _tc(testcase_id="TC-X-01", preconditions=["A unique precondition seen nowhere else"])
    governed = govern_batch([tc1], kb)
    matrix = build_dependency_matrix(governed, matrix_id="M2")
    assert matrix.reusable_component_candidates == []


def test_reusable_candidate_appears_only_with_real_repetition():
    kb = KnowledgeBase.load()
    tc1 = _tc(testcase_id="TC-X-01")
    tc2 = _tc(testcase_id="TC-X-02", scenario_type="ALTERNATE")
    governed = govern_batch([tc1, tc2], kb)
    matrix = build_dependency_matrix(governed, matrix_id="M3")
    assert len(matrix.reusable_component_candidates) == 1
    candidate = matrix.reusable_component_candidates[0]
    assert set(candidate["testcase_ids"]) == {"TC-X-01", "TC-X-02"}


def test_possible_duplicate_from_cp03_governance_is_surfaced_as_an_edge():
    kb = KnowledgeBase.load()
    tc1 = _tc(testcase_id="TC-X-01", expected_result="result A")
    tc2 = _tc(testcase_id="TC-X-02", expected_result="result B")  # same req+scenario, different result -> POSSIBLE_DUPLICATE
    governed = govern_batch([tc1, tc2], kb)
    statuses = {g.testcase.testcase_id: g.governance_status for g in governed}
    assert statuses["TC-X-02"] == GovernanceStatus.POSSIBLE_DUPLICATE

    matrix = build_dependency_matrix(governed, matrix_id="M4")
    dup_edges = [e for e in matrix.edges if e.kind == DependencyKind.POSSIBLE_DUPLICATE_TESTING]
    assert any(e.testcase_id == "TC-X-02" and e.related_testcase_id == "TC-X-01" for e in dup_edges)


def test_rejected_testcase_is_excluded_from_the_matrix_universe():
    kb = KnowledgeBase.load()
    bogus = _tc(testcase_id="TC-BOGUS-01", requirement_ids=["REQ-DOES-NOT-EXIST"], journey_id=None,
                source_attribution=[{"requirement_id": "REQ-DOES-NOT-EXIST"}])
    governed = govern_batch([bogus], kb)
    matrix = build_dependency_matrix(governed, matrix_id="M5")
    assert matrix.testcase_ids == []
    assert matrix.edges == []


def test_matrix_validation_passes_for_a_well_formed_matrix():
    kb = KnowledgeBase.load()
    tc1 = _tc(testcase_id="TC-X-01")
    tc2 = _tc(testcase_id="TC-X-02", scenario_type="ALTERNATE")
    governed = govern_batch([tc1, tc2], kb)
    matrix = build_dependency_matrix(governed, matrix_id="M6")
    validation = validate_dependency_matrix(matrix)
    assert validation["passed"] is True
