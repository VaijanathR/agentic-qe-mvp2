"""Tests for the Orchestration Expansion's failure-classification
additions (Phase I): the extended vocabulary aliases and confidence."""
from __future__ import annotations

from orchestration.failure_classification import EXTENDED_TO_BASE_CATEGORY, ExtendedFailureCategory, classify


def test_new_phase_i_aliases_resolve_to_the_same_canonical_value_as_the_original():
    assert ExtendedFailureCategory.TESTCASE_CONTENT == ExtendedFailureCategory.TESTCASE_CONTENT_LIMITATION
    assert ExtendedFailureCategory.TEST_DATA == ExtendedFailureCategory.DATA_ISSUE
    assert ExtendedFailureCategory.TOOL == ExtendedFailureCategory.TOOL_ISSUE
    assert ExtendedFailureCategory.SUT_DEFECT == ExtendedFailureCategory.APPLICATION_DEFECT
    assert ExtendedFailureCategory.THIRD_PARTY == ExtendedFailureCategory.THIRD_PARTY_DEPENDENCY
    assert ExtendedFailureCategory.AUTOMATION == ExtendedFailureCategory.AUTOMATION_DEFECT


def test_genuinely_new_categories_are_distinct_values():
    values = {
        ExtendedFailureCategory.BROWSER, ExtendedFailureCategory.DEPENDENCY,
        ExtendedFailureCategory.GOVERNANCE, ExtendedFailureCategory.UNKNOWN,
    }
    assert values == {"BROWSER", "DEPENDENCY", "GOVERNANCE", "UNKNOWN"}


def test_unknown_never_forced_onto_a_specific_real_base_category():
    assert EXTENDED_TO_BASE_CATEGORY["UNKNOWN"] is None


def test_classify_pass_has_not_applicable_confidence():
    result = classify({"overall_status": "PASS", "step_results": []})
    assert result["confidence"] == "NOT_APPLICABLE"
    assert result["base_category"] is None


def test_classify_real_fail_with_matched_step_has_high_confidence():
    execution_result = {
        "overall_status": "FAIL",
        "step_results": [
            {"step_order": 1, "action_type": "NAVIGATE", "status": "PASS", "error_information": None},
            {"step_order": 2, "action_type": "ASSERT", "status": "FAIL", "error_information": "assertion did not hold"},
        ],
    }
    result = classify(execution_result)
    assert result["confidence"] == "HIGH"
    assert result["base_subtype"] == "ASSERTION_FAILURE"
    assert result["extended_category"] == ExtendedFailureCategory.APPLICATION_DEFECT
