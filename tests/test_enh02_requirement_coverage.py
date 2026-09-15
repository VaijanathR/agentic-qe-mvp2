"""
Tests for reporting/requirement_coverage.py -- the Post-MVP2 Enhancement
02 master 35-requirement coverage matrix. Verifies completeness (no
silent omissions), governed vocabulary, and that the real-execution
enrichment reflects actually-persisted evidence, never invented data.
"""
from __future__ import annotations

import pytest

from reporting.requirement_coverage import (
    REQUIREMENT_COVERAGE,
    Disposition,
    disposition_breakdown,
    enrich_with_real_execution_data,
    validate_coverage,
)


def test_covers_exactly_35_requirements_with_no_duplicates():
    result = validate_coverage()
    assert result["total_requirements"] == 35
    assert result["duplicate_ids"] == []
    assert result["valid"] is True


def test_every_disposition_is_governed_vocabulary():
    known = {
        Disposition.FUNCTIONAL_AUTOMATABLE, Disposition.PERFORMANCE_AUTOMATABLE,
        Disposition.FUNCTIONAL_AND_PERFORMANCE, Disposition.HUMAN_REVIEW_REQUIRED,
        Disposition.NOT_AUTOMATABLE, Disposition.PARKED_BY_APPROVED_SCOPE,
        Disposition.DEPENDENCY_BLOCKED,
    }
    for r in REQUIREMENT_COVERAGE:
        assert r.disposition in known


def test_ids_match_the_real_approved_srs_requirement_ids():
    import re
    from pathlib import Path

    srs_text = Path("requirements/MVP2_SRS_v1.0_APPROVED.md").read_text(encoding="utf-8")
    real_ids = set(re.findall(r"\bREQ-[A-Z]+-\d+\b", srs_text))
    my_ids = {r.requirement_id for r in REQUIREMENT_COVERAGE}
    assert my_ids == real_ids


def test_every_automatable_requirement_has_a_real_testcase_reference():
    """No disposition is invented merely to raise a coverage percentage:
    every FUNCTIONAL_AUTOMATABLE/FUNCTIONAL_AND_PERFORMANCE record must
    carry at least one testcase_id."""
    for r in REQUIREMENT_COVERAGE:
        if r.disposition in (Disposition.FUNCTIONAL_AUTOMATABLE, Disposition.FUNCTIONAL_AND_PERFORMANCE):
            assert r.testcase_ids, f"{r.requirement_id} is automatable but has no testcase_id"


def test_every_non_automated_requirement_has_a_documented_reason():
    """Every DEPENDENCY_BLOCKED/HUMAN_REVIEW_REQUIRED record must carry a
    real, non-empty remarks explanation -- never a silent omission."""
    for r in REQUIREMENT_COVERAGE:
        if r.disposition in (Disposition.DEPENDENCY_BLOCKED, Disposition.HUMAN_REVIEW_REQUIRED):
            assert r.remarks.strip(), f"{r.requirement_id} is not automated but has no documented reason"


def test_disposition_breakdown_sums_to_35():
    breakdown = disposition_breakdown()
    assert sum(breakdown.values()) == 35


def test_enrichment_never_fabricates_execution_data_for_non_automated_requirements():
    enriched = enrich_with_real_execution_data()
    for r in enriched:
        if r.disposition in (Disposition.DEPENDENCY_BLOCKED, Disposition.HUMAN_REVIEW_REQUIRED):
            assert r.execution_ids == []
            assert r.automation_ids == []


def test_enrichment_reflects_real_persisted_execution_logs():
    """Real, corpus-dependent check: if REQ-BRW-01's real Playwright
    execution log exists on disk (it does, once the Enhancement-02 real
    test suite has been run at least once), the enrichment must reflect
    it -- never a hard-coded, stale execution_id."""
    from automation.playwright.logging_ import list_execution_log_ids

    if not any("BRW-01" in i for i in list_execution_log_ids()):
        pytest.skip("No real REQ-BRW-01 execution log present on disk in this environment")

    enriched = enrich_with_real_execution_data()
    brw = next(r for r in enriched if r.requirement_id == "REQ-BRW-01")
    assert len(brw.execution_ids) >= 1
    assert len(brw.automation_ids) >= 1
