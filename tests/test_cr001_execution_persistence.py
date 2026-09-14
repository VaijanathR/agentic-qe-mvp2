"""
CP-MVP2-CR-001 Batch 1 — additive execution persistence
(execution/persist.py) and Execution Summary (execution/summary.py).

Uses real `ExecutionResult`/`StepResult`/`AssertionResult` dataclass
instances (the frozen CP-MVP2-06 schema, unmodified) constructed
directly — these tests exercise the NEW persistence/summary code, not
a real browser (that is covered separately by
tests/test_cp_mvp2_06_execution.py and this batch's live validation
script). No code in this file modifies `execution/schema.py`,
`pipeline.py`, `engine.py`, or `evidence.py`.
"""
from __future__ import annotations

import datetime

import execution.persist as exec_persist
import execution.summary as exec_summary
from execution.schema import AssertionResult, ExecutionResult, OverallStatus, StepResult, StepStatus


def _result(**overrides) -> ExecutionResult:
    base = dict(
        execution_id="EXEC-TEST-01",
        automation_id="PW-TEST-01",
        testcase_id="TC-TEST-01",
        requirement_ids=["REQ-REG-01"],
        test_data_set_id="TD-TEST-01",
        journey_id="J-01",
        scenario_type="POSITIVE",
        browser="chromium/151.0",
        execution_start="2026-09-14T10:00:00+00:00",
        execution_end="2026-09-14T10:00:05+00:00",
        duration_seconds=5.0,
        overall_status=OverallStatus.PASS,
        step_results=[StepResult(1, "NAVIGATE", None, StepStatus.PASS)],
        assertion_results=[AssertionResult("BUSINESS_REQUIRED", "cond", "src", True, passed=True)],
        evidence_references=["runs/cp_mvp2_06/EXEC-TEST-01/screenshot.png"],
        governance_status="ACCEPTED",
    )
    base.update(overrides)
    return ExecutionResult(**base)


def test_persist_execution_result_writes_real_files_under_timestamped_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path)
    result = _result()
    out = exec_persist.persist_execution_result(result)
    out_dir = tmp_path / "2026" / "09" / "14" / "EXEC-TEST-01"
    assert out_dir.exists()
    assert (out_dir / "final_result.json").exists()
    assert (out_dir / "step_results.json").exists()
    assert (out_dir / "assertions.json").exists()

    import json
    final = json.loads((out_dir / "final_result.json").read_text())
    assert final["execution_id"] == "EXEC-TEST-01"
    assert final["overall_status"] == OverallStatus.PASS


def test_persist_execution_result_falls_back_to_now_when_no_start_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(exec_persist, "RUNS_ROOT", tmp_path)
    result = _result(execution_start=None)
    exec_persist.persist_execution_result(result)
    now = datetime.datetime.now(datetime.timezone.utc)
    expected_dir = tmp_path / f"{now.year:04d}" / f"{now.month:02d}" / f"{now.day:02d}" / "EXEC-TEST-01"
    assert expected_dir.exists()


def test_persist_execution_result_never_touches_frozen_evidence_module():
    import execution.evidence as frozen_evidence
    original_runs_dir = frozen_evidence.RUNS_DIR
    exec_persist.persist_execution_result(_result(execution_id="EXEC-ISOLATION-01"))
    assert frozen_evidence.RUNS_DIR is original_runs_dir  # never reassigned/mutated by this module


def test_execution_summary_counts_by_status():
    results = [
        _result(execution_id="E1", overall_status=OverallStatus.PASS, requirement_ids=["REQ-A"]),
        _result(execution_id="E2", overall_status=OverallStatus.FAIL, requirement_ids=["REQ-B"], testcase_id="TC-2"),
        _result(execution_id="E3", overall_status=OverallStatus.NOT_EXECUTED, requirement_ids=["REQ-C"], testcase_id="TC-3"),
    ]
    summary = exec_summary.build_execution_summary(results, batch_id="BATCH-1")
    assert summary["counts_by_status"][OverallStatus.PASS] == 1
    assert summary["counts_by_status"][OverallStatus.FAIL] == 1
    assert summary["counts_by_status"][OverallStatus.NOT_EXECUTED] == 1
    assert summary["executed_count"] == 2  # NOT_EXECUTED does not count as "executed"
    assert summary["testcase_coverage"]["total"] == 3


def test_execution_summary_requirement_coverage_only_counts_pass():
    results = [
        _result(execution_id="E1", overall_status=OverallStatus.PASS, requirement_ids=["REQ-A"]),
        _result(execution_id="E2", overall_status=OverallStatus.FAIL, requirement_ids=["REQ-B"], testcase_id="TC-2"),
    ]
    summary = exec_summary.build_execution_summary(results, batch_id="BATCH-2")
    assert summary["requirement_coverage"]["requirements_with_a_passing_execution"] == ["REQ-A"]
    assert summary["requirement_coverage"]["total_requirements_represented"] == 2  # REQ-A and REQ-B both "represented"


def test_execution_summary_persist_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(exec_summary, "BASE_DIR", tmp_path)
    summary = exec_summary.build_execution_summary([_result()], batch_id="BATCH-3")
    result = exec_summary.persist_execution_summary(summary, generator="deterministic-only")
    assert result["reused"] is False

    from persistence.envelope import load_latest
    loaded = load_latest(tmp_path, "BATCH-3")
    assert loaded["batch_id"] == "BATCH-3"
