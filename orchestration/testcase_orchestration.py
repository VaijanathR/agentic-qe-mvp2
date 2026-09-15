"""
Agentic QE Orchestration -- Testcase Selection / Generation (governing
instruction sec. 17, 18).

Selection-first: reuses whichever real, governed testcase corpus already
covers the requirement (CP-MVP2-03 persisted corpus, then Enhancement-02's
real corpus). Generation only happens when genuinely nothing exists yet,
via the frozen, unmodified CP-MVP2-03 pipeline
(`testcases.pipeline.run_cp_mvp2_03`), defaulting to `StubLLMClient` (a
real, deterministic, disclosed, non-fabricating reasoning stand-in --
never a fake/mocked production-path response, per sec. 40) unless the
caller explicitly passes a real LLM client. Generated testcases are
persisted through the same, unmodified `testcases.persist` module CP-03
already uses.

Testcase Quality Gate states (sec. 18) are computed deterministically from
real signals already available: governance_status, whether real
automation exists for the testcase (per the requirement coverage
matrix), and whether at least one real execution log exists for it.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.client import LLMClient, StubLLMClient
from orchestration.enh02_adapter import governed_testcases_for_requirement as enh02_governed_testcases
from orchestration.testcase_loader import load_governed_testcases_for_requirement as cp03_governed_testcases
from reporting.requirement_coverage import REQUIREMENT_COVERAGE
from testcases.persist import persist_batch
from testcases.pipeline import run_cp_mvp2_03
from testcases.schema import GovernanceStatus


class QualityGateState:
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    READY = "READY"
    AUTOMATABLE = "AUTOMATABLE"
    BLOCKED = "BLOCKED"
    EXECUTED = "EXECUTED"


def _quality_gate_state(testcase_id: str, governance_status: str) -> str:
    if governance_status in (GovernanceStatus.REJECTED, GovernanceStatus.QUARANTINED):
        return QualityGateState.BLOCKED
    if governance_status == GovernanceStatus.DUPLICATE:
        return QualityGateState.REVIEW_REQUIRED

    coverage = next((r for r in REQUIREMENT_COVERAGE if testcase_id in r.testcase_ids), None)
    if coverage and coverage.execution_ids:
        return QualityGateState.EXECUTED
    if coverage and coverage.automation_ids:
        return QualityGateState.AUTOMATABLE
    return QualityGateState.READY


def select_or_generate(
    requirement_id: str,
    kb: Optional[KnowledgeBase] = None,
    llm: Optional[LLMClient] = None,
    scenario_types: Optional[List[str]] = None,
) -> Dict:
    kb = kb or KnowledgeBase.load()

    existing = cp03_governed_testcases(requirement_id)
    corpus_source = "CP-MVP2-03 persisted corpus"
    if not existing:
        existing = enh02_governed_testcases(requirement_id)
        corpus_source = "Enhancement-02 real testcase corpus (adapted)"

    if existing:
        return {
            "requirement_id": requirement_id,
            "mode": "REUSE",
            "corpus_source": corpus_source,
            "testcases": [
                {
                    "testcase_id": g.testcase.testcase_id,
                    "governance_status": g.governance_status,
                    "quality_gate_state": _quality_gate_state(g.testcase.testcase_id, g.governance_status),
                }
                for g in existing
            ],
            "generated": None,
        }

    llm = llm or StubLLMClient()
    report = run_cp_mvp2_03(kb, llm, requirement_ids=[requirement_id], scenario_types=scenario_types)
    accepted = [g for g in report["governed_testcases"] if g["governance_status"] == GovernanceStatus.ACCEPTED]

    persisted = []
    if accepted:
        from testcases.schema import GovernedTestcase, Testcase

        tc_fields = set(Testcase.__dataclass_fields__.keys())
        reconstructed = [
            GovernedTestcase(
                testcase=Testcase(**{k: v for k, v in g.items() if k in tc_fields}),
                governance_status=g["governance_status"],
                reasons=g["reasons"],
            )
            for g in accepted
        ]
        persisted = persist_batch(reconstructed, generator=llm.model_name, batch_id=f"ORCH-GEN-{requirement_id}")

    return {
        "requirement_id": requirement_id,
        "mode": "GENERATE",
        "corpus_source": "newly generated via CP-MVP2-03 pipeline",
        "generator": llm.model_name,
        "testcases": [
            {
                "testcase_id": g["testcase_id"],
                "governance_status": g["governance_status"],
                "quality_gate_state": _quality_gate_state(g["testcase_id"], g["governance_status"]),
            }
            for g in report["governed_testcases"]
        ],
        "generated": report,
        "persisted": persisted,
    }
