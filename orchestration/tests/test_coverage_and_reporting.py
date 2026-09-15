"""Tests for orchestration/coverage.py -- the 7 coverage dimensions and
the Generated != Executable != Executed != Passed != Fully Covered
distinctions (governing instruction sec. 47)."""
from __future__ import annotations

from orchestration.coverage import build_coverage_report


def test_coverage_report_has_all_seven_dimensions():
    report = build_coverage_report()
    for key in (
        "requirement_coverage", "testcase_coverage", "automation_coverage",
        "execution_coverage", "evidence_coverage", "performance_coverage",
    ):
        assert key in report


def test_coverage_report_totals_35_requirements():
    report = build_coverage_report()
    assert report["requirement_coverage"]["total"] == 35


def test_coverage_report_never_collapses_the_five_distinctions():
    report = build_coverage_report()
    row = next(r for r in report["requirement_rows"] if r["requirement_id"] == "REQ-BRW-01")
    # All five keys must be independently present -- never merged into one status.
    for key in ("generated", "executable", "executed", "passed", "fully_covered"):
        assert key in row


def test_a_real_executed_and_passed_requirement_is_fully_covered():
    report = build_coverage_report()
    row = next(r for r in report["requirement_rows"] if r["requirement_id"] == "REQ-BRW-01")
    assert row["generated"] is True
    assert row["executed"] is True
    assert row["fully_covered"] is True


def test_fully_covered_count_never_exceeds_total_requirements():
    report = build_coverage_report()
    assert report["fully_covered_count"] <= report["requirement_coverage"]["total"]
