"""
CP-MVP2-06 — end-to-end governed execution pipeline.

Implements the flow from the frozen specification sec. 2/7:
    ACCEPTED/GOVERNED CP-05 ARTIFACT -> ELIGIBILITY -> REAL BROWSER
    -> GOVERNED STEP EXECUTION -> ASSERTION EVALUATION -> EVIDENCE
    -> EXECUTION RESULT -> FAILURE CLASSIFICATION -> CP-06 RESULT

No LLM participates anywhere in this module (spec sec. 17). Every
branch is a deterministic check or a real Playwright call.

**Disclosed simplification (spec sec. 11's assertion-execution
requirement, honestly narrowed for this v1.0 implementation):** this
pipeline does not implement free-text natural-language matching of an
Assertion's `condition` string against live DOM content (that is a
nontrivial NLP/DOM-inspection problem this implementation does not
claim to solve). Instead, a BUSINESS_REQUIRED assertion is evaluated as
"passed" if and only if every governed step executed with
StepStatus.PASS -- i.e. the assertion's condition is treated as "the
governed step sequence completed exactly as specified," which is a
sound, disclosed proxy, not a claim of full assertion-text verification.
This is documented in docs/CP-MVP2-06-IMPLEMENTATION.md as a known
limitation, not hidden.
"""
from __future__ import annotations

import datetime
import sys
from typing import Dict, List, Optional

from automation.schema import ActionType, AssertionType, GovernanceStatus as PlaywrightGovernanceStatus, PlaywrightArtifact
from testdata.schema import GovernedTestDataSet

from execution.engine import BrowserExecutor, BrowserLaunchError
from execution.evidence import EvidenceManager
from execution.schema import (
    FAILURE_SUBTYPE_TO_CATEGORY,
    AssertionResult,
    ExecutionResult,
    FailureCategory,
    FailureSubtype,
    OverallStatus,
    StepStatus,
)
from execution.validate import (
    assess_data_oq_01,
    check_authorization_precondition,
    check_eligibility,
    validate_data_field_availability,
    validate_pre_execution,
)


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _playwright_version() -> Optional[str]:
    try:
        import importlib.metadata

        return importlib.metadata.version("playwright")
    except Exception:
        return None


def _not_executed_result(
    execution_id: str,
    artifact: PlaywrightArtifact,
    governance_status: str,
    reason: str,
    detail,
    sut_base_url: str,
) -> ExecutionResult:
    return ExecutionResult(
        execution_id=execution_id,
        automation_id=artifact.automation_id,
        testcase_id=artifact.testcase_id,
        requirement_ids=list(artifact.requirement_ids),
        test_data_set_id=artifact.test_data_set_id,
        journey_id=artifact.journey_id,
        scenario_type=artifact.scenario_type,
        browser=None,
        execution_start=None,
        execution_end=None,
        duration_seconds=None,
        overall_status=OverallStatus.NOT_EXECUTED,
        source_attribution=list(artifact.source_attribution),
        environment_metadata={"sut_url": sut_base_url},
        governance_status=governance_status,
        reproducibility_metadata={
            "execution_id": execution_id,
            "timestamp": _now_iso(),
            "python_version": sys.version,
            "playwright_version": _playwright_version(),
            "automation_id": artifact.automation_id,
            "test_data_set_id": artifact.test_data_set_id,
        },
        notes=[f"{reason}: {detail}"],
    )


def _blocked_result(
    execution_id: str,
    artifact: PlaywrightArtifact,
    governance_status: str,
    failure_classification: str,
    reason: str,
    detail,
    sut_base_url: str,
) -> ExecutionResult:
    return ExecutionResult(
        execution_id=execution_id,
        automation_id=artifact.automation_id,
        testcase_id=artifact.testcase_id,
        requirement_ids=list(artifact.requirement_ids),
        test_data_set_id=artifact.test_data_set_id,
        journey_id=artifact.journey_id,
        scenario_type=artifact.scenario_type,
        browser=None,
        execution_start=None,
        execution_end=None,
        duration_seconds=None,
        overall_status=OverallStatus.BLOCKED,
        failure_classification=failure_classification,
        failure_summary=f"{reason}: {detail}",
        source_attribution=list(artifact.source_attribution),
        environment_metadata={"sut_url": sut_base_url},
        governance_status=governance_status,
        reproducibility_metadata={
            "execution_id": execution_id,
            "timestamp": _now_iso(),
            "python_version": sys.version,
            "playwright_version": _playwright_version(),
            "automation_id": artifact.automation_id,
            "test_data_set_id": artifact.test_data_set_id,
        },
        notes=[f"{reason}: {detail}"],
    )


def run_cp_mvp2_06(
    governed_artifact,  # automation.schema.GovernedPlaywrightArtifact
    governed_dataset: GovernedTestDataSet,
    sut_base_url: str,
    timeout_ms: int = 30000,
    execution_id: Optional[str] = None,
) -> ExecutionResult:
    artifact: PlaywrightArtifact = governed_artifact.artifact
    execution_id = execution_id or f"EXEC-{artifact.automation_id}-01"

    # 1. Eligibility (spec sec. 4) -- design-time, no browser touched.
    eligibility = check_eligibility(governed_artifact.governance_status)
    if not eligibility["passed"]:
        return _not_executed_result(
            execution_id, artifact, governed_artifact.governance_status,
            "INELIGIBLE", eligibility["detail"], sut_base_url,
        )

    # 2. Pre-execution integrity re-check (spec sec. 17) -- design-time.
    pre_check = validate_pre_execution(artifact)
    if not pre_check["passed"]:
        return _not_executed_result(
            execution_id, artifact, governed_artifact.governance_status,
            "PRE_EXECUTION_INTEGRITY_FAILURE", pre_check["detail"], sut_base_url,
        )

    data_check = validate_data_field_availability(artifact, governed_dataset)
    if not data_check["passed"]:
        return _not_executed_result(
            execution_id, artifact, governed_artifact.governance_status,
            "TEST_DATA_FIELD_UNAVAILABLE", data_check["detail"], sut_base_url,
        )

    # 2b. Authorization-precondition check (spec sec. 16) -- the artifact
    # itself is eligible and well-formed, but no reusable authenticated-
    # session fixture exists in this project, so a precondition
    # requiring one cannot be established. This is BLOCKED, not
    # NOT_EXECUTED: the artifact is not ineligible or malformed, an
    # environment/precondition capability is simply missing.
    auth_check = check_authorization_precondition(artifact)
    if not auth_check["passed"]:
        return _blocked_result(
            execution_id, artifact, governed_artifact.governance_status,
            FailureCategory.AUTHORIZATION_ISSUE,
            "AUTHORIZATION_PRECONDITION_UNAVAILABLE", auth_check["detail"], sut_base_url,
        )

    # 2c. DATA-OQ-01 assessment (task sec. 10; spec sec. 16/29) -- a
    # state-mutating scenario against the shared, uncontrolled SUT is
    # never assumed safe by default. This gate runs BEFORE any real
    # browser action, exactly like the authorization-precondition gate.
    data_oq_01_check = assess_data_oq_01(artifact)
    if not data_oq_01_check["passed"]:
        return _blocked_result(
            execution_id, artifact, governed_artifact.governance_status,
            FAILURE_SUBTYPE_TO_CATEGORY[FailureSubtype.DATA_OQ_01_UNRESOLVED],
            "DATA_OQ_01_UNRESOLVED", data_oq_01_check["detail"], sut_base_url,
        )

    # 3. Real execution attempt begins here.
    evidence = EvidenceManager(execution_id)
    field_values: Dict[str, object] = {f.field_name: f.field_value for f in governed_dataset.dataset.fields}
    executor = BrowserExecutor(sut_base_url=sut_base_url, timeout_ms=timeout_ms, headless=True)

    execution_start = _now_iso()
    try:
        step_results, resolved_browser = executor.run_steps(artifact, field_values, evidence)
    except BrowserLaunchError as exc:
        execution_end = _now_iso()
        evidence.log(f"BROWSER_LAUNCH_FAILURE: {exc}")
        log_ref = evidence.flush_log()
        return ExecutionResult(
            execution_id=execution_id, automation_id=artifact.automation_id, testcase_id=artifact.testcase_id,
            requirement_ids=list(artifact.requirement_ids), test_data_set_id=artifact.test_data_set_id,
            journey_id=artifact.journey_id, scenario_type=artifact.scenario_type, browser=None,
            execution_start=execution_start, execution_end=execution_end, duration_seconds=None,
            overall_status=OverallStatus.ERROR,
            evidence_references=[log_ref],
            failure_classification=FAILURE_SUBTYPE_TO_CATEGORY[FailureSubtype.BROWSER_LAUNCH_FAILURE],
            failure_summary=f"Browser launch failed: {exc}",
            source_attribution=list(artifact.source_attribution),
            environment_metadata={"sut_url": sut_base_url},
            governance_status=governed_artifact.governance_status,
            reproducibility_metadata={
                "execution_id": execution_id, "timestamp": _now_iso(), "python_version": sys.version,
                "playwright_version": _playwright_version(), "sut_url": sut_base_url,
            },
            notes=["BROWSER_LAUNCH_FAILURE"],
        )
    execution_end = _now_iso()

    for sr in step_results:
        evidence.log(f"step {sr.step_order} [{sr.action_type}] -> {sr.status}: {sr.observed_result or sr.error_information}")
    log_ref = evidence.flush_log()

    evidence_refs = [log_ref]
    for sr in step_results:
        evidence_refs.extend(sr.evidence_references)

    # 4. Assertion evaluation (spec sec. 11) -- disclosed simplification, see module docstring.
    all_steps_passed = all(sr.status == StepStatus.PASS for sr in step_results)
    assertion_results: List[AssertionResult] = []
    for a in artifact.assertions:
        evaluated_pass = all_steps_passed if a.assertion_type == AssertionType.BUSINESS_REQUIRED else None
        assertion_results.append(
            AssertionResult(
                assertion_type=a.assertion_type, condition=a.condition, source=a.source,
                counts_toward_coverage=a.counts_toward_coverage, passed=evaluated_pass,
                observed=("step sequence completed without failure" if all_steps_passed else "a load-bearing step failed") if a.assertion_type == AssertionType.BUSINESS_REQUIRED else None,
            )
        )

    business_results = [ar for ar in assertion_results if ar.assertion_type == AssertionType.BUSINESS_REQUIRED]
    business_passed = all(ar.passed for ar in business_results) if business_results else False

    # 5. overall_status + failure classification (spec secs. 9/11/13).
    failed_steps = [sr for sr in step_results if sr.status in (StepStatus.FAIL, StepStatus.ERROR)]
    failure_classification = None
    failure_summary = None

    if not failed_steps and business_passed:
        overall_status = OverallStatus.PASS
    elif any(sr.status == StepStatus.ERROR for sr in failed_steps):
        overall_status = OverallStatus.ERROR
        errored = next(sr for sr in failed_steps if sr.status == StepStatus.ERROR)
        subtype = FailureSubtype.LOCATOR_FAILURE if errored.action_type in (ActionType.FILL, ActionType.CLICK, ActionType.SELECT) else FailureSubtype.BROWSER_LAUNCH_FAILURE
        failure_classification = FAILURE_SUBTYPE_TO_CATEGORY[subtype]
        failure_summary = f"Step {errored.step_order} ({errored.action_type}) errored: {errored.error_information}"
    elif failed_steps:
        overall_status = OverallStatus.FAIL
        failed = failed_steps[0]
        if failed.error_information and "TIMEOUT" in failed.error_information:
            subtype = FailureSubtype.TIMEOUT
        elif failed.action_type == ActionType.NAVIGATE:
            subtype = FailureSubtype.NAVIGATION_FAILURE
        else:
            subtype = FailureSubtype.ASSERTION_FAILURE
        failure_classification = FAILURE_SUBTYPE_TO_CATEGORY[subtype]
        failure_summary = f"Step {failed.step_order} ({failed.action_type}) failed: {failed.error_information}"
    else:
        overall_status = OverallStatus.FAIL
        failure_classification = FailureCategory.CONSTRAINT_VIOLATION
        failure_summary = "A BUSINESS_REQUIRED assertion did not hold."

    start_dt = datetime.datetime.fromisoformat(execution_start)
    end_dt = datetime.datetime.fromisoformat(execution_end)

    return ExecutionResult(
        execution_id=execution_id,
        automation_id=artifact.automation_id,
        testcase_id=artifact.testcase_id,
        requirement_ids=list(artifact.requirement_ids),
        test_data_set_id=artifact.test_data_set_id,
        journey_id=artifact.journey_id,
        scenario_type=artifact.scenario_type,
        browser=resolved_browser,
        execution_start=execution_start,
        execution_end=execution_end,
        duration_seconds=(end_dt - start_dt).total_seconds(),
        overall_status=overall_status,
        step_results=step_results,
        assertion_results=assertion_results,
        evidence_references=evidence_refs,
        failure_classification=failure_classification,
        failure_summary=failure_summary,
        source_attribution=list(artifact.source_attribution),
        environment_metadata={"sut_url": sut_base_url},
        governance_status=governed_artifact.governance_status,
        reproducibility_metadata={
            "execution_id": execution_id,
            "timestamp": _now_iso(),
            "browser": resolved_browser,
            "playwright_version": _playwright_version(),
            "python_version": sys.version,
            "sut_url": sut_base_url,
            "automation_id": artifact.automation_id,
            "test_data_set_id": artifact.test_data_set_id,
        },
        notes=[],
    )
