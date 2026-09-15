"""
Agentic QE Orchestration -- Requirement Intelligence (governing
instruction sec. 12, 13, 44).

Consolidates, for one requirement ID, the two existing, real sources of
truth rather than re-deriving anything:

  1. `knowledge.lib.retrieval.KnowledgeBase` (CP-MVP2-02's real, governed
     RAG layer) -- requirement text, source, approval status, evidence
     strength, and the exact-ID retrieval mode.
  2. `reporting.requirement_coverage.REQUIREMENT_COVERAGE` (Enhancement-02's
     real, governed 35-requirement coverage matrix) -- disposition,
     testcase/dataset/automation/execution/performance-testcase coverage.

Reuses the established evidence hierarchy (sec. 13):
  1. Approved baseline (the Approved SRS itself)
  2. Direct system evidence (a chunk's evidence_strength field)
  3. Current testing artifact (requirement_coverage.py's own real,
     persisted testcase/execution references)
  4. Historical evidence (superseded/PARKED chunks, surfaced but never
     silently authoritative)
  5. Agent inference (a chunk's evidence_strength explicitly says so --
     e.g. REQ-GCO-03's own historical "AGENT INFERENCE" tag)

Never invents a requirement, a dependency, or a coverage fact -- everything
returned here traces to a real chunk or a real `RequirementCoverageRecord`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase, provenance
from reporting.requirement_coverage import REQUIREMENT_COVERAGE, RequirementCoverageRecord


class RequirementNotFoundError(RuntimeError):
    pass


@dataclass
class RequirementIntelligence:
    requirement_id: str
    requirement_text: Optional[str]
    source: Optional[str]
    version: Optional[str]
    approval_status: Optional[str]
    evidence_strength: Optional[str]
    authority_tier: Optional[int]
    business_capability: str
    disposition: Optional[str]
    testcase_coverage: List[str]
    dataset_coverage: List[str]
    automation_coverage: List[str]
    execution_coverage: List[str]
    performance_relevance: bool
    performance_testcase_coverage: List[str]
    remarks: str
    related_evidence: List[Dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _coverage_record(requirement_id: str) -> Optional[RequirementCoverageRecord]:
    for r in REQUIREMENT_COVERAGE:
        if r.requirement_id == requirement_id:
            return r
    return None


def gather(requirement_id: str, kb: Optional[KnowledgeBase] = None) -> RequirementIntelligence:
    """Real evidence, both dimensions -- raises `RequirementNotFoundError`
    if the requirement exists in neither source (never fabricates a
    requirement that is not real)."""
    kb = kb or KnowledgeBase.load()
    rag_result = kb.query(requirement_id, top_k=10, include_non_approved=True)
    chunks = rag_result["results"]
    coverage = _coverage_record(requirement_id)

    if not chunks and coverage is None:
        raise RequirementNotFoundError(
            f"{requirement_id!r} was found in neither the RAG Knowledge Base nor the "
            "Enhancement-02 requirement coverage matrix -- refusing to fabricate a "
            "requirement that does not exist in either real source."
        )

    primary = chunks[0] if chunks else None
    return RequirementIntelligence(
        requirement_id=requirement_id,
        requirement_text=(primary or {}).get("text"),
        source=(primary or {}).get("source"),
        version=(primary or {}).get("version"),
        approval_status=(primary or {}).get("approval_status"),
        evidence_strength=(primary or {}).get("evidence_strength"),
        authority_tier=(primary or {}).get("authority_tier"),
        business_capability=coverage.category if coverage else "UNKNOWN",
        disposition=coverage.disposition if coverage else None,
        testcase_coverage=list(coverage.testcase_ids) if coverage else [],
        dataset_coverage=list(coverage.dataset_ids) if coverage else [],
        automation_coverage=list(coverage.automation_ids) if coverage else [],
        execution_coverage=list(coverage.execution_ids) if coverage else [],
        performance_relevance=bool(coverage and coverage.performance_testcase_ids),
        performance_testcase_coverage=list(coverage.performance_testcase_ids) if coverage else [],
        remarks=coverage.remarks if coverage else "",
        related_evidence=[provenance(c) for c in chunks],
    )
