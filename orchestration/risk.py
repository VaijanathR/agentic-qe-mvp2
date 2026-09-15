"""
Agentic QE Orchestration -- Risk Assessment (governing instruction
sec. 15).

Reuses CR-001's real, deterministic RBTP (Risk-Based Test Prioritization)
pipeline unmodified (`rbtp.pipeline.run_rbtp_batch`), always in
deterministic-only mode (`llm=None`, per sec. 55 "avoid unnecessary LLM
calls" -- risk factors are all evidence-derived, never model-guessed).
Governed testcases are sourced from whichever real corpus already covers
the requirement: CP-MVP2-03's persisted corpus first, Enhancement-02's
real corpus (via `orchestration.enh02_adapter`) as the real fallback that
covers this project's actual majority of requirements.

`RiskLevel.UNKNOWN` (rbtp/schema.py, reused unmodified) is the honest
value whenever this project has no evidence source for a factor --
never silently upgraded to a guessed HIGH/MEDIUM/LOW. This module labels
each RBTP dimension with the governing instruction sec. 15 provenance
vocabulary (OBSERVED/CALCULATED/HISTORICAL/INFERRED/UNKNOWN) based on
`rbtp.evidence`'s own real, disclosed sourcing rules.
"""
from __future__ import annotations

from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from orchestration.enh02_adapter import governed_testcases_for_requirement as enh02_governed_testcases
from orchestration.testcase_loader import load_governed_testcases_for_requirement as cp03_governed_testcases
from rbtp.pipeline import run_rbtp_batch
from rbtp.schema import RiskLevel

#: rbtp/generate.py::_derive_priority's own disclosed rule (docstring,
#: reused verbatim as documentation here, never re-implemented): only
#: business_criticality, security_impact, and customer_impact are
#: evidence-backed in this project today; the other four RISK_FACTOR_FIELDS
#: are always RiskLevel.UNKNOWN by disclosed necessity.
_OBSERVED_DIMENSIONS = {"business_criticality", "security_impact", "customer_impact"}
_ALWAYS_UNKNOWN_DIMENSIONS = {"risk_likelihood", "change_impact", "defect_history", "dependency_impact"}


def _provenance_label(dimension: str, value: str) -> str:
    if value == RiskLevel.UNKNOWN:
        return "UNKNOWN"
    if dimension in _OBSERVED_DIMENSIONS:
        return "OBSERVED"
    return "UNKNOWN"


def assess(requirement_id: str, kb: Optional[KnowledgeBase] = None) -> Dict:
    kb = kb or KnowledgeBase.load()

    governed = cp03_governed_testcases(requirement_id)
    corpus_source = "CP-MVP2-03 persisted corpus"
    if not governed:
        governed = enh02_governed_testcases(requirement_id)
        corpus_source = "Enhancement-02 real testcase corpus (adapted)"

    if not governed:
        return {
            "requirement_id": requirement_id,
            "corpus_source": None,
            "records": [],
            "provenance": {},
            "note": "No real, governed testcase exists yet for this requirement in either real corpus -- "
                    "risk cannot be assessed from evidence that does not exist. Run Test Strategy / "
                    "Testcase orchestration first.",
        }

    result = run_rbtp_batch(kb, governed, llm=None, batch_id=f"ORCH-RISK-{requirement_id}")

    provenance: Dict[str, Dict[str, str]] = {}
    for rec in result["governed_records"]:
        provenance[rec["rbtp_id"]] = {
            dim: _provenance_label(dim, rec[dim])
            for dim in ("business_criticality", "risk_likelihood", "change_impact", "defect_history",
                        "dependency_impact", "security_impact", "customer_impact")
        }

    return {
        "requirement_id": requirement_id,
        "corpus_source": corpus_source,
        "records": result["governed_records"],
        "by_status": result["by_status"],
        "provenance": provenance,
        "persisted": result["persisted"],
    }
