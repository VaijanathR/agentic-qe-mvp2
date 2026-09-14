"""
CP-MVP2-CR-001 Batch 1 — RBTP record assembly.

Every risk-factor VALUE is computed by deterministic code
(`rbtp/evidence.py`) or explicitly set to `RiskLevel.UNKNOWN` where no
evidence source exists in this project. An optional LLM
(`llm/rbtp_client.py::RBTPLLMClient`) may append only a short narrative
elaboration to the already-final rationale string — it is never given a
surface to set a factor, priority, or execution recommendation, and
nothing it returns can change those three things (per CR-001 sec. 20:
"the LLM must never silently override deterministic governance").
"""
from __future__ import annotations

import datetime
from typing import Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.rbtp_client import RBTPLLMClient
from rbtp.evidence import (
    business_criticality_from_testcase,
    customer_impact_from_journey,
    security_impact_from_evidence,
)
from rbtp.schema import ExecutionRecommendation, Priority, RBTPRecord, RiskLevel
from testcases.schema import GovernedTestcase


def _derive_priority(business_criticality: str, security_impact: str, customer_impact: str) -> str:
    """Deterministic, explainable combination of the three factors this
    project can actually evidence today. `risk_likelihood`,
    `change_impact`, `defect_history`, and `dependency_impact` are
    UNKNOWN by disclosed necessity (see `generate_rbtp_for_testcase`)
    and are therefore never allowed to silently pull priority down --
    only the three known factors participate."""
    known_high = sum(1 for v in (business_criticality, security_impact, customer_impact) if v == RiskLevel.HIGH)
    if business_criticality == RiskLevel.HIGH and known_high >= 2:
        return Priority.P0
    if known_high >= 1:
        return Priority.P1
    if RiskLevel.MEDIUM in (business_criticality, security_impact, customer_impact):
        return Priority.P2
    return Priority.P3


_RECOMMENDATION_BY_PRIORITY = {
    Priority.P0: ExecutionRecommendation.INCLUDE_IN_SMOKE_AND_REGRESSION,
    Priority.P1: ExecutionRecommendation.INCLUDE_IN_SMOKE_AND_REGRESSION,
    Priority.P2: ExecutionRecommendation.INCLUDE_IN_REGRESSION,
    Priority.P3: ExecutionRecommendation.INCLUDE_IN_FULL_REGRESSION_ONLY,
}


def generate_rbtp_for_testcase(
    kb: KnowledgeBase,
    gtc: GovernedTestcase,
    llm: Optional[RBTPLLMClient] = None,
) -> RBTPRecord:
    requirement_ids = list(gtc.testcase.requirement_ids)

    business_criticality, bc_evidence = business_criticality_from_testcase(gtc)
    security_impact, sec_evidence = security_impact_from_evidence(kb, requirement_ids)
    customer_impact, cust_evidence = customer_impact_from_journey(kb, requirement_ids)

    # No defect-tracking, change-history, or likelihood-modelling data
    # source is integrated anywhere in this project (verified by direct
    # repository inspection during CP-MVP2-CR-001) -- these are UNKNOWN
    # by disclosed necessity, never invented.
    risk_likelihood = RiskLevel.UNKNOWN
    change_impact = RiskLevel.UNKNOWN
    defect_history = RiskLevel.UNKNOWN
    # The Dependency/Reusability Matrix runs AFTER RBTP in this pipeline
    # (CR-001 target architecture sec. 3) -- dependency_impact is
    # therefore UNKNOWN at RBTP-generation time, not fabricated ahead of
    # the stage that actually computes it.
    dependency_impact = RiskLevel.UNKNOWN

    priority = _derive_priority(business_criticality, security_impact, customer_impact)
    execution_recommendation = _RECOMMENDATION_BY_PRIORITY[priority]

    deterministic_rationale = "; ".join([
        f"business_criticality={business_criticality} ({bc_evidence})",
        f"security_impact={security_impact} ({sec_evidence})",
        f"customer_impact={customer_impact} ({cust_evidence})",
        f"risk_likelihood={risk_likelihood} (no defect/likelihood data source integrated in MVP2)",
        f"change_impact={change_impact} (no change-history data source integrated in MVP2)",
        f"defect_history={defect_history} (no defect-tracking data source integrated in MVP2)",
        f"dependency_impact={dependency_impact} (Dependency/Reusability Matrix is computed after RBTP in this pipeline)",
        f"priority={priority} (deterministically derived from the known factors above)",
        f"execution_recommendation={execution_recommendation} (fixed mapping from priority)",
    ])

    generation_metadata = {
        "deterministic_rationale": deterministic_rationale,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "evidence_sources": {
            "business_criticality": bc_evidence,
            "security_impact": sec_evidence,
            "customer_impact": cust_evidence,
        },
    }

    risk_rationale = deterministic_rationale
    if llm is not None:
        narrative = llm.propose_rationale_elaboration({
            "testcase_id": gtc.testcase.testcase_id,
            "requirement_ids": requirement_ids,
            "deterministic_rationale": deterministic_rationale,
        })
        generation_metadata["generator"] = llm.model_name
        if narrative:
            risk_rationale = (
                f"{deterministic_rationale} | LLM narrative elaboration "
                f"(non-authoritative, does not affect factor values or "
                f"priority): {narrative}"
            )
            generation_metadata["llm_narrative_elaboration"] = narrative
    else:
        generation_metadata["generator"] = "deterministic-only (no LLM narrative requested)"

    return RBTPRecord(
        rbtp_id=f"RBTP-{gtc.testcase.testcase_id}",
        testcase_id=gtc.testcase.testcase_id,
        requirement_ids=requirement_ids,
        business_criticality=business_criticality,
        risk_likelihood=risk_likelihood,
        change_impact=change_impact,
        defect_history=defect_history,
        dependency_impact=dependency_impact,
        security_impact=security_impact,
        customer_impact=customer_impact,
        priority=priority,
        execution_recommendation=execution_recommendation,
        risk_rationale=risk_rationale,
        source_attribution=list(gtc.testcase.source_attribution),
        generation_metadata=generation_metadata,
    )
