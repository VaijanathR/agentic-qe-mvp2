"""Tests for orchestration/consolidated_matrix.py -- the sec. 15
consolidated coverage matrix, built from real, persisted orchestration
journals only."""
from __future__ import annotations

from orchestration.consolidated_matrix import OrchestratedStatus, build_matrix, summarize
from orchestration.execution_planning import ExecutionMode
from orchestration.orchestrator import Orchestrator


def test_matrix_always_totals_exactly_35_rows_even_with_no_journals():
    rows = build_matrix([])
    assert len(rows) == 35
    assert all(r["orchestrated"] == OrchestratedStatus.NOT_SELECTED for r in rows)


def test_matrix_reflects_a_real_dry_run_batch_as_selected_not_executed():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(["REQ-BRW-01", "REQ-WISH-02"], mode=ExecutionMode.DRY_RUN)
    rows = build_matrix([result.orchestration_id])
    by_id = {r["requirement_id"]: r for r in rows}

    assert by_id["REQ-BRW-01"]["orchestrated"] == OrchestratedStatus.SELECTED
    assert by_id["REQ-BRW-01"]["executed"] is False
    assert by_id["REQ-WISH-02"]["dependency"] == "PREREQUISITE_DEPENDENT"


def test_matrix_never_claims_a_non_selected_requirement_was_orchestrated():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(["REQ-BRW-01"], mode=ExecutionMode.DRY_RUN)
    rows = build_matrix([result.orchestration_id])
    by_id = {r["requirement_id"]: r for r in rows}
    assert by_id["REQ-SRCH-01"]["orchestrated"] == OrchestratedStatus.NOT_SELECTED


def test_summarize_counts_are_internally_consistent():
    rows = build_matrix([])
    summary = summarize(rows)
    assert summary["total_requirements"] == 35
    assert summary["orchestrated_count"] + summary["not_selected_count"] == 35
    assert summary["executed_count"] <= summary["orchestrated_count"]
    assert summary["passed_count"] <= summary["executed_count"]
