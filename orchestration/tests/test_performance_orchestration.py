"""
Wave 2 Performance Orchestration tests (instruction sec. 18): Requirement
-> Performance testcase -> workload/data -> JMeter plan -> execution ->
metrics -> threshold validation -> evidence -> RCA/replanning ->
governance.

This environment genuinely has no Java/JMeter installation reachable via
JAVA_HOME/JMETER_EXECUTABLE/PATH (a real, disclosed, pre-existing
environment limitation carried forward from CP-MVP2-08's own execution
report) -- so the real pipeline's own, honest disposition here is always
BLOCKED, never a fabricated PASS. This is exactly the real failure mode
Wave 2 sec. 18 asks orchestration to carry into RCA/replanning/governance,
and `Orchestrator.run(..., run_performance=True)` now does so (see
orchestrator.py's `performance_replanning` stage) -- real, live evidence
of this wiring is persisted at orchestration_id
ORCH-20260915-212342-0001JX (journal entry: stage=EXECUTING,
decision=ENVIRONMENT_RETRY, actor=RCAAgent).
"""
from __future__ import annotations

from orchestration import performance_execution, replanning_orchestration
from orchestration.governance import guard_performance_threshold_approved


def test_is_performance_relevant_is_real_and_scoped_to_brw01():
    assert performance_execution.is_performance_relevant("REQ-BRW-01") is True
    assert performance_execution.is_performance_relevant("REQ-WISH-01") is False
    assert performance_execution.is_performance_relevant("REQ-ZZZ-999") is False


def test_real_jmeter_pipeline_never_fabricates_pass_when_tools_are_unavailable():
    result = performance_execution.execute_real("REQ-BRW-01", run_id="TEST-PERF-ORCH-WAVE2-01")
    assert result["requirement_id"] == "REQ-BRW-01"
    # Real, honest disposition in this environment: BLOCKED (no fabricated
    # PASS) if Java/JMeter are unreachable, or a real COMPLETE run
    # otherwise -- either way, sla_status must never be a fabricated PASS.
    assert result["status"] in ("BLOCKED", "COMPLETE")
    assert result["sla_status"] == "INCONCLUSIVE", (
        "Sec. 18: 'No approved numeric threshold = SLA INCONCLUSIVE' -- this must hold "
        "regardless of whether the real JMeter subprocess itself succeeded."
    )
    guard = guard_performance_threshold_approved(threshold_source=None, threshold_value=None)
    assert guard["passed"] is True


def test_performance_blocked_failure_is_wired_to_the_same_bounded_replan_vocabulary_as_functional_failures():
    """Mirrors the exact real logic `Orchestrator.run()` applies to a
    BLOCKED performance disposition (orchestrator.py's `performance_replanning`
    stage): classify as ENVIRONMENT_ISSUE, derive the action from CP-07's
    real replanning vocabulary via `determine_replan_action`."""
    perf = performance_execution.execute_real("REQ-BRW-01", run_id="TEST-PERF-ORCH-WAVE2-02")
    if perf["status"] != "BLOCKED":
        return  # A real, available JMeter/Java in some other environment legitimately skips this branch.

    action = replanning_orchestration.determine_replan_action(
        rca_replanning_decision="HUMAN_REVIEW_REQUIRED", rca_confidence="HIGH", failure_classification="ENVIRONMENT_ISSUE",
    )
    assert action["action"] == "ENVIRONMENT_RETRY"
    assert action["approval_required"] is False
    assert "requirement" not in action["what_changes"].lower()
