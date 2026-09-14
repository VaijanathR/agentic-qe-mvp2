"""
CP-MVP2-06 — deterministic execution-result schema.

Implements the ExecutionResult/StepResult/AssertionResult model and the
OverallStatus/StepStatus/FailureCategory vocabularies from the frozen
docs/CP-MVP2-06-SPECIFICATION-v1.0.md secs. 9/10/13, mirroring the
dataclass-plus-to_dict() convention already established by every prior
checkpoint (knowledge/lib/schema.py, testcases/schema.py,
testdata/schema.py, automation/schema.py).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class OverallStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"
    ERROR = "ERROR"


ALL_OVERALL_STATUSES = {
    OverallStatus.PASS, OverallStatus.FAIL, OverallStatus.BLOCKED,
    OverallStatus.NOT_EXECUTED, OverallStatus.ERROR,
}


class StepStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    NOT_EXECUTED = "NOT_EXECUTED"
    ERROR = "ERROR"


class FailureCategory:
    """The seven base categories named by the frozen specification sec. 13."""

    REQUIREMENT_MISMATCH_AMBIGUITY = "REQUIREMENT_MISMATCH_AMBIGUITY"
    TEST_DATA_ISSUE = "TEST_DATA_ISSUE"
    AUTHORIZATION_ISSUE = "AUTHORIZATION_ISSUE"
    TOOL_ISSUE = "TOOL_ISSUE"
    ENVIRONMENT_ISSUE = "ENVIRONMENT_ISSUE"
    THIRD_PARTY_DEPENDENCY_ISSUE = "THIRD_PARTY_DEPENDENCY_ISSUE"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"


class FailureSubtype:
    """Execution-specific subtypes, each mapped to exactly one base
    category (spec sec. 13 table) — never a hidden, parallel taxonomy."""

    BROWSER_LAUNCH_FAILURE = "BROWSER_LAUNCH_FAILURE"
    LOCATOR_FAILURE = "LOCATOR_FAILURE"
    TIMEOUT = "TIMEOUT"
    NAVIGATION_FAILURE = "NAVIGATION_FAILURE"
    ASSERTION_FAILURE = "ASSERTION_FAILURE"
    #: Implementation-time addition, explicitly permitted by the frozen
    #: specification sec. 13 ("consider whether additional execution-
    #: specific categories are required... define how they relate to
    #: the existing taxonomy"). A state-mutating scenario against the
    #: shared, third-party SUT with no established data-reset/isolation
    #: policy (DATA-OQ-01, Approved SRS §13, elevated by spec sec. 16/29
    #: to an active CP-MVP2-06 live-execution risk) is an environment-
    #: level constraint, not a tool/business/data-value problem.
    DATA_OQ_01_UNRESOLVED = "DATA_OQ_01_UNRESOLVED"


#: Explicit subtype -> base-category mapping (spec sec. 13). Every
#: subtype used anywhere in execution/ must appear here.
FAILURE_SUBTYPE_TO_CATEGORY: Dict[str, str] = {
    FailureSubtype.BROWSER_LAUNCH_FAILURE: FailureCategory.TOOL_ISSUE,
    FailureSubtype.LOCATOR_FAILURE: FailureCategory.TOOL_ISSUE,
    FailureSubtype.TIMEOUT: FailureCategory.ENVIRONMENT_ISSUE,
    FailureSubtype.NAVIGATION_FAILURE: FailureCategory.THIRD_PARTY_DEPENDENCY_ISSUE,
    FailureSubtype.ASSERTION_FAILURE: FailureCategory.CONSTRAINT_VIOLATION,
    FailureSubtype.DATA_OQ_01_UNRESOLVED: FailureCategory.ENVIRONMENT_ISSUE,
}


@dataclass
class StepResult:
    __test__ = False

    step_order: int
    action_type: str
    target_locator_reference: Optional[str]
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    observed_result: Optional[str] = None
    expected_condition: Optional[str] = None
    evidence_references: List[str] = field(default_factory=list)
    error_information: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AssertionResult:
    assertion_type: str
    condition: str
    source: str
    counts_toward_coverage: bool
    passed: Optional[bool] = None  # None when not evaluated (e.g. NOT_EXECUTED)
    observed: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionResult:
    __test__ = False

    execution_id: str
    automation_id: str
    testcase_id: str
    requirement_ids: List[str]
    test_data_set_id: str
    journey_id: Optional[str]
    scenario_type: str
    browser: Optional[str]
    execution_start: Optional[str]
    execution_end: Optional[str]
    duration_seconds: Optional[float]
    overall_status: str
    step_results: List[StepResult] = field(default_factory=list)
    assertion_results: List[AssertionResult] = field(default_factory=list)
    evidence_references: List[str] = field(default_factory=list)
    failure_classification: Optional[str] = None
    failure_summary: Optional[str] = None
    source_attribution: List[Dict] = field(default_factory=list)
    environment_metadata: Dict[str, Any] = field(default_factory=dict)
    governance_status: str = ""
    reproducibility_metadata: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
