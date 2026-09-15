"""
Tests for orchestration/agents.py -- meaningful agent specialization
(Wave 2 instruction sec. 10). Every agent must return a real
`DecisionRecord` naming itself as `actor`, built from real, already-
governed evidence -- never a static/fabricated decision.
"""
from __future__ import annotations

from orchestration.agents import (
    AutomationAgent,
    ExecutionAgent,
    QEReportingAgent,
    ReplanningAgent,
    RequirementAnalysisAgent,
    TestDataAgent,
    TestPlanningAgent,
)
from orchestration.decisions import DecisionRecord


def test_every_agent_names_itself_as_actor():
    r1 = RequirementAnalysisAgent().decide("ORCH-TEST", "REQ-BRW-01")
    r2 = TestPlanningAgent().decide("ORCH-TEST", "REQ-BRW-01")
    r3 = AutomationAgent().decide("ORCH-TEST", "REQ-BRW-01")
    r4 = ExecutionAgent().decide_mode("ORCH-TEST", "REQ-BRW-01", dry_run=True)
    r5 = QEReportingAgent().decide("ORCH-TEST", [])
    for r, cls_name in [
        (r1, "RequirementAnalysisAgent"), (r2, "TestPlanningAgent"), (r3, "AutomationAgent"),
        (r4, "ExecutionAgent"), (r5, "QEReportingAgent"),
    ]:
        assert isinstance(r, DecisionRecord)
        assert r.actor == cls_name


def test_requirement_analysis_agent_excludes_a_nonexistent_requirement():
    record = RequirementAnalysisAgent().decide("ORCH-TEST", "REQ-ZZZ-999")
    assert record.decision == "EXCLUDE"
    assert record.governance_state == "RED"


def test_requirement_analysis_agent_includes_a_real_safe_parallel_requirement():
    record = RequirementAnalysisAgent().decide("ORCH-TEST", "REQ-BRW-01")
    assert record.decision == "INCLUDE"
    assert "SAFE_PARALLEL" in record.reason


def test_execution_agent_blocks_when_no_real_driver_and_not_dry_run():
    record = ExecutionAgent().decide_mode("ORCH-TEST", "REQ-REG-05", dry_run=False)
    assert record.decision == "BLOCKED_NO_DRIVER"
    assert record.governance_state == "YELLOW"


def test_execution_agent_dry_run_never_claims_real_execution():
    record = ExecutionAgent().decide_mode("ORCH-TEST", "REQ-BRW-01", dry_run=True)
    assert record.decision == "DRY_RUN_PLANNED"


def test_replanning_agent_wraps_the_real_replan_action():
    fake_rca_result = {
        "rca": {"rca_id": "RCA-TEST", "confidence": "HIGH", "final_rca_classification": "TOOL_ISSUE"},
        "replanning": {"decision": "HUMAN_REVIEW_REQUIRED"},
    }
    record = ReplanningAgent().decide("ORCH-TEST", fake_rca_result)
    assert record.actor == "ReplanningAgent"
    assert record.decision in ("RETRY", "HUMAN_REVIEW", "ACTION_DEFERRED", "TERMINAL_FAILURE")


def test_test_data_agent_reports_not_required_for_a_dataset_free_testcase():
    record = TestDataAgent().decide("ORCH-TEST", "ENH02-TC-REQ-BRW-01-CATEGORY-GRID")
    assert record.decision == "NOT_REQUIRED"
