"""
CP-MVP2-02 Phase 2 — historical discovery-evidence provenance manifest.

This script does NOT fabricate or reconstruct anything. It only inventories
files that were already copied, verbatim, from the actual CP-MVP2-01
discovery scratchpad (confirmed present on disk before copying — see
governance rule #11: never recreate historical evidence from memory).

If a file category is genuinely unavailable, this script must record that
as a limitation rather than inventing a substitute. In this run, the JS
probe scripts, JSON/log results, and HTML captures were all found and
copied; PNG screenshots were found but deliberately excluded (documented
below as an explicit scope decision, not a missing-evidence limitation).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "knowledge" / "historical" / "discovery_evidence"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(subdir: str) -> list:
    out = []
    d = EVIDENCE_DIR / subdir
    if not d.exists():
        return out
    for p in sorted(d.iterdir()):
        if p.is_file():
            out.append(
                {
                    "file": f"{subdir}/{p.name}",
                    "bytes": p.stat().st_size,
                    "sha256": sha256_of(p),
                }
            )
    return out


def build_manifest() -> dict:
    scripts = inventory("scripts")
    results = inventory("results")
    captures = inventory("captures")
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": (
            "Copied verbatim from the CP-MVP2-01 stateful discovery session's "
            "working scratchpad, confirmed present on disk at ingestion time. "
            "No content was reconstructed from memory."
        ),
        "source_type": "historical_discovery",
        "evidence_strength_default": "DIRECT_SYSTEM_EVIDENCE for *_results.json / *.log outcomes; "
        "CURRENT_TESTING_ARTIFACT for the *.js scripts and *.html captures that substantiate them",
        "approval_status": "NOT_APPLICABLE — raw evidence, not a requirement; never authoritative "
        "over the Approved SRS (see knowledge/lib authority model)",
        "counts": {"scripts": len(scripts), "results": len(results), "captures": len(captures)},
        "files": {"scripts": scripts, "results": results, "captures": captures},
        "excluded": [
            {
                "category": "PNG screenshots",
                "count_seen_at_source": 7,
                "reason": "Deliberately excluded from ingestion — binary, not needed for "
                "text-based retrieval, and out of scope for a lightweight local RAG "
                "implementation (governance rules #14/#15). This is a scope decision, "
                "NOT a case of unavailable evidence: the screenshots were confirmed present "
                "at the same source path as everything else copied above. They can be "
                "ingested later (e.g. as an assets store) if visual-evidence retrieval "
                "becomes a requirement.",
            },
            {
                "category": "node_modules/ and localdeps/",
                "reason": "Third-party tooling (npm packages, extracted system libraries) used "
                "to run the discovery scripts. Not evidence of application behavior; excluded "
                "as unnecessary infrastructure per governance rule #15.",
            },
        ],
        "limitations": [
            "This is a single discovery session's output (2026-09-11), one browser "
            "(headless Chromium), one account, one time window — see Approved SRS §12 "
            "for the full limitations list already governed into the baseline.",
            "These files are historical evidence only. Per the authority model, they can "
            "never outrank or silently amend the Approved SRS, regardless of how detailed "
            "they are.",
        ],
    }
    return manifest


def write_manifest() -> None:
    manifest = build_manifest()
    out = EVIDENCE_DIR / "MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[historical_discovery] manifest written to {out} "
          f"({manifest['counts']})")


if __name__ == "__main__":
    write_manifest()
