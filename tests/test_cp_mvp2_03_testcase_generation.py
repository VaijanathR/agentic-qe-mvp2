"""
CP-MVP2-03 focused tests — governed LLM testcase generation.

These tests exercise the deterministic retrieval-context building,
generation orchestration, and governance/validation code under
testcases/ and llm/, against the frozen CP-MVP2-03 Specification v1.0
(docs/CP-MVP2-03-SPECIFICATION-v1.0.md).

Every governance assertion here is a plain equality/membership check —
none of them ask an LLM to decide pass/fail, per spec sec. 16
("Deterministic Responsibilities") and the project-wide governance rule
already followed in tests/test_cp_mvp2_02_knowledge.py.

Generation-path tests use StubLLMClient (see llm/client.py) rather than a
live OpenAI call: this project's sandboxed test environment has no
OPENAI_API_KEY configured, and CP-MVP2-03's own governance rules (sec.
19 of the implementation task) require that "governance tests can run
without requiring uncontrolled external behavior" and forbid fabricating
a successful live generation. StubLLMClient is a disclosed, deterministic
stand-in for the reasoning step — it never invents a scenario beyond what
the governed evidence passed to it justifies — so these tests genuinely
exercise the full RAG -> "LLM" -> governance pipeline end-to-end; they do
not verify that a live OpenAI call succeeds. See
docs/CP-MVP2-03-IMPLEMENTATION.md, "Limitations", for what this does and
does not prove.
"""
from __future__ import annotations

import pytest

from knowledge.lib.retrieval import KnowledgeBase
from knowledge.lib.schema import ApprovalStatus, EvidenceStrength
from llm.client import LLMUnavailableError, OpenAILLMClient, StubLLMClient
from testcases.generate import generate_for_requirement, requirement_context
from testcases.pipeline import run_cp_mvp2_03
from testcases.schema import GovernanceStatus, ScenarioType, Testcase
from testcases.validate import (
    calculate_coverage,
    check_duplicate_testcase_ids,
    govern_batch,
    govern_testcase,
    validate_schema,
)


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


@pytest.fixture(scope="module")
def stub():
    return StubLLMClient()


def _tc(**overrides):
    base = dict(
        testcase_id="TC-TEST-01",
        title="t",
        requirement_ids=["REQ-REG-01"],
        scenario_type=ScenarioType.POSITIVE,
        preconditions=[],
        test_steps=["step"],
        expected_result="result",
        source_attribution=[{"requirement_id": "REQ-REG-01"}],
    )
    base.update(overrides)
    return Testcase(**base)


# ---------------------------------------------------------------------------
# Functional (spec sec. 17 items 1-4)
# ---------------------------------------------------------------------------

def test_valid_approved_requirement_produces_structured_testcase_output(kb, stub):
    result = generate_for_requirement(kb, "REQ-REG-01", stub)
    assert result.testcases
    tc = result.testcases[0]
    for attr in ("testcase_id", "title", "requirement_ids", "scenario_type", "preconditions",
                 "test_steps", "expected_result", "priority", "source_attribution", "generation_metadata"):
        assert getattr(tc, attr) not in (None, "", []), attr


def test_positive_scenario_generated_where_justified(kb, stub):
    result = generate_for_requirement(kb, "REQ-REG-01", stub, scenario_types=[ScenarioType.POSITIVE])
    assert any(tc.scenario_type == ScenarioType.POSITIVE for tc in result.testcases)


def test_alternate_scenario_generated_where_justified_by_business_rule(kb, stub):
    # REQ-CART-03 has an approved business_rule (BR-04) directly attached
    # via kb.by_id — real governed evidence, not synthesized for the test.
    result = generate_for_requirement(kb, "REQ-CART-03", stub)
    assert any(tc.scenario_type == ScenarioType.ALTERNATE for tc in result.testcases)


def test_exceptional_scenario_generated_where_justified_by_journey_negative_case(kb, stub):
    # REQ-CART-03's journey J-04 includes NEG-07 as a member (real
    # journey_index data) — the negative_case evidence used to justify
    # this scenario is gathered from that membership, never invented.
    result = generate_for_requirement(kb, "REQ-CART-03", stub)
    assert any(tc.scenario_type == ScenarioType.EXCEPTIONAL for tc in result.testcases)


def test_scenario_not_manufactured_without_justifying_evidence(kb, stub):
    # REQ-WISH-02 has neither an approved business_rule nor a
    # journey-linked negative_case — ALTERNATE/EXCEPTIONAL must not be
    # invented just because they were requested.
    result = generate_for_requirement(kb, "REQ-WISH-02", stub)
    scenario_types_produced = {tc.scenario_type for tc in result.testcases}
    assert scenario_types_produced == {ScenarioType.POSITIVE}


# ---------------------------------------------------------------------------
# Traceability (spec sec. 17 items 5-8 / spec sec. 9)
# ---------------------------------------------------------------------------

def test_valid_requirement_mapping_is_accepted(kb):
    governed = govern_testcase(_tc(), kb)
    assert governed.governance_status == GovernanceStatus.ACCEPTED


def test_missing_requirement_id_is_rejected(kb):
    governed = govern_testcase(_tc(requirement_ids=[]), kb)
    assert governed.governance_status == GovernanceStatus.REJECTED


def test_unknown_requirement_id_is_quarantined(kb):
    governed = govern_testcase(_tc(requirement_ids=["REQ-DOES-NOT-EXIST"]), kb)
    assert governed.governance_status == GovernanceStatus.QUARANTINED
    assert "UNKNOWN_REQUIREMENT_ID" in governed.reasons[0]


def test_orphan_testcase_is_not_accepted(kb):
    # An orphan testcase — no valid requirement mapping at all — must not
    # reach ACCEPTED regardless of whether the ID is empty or unknown.
    assert govern_testcase(_tc(requirement_ids=[""]), kb).governance_status != GovernanceStatus.ACCEPTED
    assert govern_testcase(_tc(requirement_ids=["REQ-DOES-NOT-EXIST"]), kb).governance_status != GovernanceStatus.ACCEPTED


# ---------------------------------------------------------------------------
# Governance (spec sec. 17 items 9-12 / spec secs. 9, 11, 15)
# ---------------------------------------------------------------------------

def test_approved_requirement_is_eligible_for_generation(kb, stub):
    context = requirement_context(kb, "REQ-REG-01")
    assert context is not None
    assert context["approval_status"] == ApprovalStatus.APPROVED


def test_draft_leakage_cannot_produce_an_accepted_testcase(kb):
    # Synthetic single-chunk KB (same disclosed-synthetic-mechanism-test
    # convention used in tests/test_cp_mvp2_02_knowledge.py, since the
    # real corpus has no requirement that exists ONLY in draft — every
    # real draft requirement has an approved counterpart, so a true
    # draft-only leak cannot be demonstrated against real data). This
    # directly exercises spec sec. 11's required chain: Draft information
    # -> retrieved context -> possible generated testcase -> DETERMINISTIC
    # GOVERNANCE -> REJECT.
    synthetic_kb = KnowledgeBase()
    synthetic_kb.chunks = [
        {
            "chunk_id": "TEST__REQ-DRAFTONLY", "source": "test", "source_type": "draft_srs",
            "section": "test", "section_id": "0", "content_type": "requirement",
            "text": "draft only, never approved", "requirement_id": ["REQ-DRAFTONLY"], "journey_id": [],
            "classification": "OBSERVED", "approval_status": ApprovalStatus.DRAFT, "status_raw": "",
            "evidence_strength": EvidenceStrength.DIRECT_SYSTEM_EVIDENCE, "evidence_raw": "",
            "version": "0.1", "baseline_date": None, "scope": "in_scope", "checkpoint": "CP-MVP2-01",
            "actor": [], "source_hash": "x", "superseded_by": None, "supersedes": None, "authority_tier": 4,
        }
    ]
    synthetic_kb.manifests = {}
    governed = govern_testcase(_tc(requirement_ids=["REQ-DRAFTONLY"]), synthetic_kb)
    assert governed.governance_status == GovernanceStatus.REJECTED
    assert any("NOT_APPROVED" in r for r in governed.reasons)


def test_unsupported_requirement_is_reported_with_reason(kb, stub):
    # WISH-OQ-01 is an approved-SRS *open_question*, not an approved
    # *requirement* — insufficient governed evidence to generate from.
    result = generate_for_requirement(kb, "WISH-OQ-01", stub)
    assert result.testcases == []
    assert result.unsupported is not None
    assert result.unsupported["requirement_id"] == "WISH-OQ-01"
    assert result.unsupported["reason"] == "NO_APPROVED_REQUIREMENT_EVIDENCE"


# ---------------------------------------------------------------------------
# Quality (spec sec. 17 items 13-16 / spec secs. 13-14)
# ---------------------------------------------------------------------------

def test_schema_validation_flags_missing_fields():
    result = validate_schema(_tc(expected_result="", test_steps=[]))
    assert not result["passed"]
    assert "MISSING_EXPECTED_RESULT" in result["detail"]
    assert "MISSING_TEST_STEPS" in result["detail"]


def test_duplicate_testcase_ids_are_detected():
    result = check_duplicate_testcase_ids([_tc(testcase_id="TC-SAME"), _tc(testcase_id="TC-SAME")])
    assert not result["passed"]
    assert result["detail"] == {"TC-SAME": 2}


def test_obvious_duplicate_testcase_is_classified_duplicate(kb):
    a = _tc(testcase_id="TC-D-01", expected_result="same result text")
    b = _tc(testcase_id="TC-D-02", expected_result="Same Result Text")  # only case/whitespace differs
    governed = {g.testcase.testcase_id: g for g in govern_batch([a, b], kb)}
    assert governed["TC-D-01"].governance_status == GovernanceStatus.ACCEPTED
    assert governed["TC-D-02"].governance_status == GovernanceStatus.DUPLICATE


def test_distinct_wording_same_requirement_and_scenario_is_possible_duplicate_not_dropped(kb):
    a = _tc(testcase_id="TC-P-01", expected_result="outcome A")
    b = _tc(testcase_id="TC-P-02", expected_result="a materially different outcome B")
    governed = {g.testcase.testcase_id: g for g in govern_batch([a, b], kb)}
    assert governed["TC-P-01"].governance_status == GovernanceStatus.ACCEPTED
    # Flagged, but NOT rejected/removed — the safeguard against
    # collapsing legitimately distinct scenarios (spec sec. 13).
    assert governed["TC-P-02"].governance_status == GovernanceStatus.POSSIBLE_DUPLICATE


# ---------------------------------------------------------------------------
# Coverage (spec sec. 17 items 17-19 / spec sec. 10)
# ---------------------------------------------------------------------------

def test_coverage_is_calculated_deterministically(kb):
    accepted = govern_batch([_tc(testcase_id="TC-COV-01", requirement_ids=["REQ-REG-01"])], kb)
    coverage = calculate_coverage(kb, accepted, applicable_requirement_ids={"REQ-REG-01", "REQ-REG-02"})
    assert coverage["coverage_percentage"] == 50.0
    assert coverage["covered_requirements"] == ["REQ-REG-01"]


def test_uncovered_requirements_are_reported(kb):
    accepted = govern_batch([_tc(testcase_id="TC-COV-02", requirement_ids=["REQ-REG-01"])], kb)
    coverage = calculate_coverage(kb, accepted, applicable_requirement_ids={"REQ-REG-01", "REQ-REG-02"})
    assert coverage["uncovered_requirements"] == ["REQ-REG-02"]


def test_invalid_or_untraceable_ids_never_inflate_coverage(kb):
    from testcases.schema import GovernedTestcase

    # Force-construct an ACCEPTED-status record for an out-of-universe ID
    # (bypassing govern_testcase, which would never actually produce this)
    # to prove calculate_coverage's own defensive filter holds even if a
    # status were ever assigned incorrectly upstream.
    forced = GovernedTestcase(_tc(requirement_ids=["REQ-NOT-IN-UNIVERSE"]), GovernanceStatus.ACCEPTED, [])
    coverage = calculate_coverage(kb, [forced], applicable_requirement_ids={"REQ-REG-01"})
    assert coverage["covered_requirements"] == []
    assert coverage["coverage_percentage"] == 0.0


# ---------------------------------------------------------------------------
# Attribution (spec sec. 17 item 20 / spec sec. 14)
# ---------------------------------------------------------------------------

def test_accepted_testcase_preserves_source_attribution(kb, stub):
    result = generate_for_requirement(kb, "REQ-REG-01", stub)
    tc = result.testcases[0]
    assert tc.source_attribution
    attribution = tc.source_attribution[0]
    assert attribution["requirement_id"] == "REQ-REG-01"
    assert attribution["source_document"] == "requirements/MVP2_SRS_v1.0_APPROVED.md"
    assert attribution["source_version"] == "1.0"
    assert attribution["chunk_id"]


# ---------------------------------------------------------------------------
# External LLM dependency (task sec. 19)
# ---------------------------------------------------------------------------

def test_openai_backend_fails_fast_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMUnavailableError):
        OpenAILLMClient()


# ---------------------------------------------------------------------------
# End-to-end pipeline integration
# ---------------------------------------------------------------------------

def test_full_pipeline_produces_a_well_formed_governed_result(kb, stub):
    report = run_cp_mvp2_03(kb, stub, requirement_ids=["REQ-REG-01", "REQ-CART-03", "REQ-WISH-02"])
    assert report["duplicate_testcase_id_check"]["passed"]
    assert report["coverage"]["coverage_percentage"] == 100.0
    assert report["unsupported_requirements"] == []
    assert set(report["by_status"]) <= {
        GovernanceStatus.ACCEPTED,
        GovernanceStatus.QUARANTINED,
        GovernanceStatus.REJECTED,
        GovernanceStatus.DUPLICATE,
        GovernanceStatus.POSSIBLE_DUPLICATE,
    }
    assert report["generator"] == "stub-deterministic-v1"
