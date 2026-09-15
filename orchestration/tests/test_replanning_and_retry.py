"""Tests for orchestration/replanning_orchestration.py -- bounded retry
policy (sec. 33) and the replanning-prohibition guard (sec. 32)."""
from __future__ import annotations

from orchestration.replanning_orchestration import MAX_RETRIES, check_replanning_prohibitions, retry_decision


def test_transient_environment_issue_is_retryable_within_budget():
    first = retry_decision("ENVIRONMENT_ISSUE", retry_count_so_far=0)
    assert first["retry_allowed"] is True

    exhausted = retry_decision("ENVIRONMENT_ISSUE", retry_count_so_far=MAX_RETRIES)
    assert exhausted["retry_allowed"] is False


def test_tool_issue_is_retryable():
    result = retry_decision("TOOL_ISSUE", retry_count_so_far=0)
    assert result["retry_allowed"] is True


def test_application_defect_is_not_retryable():
    result = retry_decision("CONSTRAINT_VIOLATION", retry_count_so_far=0)
    assert result["retry_allowed"] is False


def test_requirement_mismatch_is_not_retryable():
    result = retry_decision("REQUIREMENT_MISMATCH_AMBIGUITY", retry_count_so_far=0)
    assert result["retry_allowed"] is False


def test_testcase_content_limitation_is_not_retryable():
    result = retry_decision("TEST_DATA_ISSUE", retry_count_so_far=0)
    assert result["retry_allowed"] is False


def test_prohibited_replanning_phrases_are_rejected():
    prohibited = check_replanning_prohibitions("We should change the expected result to make this pass.")
    assert prohibited["passed"] is False

    also_prohibited = check_replanning_prohibitions("Just change the Approved requirement to match reality.")
    assert also_prohibited["passed"] is False


def test_legitimate_recommendation_only_text_passes():
    legitimate = check_replanning_prohibitions(
        "RECOMMENDATION ONLY, NOT APPLIED: author a richer testcase with the missing precondition-establishing steps."
    )
    assert legitimate["passed"] is True
