"""
CP-MVP2-02 Phase 4 — deterministic validation.

Every function in this module returns a plain dict {"check", "passed",
"detail"} computed from code (set membership, equality, sorting) — never
from an LLM judgment call, per governance rule "Do not use the LLM to
decide whether validation passed. Validation must be deterministic."
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from knowledge.lib.retrieval import KnowledgeBase, ID_RE
from knowledge.lib.schema import ApprovalStatus, EvidenceStrength

REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_SRS_PATH = REPO_ROOT / "requirements" / "MVP2_SRS_v1.0_APPROVED.md"

EXPECTED_JOURNEYS = ["J-01", "J-02", "J-03", "J-04", "J-05"]


def _result(check: str, passed: bool, detail) -> dict:
    return {"check": check, "passed": bool(passed), "detail": detail}


def check_approved_requirement_retrieval(kb: KnowledgeBase) -> dict:
    manifest = kb.manifests["approved_srs"]
    bad = []
    for req_id in manifest["ids"]["requirements"]:
        hits = [c for c in kb.by_id(req_id) if c["content_type"] == "requirement" and c["source_type"] == "approved_srs"]
        if not hits or hits[0]["approval_status"] != ApprovalStatus.APPROVED:
            bad.append(req_id)
    return _result(
        "1. Approved requirement retrieval",
        not bad,
        {"total_requirements": len(manifest["ids"]["requirements"]), "failing_ids": bad},
    )


def check_requirement_id_traceability(kb: KnowledgeBase) -> dict:
    manifest = kb.manifests["approved_srs"]
    expected = set(manifest["ids"]["requirements"])
    found = {
        c["requirement_id"][0]
        for c in kb.chunks
        if c["content_type"] == "requirement" and c["source_type"] == "approved_srs"
    }
    return _result(
        "2. Requirement ID traceability",
        expected == found,
        {"missing_from_kb": sorted(expected - found), "unexpected_in_kb": sorted(found - expected)},
    )


def check_neg_id_traceability(kb: KnowledgeBase) -> dict:
    manifest = kb.manifests["approved_srs"]
    expected = set(manifest["ids"]["negatives"])
    found = {
        c["requirement_id"][0]
        for c in kb.chunks
        if c["content_type"] == "negative_case" and c["source_type"] == "approved_srs"
    }
    return _result(
        "3. NEG ID traceability",
        expected == found,
        {"missing_from_kb": sorted(expected - found), "unexpected_in_kb": sorted(found - expected)},
    )


def check_oq_id_traceability(kb: KnowledgeBase) -> dict:
    manifest = kb.manifests["approved_srs"]
    expected = set(manifest["ids"]["open_questions"])
    found = {
        c["requirement_id"][0]
        for c in kb.chunks
        if c["content_type"] == "open_question" and c["source_type"] == "approved_srs"
    }
    return _result(
        "4. OQ ID traceability",
        expected == found,
        {"missing_from_kb": sorted(expected - found), "unexpected_in_kb": sorted(found - expected)},
    )


def check_journey_traceability(kb: KnowledgeBase) -> dict:
    manifest = kb.manifests["approved_srs"]
    all_valid_ids = set(manifest["ids"]["requirements"]) | set(manifest["ids"]["negatives"])
    problems = {}
    for jid in EXPECTED_JOURNEYS:
        journey_chunks = [c for c in kb.chunks if c["content_type"] == "journey" and jid in c["journey_id"] and c["source_type"] == "approved_srs"]
        index_chunks = [c for c in kb.chunks if c["content_type"] == "journey_index" and jid in c["journey_id"] and c["source_type"] == "approved_srs"]
        if not journey_chunks:
            problems.setdefault(jid, []).append("MISSING_JOURNEY_CHUNK")
        if not index_chunks:
            problems.setdefault(jid, []).append("MISSING_JOURNEY_INDEX_CHUNK")
            continue
        members = set(index_chunks[0]["requirement_id"])
        if not members:
            problems.setdefault(jid, []).append("EMPTY_MEMBERSHIP")
        fabricated = members - all_valid_ids
        if fabricated:
            problems.setdefault(jid, []).append(f"FABRICATED_MEMBERS:{sorted(fabricated)}")
    return _result("5. Journey traceability", not problems, problems)


def check_parked_item_behavior(kb: KnowledgeBase) -> dict:
    # A parked ID's CANONICAL chunk (open_question / negative_case — the
    # chunk that owns that ID as its own identity) must never be APPROVED.
    # Other approved content is allowed to cite a parked ID for context
    # (e.g. BR-08 cites WISH-OQ-01) without that being a governance leak —
    # the leak this guards against is the canonical record itself flipping.
    known_parked = ["WISH-OQ-01", "WISH-OQ-02", "CFG-OQ-01", "NEG-09", "NFR-OQ-THRESHOLDS", "CART-OQ-01"]
    bad = []
    for pid in known_parked:
        hits = kb.by_id(pid)
        approved_srs_hits = [h for h in hits if h["source_type"] == "approved_srs"]
        canonical = [h for h in approved_srs_hits if h["content_type"] in ("open_question", "negative_case")]
        if not canonical:
            bad.append({pid: "NO_CANONICAL_CHUNK_FOUND"})
            continue
        if any(h["approval_status"] == ApprovalStatus.APPROVED for h in canonical):
            bad.append({pid: "CANONICAL_CHUNK_SILENTLY_APPROVED"})

    gift_card_query = kb.query("Can we test Gift Card wishlist behavior?", top_k=6)
    has_parked_signal = any(c["approval_status"] == ApprovalStatus.PARKED for c in gift_card_query["results"])
    if not has_parked_signal:
        bad.append({"gift_card_query": "NO_PARKED_SIGNAL_SURFACED"})

    return _result("6. Parked-item behavior", not bad, {"failures": bad})


def check_approved_vs_draft_conflict(kb: KnowledgeBase) -> dict:
    approved_ids = set(kb.manifests["approved_srs"]["ids"]["requirements"])
    draft_ids = set(kb.manifests.get("draft_srs", {}).get("ids", {}).get("requirements", []))
    shared = approved_ids & draft_ids
    bad = []
    for rid in shared:
        hits = kb.by_id(rid)
        if not hits:
            bad.append({rid: "NOT_FOUND"})
            continue
        top = hits[0]
        if not (top["source_type"] == "approved_srs" and top["approval_status"] == ApprovalStatus.APPROVED):
            bad.append({rid: f"TOP_RESULT_WAS_{top['source_type']}/{top['approval_status']}"})
        draft_present = any(h["source_type"] == "draft_srs" for h in hits)
        if not draft_present:
            bad.append({rid: "DRAFT_VERSION_MISSING_NOT_JUST_OUTRANKED"})
    return _result(
        "7. Approved-vs-Draft conflict",
        not bad,
        {"shared_requirement_count": len(shared), "failures": bad},
    )


def check_historical_vs_approved_conflict(kb: KnowledgeBase) -> dict:
    """Historical discovery evidence (Phase 2) is intentionally persisted as
    raw provenance files (see knowledge/historical/discovery_evidence/) and
    is NOT parsed into governed, retrievable chunks. This check validates
    the resulting guarantee directly: raw historical evidence structurally
    cannot enter the ranked/queryable corpus at all, so it can never
    outrank or silently conflict with the Approved SRS at retrieval time —
    a stronger guarantee than "ranks lower"."""
    historical_chunks_in_corpus = [c for c in kb.chunks if c["source_type"] == "historical_discovery"]
    return _result(
        "8. Historical-vs-Approved conflict",
        len(historical_chunks_in_corpus) == 0,
        {
            "historical_chunks_in_retrievable_corpus": len(historical_chunks_in_corpus),
            "note": "Historical discovery evidence is tracked only via "
            "knowledge/historical/discovery_evidence/MANIFEST.json (file hashes/provenance), "
            "never loaded into the queryable KnowledgeBase — so it cannot conflict with "
            "the Approved SRS at retrieval time by construction.",
        },
    )


def check_version_supersession(kb: KnowledgeBase) -> dict:
    bad = []
    for c in kb.chunks:
        if c["source_type"] == "approved_srs" and c["version"] != "1.0":
            bad.append({c["chunk_id"]: f"unexpected version {c['version']}"})
        if c["source_type"] == "draft_srs" and c["version"] != "0.1":
            bad.append({c["chunk_id"]: f"unexpected version {c['version']}"})
        if c.get("superseded_by"):
            bad.append({c["chunk_id"]: "unexpectedly marked superseded (no v1.1 exists yet)"})

    # Mechanism test (synthetic — no real v1.1 exists yet to exercise this
    # against; this proves the filter itself works, not that it has been
    # used on real data).
    synthetic_kb = KnowledgeBase()
    synthetic_kb.chunks = [
        {
            "chunk_id": "TEST__REQ-X",
            "source": "test", "source_type": "approved_srs", "section": "test", "section_id": "0",
            "content_type": "requirement", "text": "synthetic", "requirement_id": ["REQ-X"],
            "journey_id": [], "classification": "OBSERVED", "approval_status": ApprovalStatus.APPROVED,
            "status_raw": "", "evidence_strength": EvidenceStrength.DIRECT_SYSTEM_EVIDENCE, "evidence_raw": "",
            "version": "1.0", "baseline_date": "2026-09-11", "scope": "in_scope", "checkpoint": "CP-MVP2-01",
            "actor": [], "source_hash": "x", "superseded_by": "TEST__REQ-X-v1.1", "supersedes": None,
            "authority_tier": 1,
        }
    ]
    current_only = synthetic_kb.by_id("REQ-X", include_non_current=False)
    with_history = synthetic_kb.by_id("REQ-X", include_non_current=True)
    mechanism_ok = (len(current_only) == 0) and (len(with_history) == 1)

    return _result(
        "9. Version/supersession behavior",
        (not bad) and mechanism_ok,
        {
            "real_data_issues": bad,
            "synthetic_mechanism_test_passed": mechanism_ok,
            "note": "No real v1.1 exists yet — supersession is exercised here only as a "
            "synthetic mechanism test, disclosed as such rather than presented as "
            "real-data proof.",
        },
    )


def check_no_fabricated_ids(kb: KnowledgeBase) -> dict:
    raw_text = APPROVED_SRS_PATH.read_text(encoding="utf-8")
    literal_ids = set(m.group(1).upper() for m in ID_RE.finditer(raw_text))
    used_ids = set()
    for c in kb.chunks:
        if c["source_type"] != "approved_srs":
            continue
        used_ids |= {i.upper() for i in c.get("requirement_id", [])}
        used_ids |= {i.upper() for i in c.get("journey_id", [])}
    fabricated = {i for i in used_ids if i not in literal_ids and not i.startswith("NFR-OQ-THRESHOLDS")}
    return _result(
        "10. No fabricated/unknown requirement IDs",
        not fabricated,
        {"fabricated_ids": sorted(fabricated), "ids_checked": len(used_ids)},
    )


def check_evidence_approval_independence(kb: KnowledgeBase) -> dict:
    approved_inference = [
        c for c in kb.chunks
        if c["source_type"] == "approved_srs"
        and c["approval_status"] == ApprovalStatus.APPROVED
        and c["evidence_strength"] == EvidenceStrength.AGENT_INFERENCE
    ]
    parked_direct_evidence = [
        c for c in kb.chunks
        if c["source_type"] == "approved_srs"
        and c["approval_status"] == ApprovalStatus.PARKED
        and c["evidence_strength"] == EvidenceStrength.DIRECT_SYSTEM_EVIDENCE
    ]
    ok = bool(approved_inference) and bool(parked_direct_evidence)
    return _result(
        "11. Evidence/approval independence",
        ok,
        {
            "approved_but_inference_evidence": [c["chunk_id"] for c in approved_inference],
            "parked_but_direct_evidence": [c["chunk_id"] for c in parked_direct_evidence],
        },
    )


def check_source_drift(kb: KnowledgeBase) -> dict:
    findings = kb.check_drift()
    return _result("12. Source drift detection", not findings, {"drift_findings": findings})


GOLDEN_QUERIES = [
    {
        "query": "Is wishlist available for all products?",
        "top_k": 8,
        "expect_approved_ids": {"REQ-WISH-01"},
        "expect_parked_signal": True,
        "expected_classification": "APPROVED FACT (scoped) + OPEN QUESTION (catalog-wide rule unknown)",
    },
    {
        "query": "What are the approved requirements for J-01?",
        "top_k": 40,
        "expect_approved_ids": {"REQ-REG-01"},
        "expect_parked_signal": False,
        "expected_classification": "APPROVED FACT — direct enumeration via journey index",
    },
    {
        "query": "Can we test Gift Card wishlist behavior?",
        "top_k": 8,
        "expect_approved_ids": set(),
        "expect_parked_signal": True,
        "expected_classification": "PARKED / OPEN QUESTION",
    },
    {
        "query": "What is the approved performance SLA?",
        "top_k": 8,
        "expect_approved_ids": set(),
        "expect_parked_signal": True,
        "expected_classification": "OPEN QUESTION — scope approved, thresholds not approved",
    },
    {
        "query": "What happens when cart quantity becomes zero?",
        "top_k": 8,
        "expect_approved_ids": {"REQ-CART-03"},
        "expect_parked_signal": False,
        "expected_classification": "APPROVED FACT",
    },
    {
        "query": "Can guest checkout produce an order?",
        "top_k": 8,
        "expect_approved_ids": {"REQ-GCO-03"},
        "expect_parked_signal": False,
        "expected_classification": "APPROVED SCOPE with an explicitly disclosed AGENT_INFERENCE evidence gap",
    },
]


def run_golden_queries(kb: KnowledgeBase) -> List[dict]:
    rows = []
    for spec in GOLDEN_QUERIES:
        r = kb.query(spec["query"], top_k=spec["top_k"])
        result_ids = set()
        for c in r["results"]:
            result_ids |= set(c.get("requirement_id", [])) | set(c.get("journey_id", []))
        has_parked = any(c["approval_status"] == ApprovalStatus.PARKED for c in r["results"])
        passed = spec["expect_approved_ids"].issubset(result_ids) and (has_parked == spec["expect_parked_signal"] or not spec["expect_parked_signal"] and has_parked)
        # expect_parked_signal True -> must have at least one parked chunk;
        # expect_parked_signal False -> parked chunks are tolerated but not required
        if spec["expect_parked_signal"]:
            passed = spec["expect_approved_ids"].issubset(result_ids) and has_parked
        else:
            passed = spec["expect_approved_ids"].issubset(result_ids)
        rows.append(
            {
                "query": spec["query"],
                "passed": passed,
                "mode": r["mode"],
                "expected_classification": spec["expected_classification"],
                "retrieved": [
                    {
                        "chunk_id": c["chunk_id"],
                        "authority_tier": c["authority_tier"],
                        "approval_status": c["approval_status"],
                        "evidence_strength": c["evidence_strength"],
                        "source": c["source"],
                        "section": c["section"],
                    }
                    for c in r["results"]
                ],
            }
        )
    return rows


ALL_CHECKS = [
    check_approved_requirement_retrieval,
    check_requirement_id_traceability,
    check_neg_id_traceability,
    check_oq_id_traceability,
    check_journey_traceability,
    check_parked_item_behavior,
    check_approved_vs_draft_conflict,
    check_historical_vs_approved_conflict,
    check_version_supersession,
    check_no_fabricated_ids,
    check_evidence_approval_independence,
    check_source_drift,
]


def run_all() -> dict:
    kb = KnowledgeBase.load()
    checks = [fn(kb) for fn in ALL_CHECKS]
    golden = run_golden_queries(kb)
    return {
        "checks": checks,
        "all_checks_passed": all(c["passed"] for c in checks),
        "golden_queries": golden,
        "all_golden_passed": all(g["passed"] for g in golden),
    }


if __name__ == "__main__":
    import json

    report = run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nSUMMARY:")
    for c in report["checks"]:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}")
    for g in report["golden_queries"]:
        print(f"  [{'PASS' if g['passed'] else 'FAIL'}] golden: {g['query']}")
    if not (report["all_checks_passed"] and report["all_golden_passed"]):
        raise SystemExit(1)
