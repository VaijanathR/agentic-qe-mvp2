"""
CP-MVP2-02 focused tests — Knowledge Base + RAG.

These tests exercise the deterministic ingestion, retrieval, and
governance-validation code under knowledge/lib/. No LLM call is made
anywhere in this file, and no test decides pass/fail by asking an LLM —
every assertion is a plain equality/membership check, per governance
rule "Validation must be deterministic."
"""
import pytest

from knowledge.lib.retrieval import KnowledgeBase
from knowledge.lib.schema import ApprovalStatus, EvidenceStrength
from knowledge.lib import validate as v


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


def test_knowledge_base_loads_both_documents(kb):
    assert "approved_srs" in kb.manifests
    assert "draft_srs" in kb.manifests
    assert len(kb.chunks) > 0


def test_no_source_drift(kb):
    assert kb.check_drift() == []


@pytest.mark.parametrize("check_fn", v.ALL_CHECKS, ids=lambda f: f.__name__)
def test_governance_check(kb, check_fn):
    result = check_fn(kb)
    assert result["passed"], f"{result['check']} failed: {result['detail']}"


@pytest.mark.parametrize("spec", v.GOLDEN_QUERIES, ids=lambda s: s["query"])
def test_golden_query(kb, spec):
    rows = v.run_golden_queries(kb)
    row = next(r for r in rows if r["query"] == spec["query"])
    assert row["passed"], f"golden query failed: {row}"


def test_approved_requirement_always_outranks_draft(kb):
    hits = kb.by_id("REQ-REG-01")
    assert hits[0]["source_type"] == "approved_srs"
    assert hits[0]["approval_status"] == ApprovalStatus.APPROVED
    assert any(h["source_type"] == "draft_srs" for h in hits), "draft copy must still exist, just outranked"


def test_parked_item_never_reports_as_approved(kb):
    # The canonical chunk that OWNS each ID (open_question for *-OQ-* IDs,
    # negative_case for NEG-09) must be PARKED. Other approved content (a
    # business rule, a journey, a section preamble) may legitimately CITE a
    # parked ID for context — e.g. BR-08 ("wishlist availability is
    # product-specific; WISH-OQ-01 parked for the exact rule") is itself an
    # approved statement that references, but does not resolve, WISH-OQ-01.
    # That cross-reference is intentional traceability, not a governance
    # leak — the leak this test actually guards against is the canonical
    # record itself flipping to APPROVED.
    for pid in ["WISH-OQ-01", "WISH-OQ-02", "CFG-OQ-01", "CART-OQ-01", "NEG-09"]:
        hits = [h for h in kb.by_id(pid) if h["source_type"] == "approved_srs"]
        assert hits, f"{pid} should exist in the approved SRS knowledge base"
        canonical = [h for h in hits if h["content_type"] in ("open_question", "negative_case")]
        assert canonical, f"{pid} should have a canonical open_question/negative_case chunk"
        assert all(h["approval_status"] == ApprovalStatus.PARKED for h in canonical), pid


def test_gco03_is_approved_scope_but_inference_evidence(kb):
    hits = [h for h in kb.by_id("REQ-GCO-03") if h["source_type"] == "approved_srs"]
    assert hits
    assert hits[0]["approval_status"] == ApprovalStatus.APPROVED
    assert hits[0]["evidence_strength"] == EvidenceStrength.AGENT_INFERENCE


def test_historical_discovery_not_in_queryable_corpus(kb):
    assert not any(c["source_type"] == "historical_discovery" for c in kb.chunks)


def test_run_all_report_is_fully_green():
    report = v.run_all()
    assert report["all_checks_passed"]
    assert report["all_golden_passed"]
