"""
CP-MVP2-02 — Knowledge Base + RAG: deterministic metadata schema.

This module defines the fixed vocabulary used to tag every chunk in the
knowledge base. Nothing here is decided by an LLM: source classification,
approval status, and evidence strength are all assigned by deterministic
parsing/normalization code in ingest_srs.py, per CP-MVP2-02 governance
rule #10 ("Keep authority/ranking deterministic; the LLM must never decide
source authority").

approval_status and evidence_strength are intentionally kept as two
separate fields (governance rule #8) — they answer different questions:
  - approval_status: has a human business owner ratified this as a
    requirement? (APPROVED_BASELINED_V1_0 / PARKED_NOT_IN_BASELINE / ...)
  - evidence_strength: how well is the underlying fact observed?
    (DIRECT_SYSTEM_EVIDENCE / AGENT_INFERENCE / ...)
A chunk can be APPROVED with AGENT_INFERENCE evidence (REQ-GCO-03), or
DIRECT_SYSTEM_EVIDENCE but PARKED (NEG-09) — collapsing the two fields
into one would silently destroy exactly the distinction the Approved SRS
governance pass was designed to preserve.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


class SourceType:
    APPROVED_SRS = "approved_srs"
    DRAFT_SRS = "draft_srs"
    TECHNICAL_NOTE = "technical_note"
    QE_STRATEGY = "qe_strategy"
    HISTORICAL_DISCOVERY = "historical_discovery"


class ApprovalStatus:
    APPROVED = "APPROVED_BASELINED_V1_0"
    PARKED = "PARKED_NOT_IN_BASELINE"
    DRAFT = "DRAFT_REQUIRES_APPROVAL"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    HISTORICAL_SUPERSEDED = "HISTORICAL_SUPERSEDED"
    NOT_APPLICABLE = "NOT_APPLICABLE"  # e.g. section preambles, technical notes
    UNKNOWN = "UNKNOWN"


class EvidenceStrength:
    APPROVED_BASELINE = "APPROVED_BASELINE"
    DIRECT_SYSTEM_EVIDENCE = "DIRECT_SYSTEM_EVIDENCE"
    CURRENT_TESTING_ARTIFACT = "CURRENT_TESTING_ARTIFACT"
    HISTORICAL_EVIDENCE = "HISTORICAL_EVIDENCE"
    AGENT_INFERENCE = "AGENT_INFERENCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


# Deterministic authority tier, lowest number = highest authority.
# This is the ONLY place that decides precedence — retrieval.py consults
# this table and never lets an LLM reorder it (governance rule #10).
_AUTHORITY_BY_SOURCE_APPROVAL = {
    (SourceType.APPROVED_SRS, ApprovalStatus.APPROVED): 1,
    (SourceType.APPROVED_SRS, ApprovalStatus.PARKED): 2,
    (SourceType.APPROVED_SRS, ApprovalStatus.OUT_OF_SCOPE): 2,
    (SourceType.APPROVED_SRS, ApprovalStatus.NOT_APPLICABLE): 2,
    (SourceType.APPROVED_SRS, ApprovalStatus.UNKNOWN): 2,
}
_AUTHORITY_BY_SOURCE = {
    SourceType.TECHNICAL_NOTE: 3,
    SourceType.QE_STRATEGY: 3,
    SourceType.DRAFT_SRS: 4,
    SourceType.HISTORICAL_DISCOVERY: 5,
}
AGENT_INFERENCE_TIER = 6


def authority_tier(source_type: str, approval_status: str) -> int:
    """Deterministic authority tier lookup. Never delegated to an LLM."""
    key = (source_type, approval_status)
    if key in _AUTHORITY_BY_SOURCE_APPROVAL:
        return _AUTHORITY_BY_SOURCE_APPROVAL[key]
    if source_type in _AUTHORITY_BY_SOURCE:
        return _AUTHORITY_BY_SOURCE[source_type]
    # Unknown source_type: treat as lowest-but-one authority rather than
    # silently granting it high precedence.
    return 5


ID_FULL_RE_SOURCE = r"^(REQ-[A-Z]+-\d+|NEG-\d+|[A-Z]+-OQ-\d+|J-\d+)$"


@dataclass
class Chunk:
    chunk_id: str
    source: str
    source_type: str
    section: str
    section_id: str
    content_type: str
    text: str
    requirement_id: List[str] = field(default_factory=list)
    journey_id: List[str] = field(default_factory=list)
    classification: str = "UNKNOWN"
    approval_status: str = ApprovalStatus.NOT_APPLICABLE
    status_raw: str = ""
    evidence_strength: str = EvidenceStrength.NOT_APPLICABLE
    evidence_raw: str = ""
    version: str = ""
    baseline_date: Optional[str] = None
    scope: str = "in_scope"
    checkpoint: str = "CP-MVP2-01"
    actor: List[str] = field(default_factory=list)
    source_hash: str = ""
    superseded_by: Optional[str] = None
    supersedes: Optional[str] = None

    def authority_tier(self) -> int:
        if self.evidence_strength == EvidenceStrength.AGENT_INFERENCE and self.source_type not in (
            SourceType.APPROVED_SRS,
        ):
            return AGENT_INFERENCE_TIER
        return authority_tier(self.source_type, self.approval_status)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["authority_tier"] = self.authority_tier()
        return d
