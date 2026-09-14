"""
CP-MVP2-06 focused tests — governed real browser execution.

Exercises execution/{schema,validate,evidence,engine,pipeline}.py
against the frozen CP-MVP2-06 Specification v1.0
(docs/CP-MVP2-06-SPECIFICATION-v1.0.md). There is no LLM anywhere in
CP-MVP2-06 (spec sec. 17) -- every test here is a deterministic
unit/integration/negative/governance check.

**Explicitly labeled test categories, per this checkpoint's own testing
requirement (never blended):**
  - UNIT: deterministic components only, no Playwright/browser involved.
  - INTEGRATION (mocked): exercises pipeline control flow with
    `execution.engine.BrowserExecutor` mocked -- the mock is always
    named/asserted explicitly; its output is never presented as live
    evidence.
  - NEGATIGE/GOVERNANCE: invalid/ineligible artifacts and prohibited
    behaviors.
  - SECURITY: secret/credential redaction.
No test in this file launches a real browser. Real browser evidence
(genuine Chromium launch, genuine navigation to the real SUT, a real
captured screenshot) is recorded separately in this task's execution
report, never inside the automated unit-test suite -- mirroring the
exact "never blend mocked and live evidence" discipline this project
has applied at every prior checkpoint.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from automation.schema import (
    ActionType,
    Assertion,
    AssertionType,
    GovernanceStatus as PlaywrightGovernanceStatus,
    GovernedPlaywrightArtifact,
    LocatorSpec,
    LocatorStatus,
    LocatorStrategy,
    PlaywrightArtifact,
    PlaywrightStep,
)
from testdata.schema import DataGovernanceStatus, GovernedTestDataSet, TestDataField, TestDataSet, ValueType

from execution.engine import BrowserExecutor, BrowserLaunchError
from execution.evidence import EvidenceManager, redact_field_value
from execution.pipeline import run_cp_mvp2_06
from execution.schema import (
    FAILURE_SUBTYPE_TO_CATEGORY,
    ExecutionResult,
    FailureCategory,
    FailureSubtype,
    OverallStatus,
    StepResult,
    StepStatus,
)
from execution.validate import (
    STATE_MUTATING_REQUIREMENT_IDS,
    assess_data_oq_01,
    check_authorization_precondition,
    check_eligibility,
    validate_data_field_availability,
    validate_pre_execution,
)


def _artifact(**overrides) -> PlaywrightArtifact:
    base = dict(
        automation_id="PW-TEST-01",
        testcase_id="TC-TEST-01",
        requirement_ids=["REQ-ACO-03"],
        test_data_set_id="TD-TEST-01",
        journey_id="J-01",
        scenario_type="POSITIVE",
        browser_intent="chromium-headless",
        preconditions=[],
        steps=[
            PlaywrightStep(1, ActionType.NAVIGATE),
            PlaywrightStep(
                2, ActionType.FILL,
                locator=LocatorSpec(LocatorStrategy.STABLE_ATTRIBUTE, "#first_name", "checkout_00.html", LocatorStatus.EVIDENCED),
                input_mapping="first_name",
            ),
        ],
        assertions=[Assertion(AssertionType.BUSINESS_REQUIRED, "result", "testcase:TC-TEST-01.expected_result", True)],
        source_attribution=[{"requirement_id": "REQ-ACO-03"}],
    )
    base.update(overrides)
    return PlaywrightArtifact(**base)


def _dataset(**overrides) -> TestDataSet:
    base = dict(
        data_set_id="TD-TEST-01",
        testcase_id="TC-TEST-01",
        requirement_ids=["REQ-ACO-03"],
        data_category="POSITIVE",
        purpose="p",
        validity="VALID",
        fields=[TestDataField("first_name", "Jane", ValueType.STRING)],
    )
    base.update(overrides)
    return TestDataSet(**base)


def _governed(artifact, status=PlaywrightGovernanceStatus.ACCEPTED, reasons=None):
    return GovernedPlaywrightArtifact(artifact, status, reasons or [])


def _governed_dataset(dataset, status=DataGovernanceStatus.ACCEPTED):
    return GovernedTestDataSet(dataset, status, [])


# ===========================================================================
# UNIT: eligibility
# ===========================================================================

def test_accepted_is_eligible():
    assert check_eligibility(PlaywrightGovernanceStatus.ACCEPTED)["passed"]


def test_possible_duplicate_is_eligible():
    assert check_eligibility(PlaywrightGovernanceStatus.POSSIBLE_DUPLICATE)["passed"]


@pytest.mark.parametrize("status", ["REJECTED", "QUARANTINED", "UNSUPPORTED_NEEDS_CLARIFICATION", "DUPLICATE"])
def test_other_statuses_are_not_eligible(status):
    assert not check_eligibility(status)["passed"]


# ===========================================================================
# UNIT: pre-execution validation
# ===========================================================================

def test_well_formed_artifact_passes_pre_execution():
    result = validate_pre_execution(_artifact())
    assert result["passed"], result["detail"]


def test_wrong_browser_intent_fails_pre_execution():
    result = validate_pre_execution(_artifact(browser_intent="firefox"))
    assert not result["passed"]
    assert any("UNSUPPORTED_BROWSER_INTENT" in p for p in result["detail"])


def test_no_business_required_assertion_fails_pre_execution():
    result = validate_pre_execution(_artifact(assertions=[Assertion(AssertionType.TECHNICAL_USEFUL, "x", "llm", False)]))
    assert not result["passed"]
    assert "NO_BUSINESS_REQUIRED_ASSERTION" in result["detail"]


def test_unsupported_locator_fails_pre_execution_never_fabricated():
    # A step whose locator status is UNSUPPORTED must never reach real
    # execution -- CP-06 never invents a locator to route around this.
    bad_step = PlaywrightStep(2, ActionType.CLICK, locator=LocatorSpec(LocatorStrategy.UNSUPPORTED, None, None, LocatorStatus.UNSUPPORTED))
    result = validate_pre_execution(_artifact(steps=[PlaywrightStep(1, ActionType.NAVIGATE), bad_step]))
    assert not result["passed"]
    assert any("LOCATOR_NOT_EVIDENCED" in p for p in result["detail"])


def test_missing_input_mapping_fails_pre_execution():
    bad_step = PlaywrightStep(2, ActionType.FILL, locator=LocatorSpec(LocatorStrategy.STABLE_ATTRIBUTE, "#x", "src", LocatorStatus.EVIDENCED), input_mapping=None)
    result = validate_pre_execution(_artifact(steps=[PlaywrightStep(1, ActionType.NAVIGATE), bad_step]))
    assert not result["passed"]


# ===========================================================================
# UNIT: data-field availability
# ===========================================================================

def test_data_field_available():
    result = validate_data_field_availability(_artifact(), _governed_dataset(_dataset()))
    assert result["passed"]


def test_data_field_unavailable_detected():
    bad_step = PlaywrightStep(2, ActionType.FILL, locator=LocatorSpec(LocatorStrategy.STABLE_ATTRIBUTE, "#x", "src", LocatorStatus.EVIDENCED), input_mapping="does_not_exist")
    result = validate_data_field_availability(_artifact(steps=[PlaywrightStep(1, ActionType.NAVIGATE), bad_step]), _governed_dataset(_dataset()))
    assert not result["passed"]
    assert 2 in result["detail"]["missing_field_steps"]


# ===========================================================================
# UNIT: authorization-precondition
# ===========================================================================

def test_no_authorization_precondition_passes():
    result = check_authorization_precondition(_artifact(preconditions=["Approved requirement REQ-ACO-03 is in effect"]))
    assert result["passed"]


def test_authenticated_precondition_is_flagged_unsatisfiable():
    result = check_authorization_precondition(_artifact(preconditions=["User has an existing account and is authenticated"]))
    assert not result["passed"]
    assert result["detail"]["unsatisfiable_preconditions"]


# ===========================================================================
# UNIT: DATA-OQ-01 assessment
# ===========================================================================

def test_non_mutating_requirement_passes_data_oq_01():
    result = assess_data_oq_01(_artifact(requirement_ids=["REQ-ACO-03"]))
    assert result["passed"]


@pytest.mark.parametrize("req_id", sorted(STATE_MUTATING_REQUIREMENT_IDS))
def test_state_mutating_requirement_blocked_by_data_oq_01(req_id):
    result = assess_data_oq_01(_artifact(requirement_ids=[req_id]))
    assert not result["passed"]
    assert result["detail"]["state_mutating"] is True


def test_synthetic_test_data_alone_does_not_bypass_data_oq_01():
    # Explicit governance check: synthetic CP-04 data does not, by
    # itself, make a state-mutating scenario safe (task sec. 10).
    result = assess_data_oq_01(_artifact(requirement_ids=["REQ-REG-01"]))
    assert not result["passed"]


# ===========================================================================
# UNIT: failure taxonomy
# ===========================================================================

def test_every_subtype_maps_to_exactly_one_base_category():
    for subtype in (
        FailureSubtype.BROWSER_LAUNCH_FAILURE, FailureSubtype.LOCATOR_FAILURE,
        FailureSubtype.TIMEOUT, FailureSubtype.NAVIGATION_FAILURE,
        FailureSubtype.ASSERTION_FAILURE, FailureSubtype.DATA_OQ_01_UNRESOLVED,
    ):
        assert FAILURE_SUBTYPE_TO_CATEGORY[subtype] in vars(FailureCategory).values()


# ===========================================================================
# UNIT: evidence / security
# ===========================================================================

def test_evidence_manager_creates_real_files():
    # Uses the real, already-.gitignore'd runs/cp_mvp2_06/ convention
    # (not an external tmp_path) so EvidenceManager's own relative-path
    # computation, which is intentionally scoped to the repository root,
    # is exercised as it actually behaves in production.
    manager = EvidenceManager("TEST-EXEC-UNIT-TEST-ONLY")
    manager.log("line one")
    manager.log("line two")
    log_ref = manager.flush_log()
    assert manager.directory.exists()
    assert (manager.directory / "execution.log").exists()
    assert "TEST-EXEC-UNIT-TEST-ONLY" in log_ref
    # Clean up this unit test's own artifact -- runs/ is gitignored and
    # this is the only file this test creates.
    (manager.directory / "execution.log").unlink()
    manager.directory.rmdir()


def test_password_field_value_is_redacted_in_logs():
    assert redact_field_value("password", "Sup3rSecret!") == "[REDACTED]"
    assert redact_field_value("confirm_password", "Sup3rSecret!") == "[REDACTED]"
    assert redact_field_value("api_key", "sk-fake") == "[REDACTED]"


def test_non_credential_field_value_is_not_redacted():
    assert redact_field_value("first_name", "Jane") == "Jane"


# ===========================================================================
# INTEGRATION (mocked BrowserExecutor) -- explicitly labeled, never live
# ===========================================================================

def test_ineligible_artifact_never_reaches_browser_layer():
    with patch("execution.pipeline.BrowserExecutor") as mock_executor_cls:
        result = run_cp_mvp2_06(
            _governed(_artifact(), status=PlaywrightGovernanceStatus.REJECTED),
            _governed_dataset(_dataset()),
            sut_base_url="https://demowebshop.tricentis.com/",
        )
        mock_executor_cls.assert_not_called()
    assert result.overall_status == OverallStatus.NOT_EXECUTED
    assert result.browser is None
    assert result.step_results == []


def test_unsupported_artifact_never_reaches_browser_layer():
    with patch("execution.pipeline.BrowserExecutor") as mock_executor_cls:
        result = run_cp_mvp2_06(
            _governed(_artifact(), status=PlaywrightGovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION),
            _governed_dataset(_dataset()),
            sut_base_url="https://demowebshop.tricentis.com/",
        )
        mock_executor_cls.assert_not_called()
    assert result.overall_status == OverallStatus.NOT_EXECUTED
    assert result.governance_status == PlaywrightGovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION


def test_authorization_issue_never_reaches_browser_layer():
    artifact = _artifact(preconditions=["Requires an existing authenticated account"])
    with patch("execution.pipeline.BrowserExecutor") as mock_executor_cls:
        result = run_cp_mvp2_06(_governed(artifact), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
        mock_executor_cls.assert_not_called()
    assert result.overall_status == OverallStatus.BLOCKED
    assert result.failure_classification == FailureCategory.AUTHORIZATION_ISSUE


def test_data_oq_01_block_never_reaches_browser_layer():
    artifact = _artifact(requirement_ids=["REQ-REG-01"])
    with patch("execution.pipeline.BrowserExecutor") as mock_executor_cls:
        result = run_cp_mvp2_06(_governed(artifact), _governed_dataset(_dataset(requirement_ids=["REQ-REG-01"])), sut_base_url="https://demowebshop.tricentis.com/")
        mock_executor_cls.assert_not_called()
    assert result.overall_status == OverallStatus.BLOCKED
    assert result.failure_classification == FailureCategory.ENVIRONMENT_ISSUE
    assert "DATA_OQ_01" in result.notes[0]


def test_eligible_artifact_reaches_mocked_browser_and_pass_is_governed(monkeypatch):
    # MOCKED integration test: the browser layer itself is replaced with
    # a controlled double that reports success -- this is explicitly a
    # mocked-integration result, never presented as live evidence.
    step_results = [
        StepResult(1, ActionType.NAVIGATE, None, StepStatus.PASS),
        StepResult(2, ActionType.FILL, "#first_name", StepStatus.PASS),
    ]
    mock_instance = MagicMock()
    mock_instance.run_steps.return_value = (step_results, "chromium/mocked-999")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_instance):
        result = run_cp_mvp2_06(_governed(_artifact()), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.overall_status == OverallStatus.PASS
    assert result.browser == "chromium/mocked-999"
    assert result.assertion_results[0].passed is True


def test_eligible_artifact_mocked_step_failure_is_governed_fail(monkeypatch):
    step_results = [
        StepResult(1, ActionType.NAVIGATE, None, StepStatus.PASS),
        StepResult(2, ActionType.FILL, "#first_name", StepStatus.FAIL, error_information="element not interactable"),
    ]
    mock_instance = MagicMock()
    mock_instance.run_steps.return_value = (step_results, "chromium/mocked-999")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_instance):
        result = run_cp_mvp2_06(_governed(_artifact()), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.overall_status == OverallStatus.FAIL
    assert result.assertion_results[0].passed is False


def test_browser_launch_failure_is_governed_error():
    mock_instance = MagicMock()
    mock_instance.run_steps.side_effect = BrowserLaunchError("could not start chromium")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_instance):
        result = run_cp_mvp2_06(_governed(_artifact()), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.overall_status == OverallStatus.ERROR
    assert result.failure_classification == FailureCategory.TOOL_ISSUE


def test_technical_assertion_never_overrides_business_result(monkeypatch):
    # A TECHNICAL_USEFUL assertion is present but must never influence
    # overall_status -- only BUSINESS_REQUIRED does (spec sec. 11).
    artifact = _artifact(
        assertions=[
            Assertion(AssertionType.BUSINESS_REQUIRED, "result", "testcase:TC.expected_result", True),
            Assertion(AssertionType.TECHNICAL_USEFUL, "some diagnostic", "llm", False),
        ]
    )
    step_results = [StepResult(1, ActionType.NAVIGATE, None, StepStatus.PASS), StepResult(2, ActionType.FILL, "#x", StepStatus.PASS)]
    mock_instance = MagicMock()
    mock_instance.run_steps.return_value = (step_results, "chromium/mocked-999")
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_instance):
        result = run_cp_mvp2_06(_governed(artifact), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.overall_status == OverallStatus.PASS
    technical = next(a for a in result.assertion_results if a.assertion_type == AssertionType.TECHNICAL_USEFUL)
    assert technical.passed is None  # not evaluated as a pass/fail determinant


# ===========================================================================
# GOVERNANCE: traceability / no orphan results
# ===========================================================================

def test_execution_result_preserves_full_traceability():
    mock_instance = MagicMock()
    mock_instance.run_steps.return_value = ([StepResult(1, ActionType.NAVIGATE, None, StepStatus.PASS)], "chromium/mocked-999")
    artifact = _artifact()
    with patch("execution.pipeline.BrowserExecutor", return_value=mock_instance):
        result = run_cp_mvp2_06(_governed(artifact), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.automation_id == artifact.automation_id
    assert result.testcase_id == artifact.testcase_id
    assert result.requirement_ids == artifact.requirement_ids
    assert result.test_data_set_id == artifact.test_data_set_id
    assert result.source_attribution == artifact.source_attribution


def test_reproducibility_metadata_present_on_every_result():
    result = run_cp_mvp2_06(_governed(_artifact(), status=PlaywrightGovernanceStatus.REJECTED), _governed_dataset(_dataset()), sut_base_url="https://demowebshop.tricentis.com/")
    assert result.reproducibility_metadata.get("execution_id")
    assert result.reproducibility_metadata.get("timestamp")
    assert "python_version" in result.reproducibility_metadata
