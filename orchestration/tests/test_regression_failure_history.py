"""Tests for orchestration.regression's failure-history-aware selection
(Phase H) -- real, live proof against this repository's own committed
CP-07 RCA evidence from the controlled-failure demonstration."""
from __future__ import annotations

from orchestration.regression import RegressionScope, select_scope, find_testcases_with_real_failure_history


def test_real_failure_history_is_found_for_the_controlled_failure_fixture():
    found = find_testcases_with_real_failure_history(
        ["ORCH-CONTROLLED-TEST-FAILURE-FIXTURE", "ENH02-TC-REQ-BRW-01-CATEGORY-GRID"]
    )
    assert found == ["ORCH-CONTROLLED-TEST-FAILURE-FIXTURE"]


def test_no_history_for_unknown_testcase_is_honestly_empty():
    found = find_testcases_with_real_failure_history(["TC-THAT-NEVER-RAN"])
    assert found == []


def test_regression_scope_prefers_failure_history_over_risk():
    result = select_scope(
        {"directly_impacted_testcase_ids": ["ORCH-CONTROLLED-TEST-FAILURE-FIXTURE"], "indirectly_impacted_testcase_ids": []},
        {"records": [{"testcase_id": "ORCH-CONTROLLED-TEST-FAILURE-FIXTURE", "priority": "P3"}]},
    )
    assert result["scope"] == RegressionScope.FAILURE_HISTORY_REGRESSION
