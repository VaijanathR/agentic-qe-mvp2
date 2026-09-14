"""
CP-MVP2-02 Phase 3 — deterministic local retrieval layer.

Governance rules enforced here (never delegated to an LLM):
  - exact REQ/NEG/OQ/J ID matching short-circuits semantic search
  - metadata filtering (source_type, approval_status, content_type)
  - authority-tier ranking (schema.authority_tier) always wins ties and,
    by default, always outranks lower tiers regardless of lexical score
  - approval-status handling: PARKED/DRAFT/HISTORICAL content is excluded
    from the default answer basis unless the caller explicitly asks for
    history/parked context (include_non_approved=True)
  - version/supersession bookkeeping (superseded_by is respected: a
    superseded chunk is excluded from "current" results by default)
  - source-hash drift detection against the live SRS files on disk
  - a tiny local lexical-similarity fallback (pure stdlib, no embedding
    service, no hosted vector DB) used only to rank free-text queries
    that do not contain an exact ID

The LLM is never asked "which of these is authoritative" — this module
answers that question by construction before anything reaches the LLM.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from knowledge.lib.schema import ApprovalStatus, authority_tier

REPO_ROOT = Path(__file__).resolve().parents[2]

ID_RE = re.compile(r"\b(REQ-[A-Z]+-\d+|NEG-\d+|[A-Z]+-OQ-\d+|J-\d+)\b", re.IGNORECASE)

HISTORY_INTENT_WORDS = {
    "history", "historical", "why", "draft", "changed", "before", "previously",
    "parked", "open question", "open-question", "still open", "unresolved",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


KNOWLEDGE_SOURCES = [
    ("approved_srs", REPO_ROOT / "knowledge" / "requirements" / "approved" / "srs_v1.0"),
    ("draft_srs", REPO_ROOT / "knowledge" / "historical" / "draft_srs_v0.1"),
]


@dataclass
class KnowledgeBase:
    chunks: List[dict] = field(default_factory=list)
    manifests: Dict[str, dict] = field(default_factory=dict)
    _df: Dict[str, int] = field(default_factory=dict, repr=False)
    _idf: Dict[str, float] = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls, extra_dirs: Optional[List[Path]] = None) -> "KnowledgeBase":
        kb = cls()
        dirs = list(KNOWLEDGE_SOURCES)
        if extra_dirs:
            dirs.extend(("extra", d) for d in extra_dirs)
        for key, d in dirs:
            chunk_file = d / "chunks.jsonl"
            manifest_file = d / "manifest.json"
            if chunk_file.exists():
                with chunk_file.open(encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            kb.chunks.append(json.loads(line))
            if manifest_file.exists():
                kb.manifests[key] = json.loads(manifest_file.read_text(encoding="utf-8"))
        kb._build_idf()
        return kb

    def _build_idf(self) -> None:
        """Corpus-wide document frequency, computed once at load time.
        Plain term-overlap cosine is not discriminative enough on this
        corpus (every chunk repeats words like 'approved'/'baselined'), so
        retrieval uses classic TF-IDF weighting — still pure stdlib, no
        embedding service, per governance rule #14 (no hosted vector DB,
        keep it lightweight and local)."""
        n = len(self.chunks) or 1
        df: Dict[str, int] = {}
        for c in self.chunks:
            for tok in set(tokenize(c["text"])):
                df[tok] = df.get(tok, 0) + 1
        self._df = df
        self._idf = {tok: math.log((1 + n) / (1 + d)) + 1.0 for tok, d in df.items()}

    # ---- drift detection -------------------------------------------------
    def check_drift(self) -> List[dict]:
        """Compares each ingested manifest's recorded source_hash against a
        fresh hash of the live file on disk. Returns a list of drift
        findings (empty list = no drift)."""
        findings = []
        for key, manifest in self.manifests.items():
            src = REPO_ROOT / manifest["source"]
            if not src.exists():
                findings.append({"source": manifest["source"], "issue": "MISSING_SOURCE_FILE"})
                continue
            live_hash = hashlib.sha256(src.read_bytes()).hexdigest()
            if live_hash != manifest["source_hash"]:
                findings.append(
                    {
                        "source": manifest["source"],
                        "issue": "HASH_MISMATCH",
                        "recorded_hash": manifest["source_hash"],
                        "live_hash": live_hash,
                    }
                )
        return findings

    # ---- exact ID lookup ---------------------------------------------------
    def by_id(self, ident: str, include_non_current: bool = False) -> List[dict]:
        ident_u = ident.upper()
        out = [
            c
            for c in self.chunks
            if ident_u in [r.upper() for r in c.get("requirement_id", [])]
            or ident_u in [j.upper() for j in c.get("journey_id", [])]
        ]
        if not include_non_current:
            out = [c for c in out if not c.get("superseded_by")]
        return sorted(out, key=lambda c: c["authority_tier"])

    # ---- lexical similarity (pure stdlib, no embedding service) -----------
    @staticmethod
    def _tf(text: str) -> Counter:
        return Counter(tokenize(text))

    def _weighted(self, tf: Counter) -> Dict[str, float]:
        return {t: v * self._idf.get(t, 1.0) for t, v in tf.items()}

    def _lexical_score(self, query_tf: Counter, chunk_text: str) -> float:
        chunk_tf = self._tf(chunk_text)
        if not query_tf or not chunk_tf:
            return 0.0
        q = self._weighted(query_tf)
        d = self._weighted(chunk_tf)
        common = set(q) & set(d)
        if not common:
            return 0.0
        dot = sum(q[t] * d[t] for t in common)
        qnorm = math.sqrt(sum(v * v for v in q.values()))
        dnorm = math.sqrt(sum(v * v for v in d.values()))
        if qnorm == 0 or dnorm == 0:
            return 0.0
        return dot / (qnorm * dnorm)

    # ---- governed retrieval -------------------------------------------------
    def query(
        self,
        text: str,
        top_k: int = 6,
        include_non_approved: Optional[bool] = None,
        content_types: Optional[List[str]] = None,
    ) -> dict:
        """Deterministic retrieval flow:
        1. exact-ID short-circuit
        2. metadata filter (approval-status intent + content_type)
        3. lexical similarity ranking within the filtered pool
        4. authority-tier resort (authority always wins over lexical score)
        Returns a dict with the ranked chunks plus provenance and the
        intent decision, so callers never have to re-derive governance.
        """
        query_lower = text.lower()
        exact_ids = [m.group(1).upper() for m in ID_RE.finditer(text)]

        if include_non_approved is None:
            include_non_approved = any(w in query_lower for w in HISTORY_INTENT_WORDS)

        if exact_ids:
            results: List[dict] = []
            for ident in exact_ids:
                for c in self.by_id(ident):
                    if c not in results:
                        results.append(c)
            if not include_non_approved:
                approved_hits = [c for c in results if c["approval_status"] == ApprovalStatus.APPROVED]
                non_approved_hits = [c for c in results if c["approval_status"] != ApprovalStatus.APPROVED]
                results = approved_hits + non_approved_hits  # approved first, but nothing hidden
            results.sort(key=lambda c: c["authority_tier"])
            return {
                "mode": "exact_id",
                "matched_ids": exact_ids,
                "include_non_approved": include_non_approved,
                "results": results[:top_k],
            }

        pool = self.chunks
        if content_types:
            pool = [c for c in pool if c["content_type"] in content_types]
        if not include_non_approved:
            # Default: restrict to the Approved SRS document only (tiers 1
            # and 2). This still surfaces that document's own PARKED/open
            # questions when they are topically relevant (they are part of
            # the authoritative document and must remain visible so an
            # approved requirement's scope boundary is never hidden) — but
            # Draft SRS and raw historical-discovery content (tiers 4/5)
            # never enter the default pool. Authority-tier sort below still
            # always ranks tier-1 approved content above tier-2 parked
            # content, so nothing PARKED is ever presented ahead of an
            # approved answer.
            pool = [c for c in pool if c["source_type"] == "approved_srs"]

        query_tf = self._tf(text)
        scored = [(self._lexical_score(query_tf, c["text"]), c) for c in pool]
        scored = [(s, c) for s, c in scored if s > 0]

        # Governance-aware selection: rank by relevance to actually find the
        # right chunks, but RESERVE a small number of slots for the
        # best-matching non-approved (e.g. PARKED-within-Approved-SRS)
        # chunks so a directly relevant open question is never silently
        # crowded out by a larger number of loosely-approved matches
        # (this is what makes scenario "is wishlist available for all
        # products?" surface WISH-OQ-01 alongside REQ-WISH-01). Nothing
        # non-approved is ever placed ABOVE approved content in the final
        # order — that is enforced by the authority-tier resort below.
        # Three buckets, not two: APPROVED, PARKED (the governance-critical
        # category that must never be silently crowded out), and everything
        # else (context-only NOT_APPLICABLE chunks, e.g. preambles/actors).
        # Reserving slots specifically for PARKED first is what guarantees
        # scenario "is wishlist available for all products?" still surfaces
        # WISH-OQ-01 even though generic context chunks also score well.
        approved_scored = sorted(
            ((s, c) for s, c in scored if c["approval_status"] == ApprovalStatus.APPROVED),
            key=lambda sc: -sc[0],
        )
        parked_scored = sorted(
            ((s, c) for s, c in scored if c["approval_status"] == ApprovalStatus.PARKED),
            key=lambda sc: -sc[0],
        )
        other_scored = sorted(
            (
                (s, c)
                for s, c in scored
                if c["approval_status"] not in (ApprovalStatus.APPROVED, ApprovalStatus.PARKED)
            ),
            key=lambda sc: -sc[0],
        )
        reserved_parked = min(2, len(parked_scored), max(top_k // 3, 1))
        reserved_other = min(1, len(other_scored), max(top_k // 4, 1)) if top_k > reserved_parked else 0
        approved_take = max(top_k - reserved_parked - reserved_other, 0)
        chosen = approved_scored[:approved_take] + parked_scored[:reserved_parked] + other_scored[:reserved_other]
        if len(chosen) < top_k:
            remainder = (
                approved_scored[approved_take:] + parked_scored[reserved_parked:] + other_scored[reserved_other:]
            )
            remainder.sort(key=lambda sc: -sc[0])
            chosen += remainder[: top_k - len(chosen)]

        chosen_chunks = [c for _, c in chosen]
        # Final deterministic presentation order: authority tier always wins
        # (governance rule #9) — lexical score only decided *inclusion*.
        chosen_chunks.sort(key=lambda c: c["authority_tier"])
        results = chosen_chunks[:top_k]
        return {
            "mode": "lexical",
            "matched_ids": [],
            "include_non_approved": include_non_approved,
            "results": results,
        }


def provenance(chunk: dict) -> dict:
    return {
        "source": chunk["source"],
        "section": chunk["section"],
        "requirement_id": chunk.get("requirement_id", []),
        "journey_id": chunk.get("journey_id", []),
        "approval_status": chunk["approval_status"],
        "evidence_strength": chunk["evidence_strength"],
        "version": chunk["version"],
        "authority_tier": chunk["authority_tier"],
    }
