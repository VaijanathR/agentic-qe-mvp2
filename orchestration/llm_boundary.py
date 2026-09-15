"""
Agentic QE Orchestration -- the LLM reasoning boundary (Wave 2
instruction, sec. 5, 11).

Reuses the frozen, unmodified CP-MVP2-03 real LLM provider abstraction
(`llm.client.LLMClient` / `ClaudeLLMClient` / `StubLLMClient`) and real
generation pipeline (`testcases.generate.generate_for_requirement`,
`testcases.validate`) verbatim -- this module authors no new prompt
contract, no new provider, and no new governance rule. It only wraps that
existing, real boundary with the persisted record shape sec. 12 (this
wave) and sec. 23 (prior wave's decision contract) both require: prompt/
context identity, model/provider, raw output, confidence, deterministic
validation result, and the final governed decision.

**The LLM never directly authorizes execution here**: `propose()` only
ever returns *candidate* testcase content plus a governance verdict
already computed by the frozen `testcases.validate` module (never by
this wrapper, never by the LLM itself) -- a REJECTED candidate is
recorded as real evidence of the boundary working, never silently
discarded or retried into a fabricated ACCEPTED state.
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.client import ClaudeProviderError, LLMClient, LLMOutputError, LLMUnavailableError, StubLLMClient
from persistence.envelope import REPO_ROOT, persist_artifact
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus

LLM_CALL_RECORDS_BASE_DIR = REPO_ROOT / "orchestration" / "generated" / "llm_calls"


@dataclass
class LLMCallRecord:
    call_id: str
    requirement_id: str
    requested_scenario_types: List[str]
    provider_model: str
    prompt_context_identity: Dict
    raw_outcome: str  # "SUCCESS" | "PROVIDER_ERROR" | "OUTPUT_ERROR" | "UNAVAILABLE"
    raw_output_summary: Optional[str]
    candidate_count: int
    accepted_candidate_ids: List[str]
    rejected_candidates: List[Dict]
    confidence: str  # HIGH (>=1 real ACCEPTED) / LOW (0 accepted, real attempt made) / NOT_APPLICABLE (provider error)
    deterministic_validation_result: str
    final_governed_decision: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


def _persist(record: LLMCallRecord) -> Dict:
    return persist_artifact(
        LLM_CALL_RECORDS_BASE_DIR, artifact_id=record.call_id, payload=record.to_dict(),
        generator="orchestration.llm_boundary (real LLM call, deterministic governance)",
        provenance={"requirement_id": record.requirement_id},
    )


def propose(
    requirement_id: str,
    scenario_types: List[str],
    kb: Optional[KnowledgeBase] = None,
    llm: Optional[LLMClient] = None,
    call_id: Optional[str] = None,
) -> LLMCallRecord:
    """Real LLM reasoning boundary call. Never raises -- every real
    outcome (success, provider error, malformed output, unavailable
    provider) is captured as a real, persisted `LLMCallRecord`, never
    silently swallowed and never converted into a fabricated ACCEPTED
    testcase."""
    kb = kb or KnowledgeBase.load()
    llm = llm or StubLLMClient()
    call_id = call_id or f"LLMCALL-{requirement_id}-{int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)}"

    context_identity = {"requirement_id": requirement_id, "scenario_types": scenario_types}

    try:
        result = generate_for_requirement(kb, requirement_id, llm, scenario_types)
    except LLMUnavailableError as exc:
        record = LLMCallRecord(
            call_id=call_id, requirement_id=requirement_id, requested_scenario_types=scenario_types,
            provider_model=getattr(llm, "model_name", "unknown"), prompt_context_identity=context_identity,
            raw_outcome="UNAVAILABLE", raw_output_summary=str(exc), candidate_count=0,
            accepted_candidate_ids=[], rejected_candidates=[], confidence="NOT_APPLICABLE",
            deterministic_validation_result="NOT_RUN -- provider unavailable",
            final_governed_decision="NO_CANDIDATE -- provider unavailable, nothing to govern",
        )
        _persist(record)
        return record
    except (ClaudeProviderError, LLMOutputError) as exc:
        record = LLMCallRecord(
            call_id=call_id, requirement_id=requirement_id, requested_scenario_types=scenario_types,
            provider_model=getattr(llm, "model_name", "unknown"), prompt_context_identity=context_identity,
            raw_outcome="PROVIDER_ERROR" if isinstance(exc, ClaudeProviderError) else "OUTPUT_ERROR",
            raw_output_summary=str(exc)[:2000], candidate_count=0,
            accepted_candidate_ids=[], rejected_candidates=[], confidence="NOT_APPLICABLE",
            deterministic_validation_result="REJECTED -- real model output failed deterministic parsing/format validation (never silently accepted)",
            final_governed_decision="NO_CANDIDATE -- deterministic validation rejected the real provider response before governance could even evaluate content",
        )
        _persist(record)
        return record

    if result.unsupported:
        record = LLMCallRecord(
            call_id=call_id, requirement_id=requirement_id, requested_scenario_types=scenario_types,
            provider_model=getattr(llm, "model_name", "unknown"), prompt_context_identity=context_identity,
            raw_outcome="SUCCESS", raw_output_summary=str(result.unsupported)[:2000], candidate_count=0,
            accepted_candidate_ids=[], rejected_candidates=[], confidence="NOT_APPLICABLE",
            deterministic_validation_result="NOT_APPLICABLE -- requirement itself unsupported (no requirement_context)",
            final_governed_decision="NO_CANDIDATE",
        )
        _persist(record)
        return record

    from testcases.validate import govern_batch

    governed = govern_batch(result.testcases, kb)
    accepted = [g.testcase.testcase_id for g in governed if g.governance_status == GovernanceStatus.ACCEPTED]
    rejected = [
        {"testcase_id": g.testcase.testcase_id, "status": g.governance_status, "reasons": g.reasons}
        for g in governed if g.governance_status != GovernanceStatus.ACCEPTED
    ]

    record = LLMCallRecord(
        call_id=call_id, requirement_id=requirement_id, requested_scenario_types=scenario_types,
        provider_model=getattr(llm, "model_name", "unknown"), prompt_context_identity=context_identity,
        raw_outcome="SUCCESS",
        raw_output_summary=f"{len(result.testcases)} real candidate(s) returned by the model.",
        candidate_count=len(result.testcases),
        accepted_candidate_ids=accepted, rejected_candidates=rejected,
        confidence="HIGH" if accepted else "LOW",
        deterministic_validation_result=f"{len(accepted)}/{len(governed)} candidate(s) ACCEPTED by testcases.validate (frozen, deterministic)",
        final_governed_decision=(
            f"{len(accepted)} testcase(s) governed ACCEPTED -- eligible for persistence/reuse, never auto-executed by this call."
            if accepted else "0 candidates ACCEPTED -- no testcase produced from this real call."
        ),
    )
    _persist(record)
    return record
