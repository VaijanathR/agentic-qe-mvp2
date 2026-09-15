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
    #: Alias for TESTCASE_CONTENT_LIMITATION -- the Orchestration
    #: Expansion instruction's own Phase I vocabulary names this
    #: "TESTCASE_CONTENT" (no "_LIMITATION" suffix); both names resolve
    #: to the identical base category/mapping so neither call site has
    #: to change.
    TESTCASE_CONTENT = "TESTCASE_CONTENT_LIMITATION"
    DATA_ISSUE = "DATA_ISSUE"
    #: Alias for DATA_ISSUE (Phase I names it "TEST_DATA").
    TEST_DATA = "DATA_ISSUE"
    AUTHORIZATION_ISSUE = "AUTHORIZATION_ISSUE"
    #: Alias (Phase I: "AUTHENTICATION" -- distinct real-world concept
    #: from authorization, but this project has no separate frozen base
    #: category for it; mapped onto the same AUTHORIZATION_ISSUE base
    #: category, disclosed here rather than silently conflated).
    AUTHENTICATION = "AUTHENTICATION"
    TOOL_ISSUE = "TOOL_ISSUE"
    #: Alias for TOOL_ISSUE (Phase I: "TOOL").
    TOOL = "TOOL_ISSUE"
    ENVIRONMENT_ISSUE = "ENVIRONMENT_ISSUE"
    APPLICATION_DEFECT = "APPLICATION_DEFECT"
    #: Alias for APPLICATION_DEFECT (Phase I: "SUT_DEFECT" -- same real
    #: concept, this project's own established vocabulary already used
    #: "APPLICATION_DEFECT" first).
    SUT_DEFECT = "APPLICATION_DEFECT"
    THIRD_PARTY_DEPENDENCY = "THIRD_PARTY_DEPENDENCY"
    #: Alias for THIRD_PARTY_DEPENDENCY (Phase I: "THIRD_PARTY").
    THIRD_PARTY = "THIRD_PARTY_DEPENDENCY"
    CONSTRAINT = "CONSTRAINT"
    AUTOMATION_DEFECT = "AUTOMATION_DEFECT"
    #: Alias for AUTOMATION_DEFECT (Phase I: "AUTOMATION").
    AUTOMATION = "AUTOMATION_DEFECT"
    LOCATOR_ISSUE = "LOCATOR_ISSUE"
    PERFORMANCE_THRESHOLD_MISSING = "PERFORMANCE_THRESHOLD_MISSING"
    #: Genuinely new categories added by the Orchestration Expansion
    #: instruction, Phase I, with no prior equivalent in this project.
    BROWSER = "BROWSER"
    DEPENDENCY = "DEPENDENCY"
    GOVERNANCE = "GOVERNANCE"
    UNKNOWN = "UNKNOWN"


#: Every extended category maps to exactly one frozen base category
#: (never a parallel, disconnected taxonomy). Aliases above already
#: collapse onto their canonical string value before this dict is even
#: consulted (an alias IS its canonical value, not a separate key), so
#: only the canonical values need an entry here.
EXTENDED_TO_BASE_CATEGORY = {
    ExtendedFailureCategory.REQUIREMENT_MISMATCH: FailureCategory.REQUIREMENT_MISMATCH_AMBIGUITY,
    ExtendedFailureCategory.REQUIREMENT_AMBIGUITY: FailureCategory.REQUIREMENT_MISMATCH_AMBIGUITY,
    ExtendedFailureCategory.TESTCASE_CONTENT_LIMITATION: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.DATA_ISSUE: FailureCategory.TEST_DATA_ISSUE,
    ExtendedFailureCategory.AUTHORIZATION_ISSUE: FailureCategory.AUTHORIZATION_ISSUE,
    "AUTHENTICATION": FailureCategory.AUTHORIZATION_ISSUE,
    ExtendedFailureCategory.TOOL_ISSUE: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.ENVIRONMENT_ISSUE: FailureCategory.ENVIRONMENT_ISSUE,
    ExtendedFailureCategory.APPLICATION_DEFECT: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.THIRD_PARTY_DEPENDENCY: FailureCategory.THIRD_PARTY_DEPENDENCY_ISSUE,
    ExtendedFailureCategory.CONSTRAINT: FailureCategory.CONSTRAINT_VIOLATION,
    ExtendedFailureCategory.AUTOMATION_DEFECT: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.LOCATOR_ISSUE: FailureCategory.TOOL_ISSUE,
    ExtendedFailureCategory.PERFORMANCE_THRESHOLD_MISSING: FailureCategory.CONSTRAINT_VIOLATION,
    "BROWSER": FailureCategory.TOOL_ISSUE,
    "DEPENDENCY": FailureCategory.THIRD_PARTY_DEPENDENCY_ISSUE,
    "GOVERNANCE": FailureCategory.CONSTRAINT_VIOLATION,
    # UNKNOWN deliberately maps to None, not a real base category -- the
    # frozen FailureCategory enum has no "unknown" value, and forcing
    # UNKNOWN onto any specific real category would manufacture
    # certainty this module does not have (Phase I: "Do not manufacture
    # certainty").
    "UNKNOWN": None,
}

#: Base subtype -> extended category refinement, where the frozen subtype
#: already disambiguates further than the base category alone.
_SUBTYPE_TO_EXTENDED = {
    FailureSubtype.LOCATOR_FAILURE: ExtendedFailureCategory.LOCATOR_ISSUE,
    FailureSubtype.BROWSER_LAUNCH_FAILURE: "BROWSER",
    FailureSubtype.TIMEOUT: ExtendedFailureCategory.TESTCASE_CONTENT_LIMITATION,
    FailureSubtype.NAVIGATION_FAILURE: ExtendedFailureCategory.THIRD_PARTY_DEPENDENCY,
    FailureSubtype.ASSERTION_FAILURE: ExtendedFailureCategory.APPLICATION_DEFECT,
    FailureSubtype.DATA_OQ_01_UNRESOLVED: ExtendedFailureCategory.ENVIRONMENT_ISSUE,
}


def classify(execution_result: Dict) -> Dict:
    """Real, evidence-based classification -- never a default/guessed
    value. Returns None/None (base) and None (extended) for a genuine
    PASS/NOT_EXECUTED, exactly mirroring `reclassify_from_evidence`.

    `confidence` (Phase I: "Include confidence. Do not manufacture
    certainty"): HIGH when a real failed step matched one of this
    module's disclosed subtype heuristics; LOW when the execution really
    did fail/error but no step-level pattern matched (category trusted
    from the stored field alone, subtype None -- genuinely UNKNOWN, not
    guessed); UNKNOWN is never silently upgraded to HIGH."""
    category, subtype = reclassify_from_evidence(execution_result)
    extended = _SUBTYPE_TO_EXTENDED.get(subtype) if subtype else None
    if category is None:
        confidence = "NOT_APPLICABLE"  # PASS/NOT_EXECUTED -- no failure to classify
    elif subtype is not None:
        confidence = "HIGH"
    else:
        confidence = "LOW"
        extended = extended or "UNKNOWN"
    return {
        "base_category": category,
        "base_subtype": subtype,
        "extended_category": extended,
        "confidence": confidence,
        "confidence_note": (
            "Derived deterministically from real step_results evidence (rca.classify.reclassify_from_evidence); "
            "never an LLM guess."
        ),
    }
