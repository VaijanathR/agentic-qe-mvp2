"""
CP-MVP2-CR-001 Batch 1 — RBTP (Risk-Based Test Prioritization) tests.

Covers: evidence-backed factor derivation (never fabricated), the
explainability requirement ("why is TC-X P0 while TC-Y P2"), governance
rejection of an unknown testcase, the LLM's narrow non-authoritative
surface, and RBTP's schema-level distinctness from the Dependency
Matrix.
"""
from __future__ import annotations

import pytest

import rbtp.persist as rbtp_persist
from dependencies.schema import DependencyMatrix
from knowledge.lib.retrieval import KnowledgeBase
from llm.client import StubLLMClient
from llm.rbtp_client import StubRBTPClient
from rbtp.generate import generate_rbtp_for_testcase
from rbtp.schema import RISK_FACTOR_FIELDS, Priority, RiskLevel
from rbtp.validate import govern_batch
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus
from testcases.validate import govern_batch as govern_testcases


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


@pytest.fixture(scope="module")
def stub():
    return StubLLMClient()


def _accepted_testcase(kb, stub, requirement_id, scenario_types=("POSITIVE",)):
    result = generate_for_requirement(kb, requirement_id, stub, list(scenario_types))
    governed = govern_testcases(result.testcases, kb)
    accepted = [g for g in governed if g.governance_status == GovernanceStatus.ACCEPTED]
    assert accepted, f"expected at least one ACCEPTED testcase for {requirement_id}"
    return accepted[0]


def test_security_relevant_requirement_yields_high_security_impact(kb, stub):
    """REQ-REG-01's real, approved requirement text mentions Password /
    Confirm password -- security_impact must be HIGH, evidenced, not
    invented."""
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    assert record.security_impact == RiskLevel.HIGH
    assert "password" in record.generation_metadata["evidence_sources"]["security_impact"].lower()


def test_non_security_requirement_yields_low_not_unknown_security_impact(kb, stub):
    """REQ-WISH-03's real requirement text is not security-relevant --
    the scan ran and found nothing, which is LOW (checked), not UNKNOWN
    (no check possible)."""
    gtc = _accepted_testcase(kb, stub, "REQ-WISH-03")
    record = generate_rbtp_for_testcase(kb, gtc)
    assert record.security_impact == RiskLevel.LOW


def test_no_fabricated_factors_for_unavailable_evidence(kb, stub):
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    assert record.risk_likelihood == RiskLevel.UNKNOWN
    assert record.change_impact == RiskLevel.UNKNOWN
    assert record.defect_history == RiskLevel.UNKNOWN
    assert record.dependency_impact == RiskLevel.UNKNOWN
    for factor in ("risk_likelihood", "change_impact", "defect_history", "dependency_impact"):
        assert "no" in record.risk_rationale.lower() or "computed after" in record.risk_rationale.lower()


def test_customer_impact_derived_from_real_journey_membership(kb, stub):
    """REQ-REG-01 belongs to journey J-01 (order-culminating), so
    customer_impact must be HIGH via the disclosed journey mapping."""
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    assert record.customer_impact == RiskLevel.HIGH
    assert "J-01" in record.generation_metadata["evidence_sources"]["customer_impact"]


def test_priority_is_explainable_from_the_persisted_rationale_alone(kb, stub):
    """'Why is TC-X P0 while TC-Y P2?' must be answerable purely from
    the persisted risk_rationale string -- no need to ask an LLM."""
    high = _accepted_testcase(kb, stub, "REQ-REG-01")   # HIGH security + HIGH customer impact -> at least P1
    low = _accepted_testcase(kb, stub, "REQ-WISH-03")   # LOW security, LOW customer impact -> P2/P3
    high_record = generate_rbtp_for_testcase(kb, high)
    low_record = generate_rbtp_for_testcase(kb, low)

    assert high_record.priority in (Priority.P0, Priority.P1)
    assert low_record.priority in (Priority.P2, Priority.P3)
    assert high_record.priority != low_record.priority
    # every factor that contributed is named, with its value, in the rationale
    assert f"security_impact={high_record.security_impact}" in high_record.risk_rationale
    assert f"customer_impact={high_record.customer_impact}" in high_record.risk_rationale
    assert f"priority={high_record.priority}" in high_record.risk_rationale


def test_llm_narrative_is_appended_but_never_authoritative(kb, stub):
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    llm = StubRBTPClient()
    record = generate_rbtp_for_testcase(kb, gtc, llm)
    assert "Stub narrative" in record.risk_rationale
    assert "non-authoritative" in record.risk_rationale
    # the deterministic factors/priority are unaffected by the LLM's presence
    deterministic_only = generate_rbtp_for_testcase(kb, gtc, None)
    assert record.priority == deterministic_only.priority
    assert record.security_impact == deterministic_only.security_impact
    assert record.customer_impact == deterministic_only.customer_impact


def test_governance_rejects_a_record_for_an_unaccepted_testcase(kb, stub):
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    governed = govern_batch([record], accepted_testcases_by_id={})  # anchor testcase not in the accepted map
    assert governed[0].governance_status == "REJECTED"
    assert "TESTCASE_NOT_ACCEPTED_OR_UNKNOWN" in governed[0].reasons


def test_governance_accepts_a_well_formed_record(kb, stub):
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    governed = govern_batch([record], accepted_testcases_by_id={gtc.testcase.testcase_id: gtc})
    assert governed[0].governance_status == "ACCEPTED"


def test_rbtp_and_dependency_matrix_schemas_are_disjoint():
    """RBTP is a prioritization concern; the Dependency Matrix is a
    structural-relationship concern -- neither schema carries the
    other's field."""
    import dataclasses
    dep_fields = {f.name for f in dataclasses.fields(DependencyMatrix)}
    assert not (dep_fields & set(RISK_FACTOR_FIELDS))
    assert "priority" not in dep_fields
    assert "risk_rationale" not in dep_fields


def test_rbtp_persist_roundtrip(tmp_path, monkeypatch, kb, stub):
    monkeypatch.setattr(rbtp_persist, "BASE_DIR", tmp_path)
    gtc = _accepted_testcase(kb, stub, "REQ-REG-01")
    record = generate_rbtp_for_testcase(kb, gtc)
    governed = govern_batch([record], accepted_testcases_by_id={gtc.testcase.testcase_id: gtc})
    result = rbtp_persist.persist_governed_record(governed[0], generator="deterministic-only", batch_id="B1")
    assert result["reused"] is False
    loaded = rbtp_persist.load_persisted_record(record.rbtp_id)
    assert loaded["testcase_id"] == gtc.testcase.testcase_id
    assert loaded["priority"] == record.priority
