"""
Tests for reporting/ — the new, additive CP-MVP2-09 unified-reporting
aggregation package (docs/CP-MVP2-09-SPECIFICATION-v1.0.md).

All assertions are against real, already-persisted CP01-CP08 evidence on
disk in this repository -- never synthetic fixtures -- consistent with this
project's standing practice. Every gather_* function is read-only (frozen
spec sec. 1: "no LLM, no inference, no fabrication"); these tests verify
that the counts/breakdowns it returns are correct and that real-vs-fixture
execution records are correctly separated (sec. 4/21 of the CP09 governing
instruction).
"""
from __future__ import annotations

import pytest

from reporting.gather import (
    gather_all,
    gather_automation,
    gather_dependencies,
    gather_performance,
    gather_rbtp,
    gather_rca,
    gather_real_execution_results,
    gather_testcases,
    gather_testdata,
    gather_traceability,
)


def _skip_if_empty(value, msg):
    if not value:
        pytest.skip(msg)


# ---------------------------------------------------------------------------
# Testcases (CP03)
# ---------------------------------------------------------------------------

def test_gather_testcases_real_corpus():
    facts = gather_testcases()
    _skip_if_empty(facts["testcase_ids"], "No persisted testcases on disk in this environment")
    assert facts["count"] == len(facts["testcase_ids"])
    assert "TC-REQ-ACO-03-01" in facts["testcase_ids"]
    assert "REQ-ACO-03" in facts["requirement_to_testcase_ids"]
    assert facts["governance_status_breakdown"].get("ACCEPTED", 0) == facts["count"]


# ---------------------------------------------------------------------------
# Test data (CP04)
# ---------------------------------------------------------------------------

def test_gather_testdata_real_corpus_includes_rejected_and_possible_duplicate():
    facts = gather_testdata()
    _skip_if_empty(facts["data_set_ids"], "No persisted test data on disk in this environment")
    assert facts["count"] == len(facts["data_set_ids"])
    # This corpus is known to include real REJECTED and POSSIBLE_DUPLICATE
    # datasets -- CP09 sec. 8 requires these never be silently hidden.
    assert facts["validation_status_breakdown"].get("REJECTED", 0) >= 1
    assert facts["validation_status_breakdown"].get("POSSIBLE_DUPLICATE", 0) >= 1
    total = sum(facts["validation_status_breakdown"].values())
    assert total == facts["count"]


# ---------------------------------------------------------------------------
# RBTP / dependencies
# ---------------------------------------------------------------------------

def test_gather_rbtp_real_corpus():
    facts = gather_rbtp()
    _skip_if_empty(facts["rbtp_ids"], "No persisted RBTP records on disk in this environment")
    assert facts["count"] == len(facts["rbtp_ids"])


def test_gather_dependencies_real_corpus():
    facts = gather_dependencies()
    _skip_if_empty(facts["matrix_ids"], "No persisted dependency matrix on disk in this environment")
    assert facts["count"] == len(facts["matrix_ids"])
    assert all(v >= 0 for v in facts["edge_counts"].values())


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def test_gather_traceability_real_corpus():
    facts = gather_traceability()
    _skip_if_empty(facts["req_to_testcase"], "No persisted traceability records on disk in this environment")
    coverage = facts["req_to_testcase"][0]
    assert coverage["coverage_percentage"] == 100.0
    # This coverage figure is scoped to the batch's own "applicable"
    # requirements, not all Approved SRS requirements -- CP09 sec. 6
    # requires the report layer, not this raw gather layer, to make that
    # distinction explicit; this test only pins the raw fact.
    assert coverage["total_applicable_requirements"] == len(coverage["covered_requirements"])


# ---------------------------------------------------------------------------
# Automation (CP05) — committed vs local-only distinction
# ---------------------------------------------------------------------------

def test_gather_automation_distinguishes_standard_from_multi_locator():
    facts = gather_automation()
    _skip_if_empty(facts["standard_automation_ids"], "No persisted automation on disk in this environment")
    assert facts["standard_automation_count"] == len(facts["standard_automation_ids"])
    assert facts["multi_locator_automation_count"] == len(facts["multi_locator_automation_ids"])
    # every multi-locator id is also a standard-store id (same BASE_DIR
    # convention reused, per this project's established pattern)
    assert set(facts["multi_locator_automation_ids"]).issubset(set(facts["standard_automation_ids"]))


def test_gather_automation_never_hides_unsupported_needs_clarification():
    facts = gather_automation()
    _skip_if_empty(facts["standard_automation_ids"], "No persisted automation on disk in this environment")
    breakdown = facts["standard_governance_status_breakdown"]
    # This corpus is known to contain real UNSUPPORTED_NEEDS_CLARIFICATION
    # automation artifacts (most requirements' locators were never fully
    # evidenced) -- CP09 sec. 9 requires this never be hidden.
    assert breakdown.get("UNSUPPORTED_NEEDS_CLARIFICATION", 0) >= 1


# ---------------------------------------------------------------------------
# Real execution (CP06) — real vs fixture separation
# ---------------------------------------------------------------------------

def test_gather_real_execution_results_excludes_pytest_fixture_noise():
    facts = gather_real_execution_results()
    _skip_if_empty(facts["records"], "No real execution evidence on disk in this environment")
    fixture_testcase_ids = {"TC-X", "TC-X-01", "TC-TEST-01"}
    for r in facts["records"]:
        assert r["testcase_id"] not in fixture_testcase_ids
    fixture_execution_ids = {"T1", "T2", "T3", "T4", "T6", "T7", "T9", "T-UNRESOLVED", "EXEC-ISOLATION-01"}
    for r in facts["records"]:
        assert r["execution_id"] not in fixture_execution_ids


def test_gather_real_execution_results_never_reinterprets_not_executed_as_pass():
    facts = gather_real_execution_results()
    _skip_if_empty(facts["records"], "No real execution evidence on disk in this environment")
    for r in facts["records"]:
        if "NOT_EXECUTED" in (r["notes"] or [""])[0]:
            assert r["overall_status"] == "NOT_EXECUTED"


def test_gather_real_execution_results_preserves_real_fail_classification():
    facts = gather_real_execution_results()
    fail_records = [r for r in facts["records"] if r["overall_status"] == "FAIL"]
    _skip_if_empty(fail_records, "No real FAIL execution evidence on disk in this environment")
    for r in fail_records:
        assert r["failure_classification"] == "ENVIRONMENT_ISSUE"


# ---------------------------------------------------------------------------
# RCA / replanning / governance (CP07)
# ---------------------------------------------------------------------------

def test_gather_rca_reflects_real_governance_and_cr002_status():
    facts = gather_rca()
    _skip_if_empty(facts["rca_summaries"], "No persisted RCA records on disk in this environment")
    assert facts["rca_count"] == facts["replanning_count"] == facts["governance_count"]
    assert facts["governance_guard_all_passed"] is True
    # CR-002 must never appear as authorized in real, persisted governance
    # evidence (frozen spec sec. 15 / this project's standing CR-002 rule).
    assert all(status == "OPEN_NOT_AUTHORIZED" for status in facts["cr002_status_breakdown"])


def test_gather_rca_confidences_are_real_not_fabricated():
    facts = gather_rca()
    _skip_if_empty(facts["rca_summaries"], "No persisted RCA records on disk in this environment")
    for s in facts["rca_summaries"]:
        assert s["confidence"] in ("HIGH", "MEDIUM", "LOW")


# ---------------------------------------------------------------------------
# Performance (CP08)
# ---------------------------------------------------------------------------

def test_gather_performance_numeric_sla_always_inconclusive():
    facts = gather_performance()
    _skip_if_empty(facts["runs"], "No persisted performance evidence on disk in this environment")
    for run in facts["runs"].values():
        assert run["numeric_sla_result"] == "INCONCLUSIVE"
        assert run["capability_result"] in ("PASS", "FAIL", "BLOCKED", "NOT_EXECUTED")


# ---------------------------------------------------------------------------
# Top-level orchestration and determinism
# ---------------------------------------------------------------------------

def test_gather_all_returns_every_section():
    facts = gather_all()
    for key in ("testcases", "testdata", "rbtp", "dependencies", "traceability", "automation", "execution", "rca", "performance"):
        assert key in facts


def test_gather_all_is_deterministic_on_repeated_calls():
    first = gather_all()
    second = gather_all()
    assert first == second
