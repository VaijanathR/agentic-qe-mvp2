"""
CP-MVP2-02 Phase 1 — deterministic ingestion of the SRS markdown files into
governed knowledge-base chunks + a requirement/journey/open-question manifest.

Everything in this module is deterministic parsing and normalization of the
literal text already present in the source file. No content is invented:
every chunk's `text` field is built only from strings copied out of the
source markdown. The LLM is never involved in this step.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from knowledge.lib import md_tables as mt
from knowledge.lib.schema import ApprovalStatus, Chunk, EvidenceStrength, SourceType

REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_status(raw: str) -> str:
    t = mt.strip_md(raw or "").strip()
    t = re.sub(r"^[\*`]+", "", t).strip()
    tu = t.upper()
    if tu.startswith("APPROVED"):
        return ApprovalStatus.APPROVED
    if tu.startswith("PARKED") or tu.startswith("TBD"):
        return ApprovalStatus.PARKED
    if tu.startswith("DRAFT"):
        return ApprovalStatus.DRAFT
    if tu.startswith("OUT OF SCOPE"):
        return ApprovalStatus.OUT_OF_SCOPE
    if t == "":
        return ApprovalStatus.NOT_APPLICABLE
    return ApprovalStatus.UNKNOWN


def normalize_evidence(raw: str) -> str:
    tu = (raw or "").upper()
    if "AGENT INFERENCE" in tu:
        return EvidenceStrength.AGENT_INFERENCE
    if "HISTORICAL EVIDENCE" in tu:
        return EvidenceStrength.HISTORICAL_EVIDENCE
    if "CURRENT TESTING ARTIFACT" in tu and "DIRECT SYSTEM EVIDENCE" not in tu:
        return EvidenceStrength.CURRENT_TESTING_ARTIFACT
    if "DIRECT SYSTEM EVIDENCE" in tu:
        return EvidenceStrength.DIRECT_SYSTEM_EVIDENCE
    if "APPROVED BASELINE" in tu:
        return EvidenceStrength.APPROVED_BASELINE
    if tu.strip() == "":
        return EvidenceStrength.NOT_APPLICABLE
    return EvidenceStrength.UNKNOWN


def split_actors(raw: str) -> List[str]:
    raw = mt.strip_md(raw or "")
    parts = re.split(r",|→", raw)
    return [p.strip() for p in parts if p.strip()]


def slugify(text: str) -> str:
    t = mt.strip_md(text).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60] if t else "item"


SECTION_PROSE_TYPE = {
    "1": "purpose",
    "2": "scope_note",
    "2.1": "scope_note",
    "2.2": "scope_note",
    "2.3": "scope_note",
    "2.4": "scope_note",
    "2.5": "scope_note",
    "3": "out_of_scope",
    "8": "business_rule_section",  # handled specially, see extract_business_rules
    "9.1": "nfr_scope",
    "10": "data_requirement",
    "11": "environment_note",
    "12": "limitation_note",
    "13": "governance_note",
    "15": "approval_metadata",
}


def extract_business_rules(prose_blocks: List[mt.Prose], section_id: str, source_meta: dict) -> List[Chunk]:
    chunks = []
    for block in prose_blocks:
        if block.section_id != section_id:
            continue
        for m in re.finditer(r"^(\d+)\.\s+(.*)$", block.text, flags=re.MULTILINE):
            n = int(m.group(1))
            text = m.group(2).strip()
            ref_ids = mt.expand_ids(text)
            chunk_id = f"{source_meta['doc_key']}__BR-{n:02d}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    source=source_meta["source"],
                    source_type=source_meta["source_type"],
                    section=f"{section_id} Business Rules",
                    section_id=section_id,
                    content_type="business_rule",
                    text=f"BR-{n:02d}: {text}",
                    requirement_id=ref_ids,
                    journey_id=[],
                    classification="DERIVED_CANDIDATE",
                    approval_status=source_meta["default_status"],
                    status_raw="",
                    evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                    evidence_raw="",
                    version=source_meta["version"],
                    baseline_date=source_meta["baseline_date"],
                    scope="in_scope",
                    checkpoint="CP-MVP2-01",
                    actor=[],
                    source_hash=source_meta["source_hash"],
                )
            )
    return chunks


def render_requirement_text(item: Dict[str, str]) -> str:
    lines = [f"{item['_id']}: {item.get('Statement', '')}"]
    if item.get("Rationale"):
        lines.append(f"Rationale: {item['Rationale']}")
    if item.get("Evidence Basis"):
        lines.append(f"Evidence Basis: {item['Evidence Basis']}")
    if item.get("Acceptance Criteria"):
        lines.append(f"Acceptance Criteria: {item['Acceptance Criteria']}")
    if item.get("Actor"):
        lines.append(f"Actor: {item['Actor']}")
    if item.get("Journey"):
        lines.append(f"Journey: {item['Journey']}")
    status = item.get("Status") or item.get("Approval Status") or ""
    if status:
        lines.append(f"Status: {mt.strip_md(status)}")
    return "\n".join(lines)


def build_chunks(md_path: Path, source_type: str, doc_key: str, version: str) -> (List[Chunk], dict):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    source_hash = sha256_of_text(text)
    source_rel = str(md_path.relative_to(REPO_ROOT)).replace("\\", "/")

    baseline_date = None
    m = re.search(r"\*\*Baseline date:\*\*\s*(\S+)", text)
    if m:
        baseline_date = m.group(1)

    default_status = ApprovalStatus.APPROVED if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT

    sections = mt.parse_sections(lines)
    tables = mt.parse_tables(lines, sections)
    prose_blocks = mt.extract_prose_blocks(lines, sections, tables)

    source_meta = {
        "source": source_rel,
        "source_type": source_type,
        "doc_key": doc_key,
        "version": version,
        "baseline_date": baseline_date,
        "source_hash": source_hash,
        "default_status": default_status,
    }

    chunks: List[Chunk] = []

    # --- Document header / evidence-hierarchy preamble (lines before first section) ---
    first_section_line = sections[0].start_line if sections else len(lines)
    header_text = "\n".join(lines[:first_section_line]).strip()
    if header_text:
        chunks.append(
            Chunk(
                chunk_id=f"{doc_key}__DOC-HEADER",
                source=source_rel,
                source_type=source_type,
                section="Document Header / Evidence Hierarchy",
                section_id="0",
                content_type="document_metadata",
                text=header_text,
                approval_status=ApprovalStatus.NOT_APPLICABLE,
                evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                version=version,
                baseline_date=baseline_date,
                source_hash=source_hash,
            )
        )

    # --- Tables ---
    for table in tables:
        sid = table.section_id
        items = mt.table_to_items(table)
        if not items:
            continue

        if sid.startswith("6."):
            for item in items:
                if not re.match(r"^REQ-[A-Z]+-\d+$", item["_id"]):
                    continue
                journeys = mt.expand_ids(item.get("Journey", ""))
                status_raw = item.get("Status") or item.get("Approval Status") or ""
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__{item['_id']}",
                        source=source_rel,
                        source_type=source_type,
                        section=f"{sid} {[s.title for s in sections if s.section_id == sid][0]}",
                        section_id=sid,
                        content_type="requirement",
                        text=render_requirement_text(item),
                        requirement_id=[item["_id"]],
                        journey_id=journeys,
                        classification="DERIVED_CANDIDATE",
                        approval_status=normalize_status(status_raw) if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT,
                        status_raw=mt.strip_md(status_raw),
                        evidence_strength=normalize_evidence(item.get("Evidence Strength", "")),
                        evidence_raw=item.get("Evidence Strength", ""),
                        version=version,
                        baseline_date=baseline_date,
                        actor=split_actors(item.get("Actor", "")),
                        source_hash=source_hash,
                    )
                )
        elif sid == "4":
            for item in items:
                status_raw = item.get("Approval Status", "")
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__ACTOR-{slugify(item['_id'])}",
                        source=source_rel,
                        source_type=source_type,
                        section="4 Actors and Personas",
                        section_id="4",
                        content_type="actor_definition",
                        text=f"{mt.strip_md(item['_id'])}: {item.get('Basis', '')}",
                        classification="DERIVED_CANDIDATE",
                        approval_status=normalize_status(status_raw) if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT,
                        status_raw=mt.strip_md(status_raw),
                        evidence_strength=normalize_evidence(item.get("Evidence Strength", "")),
                        evidence_raw=item.get("Evidence Strength", ""),
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        elif sid == "5":
            for item in items:
                if not re.match(r"^J-\d+$", item["_id"]):
                    continue
                status_raw = item.get("Approval Status", "")
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__{item['_id']}",
                        source=source_rel,
                        source_type=source_type,
                        section="5 Business Journeys",
                        section_id="5",
                        content_type="journey",
                        text=f"{item['_id']}: {item.get('Journey', '')}\nNotes: {item.get('Notes', '')}",
                        journey_id=[item["_id"]],
                        classification="DERIVED_CANDIDATE",
                        approval_status=normalize_status(status_raw) if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT,
                        status_raw=mt.strip_md(status_raw),
                        evidence_strength=normalize_evidence(item.get("Evidence Strength", "")),
                        evidence_raw=item.get("Evidence Strength", ""),
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        elif sid == "7":
            for item in items:
                if not re.match(r"^NEG-\d+$", item["_id"]):
                    continue
                status_raw = item.get("Status", "")
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__{item['_id']}",
                        source=source_rel,
                        source_type=source_type,
                        section="7 Negative and Exceptional Requirements",
                        section_id="7",
                        content_type="negative_case",
                        text=f"{item['_id']}: {item.get('Statement', '')}",
                        requirement_id=[item["_id"]],
                        classification="DERIVED_CANDIDATE",
                        approval_status=normalize_status(status_raw) if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT,
                        status_raw=mt.strip_md(status_raw),
                        evidence_strength=normalize_evidence(item.get("Evidence Strength", "")),
                        evidence_raw=item.get("Evidence Strength", ""),
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        elif sid == "9.2":
            for item in items:
                status_raw = item.get("Status", "")
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__NFR-THRESHOLD-{slugify(item['_id'])}",
                        source=source_rel,
                        source_type=source_type,
                        section="9.2 Numeric Thresholds",
                        section_id="9.2",
                        content_type="nfr_threshold_placeholder",
                        text=f"{item['_id']}: {mt.strip_md(status_raw)}",
                        classification="OPEN_QUESTION",
                        approval_status=normalize_status(status_raw),
                        status_raw=mt.strip_md(status_raw),
                        evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        elif sid == "13":
            for item in items:
                raw_id = item["_id"]
                oq_id = raw_id if re.match(r"^[A-Z]+-OQ-\d+$", raw_id) else "NFR-OQ-THRESHOLDS"
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__{oq_id}",
                        source=source_rel,
                        source_type=source_type,
                        section="13 Open Questions / Parked Items",
                        section_id="13",
                        content_type="open_question",
                        text=(
                            f"{oq_id}: {item.get('Question', '')}\n"
                            f"Parked Because: {item.get('Parked Because', '')}\n"
                            f"Blocks Baseline?: {item.get('Blocks Baseline?', '')}"
                        ),
                        requirement_id=[oq_id],
                        classification="OPEN_QUESTION",
                        approval_status=ApprovalStatus.PARKED,
                        status_raw="PARKED — NOT IN BASELINE",
                        evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        elif sid == "14":
            for item in items:
                jid_match = re.match(r"^(J-\d+)$", item["_id"])
                if not jid_match:
                    continue
                member_ids = mt.expand_ids(item.get("Traceable Requirements", ""))
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_key}__JIDX-{item['_id']}",
                        source=source_rel,
                        source_type=source_type,
                        section="14 Requirement Traceability",
                        section_id="14",
                        content_type="journey_index",
                        text=(
                            f"{item['_id']} traceable requirements: {', '.join(member_ids)}\n"
                            f"Test Case ID: {item.get('Test Case ID', '')}\n"
                            f"Automation ID: {item.get('Automation ID', '')}\n"
                            f"Evidence Artifacts: {item.get('Evidence Artifacts', '')}"
                        ),
                        requirement_id=member_ids,
                        journey_id=[item["_id"]],
                        classification="DERIVED_CANDIDATE",
                        approval_status=ApprovalStatus.APPROVED if source_type == SourceType.APPROVED_SRS else ApprovalStatus.DRAFT,
                        evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                        version=version,
                        baseline_date=baseline_date,
                        source_hash=source_hash,
                    )
                )
        # other tables (e.g. §15 Approval Decision key/value table) are
        # captured via the prose/metadata chunk instead of per-row chunks.

    # --- Business rules (§8, numbered prose list) ---
    chunks.extend(extract_business_rules(prose_blocks, "8", source_meta))

    # --- Section preambles / framing prose (everything not already a table row) ---
    handled_table_sections = {t.section_id for t in tables} | {"8"}
    for block in prose_blocks:
        if block.section_id in ("8",):
            continue  # already turned into business_rule chunks
        title = next((s.title for s in sections if s.section_id == block.section_id), block.section_id)
        content_type = SECTION_PROSE_TYPE.get(block.section_id, "section_preamble")
        ref_ids = mt.expand_ids(block.text)
        req_refs = [r for r in ref_ids if not r.startswith("J-")]
        journey_refs = [r for r in ref_ids if r.startswith("J-")]
        chunk_id = f"{doc_key}__PROSE-{block.section_id}-{block.start_line}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                source=source_rel,
                source_type=source_type,
                section=f"{block.section_id} {title}".strip(),
                section_id=block.section_id,
                content_type=content_type,
                text=block.text,
                requirement_id=req_refs,
                journey_id=journey_refs,
                classification="OBSERVED",
                approval_status=ApprovalStatus.NOT_APPLICABLE,
                evidence_strength=EvidenceStrength.NOT_APPLICABLE,
                version=version,
                baseline_date=baseline_date,
                source_hash=source_hash,
            )
        )

    return chunks, source_meta


def build_manifest(chunks: List[Chunk], source_meta: dict) -> dict:
    def ids_of(content_type: str, key: str = "requirement_id") -> List[str]:
        out = []
        for c in chunks:
            if c.content_type == content_type:
                out.extend(getattr(c, key))
        return sorted(set(out))

    requirement_ids = sorted({c.requirement_id[0] for c in chunks if c.content_type == "requirement"})
    negative_ids = sorted({c.requirement_id[0] for c in chunks if c.content_type == "negative_case"})
    open_question_ids = sorted({c.requirement_id[0] for c in chunks if c.content_type == "open_question"})
    journey_ids = sorted({c.journey_id[0] for c in chunks if c.content_type == "journey"})
    business_rule_ids = sorted({c.chunk_id.split("__")[-1] for c in chunks if c.content_type == "business_rule"})

    counts: Dict[str, int] = {}
    for c in chunks:
        counts[c.content_type] = counts.get(c.content_type, 0) + 1

    return {
        "source": source_meta["source"],
        "source_type": source_meta["source_type"],
        "version": source_meta["version"],
        "baseline_date": source_meta["baseline_date"],
        "source_hash": source_meta["source_hash"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chunk_count": len(chunks),
        "counts_by_content_type": counts,
        "ids": {
            "requirements": requirement_ids,
            "negatives": negative_ids,
            "open_questions": open_question_ids,
            "journeys": journey_ids,
            "business_rules": business_rule_ids,
        },
    }


def write_jsonl(chunks: List[Chunk], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")


def write_manifest(manifest: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ingest_approved_srs() -> None:
    md_path = REPO_ROOT / "requirements" / "MVP2_SRS_v1.0_APPROVED.md"
    chunks, meta = build_chunks(md_path, SourceType.APPROVED_SRS, doc_key="srs_v1.0", version="1.0")
    out_dir = REPO_ROOT / "knowledge" / "requirements" / "approved" / "srs_v1.0"
    write_jsonl(chunks, out_dir / "chunks.jsonl")
    manifest = build_manifest(chunks, meta)
    write_manifest(manifest, out_dir / "manifest.json")
    print(f"[approved_srs] {len(chunks)} chunks written to {out_dir}")


def ingest_draft_srs() -> None:
    md_path = REPO_ROOT / "requirements" / "MVP2_SRS_DRAFT.md"
    if not md_path.exists():
        print(f"[draft_srs] SKIPPED — file not found at {md_path}")
        return
    chunks, meta = build_chunks(md_path, SourceType.DRAFT_SRS, doc_key="srs_draft_v0.1", version="0.1")
    out_dir = REPO_ROOT / "knowledge" / "historical" / "draft_srs_v0.1"
    write_jsonl(chunks, out_dir / "chunks.jsonl")
    manifest = build_manifest(chunks, meta)
    write_manifest(manifest, out_dir / "manifest.json")
    print(f"[draft_srs] {len(chunks)} chunks written to {out_dir}")


if __name__ == "__main__":
    ingest_approved_srs()
    ingest_draft_srs()
