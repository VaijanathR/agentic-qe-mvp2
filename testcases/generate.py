"""
CP-MVP2-03 — governed requirement retrieval + LLM testcase generation.

Implements the flow from the frozen specification (sec. 3):
    APPROVED SRS -> MVP2 KNOWLEDGE BASE -> GOVERNED RAG RETRIEVAL ->
    RETRIEVED REQUIREMENT CONTEXT -> LLM -> STRUCTURED TESTCASE OUTPUT

Everything an LLMClient is allowed to decide is narrative/reasoning only
(title, preconditions, test_steps, expected_result, priority — see
llm/client.py). This module is what assembles the rest of the record
deterministically:
  - testcase_id, requirement_ids, journey_id: derived from the retrieval
    result, never trusted from the model.
  - source_attribution: built exclusively from the KnowledgeBase chunk(s)
    actually retrieved for this requirement — never fabricated.
  - generation_metadata: records which LLMClient backend was used, when,
    and what scenario types were authorized, so evidence is always
    auditable.

Retrieval never bypasses the governed KB/RAG layer: every requirement
context is built through KnowledgeBase.by_id(), the same exact-ID
governed lookup CP-MVP2-02 already validated (authority-tier resort,
draft/parked exclusion from "current" results, etc.). This module adds no
independent scraping or invention on top of it.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from knowledge.lib.schema import ApprovalStatus
from llm.client import LLMClient
from testcases.schema import ALL_SCENARIO_TYPES, Priority, Testcase

DEFAULT_SCENARIO_TYPES = sorted(ALL_SCENARIO_TYPES)


@dataclass
class GenerationResult:
    requirement_id: str
    testcases: List[Testcase] = field(default_factory=list)
    unsupported: Optional[Dict] = None

    def to_dict(self) -> dict:
        return {
            "requirement_id": self.requirement_id,
            "testcases": [tc.to_dict() for tc in self.testcases],
            "unsupported": self.unsupported,
        }


def _journey_negative_case_evidence(kb: KnowledgeBase, journey_ids: List[str]) -> List[dict]:
    """Deterministically gathers APPROVED negative_case chunks that belong
    to the same journey(s) as the requirement being generated for, via the
    journey_index chunk's own membership list (the same membership CP-
    MVP2-02's check_journey_traceability already validates as non-
    fabricated). This is the only mechanism used to justify an EXCEPTIONAL
    scenario — never free-text similarity, never invention."""
    out: List[dict] = []
    seen_ids = set()
    for jid in journey_ids:
        idx_chunks = [
            c for c in kb.chunks
            if c["content_type"] == "journey_index" and jid in c.get("journey_id", []) and c["source_type"] == "approved_srs"
        ]
        if not idx_chunks:
            continue
        neg_ids = [m for m in idx_chunks[0].get("requirement_id", []) if m.startswith("NEG-")]
        for nid in neg_ids:
            for hit in kb.by_id(nid):
                if hit["content_type"] == "negative_case" and hit["source_type"] == "approved_srs" and hit["chunk_id"] not in seen_ids:
                    out.append(hit)
                    seen_ids.add(hit["chunk_id"])
    return out


def requirement_context(kb: KnowledgeBase, requirement_id: str) -> Optional[Dict]:
    """Builds the governed requirement_context for one requirement ID, or
    None if the ID does not resolve to an APPROVED requirement chunk in
    the governed KB (draft-only, parked, open-question, or unknown IDs all
    correctly return None here — they are handled as UNSUPPORTED by the
    caller, never silently treated as approved)."""
    hits = kb.by_id(requirement_id)
    approved_hits = [
        h for h in hits
        if h["content_type"] == "requirement" and h["source_type"] == "approved_srs" and h["approval_status"] == ApprovalStatus.APPROVED
    ]
    if not approved_hits:
        return None
    primary = approved_hits[0]

    business_rule_evidence = [
        h for h in hits
        if h["content_type"] == "business_rule" and h["source_type"] == "approved_srs" and h["approval_status"] == ApprovalStatus.APPROVED
    ]
    negative_case_evidence = _journey_negative_case_evidence(kb, primary.get("journey_id", []))

    evidence_chunks = [primary] + business_rule_evidence + negative_case_evidence
    return {
        "requirement_id": requirement_id,
        "requirement_text": primary["text"],
        "source_document": primary["source"],
        "source_version": primary["version"],
        "approval_status": primary["approval_status"],
        "journey_id": primary.get("journey_id", []),
        "evidence": [
            {
                "chunk_id": c["chunk_id"],
                "source": c["source"],
                "section": c["section"],
                "content_type": c["content_type"],
                "text": c["text"],
                "approval_status": c["approval_status"],
                "source_type": c["source_type"],
            }
            for c in evidence_chunks
        ],
    }


def generate_for_requirement(
    kb: KnowledgeBase,
    requirement_id: str,
    llm: LLMClient,
    scenario_types: Optional[List[str]] = None,
) -> GenerationResult:
    """Generates candidate testcases for one requirement. Returns
    testcases=[] and a populated `unsupported` dict whenever there is
    insufficient governed evidence — this function never fabricates a
    testcase to make a requirement look covered."""
    requested_types = [s for s in (scenario_types or DEFAULT_SCENARIO_TYPES) if s in ALL_SCENARIO_TYPES]

    context = requirement_context(kb, requirement_id)
    if context is None:
        return GenerationResult(
            requirement_id=requirement_id,
            testcases=[],
            unsupported={
                "requirement_id": requirement_id,
                "reason": "NO_APPROVED_REQUIREMENT_EVIDENCE",
                "detail": (
                    f"{requirement_id} did not resolve to an APPROVED requirement chunk "
                    "via the governed MVP2 Knowledge Base/RAG layer (unknown ID, or the "
                    "canonical record is draft/parked/open-question, not an approved "
                    "requirement)."
                ),
            },
        )

    raw_candidates = llm.propose_testcases(context, requested_types)

    testcases: List[Testcase] = []
    primary_chunk_id = context["evidence"][0]["chunk_id"] if context["evidence"] else None
    for seq, candidate in enumerate(raw_candidates, start=1):
        scenario_type = candidate.get("scenario_type")
        if scenario_type not in requested_types:
            # Deterministic guard: a candidate outside the authorized
            # scenario types is dropped regardless of what the LLM
            # returned. Governance decides acceptance, not the model.
            continue
        testcases.append(
            Testcase(
                testcase_id=f"TC-{requirement_id}-{seq:02d}",
                title=str(candidate.get("title", "")).strip(),
                requirement_ids=[requirement_id],
                scenario_type=scenario_type,
                preconditions=list(candidate.get("preconditions", [])),
                test_steps=list(candidate.get("test_steps", [])),
                expected_result=str(candidate.get("expected_result", "")).strip(),
                priority=candidate.get("priority", Priority.MEDIUM),
                journey_id=(context["journey_id"][0] if context["journey_id"] else None),
                test_data_reference=candidate.get("test_data_reference"),
                source_attribution=[
                    {
                        "requirement_id": requirement_id,
                        "source_document": context["source_document"],
                        "source_version": context["source_version"],
                        "chunk_id": primary_chunk_id,
                    }
                ],
                generation_metadata={
                    "generator": llm.model_name,
                    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "retrieval_mode": "exact_id",
                    "scenario_types_requested": requested_types,
                },
            )
        )

    unsupported = None
    if not testcases:
        unsupported = {
            "requirement_id": requirement_id,
            "reason": "NO_JUSTIFIED_SCENARIO",
            "detail": (
                f"Governed evidence for {requirement_id} did not justify any of the "
                f"requested scenario types {requested_types}."
            ),
        }
    return GenerationResult(requirement_id=requirement_id, testcases=testcases, unsupported=unsupported)


def generate_for_requirements(
    kb: KnowledgeBase,
    requirement_ids: List[str],
    llm: LLMClient,
    scenario_types: Optional[List[str]] = None,
) -> List[GenerationResult]:
    return [generate_for_requirement(kb, rid, llm, scenario_types) for rid in requirement_ids]
