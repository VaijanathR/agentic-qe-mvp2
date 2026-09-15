"""Tests for orchestration/approval.py and regression.py."""
from __future__ import annotations

import pytest

from orchestration.approval import ApprovalDecision, record_decision, request_approval
from orchestration.regression import RegressionScope, select_scope


def test_approval_cannot_be_recorded_anonymously():
    record = request_approval(
        orchestration_id="ORCH-TEST-0001", reason="test", evidence_references=[], proposed_action="test action",
        risk="LOW", affected_requirements=[], affected_artifacts=[], impact="none", requested_decision="APPROVE?",
    )
    assert record.decision == ApprovalDecision.PENDING
    with pytest.raises(ValueError):
        record_decision(record, ApprovalDecision.APPROVED, approved_by="")


def test_approval_records_a_real_decision():
    record = request_approval(
        orchestration_id="ORCH-TEST-0002", reason="test", evidence_references=[], proposed_action="test action",
        risk="LOW", affected_requirements=[], affected_artifacts=[], impact="none", requested_decision="APPROVE?",
    )
    decided = record_decision(record, ApprovalDecision.APPROVED, approved_by="Human+Di")
    assert decided.decision == ApprovalDecision.APPROVED
    assert decided.approved_by == "Human+Di"
    assert decided.decided_at is not None


def test_regression_falls_back_to_full_when_no_impact_data():
    result = select_scope({"directly_impacted_testcase_ids": [], "indirectly_impacted_testcase_ids": []}, {"records": []})
    assert result["scope"] == RegressionScope.FULL_REGRESSION


def test_regression_targeted_when_only_direct_impact():
    result = select_scope(
        {"directly_impacted_testcase_ids": ["TC-1"], "indirectly_impacted_testcase_ids": []},
        {"records": [{"testcase_id": "TC-1", "priority": "P3"}]},
    )
    assert result["scope"] == RegressionScope.TARGETED_REGRESSION


def test_regression_risk_scope_when_high_priority_present():
    result = select_scope(
        {"directly_impacted_testcase_ids": ["TC-1"], "indirectly_impacted_testcase_ids": []},
        {"records": [{"testcase_id": "TC-1", "priority": "P0"}]},
    )
    assert result["scope"] == RegressionScope.RISK_REGRESSION


def test_force_full_always_wins():
    result = select_scope({"directly_impacted_testcase_ids": ["TC-1"]}, {"records": []}, force_full=True)
    assert result["scope"] == RegressionScope.FULL_REGRESSION
