"""
Agentic QE Orchestration -- Failure Classification (governing
instruction sec. 29).

Reuses `execution.schema.FailureCategory`/`FailureSubtype` (CP-MVP2-06,
frozen) and `rca.classify.reclassify_from_evidence` (CP-MVP2-07, frozen)
unmodified. The governing instruction's sec. 29 vocabulary is a superset
of what those two frozen modules define; the extra categories
(REQUIREMENT_MISMATCH, REQUIREMENT_AMBIGUITY,
TESTCASE_CONTENT_LIMITATION, DATA_ISSUE, AUTOMATION_DEFECT,
LOCATOR_ISSUE, PERFORMANCE_THRESHOLD_MISSING) are orchestration-level
refinements layered on top of the frozen base categories/subtypes --
never a second, conflicting taxonomy; each maps onto exactly one frozen
base category, disclosed in `EXTENDED_TO_BASE_CATEGORY` below.
"""
from __future__ import annotations

from typing import Dict, Optional

from execution.schema import FailureCategory, FailureSubtype
from rca.classify import reclassify_from_evidence


class ExtendedFailureCategory:
    REQUIREMENT_MISMATCH = "REQUIREMENT_MISMATCH"
    REQUIREMENT_AMBIGUITY = "REQUIREMENT_AMBIGUITY"
    TESTCASE_CONTENT_LIMITATION = "TESTCASE_CONTENT_LIMITATION"
    DATA_ISSUE = "DATA_ISSUE"
    AUTHORIZATION_ISSUE = "AUTHORIZATION_ISSUE"
    TOOL_ISSUE = "TOOL_ISSUE"
    ENVIRONMENT_ISSUE = "ENVIRONMENT_ISSUE"
    APPLICATION_DEFECT = "APPLICATION_DEFECT"
    THIRD_PARTY_DEPENDENCY = "THIRD_PARTY_DEPENDENCY"
    CONSTRAINT = "CONSTRAINT"
    AUTOMATION_DEFECT = "AUTOMATION_DEFECT"
    LOCATOR_ISSUE = "LOCATOR_ISSUE"
    PERFORMANCE_THRESHOLD_MISSING = "PERFORMANCE_THRESHOLD_MISSING"


#: Every extended category maps to exactly one frozen base category
#: (never a parallel, disconnected taxonomy).
EXTENDED_TO_BASE_CATEGORY = {
    ExtendedFailureCategory.REQUIREMENT_MISMATCH: FailureCategory.REQUIREMENT_MISMATCH_AMBIGUITY,
    ExtendedFailureCategory.REQUIREMENT_AMBIGUITY: FailureCategory.REQUIREMENT_MISMATCH_AMBIGUITY,
    ExtendedFailureCategory.TESTCASE_CONTENT_LIMITATION: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.DATA_ISSUE: FailureCategory.TEST_DATA_ISSUE,
    ExtendedFailureCategory.AUTHORIZATION_ISSUE: FailureCategory.AUTHORIZATION_ISSUE,
    ExtendedFailureCategory.TOOL_ISSUE: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.ENVIRONMENT_ISSUE: FailureCategory.ENVIRONMENT_ISSUE,
    ExtendedFailureCategory.APPLICATION_DEFECT: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.THIRD_PARTY_DEPENDENCY: FailureCategory.THIRD_PARTY_DEPENDENCY_ISSUE,
    ExtendedFailureCategory.CONSTRAINT: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.AUTOMATION_DEFECT: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.LOCATOR_ISSUE: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.PERFORMANCE_THRESHOLD_MISSING: FailureCategory.CONSTRAINT_VIOLATION,
}

#: Base subtype -> extended category refinement, where the frozen subtype
#: already disambiguates further than the base category alone.
_SUBTYPE_TO_EXTENDED = {
    FailureSubtype.LOCATOR_FAILURE: ExtendedFailureCategory.LOCATOR_ISSUE,
    FailureSubtype.BROWSER_LAUNCH_FAILURE: ExtendedFailureCategory.TOOL_ISSUE,
    FailureSubtype.TIMEOUT: ExtendedFailureCategory.TESTCASE_CONTENT_LIMITATION,
    FailureSubtype.NAVIGATION_FAILURE: ExtendedFailureCategory.THIRD_PARTY_DEPENDENCY,
    FailureSubtype.ASSERTION_FAILURE: ExtendedFailureCategory.APPLICATION_DEFECT,
    FailureSubtype.DATA_OQ_01_UNRESOLVED: ExtendedFailureCategory.ENVIRONMENT_ISSUE,
}


def classify(execution_result: Dict) -> Dict:
    """Real, evidence-based classification -- never a default/guessed
    value. Returns None/None (base) and None (extended) for a genuine
    PASS/NOT_EXECUTED, exactly mirroring `reclassify_from_evidence`."""
    category, subtype = reclassify_from_evidence(execution_result)
    extended = _SUBTYPE_TO_EXTENDED.get(subtype) if subtype else None
    return {
        "base_category": category,
        "base_subtype": subtype,
        "extended_category": extended,
        "confidence_note": (
            "Derived deterministically from real step_results evidence (rca.classify.reclassify_from_evidence); "
            "never an LLM guess."
        ),
    }
