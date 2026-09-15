"""
Tests for orchestration/resume.py -- governed resume/recovery (Phase N).

Per the governing instruction's own permitted fallback ("If a safe
demonstration cannot be performed against the live SUT, use a
deterministic orchestration-state test rather than fabricate live
evidence"), these tests exercise the real, persisted journal mechanism
deterministically -- no live SUT interruption is simulated.
"""
from __future__ import annotations

from orchestration.execution_planning import ExecutionMode
from orchestration.journal import OrchestrationJournal
from orchestration.orchestrator import Orchestrator
from orchestration.resume import ResumeState, plan_resume


def test_resume_plan_for_nonexistent_orchestration_id():
    plan = plan_resume("ORCH-DOES-NOT-EXIST-00000000-000000-0000")
    assert plan.resume_state == ResumeState.NOT_FOUND


def test_resume_plan_for_a_real_completed_dry_run_batch():
    """A real DRY_RUN batch always reaches EXECUTION_PLANNED, never
    FINAL_REPORT -- resume must report NO_PENDING_WORK or RESUMABLE,
    never silently claim ALREADY_COMPLETE for a run that never finished."""
    orchestrator = Orchestrator()
    result = orchestrator.run_batch(["REQ-BRW-01", "REQ-SRCH-01"], mode=ExecutionMode.DRY_RUN)
    plan = plan_resume(result.orchestration_id)
    assert plan.resume_state != ResumeState.ALREADY_COMPLETE
    assert plan.selected_requirements == ["REQ-BRW-01", "REQ-SRCH-01"]


def test_resume_plan_detects_pending_work_from_a_simulated_interruption():
    """Deterministic simulation of an interrupted orchestration: a real
    journal is written showing 3 selected requirements, 1 already
    completed, and a non-FINAL_REPORT current_state -- exactly what a
    real process interruption would leave behind."""
    journal = OrchestrationJournal("ORCH-TEST-RESUME-SIMULATED-0001", "REQ-A,REQ-B,REQ-C")
    journal.record_transition(None, "RECEIVED", "test start")
    journal.record_transition("RECEIVED", "EXECUTING", "test simulated progress")
    journal.update_summary(
        selected_requirements=["REQ-A", "REQ-B", "REQ-C"],
        completed_requirement_ids=["REQ-A"],
    )

    plan = plan_resume("ORCH-TEST-RESUME-SIMULATED-0001")
    assert plan.resume_state == ResumeState.RESUMABLE
    assert plan.completed_requirement_ids == ["REQ-A"]
    assert plan.pending_requirement_ids == ["REQ-B", "REQ-C"]


def test_resume_never_reexecutes_a_completed_requirement():
    """The core Phase N safety property: a requirement already marked
    completed must never appear in pending_requirement_ids, regardless
    of its real PASS/FAIL outcome."""
    journal = OrchestrationJournal("ORCH-TEST-RESUME-SIMULATED-0002", "REQ-A,REQ-B")
    journal.update_summary(selected_requirements=["REQ-A", "REQ-B"], completed_requirement_ids=["REQ-A", "REQ-B"])
    journal.record_transition(None, "RECEIVED", "test")

    plan = plan_resume("ORCH-TEST-RESUME-SIMULATED-0002")
    assert plan.resume_state == ResumeState.NO_PENDING_WORK
    assert "REQ-A" not in plan.pending_requirement_ids
    assert "REQ-B" not in plan.pending_requirement_ids


def test_orchestrator_resume_batch_returns_plan_only_when_not_resumable():
    orchestrator = Orchestrator()
    result = orchestrator.resume_batch("ORCH-DOES-NOT-EXIST-00000000-000000-0000")
    assert result["resumed"] is False
    assert result["plan"]["resume_state"] == ResumeState.NOT_FOUND


def test_orchestrator_resume_batch_dry_runs_only_pending_requirements():
    journal = OrchestrationJournal("ORCH-TEST-RESUME-SIMULATED-0003", "REQ-BRW-01,REQ-SRCH-01")
    journal.update_summary(selected_requirements=["REQ-BRW-01", "REQ-SRCH-01"], completed_requirement_ids=["REQ-BRW-01"])
    journal.record_transition(None, "RECEIVED", "test")

    orchestrator = Orchestrator()
    outcome = orchestrator.resume_batch("ORCH-TEST-RESUME-SIMULATED-0003", mode=ExecutionMode.DRY_RUN)
    assert outcome["resumed"] is True
    assert outcome["plan"]["pending_requirement_ids"] == ["REQ-SRCH-01"]
    assert outcome["new_orchestration_result"]["stages"]["requirement_intelligence"].keys() == {"REQ-SRCH-01"}
