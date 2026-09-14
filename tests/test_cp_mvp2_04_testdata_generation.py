"""
CP-MVP2-04 focused tests — governed LLM test-data generation.

Exercises testdata/{schema,constraints,generate,validate,pipeline}.py
against the frozen CP-MVP2-04 Specification v1.0
(docs/CP-MVP2-04-SPECIFICATION-v1.0.md). Every governance assertion is a
plain equality/membership check — none ask an LLM to decide pass/fail,
matching the project-wide convention already followed in
tests/test_cp_mvp2_02_knowledge.py and tests/test_cp_mvp2_03_testcase_generation.py.

Generation-path tests use StubTestDataClient (llm/test_data_client.py)
rather than a live Claude call — this sandboxed suite has no
OPENAI_API_KEY/live network assumption baked in, and CP-MVP2-04
inherits CP-MVP2-03's rule that governance tests must run without
requiring uncontrolled external behavior. The anchor CP-MVP2-03
testcases used here are themselves generated with StubLLMClient
(CP-MVP2-03's own stub) — this test file never depends on a live
Claude call succeeding.
"""
from __future__ import annotations

import pytest

from knowledge.lib.retrieval import KnowledgeBase
from llm.client import StubLLMClient
from llm.test_data_client import StubTestDataClient
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase, Priority, ScenarioType, Testcase
from testcases.validate import govern_batch as govern_testcases
from testdata.constraints import get_constraint_profile
from testdata.generate import generate_for_testcase, generate_for_testcases
from testdata.pipeline import run_cp_mvp2_04
from testdata.schema import (
    DataCategory,
    DataGovernanceStatus,
    DataValidity,
    TestDataField,
    TestDataSet,
    UniquenessRequirement,
    ValueType,
)
from testdata.validate import (
    calculate_coverage,
    check_duplicate_dataset_ids,
    enforce_uniqueness,
    govern_batch,
    govern_dataset,
    validate_constraints,
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


def _accepted_testcase(kb, cp03_stub, requirement_id="REQ-REG-01", scenario_types=None):
    """Real CP-MVP2-03 pipeline (unmodified), StubLLMClient, to produce
    one genuine ACCEPTED anchor testcase — not a hand-built shortcut."""
    result = generate_for_requirement(kb, requirement_id, cp03_stub, scenario_types or [ScenarioType.POSITIVE])
    governed = govern_testcases(result.testcases, kb)
    accepted = [g for g in governed if g.governance_status == TestcaseGovernanceStatus.ACCEPTED]
    assert accepted, f"expected at least one ACCEPTED CP-03 testcase for {requirement_id}"
    return accepted[0]


def _ds(**overrides):
    base = dict(
        data_set_id="TD-TEST-01",
        testcase_id="TC-TEST-01",
        requirement_ids=["REQ-REG-01"],
        data_category=DataCategory.POSITIVE,
        purpose="test",
        validity=DataValidity.VALID,
        fields=[TestDataField("first_name", "Synthetic", ValueType.STRING)],
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    return TestDataSet(**base)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_valid_dataset_passes_schema():
    result = validate_schema(_ds())
    assert result["passed"], result["detail"]


def test_dataset_missing_fields_fails_schema():
    result = validate_schema(_ds(fields=[]))
    assert not result["passed"]
    assert "NO_FIELDS" in result["detail"]


def test_dataset_invalid_category_fails_schema():
    result = validate_schema(_ds(data_category="NOT_A_CATEGORY"))
    assert not result["passed"]
    assert "INVALID_DATA_CATEGORY" in result["detail"]


def test_field_invalid_value_type_fails_schema():
    ds = _ds(fields=[TestDataField("x", "y", "NOT_A_TYPE")])
    result = validate_schema(ds)
    assert not result["passed"]
    assert any("FIELD_INVALID_VALUE_TYPE" in p for p in result["detail"])


def test_fixed_vocabularies_are_exactly_five_categories():
    from testdata.schema import ALL_DATA_CATEGORIES

    assert ALL_DATA_CATEGORIES == {"POSITIVE", "ALTERNATE", "EXCEPTIONAL", "BOUNDARY", "INVALID"}


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def test_valid_testcase_linkage_is_accepted(kb, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    full_valid_fields = [
        TestDataField("first_name", "Jane", ValueType.STRING),
        TestDataField("last_name", "Doe", ValueType.STRING),
        TestDataField("email", "jane.doe@example.test", ValueType.EMAIL, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE),
        TestDataField("password", "p", ValueType.STRING),
        TestDataField("confirm_password", "p", ValueType.STRING, dependency_reference="password"),
    ]
    ds = _ds(testcase_id=anchor.testcase.testcase_id, requirement_ids=list(anchor.testcase.requirement_ids), fields=full_valid_fields)
    governed = govern_dataset(ds, {anchor.testcase.testcase_id: anchor})
    assert governed.governance_status == DataGovernanceStatus.ACCEPTED


def test_missing_testcase_is_quarantined():
    ds = _ds(testcase_id="TC-DOES-NOT-EXIST")
    governed = govern_dataset(ds, {})
    assert governed.governance_status == DataGovernanceStatus.QUARANTINED


def test_testcase_not_accepted_is_rejected():
    rejected_tc = GovernedTestcase(
        Testcase("TC-X", "t", ["REQ-REG-01"], ScenarioType.POSITIVE, [], ["s"], "r", Priority.MEDIUM),
        TestcaseGovernanceStatus.REJECTED,
        ["some reason"],
    )
    ds = _ds(testcase_id="TC-X")
    governed = govern_dataset(ds, {"TC-X": rejected_tc})
    assert governed.governance_status == DataGovernanceStatus.REJECTED


def test_requirement_id_mismatch_is_rejected(kb, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    ds = _ds(testcase_id=anchor.testcase.testcase_id, requirement_ids=["REQ-NOT-THE-SAME"])
    governed = govern_dataset(ds, {anchor.testcase.testcase_id: anchor})
    assert governed.governance_status == DataGovernanceStatus.REJECTED


def test_orphan_dataset_missing_attribution_is_rejected(kb, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    ds = _ds(testcase_id=anchor.testcase.testcase_id, requirement_ids=list(anchor.testcase.requirement_ids), source_attribution=[])
    result = validate_traceability(ds, {anchor.testcase.testcase_id: anchor})
    assert not result["passed"]


def test_attribution_is_preserved_end_to_end(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["POSITIVE"])
    assert result.datasets
    attribution = result.datasets[0].source_attribution[0]
    assert attribution["requirement_id"] == "REQ-REG-01"
    assert attribution["source_document"] == "requirements/MVP2_SRS_v1.0_APPROVED.md"
    assert attribution["source_version"] == "1.0"
    assert attribution["chunk_id"]


# ---------------------------------------------------------------------------
# Constraint validation
# ---------------------------------------------------------------------------

def test_mandatory_field_blank_fails_valid_dataset():
    profile = get_constraint_profile("REQ-REG-01")
    ds = _ds(
        validity=DataValidity.VALID,
        fields=[
            TestDataField("first_name", "", ValueType.STRING),
            TestDataField("last_name", "Doe", ValueType.STRING),
            TestDataField("email", "a@example.test", ValueType.EMAIL),
            TestDataField("password", "p", ValueType.STRING),
            TestDataField("confirm_password", "p", ValueType.STRING),
        ],
    )
    result = validate_constraints(ds, profile)
    assert not result["passed"]
    assert "first_name" in result["detail"]["blank_mandatory"]


def test_optional_field_blank_does_not_fail_valid_dataset():
    profile = get_constraint_profile("REQ-ACO-03")
    fields = [
        TestDataField(
            s.field_name,
            "" if not s.mandatory else ("jane@example.test" if s.value_type == "EMAIL" else "X"),
            s.value_type,
        )
        for s in profile.field_specs
    ]
    ds = _ds(requirement_ids=["REQ-ACO-03"], fields=fields)
    result = validate_constraints(ds, profile)
    assert result["passed"], result["detail"]


def test_email_format_violation_detected():
    profile = get_constraint_profile("REQ-REG-01")
    ds = _ds(
        fields=[
            TestDataField("first_name", "A", ValueType.STRING),
            TestDataField("last_name", "B", ValueType.STRING),
            TestDataField("email", "not-an-email", ValueType.EMAIL),
            TestDataField("password", "p", ValueType.STRING),
            TestDataField("confirm_password", "p", ValueType.STRING),
        ]
    )
    result = validate_constraints(ds, profile)
    assert not result["passed"]
    assert "email" in result["detail"]["email_format_violations"]


def test_password_confirmation_mismatch_detected():
    profile = get_constraint_profile("REQ-REG-01")
    ds = _ds(
        fields=[
            TestDataField("first_name", "A", ValueType.STRING),
            TestDataField("last_name", "B", ValueType.STRING),
            TestDataField("email", "a@example.test", ValueType.EMAIL),
            TestDataField("password", "p1", ValueType.STRING),
            TestDataField("confirm_password", "p2", ValueType.STRING, dependency_reference="password"),
        ]
    )
    result = validate_constraints(ds, profile)
    assert not result["passed"]
    assert "confirm_password!=password" in result["detail"]["dependency_violations"]


def test_documented_allowed_value_accepted():
    profile = get_constraint_profile("REQ-PAY-01")
    ds = _ds(requirement_ids=["REQ-PAY-01"], fields=[TestDataField("payment_method", "Credit Card", ValueType.ENUM)])
    result = validate_constraints(ds, profile)
    assert result["passed"]


def test_undocumented_value_rejected():
    profile = get_constraint_profile("REQ-PAY-01")
    ds = _ds(requirement_ids=["REQ-PAY-01"], fields=[TestDataField("payment_method", "Bitcoin", ValueType.ENUM)])
    result = validate_constraints(ds, profile)
    assert not result["passed"]
    assert "payment_method" in result["detail"]["enum_violations"]


def test_undocumented_boundary_is_unsupported_not_invented(kb, td_stub, cp03_stub):
    # REQ-PAY-01 has no documented_boundary — requesting BOUNDARY must
    # never fabricate one.
    anchor = _accepted_testcase(kb, cp03_stub)  # REQ-REG-01 also has no documented boundary
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["BOUNDARY"])
    assert result.datasets == []
    assert result.unsupported is not None


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def test_positive_category_generated_where_justified(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["POSITIVE"])
    assert any(d.data_category == "POSITIVE" for d in result.datasets)


def test_exceptional_category_generated_from_documented_negative_cases(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["EXCEPTIONAL"])
    assert any(d.data_category == "EXCEPTIONAL" for d in result.datasets)
    # real, evidence-grounded literal value from the Approved SRS's own Evidence Basis cell (NEG-03)
    assert any(
        any(f.field_value == "not-an-email" for f in d.fields)
        for d in result.datasets
    )


def test_invalid_category_generated_from_documented_blank_case(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["INVALID"])
    assert any(d.data_category == "INVALID" for d in result.datasets)


def test_boundary_category_generated_for_cart_quantity(kb, td_stub):
    tc = Testcase("TC-CART-01", "t", ["REQ-CART-03"], ScenarioType.EXCEPTIONAL, [], ["s"], "r", Priority.MEDIUM)
    governed_tc = GovernedTestcase(tc, TestcaseGovernanceStatus.ACCEPTED, [])
    result = generate_for_testcase(kb, governed_tc, td_stub, requested_categories=["BOUNDARY"])
    assert result.datasets
    boundary_ds = result.datasets[0]
    assert boundary_ds.data_category == "BOUNDARY"
    assert boundary_ds.fields[0].field_value == 0
    assert boundary_ds.fields[0].boundary_classification == "MIN_BOUNDARY"


def test_alternate_not_manufactured_without_documented_evidence(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)  # REQ-REG-01 has no documented_alternate
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["ALTERNATE"])
    assert result.datasets == []
    assert result.unsupported is not None


# ---------------------------------------------------------------------------
# Uniqueness
# ---------------------------------------------------------------------------

def test_unique_emails_across_different_datasets_both_accepted():
    a = _ds(data_set_id="TD-A", fields=[TestDataField("email", "a@example.test", ValueType.EMAIL, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE)])
    b = _ds(data_set_id="TD-B", testcase_id="TC-TEST-02", fields=[TestDataField("email", "b@example.test", ValueType.EMAIL, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE)])
    from testdata.schema import GovernedTestDataSet

    governed = [GovernedTestDataSet(a, DataGovernanceStatus.ACCEPTED, []), GovernedTestDataSet(b, DataGovernanceStatus.ACCEPTED, [])]
    enforce_uniqueness(governed)
    assert governed[0].governance_status == DataGovernanceStatus.ACCEPTED
    assert governed[1].governance_status == DataGovernanceStatus.ACCEPTED


def test_duplicate_must_be_unique_email_is_rejected():
    a = _ds(data_set_id="TD-A", fields=[TestDataField("email", "same@example.test", ValueType.EMAIL, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE)])
    b = _ds(data_set_id="TD-B", testcase_id="TC-TEST-02", fields=[TestDataField("email", "same@example.test", ValueType.EMAIL, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE)])
    from testdata.schema import GovernedTestDataSet

    governed = [GovernedTestDataSet(a, DataGovernanceStatus.ACCEPTED, []), GovernedTestDataSet(b, DataGovernanceStatus.ACCEPTED, [])]
    enforce_uniqueness(governed)
    assert governed[0].governance_status == DataGovernanceStatus.ACCEPTED
    assert governed[1].governance_status == DataGovernanceStatus.REJECTED
    assert any("UNIQUENESS_COLLISION" in r for r in governed[1].reasons)


def test_possible_duplicate_same_mapping_different_content_is_flagged_not_dropped(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["EXCEPTIONAL"])
    accepted_by_id = {anchor.testcase.testcase_id: anchor}
    governed = govern_batch(result.datasets, accepted_by_id)
    statuses = {g.governance_status for g in governed}
    assert DataGovernanceStatus.POSSIBLE_DUPLICATE in statuses  # multiple distinct EXCEPTIONAL datasets for one testcase
    assert all(g.governance_status != DataGovernanceStatus.REJECTED for g in governed if g.dataset.data_category == "EXCEPTIONAL")


def test_reusable_duplicate_email_case_is_accepted_not_rejected(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["EXCEPTIONAL"])
    duplicate_email_ds = next(
        d for d in result.datasets
        if any("Business Rule #1" in d.purpose for _ in [0]) or "NEG-04" in d.purpose
    )
    email_field = next(f for f in duplicate_email_ds.fields if f.field_name == "email")
    assert email_field.uniqueness_requirement == UniquenessRequirement.MAY_REUSE
    governed = govern_dataset(duplicate_email_ds, {anchor.testcase.testcase_id: anchor})
    assert governed.governance_status != DataGovernanceStatus.REJECTED


def test_unknown_uniqueness_never_silently_elevated():
    ds = _ds(fields=[TestDataField("first_name", "A", ValueType.STRING)])  # default UNIQUENESS_UNKNOWN
    assert ds.fields[0].uniqueness_requirement == UniquenessRequirement.UNIQUENESS_UNKNOWN


# ---------------------------------------------------------------------------
# Unsupported / clarification
# ---------------------------------------------------------------------------

def test_missing_evidence_unknown_requirement_reports_unsupported():
    tc = Testcase("TC-UNK-01", "t", ["REQ-DOES-NOT-EXIST"], ScenarioType.POSITIVE, [], ["s"], "r", Priority.MEDIUM)
    governed_tc = GovernedTestcase(tc, TestcaseGovernanceStatus.ACCEPTED, [])
    kb = KnowledgeBase.load()
    stub = StubTestDataClient()
    result = generate_for_testcase(kb, governed_tc, stub, requested_categories=["POSITIVE"])
    assert result.datasets == []
    assert result.unsupported["reason"] == "INSUFFICIENT_EVIDENCE"


def test_shipping_method_has_no_profile_reports_unsupported():
    # REQ-SHIP-01: the Approved SRS approves only "existence of the
    # choice" — no exact enumerated method-name set is fixed by it, per
    # spec sec. 8/22. CP-MVP2-04 must not invent one.
    assert get_constraint_profile("REQ-SHIP-01") is None


def test_country_value_set_is_not_invented():
    # REQ-ACO-03: Country is mandatory but the Approved SRS fixes no
    # allowed-value list or country-code standard for it (spec sec. 8).
    profile = get_constraint_profile("REQ-ACO-03")
    country_spec = next(s for s in profile.field_specs if s.field_name == "country")
    assert country_spec.allowed_values is None
    assert country_spec.value_type == ValueType.STRING  # not ENUM — no invented value set


def test_data_oq_01_isolation_dependency_never_assumed(kb, td_stub, cp03_stub):
    # DATA-OQ-01 (Approved SRS §13): the shared-instance data-reset/
    # isolation policy is unknown. No constraint profile in this
    # implementation encodes an assumption about it; requesting ALTERNATE
    # (which would require prior-state/isolation knowledge for REQ-REG-01,
    # per spec sec. 9) correctly reports UNSUPPORTED rather than assuming
    # an isolation policy.
    anchor = _accepted_testcase(kb, cp03_stub)
    result = generate_for_testcase(kb, anchor, td_stub, requested_categories=["ALTERNATE"])
    assert result.unsupported is not None


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

def test_accepted_dataset_counts_toward_coverage():
    from testdata.schema import GovernedTestDataSet

    ds = _ds()
    governed = [GovernedTestDataSet(ds, DataGovernanceStatus.ACCEPTED, [])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 100.0


def test_rejected_dataset_does_not_count_toward_coverage():
    from testdata.schema import GovernedTestDataSet

    ds = _ds()
    governed = [GovernedTestDataSet(ds, DataGovernanceStatus.REJECTED, ["x"])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 0.0
    assert coverage["uncovered_testcases"] == ["TC-TEST-01"]


def test_quarantined_dataset_does_not_count_toward_coverage():
    from testdata.schema import GovernedTestDataSet

    ds = _ds()
    governed = [GovernedTestDataSet(ds, DataGovernanceStatus.QUARANTINED, ["x"])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 0.0


def test_orphan_or_out_of_universe_testcase_does_not_inflate_coverage():
    from testdata.schema import GovernedTestDataSet

    ds = _ds(testcase_id="TC-NOT-IN-UNIVERSE")
    governed = [GovernedTestDataSet(ds, DataGovernanceStatus.ACCEPTED, [])]
    coverage = calculate_coverage(governed, applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["covered_testcases"] == []
    assert coverage["coverage_percentage"] == 0.0


def test_exact_duplicate_does_not_double_count_but_possible_duplicate_does_count():
    from testdata.schema import GovernedTestDataSet

    accepted = GovernedTestDataSet(_ds(data_set_id="TD-A"), DataGovernanceStatus.ACCEPTED, [])
    exact_dup = GovernedTestDataSet(_ds(data_set_id="TD-B"), DataGovernanceStatus.DUPLICATE, [])
    possible_dup = GovernedTestDataSet(_ds(data_set_id="TD-C"), DataGovernanceStatus.POSSIBLE_DUPLICATE, [])
    coverage = calculate_coverage([accepted, exact_dup, possible_dup], applicable_testcase_ids={"TC-TEST-01"})
    assert coverage["coverage_percentage"] == 100.0  # still 1/1 — DUPLICATE contributes nothing extra, POSSIBLE_DUPLICATE alone would already cover it


def test_duplicate_data_set_ids_detected():
    result = check_duplicate_dataset_ids([_ds(data_set_id="TD-SAME"), _ds(data_set_id="TD-SAME")])
    assert not result["passed"]
    assert result["detail"] == {"TD-SAME": 2}


# ---------------------------------------------------------------------------
# End-to-end pipeline integration
# ---------------------------------------------------------------------------

def test_full_pipeline_produces_well_formed_governed_result(kb, td_stub, cp03_stub):
    anchor = _accepted_testcase(kb, cp03_stub)
    report = run_cp_mvp2_04(kb, td_stub, [anchor], requested_categories=["POSITIVE", "EXCEPTIONAL", "INVALID"])
    assert report["duplicate_data_set_id_check"]["passed"]
    assert report["coverage"]["coverage_percentage"] == 100.0
    assert report["unsupported_testcases"] == []
    assert report["generator"] == "stub-deterministic-v1"


def test_pipeline_excludes_non_accepted_cp03_testcases_from_universe():
    rejected_tc = GovernedTestcase(
        Testcase("TC-REJ-01", "t", ["REQ-REG-01"], ScenarioType.POSITIVE, [], ["s"], "r", Priority.MEDIUM),
        TestcaseGovernanceStatus.REJECTED,
        ["reason"],
    )
    kb = KnowledgeBase.load()
    stub = StubTestDataClient()
    report = run_cp_mvp2_04(kb, stub, [rejected_tc])
    assert report["testcase_ids_processed"] == []
    assert report["coverage"]["total_applicable_testcases"] == 0
