"""
Real, non-mocked DRY_RUN multi-requirement batch orchestration test (no
SUT interaction). Exercises Orchestrator.run_batch() -- Orchestration
Expansion instruction, Phase A/E/F.
"""
from __future__ import annotations

from orchestration.dependency_planning import ExecutionCategory
from orchestration.execution_planning import ExecutionMode
from orchestration.orchestrator import Orchestrator
from orchestration.state import OrchestrationState

BATCH = ["REQ-BRW-01", "REQ-SRCH-01", "REQ-WISH-01", "REQ-WISH-02", "REQ-WISH-03", "REQ-REG-05", "REQ-DOES-NOT-EXIST-999"]


def test_batch_dry_run_reaches_execution_planned_without_touching_the_sut():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    assert result.final_state == OrchestrationState.EXECUTION_PLANNED
    assert result.final_status == "DRY_RUN_COMPLETE"


def test_batch_dry_run_classifies_all_five_categories_correctly():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    by_category = result.stages["execution_plan_by_category"]

    assert set(by_category[ExecutionCategory.SAFE_PARALLEL]) == {"REQ-BRW-01", "REQ-SRCH-01", "REQ-WISH-01"}
    assert set(by_category[ExecutionCategory.PREREQUISITE_DEPENDENT]) == {"REQ-WISH-02", "REQ-WISH-03"}
    assert by_category[ExecutionCategory.EXCLUSIVE] == ["REQ-REG-05"]
    assert by_category[ExecutionCategory.BLOCKED] == ["REQ-DOES-NOT-EXIST-999"]


def test_batch_dry_run_gathers_real_intelligence_for_every_requirement():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    intel = result.stages["requirement_intelligence"]
    assert set(intel.keys()) == set(BATCH)
    assert "error" in intel["REQ-DOES-NOT-EXIST-999"]
    assert intel["REQ-BRW-01"]["requirement_text"] is not None


def test_batch_dry_run_never_reports_generated_as_executed():
    """Phase A: distinguish orchestratable/planned/generated/
    automation-ready/executable from executed/passed/failed/blocked/
    deferred. A DRY_RUN must never claim any real execution."""
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    assert "execution" not in result.stages
    assert "per_requirement_execution" not in result.stages
    assert result.final_status == "DRY_RUN_COMPLETE"


def test_batch_journal_summary_persists_selected_requirements():
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    from orchestration.journal import load_journal

    journal = load_journal(result.orchestration_id)
    assert journal["summary"]["selected_requirements"] == BATCH
