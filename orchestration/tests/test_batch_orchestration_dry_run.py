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


def test_batch_dry_run_summary_covers_the_full_sec17_checklist():
    """Wave 2 sec. 17: dry-run must explicitly produce selected
    requirements/testcases/datasets/dependencies/planned execution
    order/parallel groups/expected resources/excluded-deferred
    items+reasons/governance constraints -- all in one place, never
    scattered/reconstructed by the reader."""
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(BATCH, mode=ExecutionMode.DRY_RUN)
    summary = result.stages["dry_run_summary"]

    for key in (
        "selected_requirements", "selected_testcases", "datasets", "dependencies",
        "planned_execution_order", "parallel_groups", "expected_resources",
        "excluded_or_deferred", "governance_constraints",
    ):
        assert key in summary, f"Missing sec. 17 checklist item: {key}"

    assert summary["selected_requirements"] == BATCH
    excluded_ids = {e["requirement_id"] for e in summary["excluded_or_deferred"]}
    assert "REQ-REG-05" in excluded_ids  # EXCLUSIVE
    assert "REQ-DOES-NOT-EXIST-999" in excluded_ids  # BLOCKED
    for entry in summary["excluded_or_deferred"]:
        assert entry["reason"], f"{entry['requirement_id']} excluded/deferred without a reason."

    assert summary["governance_constraints"]["srs_content_hash"]
    assert "OPEN" in summary["governance_constraints"]["cr002_status"] or "NOT" in summary["governance_constraints"]["cr002_status"].upper()

    # BLOCKED must never appear in the planned execution order.
    assert "REQ-DOES-NOT-EXIST-999" not in summary["planned_execution_order"]
