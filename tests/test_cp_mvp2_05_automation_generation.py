"""
CP-MVP2-05 focused tests — governed Playwright artifact generation.

Exercises automation/{schema,evidence,generate,validate,pipeline}.py
against the frozen CP-MVP2-05 Specification v1.0
(docs/CP-MVP2-05-SPECIFICATION-v1.0.md). Every governance assertion is a
plain equality/membership check — none ask an LLM to decide pass/fail.

Generation-path tests use StubAutomationClient (llm/automation_client.py)
and the CP-MVP2-03/04 stubs — no live Claude call in this file. Anchor
CP-MVP2-03 testcases and CP-MVP2-04 datasets are produced by those
checkpoints' own real, unmodified pipelines with their respective
stubs — never hand-built shortcuts, except where a test explicitly
constructs a synthetic fixture and discloses it as such (mirroring the
project-wide convention already used for draft-leakage/supersession
mechanism tests).
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from knowledge.lib.retrieval import KnowledgeBase
from llm.automation_client import StubAutomationClient
from llm.client import StubLLMClient
from llm.test_data_client import StubTestDataClient
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase, Priority, ScenarioType, Testcase
from testcases.validate import govern_batch as govern_testcases
from testdata.generate import generate_for_testcases as td_generate_for_testcases
from testdata.schema import DataGovernanceStatus, GovernedTestDataSet, TestDataField, TestDataSet, ValueType
from testdata.validate import govern_batch as govern_datasets

from automation.evidence import lookup_locator, lookup_submit_locator
from automation.generate import build_artifact_context, generate_for_testcase
from automation.pipeline import run_cp_mvp2_05
from automation.schema import (
    ActionType,
    Assertion,
    AssertionType,
    GovernanceStatus,
    LocatorSpec,
    LocatorStatus,
    LocatorStrategy,
    PlaywrightArtifact,
    PlaywrightStep,
    SyncStrategy,
)
from automation.validate import (
    calculate_coverage,
    check_duplicate_automation_ids,
    govern_artifact,
    govern_batch,
    validate_assertions,
    validate_data_mapping,
    validate_locators,
    validate_schema,
    validate_traceability,
)


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


@pytest.fixture(scope="module")
def cp03_stub():
    return StubLLMClient()


@pytest.fixture(scope="module")
def td_stub():
    return StubTestDataClient()


@pytest.fixture(scope="module")
def pw_stub():
    return StubAutomationClient()


def _accepted_aco03(kb, cp03_stub, td_stub):
    """Real, unmodified CP-03 + CP-04 pipelines (stubs) anchored on
    REQ-ACO-03, which has genuine, real locator evidence (unlike
    REQ-REG-01) -- used throughout as the "has evidence" anchor."""
    gen = generate_for_requirement(kb, "REQ-ACO-03", cp03_stub, scenario_types=[ScenarioType.POSITIVE])
    governed_tcs = govern_testcases(gen.testcases, kb)
    accepted_tc = next(g for g in governed_tcs if g.governance_status == TestcaseGovernanceStatus.ACCEPTED)
    gen_results = td_generate_for_testcases(kb, [accepted_tc], td_stub, requested_categories=[ScenarioType.POSITIVE])
    all_datasets = [d for r in gen_results for d in r.datasets]
    governed_datasets = govern_datasets(all_datasets, {accepted_tc.testcase.testcase_id: accepted_tc})
    accepted_ds = next(g for g in governed_datasets if g.governance_status == DataGovernanceStatus.ACCEPTED)
    return accepted_tc, accepted_ds


def _accepted_reg01(kb, cp03_stub, td_stub):
    gen = generate_for_requirement(kb, "REQ-REG-01", cp03_stub, scenario_types=[ScenarioType.POSITIVE])
    governed_tcs = govern_testcases(gen.testcases, kb)
    accepted_tc = next(g for g in governed_tcs if g.governance_status == TestcaseGovernanceStatus.ACCEPTED)
    gen_results = td_generate_for_testcases(kb, [accepted_tc], td_stub, requested_categories=[ScenarioType.POSITIVE])
    all_datasets = [d for r in gen_results for d in r.datasets]
    governed_datasets = govern_datasets(all_datasets, {accepted_tc.testcase.testcase_id: accepted_tc})
    accepted_ds = next(g for g in governed_datasets if g.governance_status == DataGovernanceStatus.ACCEPTED)
    return accepted_tc, accepted_ds


def _artifact(**overrides):
    base = dict(
        automation_id="PW-TEST-01",
        testcase_id="TC-TEST-01",
        requirement_ids=["REQ-ACO-03"],
        test_data_set_id="TD-TEST-01",
        journey_id="J-01",
        scenario_type=ScenarioType.POSITIVE,
        browser_intent="chromium-headless",
        preconditions=[],
        steps=[PlaywrightStep(1, ActionType.NAVIGATE)],
        assertions=[Assertion(AssertionType.BUSINESS_REQUIRED, "result", "testcase:TC-TEST-01.expected_result", True)],
        source_attribution=[{"requirement_id": "REQ-ACO-03"}],
    )
    base.update(overrides)
    return PlaywrightArtifact(**base)


# ---------------------------------------------------------------------------
# Valid artifact generation (real evidence path)
# ---------------------------------------------------------------------------

def test_valid_artifact_generated_with_real_address_evidence(kb, cp03_stub, td_stub, pw_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    result = generate_for_testcase(kb, tc, ds, pw_stub)
    assert result.artifact is not None
    fill_steps = [s for s in result.artifact.steps if s.action_type == ActionType.FILL]
    assert fill_steps
    evidenced = [s for s in fill_steps if s.locator and s.locator.status == LocatorStatus.EVIDENCED]
    assert len(evidenced) == len(fill_steps), "every REQ-ACO-03 address field is genuinely evidenced in checkout_00.html"


def test_valid_artifact_reaches_accepted_with_synthetic_unambiguous_evidence(kb, cp03_stub, td_stub):
    # DISCLOSED SYNTHETIC MECHANISM TEST (mirrors the project-wide
    # precedent, e.g. tests/test_cp_mvp2_02_knowledge.py's supersession
    # test and tests/test_cp_mvp2_04_testdata_generation.py's draft-
    # leakage test): the REAL REQ-ACO-03 evidence has a genuinely
    # ambiguous submit-button locator (two elements share one class),
    # so a real end-to-end ACCEPTED artifact cannot be demonstrated
    # against real evidence today. This test proves the ACCEPTED
    # mechanism itself works correctly when locator evidence is NOT
    # ambiguous, using a mocked evidence lookup -- it does not claim
    # the real capture is unambiguous.
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    from automation.evidence import LocatorEvidence

    def fake_lookup(requirement_id, field_name):
        return LocatorEvidence(LocatorStrategy.STABLE_ATTRIBUTE, f"#fake_{field_name}", "synthetic_test_fixture")

    def fake_submit(requirement_id):
        return LocatorEvidence(LocatorStrategy.STABLE_ATTRIBUTE, "#fake_submit", "synthetic_test_fixture")

    from llm.automation_client import StubAutomationClient

    with patch("automation.generate.lookup_locator", side_effect=fake_lookup), \
         patch("automation.generate.lookup_submit_locator", side_effect=fake_submit):
        result = generate_for_testcase(kb, tc, ds, StubAutomationClient())
    assert result.artifact is not None
    governed = govern_artifact(result.artifact, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert governed.governance_status == GovernanceStatus.ACCEPTED, governed.reasons


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_valid_artifact_passes_schema():
    result = validate_schema(_artifact())
    assert result["passed"], result["detail"]


def test_artifact_with_no_steps_fails_schema():
    result = validate_schema(_artifact(steps=[]))
    assert not result["passed"]
    assert "NO_STEPS" in result["detail"]


def test_artifact_with_no_assertions_fails_schema():
    result = validate_schema(_artifact(assertions=[]))
    assert not result["passed"]
    assert "NO_ASSERTIONS" in result["detail"]


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def test_testcase_traceability_valid(kb, cp03_stub, td_stub, pw_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    result = generate_for_testcase(kb, tc, ds, pw_stub)
    trace = validate_traceability(result.artifact, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert trace["passed"], trace["detail"]


def test_unknown_testcase_id_is_quarantined():
    governed = govern_artifact(_artifact(testcase_id="TC-UNKNOWN"), {}, {})
    assert governed.governance_status == GovernanceStatus.QUARANTINED


def test_requirement_traceability_mismatch_is_rejected(kb, cp03_stub, td_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    art = _artifact(testcase_id=tc.testcase.testcase_id, test_data_set_id=ds.dataset.data_set_id, requirement_ids=["REQ-NOT-THE-SAME"])
    governed = govern_artifact(art, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert governed.governance_status == GovernanceStatus.REJECTED


def test_test_data_traceability_unknown_dataset_is_quarantined(kb, cp03_stub, td_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    art = _artifact(testcase_id=tc.testcase.testcase_id, requirement_ids=list(tc.testcase.requirement_ids), test_data_set_id="TD-UNKNOWN")
    governed = govern_artifact(art, {tc.testcase.testcase_id: tc}, {})
    assert governed.governance_status == GovernanceStatus.QUARANTINED


def test_orphan_artifact_missing_attribution_fails_traceability(kb, cp03_stub, td_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    art = _artifact(
        testcase_id=tc.testcase.testcase_id,
        requirement_ids=list(tc.testcase.requirement_ids),
        test_data_set_id=ds.dataset.data_set_id,
        source_attribution=[],
    )
    result = validate_traceability(art, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert not result["passed"]


# ---------------------------------------------------------------------------
# Locator evidence / fabrication rejection / non-generalization
# ---------------------------------------------------------------------------

def test_real_address_field_locator_is_evidenced_and_matches_real_capture():
    evidence = lookup_locator("REQ-ACO-03", "first_name")
    assert evidence is not None
    assert evidence.value == "#BillingNewAddress_FirstName"
    assert "checkout_00.html" in evidence.evidence_source


def test_registration_has_zero_locator_evidence():
    # No /register capture exists anywhere (spec sec. 20 item 1) --
    # every field must report no evidence, never a guessed locator.
    for field_name in ("first_name", "last_name", "email", "password", "confirm_password"):
        assert lookup_locator("REQ-REG-01", field_name) is None


def test_cart_quantity_locator_is_never_fabricated():
    # spec sec. 20 item 3: the only evidenced form is item-specific
    # (itemquantity<id>) and is not generalized here.
    assert lookup_locator("REQ-CART-03", "quantity") is None


def test_payment_method_option_locator_is_not_invented():
    # spec sec. 20 item 2: option-level locators unconfirmed.
    assert lookup_locator("REQ-PAY-01", "payment_method") is None


def test_ambiguous_submit_button_is_unsupported_not_guessed():
    # Real inspection: "new-address-next-step-button" class is shared by
    # 2 elements (Billing.save() and Shipping.save()) on the same real
    # page -- an ambiguous locator must never be resolved by picking one.
    assert lookup_submit_locator("REQ-ACO-03") is None


def test_no_lookup_function_ever_returns_a_value_for_an_unmapped_field():
    assert lookup_locator("REQ-ACO-03", "totally_made_up_field") is None


def test_unsupported_locator_makes_whole_artifact_unsupported_not_accepted(kb, cp03_stub, td_stub, pw_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    result = generate_for_testcase(kb, tc, ds, pw_stub)
    governed = govern_artifact(result.artifact, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    # The real submit-button step is UNSUPPORTED -> whole artifact UNSUPPORTED.
    assert governed.governance_status == GovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION
    assert governed.governance_status != GovernanceStatus.ACCEPTED


# ---------------------------------------------------------------------------
# Test-data mapping / missing data handling
# ---------------------------------------------------------------------------

def test_fill_step_field_not_in_dataset_fails_data_mapping():
    ds = GovernedTestDataSet(
        TestDataSet("TD-X", "TC-X", ["REQ-ACO-03"], "POSITIVE", "p", "VALID", fields=[TestDataField("first_name", "A", ValueType.STRING)]),
        DataGovernanceStatus.ACCEPTED,
        [],
    )
    art = _artifact(steps=[PlaywrightStep(1, ActionType.FILL, input_mapping="email")])
    result = validate_data_mapping(art, ds)
    assert not result["passed"]
    assert 1 in result["detail"]["unmapped_steps"]


def test_missing_test_data_field_is_unsupported_via_no_input_mapping():
    # A FILL step whose field_name the LLM proposed is not among the
    # dataset's available fields is assembled with input_mapping=None
    # by automation.generate (never invented) -- and rejected by
    # validate_data_mapping, never silently accepted.
    art = _artifact(steps=[PlaywrightStep(1, ActionType.FILL, input_mapping=None)])
    ds = GovernedTestDataSet(
        TestDataSet("TD-X", "TC-TEST-01", ["REQ-ACO-03"], "POSITIVE", "p", "VALID", fields=[TestDataField("first_name", "A", ValueType.STRING)]),
        DataGovernanceStatus.ACCEPTED,
        [],
    )
    result = validate_data_mapping(art, ds)
    assert not result["passed"]


# ---------------------------------------------------------------------------
# Assertion governance
# ---------------------------------------------------------------------------

def test_assertion_governance_requires_business_required():
    result = validate_assertions(_artifact(assertions=[Assertion(AssertionType.TECHNICAL_USEFUL, "x", "llm", False)]))
    assert not result["passed"]
    assert "NO_BUSINESS_REQUIRED_ASSERTION" in result["detail"]


def test_technical_assertion_never_counts_toward_coverage():
    bad = Assertion(AssertionType.TECHNICAL_USEFUL, "x", "llm", True)  # deliberately mis-flagged
    result = validate_assertions(_artifact(assertions=[
        Assertion(AssertionType.BUSINESS_REQUIRED, "y", "testcase:TC.expected_result", True),
        bad,
    ]))
    assert not result["passed"]
    assert any("NON_BUSINESS_ASSERTION_FALSELY_COUNTS" in p for p in result["detail"])


def test_deterministic_business_assertion_is_always_present(kb, cp03_stub, td_stub, pw_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    result = generate_for_testcase(kb, tc, ds, pw_stub)
    business = [a for a in result.artifact.assertions if a.assertion_type == AssertionType.BUSINESS_REQUIRED]
    assert len(business) == 1
    assert business[0].condition == tc.testcase.expected_result
    assert business[0].counts_toward_coverage is True


# ---------------------------------------------------------------------------
# Governance states / unsupported handling
# ---------------------------------------------------------------------------

def test_testcase_not_accepted_yields_unsupported_generation():
    rejected_tc = GovernedTestcase(
        Testcase("TC-X", "t", ["REQ-ACO-03"], ScenarioType.POSITIVE, [], ["s"], "r", Priority.MEDIUM),
        TestcaseGovernanceStatus.REJECTED,
        ["reason"],
    )
    ds = GovernedTestDataSet(
        TestDataSet("TD-X", "TC-X", ["REQ-ACO-03"], "POSITIVE", "p", "VALID", fields=[TestDataField("first_name", "A", ValueType.STRING)]),
        DataGovernanceStatus.ACCEPTED,
        [],
    )
    kb = KnowledgeBase.load()
    result = generate_for_testcase(kb, rejected_tc, ds, StubAutomationClient())
    assert result.artifact is None
    assert result.unsupported["reason"] == "TESTCASE_NOT_ACCEPTED"


def test_dataset_not_eligible_yields_unsupported_generation(kb, cp03_stub):
    gen = generate_for_requirement(kb, "REQ-ACO-03", cp03_stub, scenario_types=[ScenarioType.POSITIVE])
    governed_tcs = govern_testcases(gen.testcases, kb)
    accepted_tc = next(g for g in governed_tcs if g.governance_status == TestcaseGovernanceStatus.ACCEPTED)
    rejected_ds = GovernedTestDataSet(
        TestDataSet("TD-X", accepted_tc.testcase.testcase_id, ["REQ-ACO-03"], "POSITIVE", "p", "VALID", fields=[]),
        DataGovernanceStatus.REJECTED,
        ["x"],
    )
    result = generate_for_testcase(kb, accepted_tc, rejected_ds, StubAutomationClient())
    assert result.artifact is None
    assert result.unsupported["reason"] == "DATASET_NOT_ELIGIBLE"


def test_registration_artifact_is_unsupported_end_to_end(kb, cp03_stub, td_stub, pw_stub):
    tc, ds = _accepted_reg01(kb, cp03_stub, td_stub)
    result = generate_for_testcase(kb, tc, ds, pw_stub)
    assert result.artifact is not None  # steps ARE proposed and assembled
    governed = govern_artifact(result.artifact, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert governed.governance_status == GovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION


# ---------------------------------------------------------------------------
# Duplicate / orphan handling
# ---------------------------------------------------------------------------

def test_duplicate_automation_ids_detected():
    result = check_duplicate_automation_ids([_artifact(automation_id="PW-SAME"), _artifact(automation_id="PW-SAME")])
    assert not result["passed"]
    assert result["detail"] == {"PW-SAME": 2}


def test_orphan_artifact_referencing_unknown_dataset_is_quarantined_in_batch(kb, cp03_stub, td_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    orphan = _artifact(
        automation_id="PW-ORPHAN",
        testcase_id=tc.testcase.testcase_id,
        requirement_ids=list(tc.testcase.requirement_ids),
        test_data_set_id="TD-DOES-NOT-EXIST",
    )
    governed = govern_batch([orphan], {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert governed[0].governance_status == GovernanceStatus.QUARANTINED


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

def test_accepted_artifact_counts_toward_coverage():
    from automation.schema import GovernedPlaywrightArtifact

    governed = [GovernedPlaywrightArtifact(_artifact(), GovernanceStatus.ACCEPTED, [])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 100.0


def test_unsupported_artifact_does_not_count_toward_coverage():
    from automation.schema import GovernedPlaywrightArtifact

    governed = [GovernedPlaywrightArtifact(_artifact(), GovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION, ["x"])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 0.0
    assert coverage["uncovered_testcases"] == ["TC-TEST-01"]


def test_llm_attempting_every_testcase_does_not_imply_100_percent_coverage(kb, cp03_stub, td_stub, pw_stub):
    # Real end-to-end proof: REQ-ACO-03 gets a *generated* artifact (the
    # LLM/stub did propose something for it), but because the real
    # submit-button evidence is ambiguous, it is NOT accepted, so
    # coverage must be 0%, not 100%, for this single-testcase universe.
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    report = run_cp_mvp2_05(kb, pw_stub, [tc], [ds])
    assert report["testcase_ids_processed"] == [tc.testcase.testcase_id]
    assert any(g["automation_id"] for g in report["governed_artifacts"])  # something was generated
    assert report["coverage"]["coverage_percentage"] == 0.0  # but not accepted


# ---------------------------------------------------------------------------
# End-to-end pipeline integration
# ---------------------------------------------------------------------------

def test_full_pipeline_scopes_to_accepted_cp03_testcases_only():
    rejected_tc = GovernedTestcase(
        Testcase("TC-REJ-01", "t", ["REQ-ACO-03"], ScenarioType.POSITIVE, [], ["s"], "r", Priority.MEDIUM),
        TestcaseGovernanceStatus.REJECTED,
        ["reason"],
    )
    kb = KnowledgeBase.load()
    report = run_cp_mvp2_05(kb, StubAutomationClient(), [rejected_tc], [])
    assert report["testcase_ids_processed"] == []
    assert report["coverage"]["total_applicable_testcases"] == 0


def test_build_artifact_context_never_leaks_locator_or_value_surface(kb, cp03_stub, td_stub):
    tc, ds = _accepted_aco03(kb, cp03_stub, td_stub)
    context = build_artifact_context(tc, ds, "REQ-ACO-03")
    assert "locator" not in context
    assert "field_value" not in str(context.get("available_fields"))  # only field NAMES, never values
    assert set(context["available_fields"]) <= {f.field_name for f in ds.dataset.fields}
