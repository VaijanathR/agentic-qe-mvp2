"""
CP-MVP2-07 — governance decision + prohibited-change guard.

Two real, functioning checks, never simulated:

1. `verify_frozen_artifacts_unchanged()` -- a deterministic, in-process
   SHA-256 content-hash comparison of the same curated list of frozen
   paths already enumerated in
   `docs/CP-MVP2-07-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`'s upstream
   verification. Captured once at pipeline start, re-verified at
   pipeline end (`rca/pipeline.py`) -- if any hash differs, the
   governance decision is forced to GOVERNANCE_BLOCKED regardless of
   the replanning decision, per sec. 9 "No Silent Changes".

2. `check_cr002_status()` -- reads the *live* CR-002 proposal document
   on disk and asserts its status line still reads
   "PROPOSED" / "NOT AUTHORIZED" / "NOT IMPLEMENTED". If CR-002 were
   ever silently authorized/implemented outside a real, separate,
   governed task, this check fails loudly rather than CP-07 silently
   assuming it remains closed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List

from persistence.envelope import REPO_ROOT
from rca.schema import GovernanceDecision, GovernanceRecord, ReplanningDecision, ReplanningRecord

FROZEN_ARTIFACT_PATHS: List[str] = [
    "docs/CP-MVP2-06-SPECIFICATION-v1.0.md",
    "docs/CP-MVP2-06-FINAL-IMPLEMENTATION-FREEZE-CHECKPOINT.md",
    "docs/CP-MVP2-07-SPECIFICATION-v1.0.md",
    "docs/CP-MVP2-07-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md",
    "docs/claude-execution-reports/CP-MVP2-06/CP-MVP2-06-GOVERNANCE-CLOSURE-20260914-205228.md",
    "requirements/MVP2_SRS_v1.0_APPROVED.md",
    "execution/schema.py",
    "execution/validate.py",
    "execution/evidence.py",
    "execution/engine.py",
    "execution/pipeline.py",
    "automation/schema.py",
    "automation/generate.py",
    "automation/validate.py",
    "automation/pipeline.py",
    "automation/evidence.py",
]

CR002_DOC_PATH = "docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md"


def _sha256_of(rel_path: str) -> str:
    full = REPO_ROOT / rel_path
    if not full.exists():
        return "MISSING"
    return hashlib.sha256(full.read_bytes()).hexdigest()


def snapshot_frozen_artifacts() -> Dict[str, str]:
    return {p: _sha256_of(p) for p in FROZEN_ARTIFACT_PATHS}


def verify_frozen_artifacts_unchanged(baseline: Dict[str, str]) -> Dict:
    current = snapshot_frozen_artifacts()
    diffs = {p: {"baseline": baseline.get(p), "current": current.get(p)} for p in FROZEN_ARTIFACT_PATHS if baseline.get(p) != current.get(p)}
    return {"passed": not diffs, "checked_paths": FROZEN_ARTIFACT_PATHS, "diffs": diffs}


def check_cr002_status() -> Dict:
    full = REPO_ROOT / CR002_DOC_PATH
    if not full.exists():
        return {"found": False, "still_unauthorized": False, "detail": f"{CR002_DOC_PATH} not found."}
    text = full.read_text(encoding="utf-8")
    still_unauthorized = ("NOT AUTHORIZED" in text) and ("NOT IMPLEMENTED" in text) and ("PROPOSED" in text)
    return {
        "found": True,
        "still_unauthorized": still_unauthorized,
        "detail": "CR-002 status line still reads PROPOSED / NOT AUTHORIZED / NOT IMPLEMENTED." if still_unauthorized else "CR-002 status has changed since this guard was authored -- STOP, do not assume closed.",
    }


def decide_governance(
    replanning: ReplanningRecord,
    governance_id: str,
    frozen_guard_result: Dict,
) -> GovernanceRecord:
    cr002 = check_cr002_status()
    cr002_status = "OPEN_NOT_AUTHORIZED" if cr002.get("still_unauthorized") else "STATUS_CHANGED_REQUIRES_HUMAN_REVIEW"

    if not frozen_guard_result["passed"]:
        decision = GovernanceDecision.GOVERNANCE_BLOCKED
        rationale = (
            "Prohibited-change guard FAILED: one or more frozen artifacts changed content-hash "
            f"during this pipeline run: {list(frozen_guard_result['diffs'].keys())}. Per sec. 9 "
            "'No Silent Changes', no governance action may be authorized while frozen-artifact "
            "integrity is unverified."
        )
    elif not cr002.get("still_unauthorized", False):
        decision = GovernanceDecision.GOVERNANCE_BLOCKED
        rationale = f"CR-002 status re-affirmation check FAILED: {cr002.get('detail')} No governance action may be authorized until this is resolved by Human + Di."
    elif replanning.decision == ReplanningDecision.REPLAN_NOT_ALLOWED:
        decision = GovernanceDecision.NO_ACTION_REQUIRED
        rationale = "Replanning decision was REPLAN_NOT_ALLOWED (execution PASSED); no governance action is required."
    elif replanning.decision == ReplanningDecision.GOVERNANCE_BLOCKED:
        decision = GovernanceDecision.GOVERNANCE_BLOCKED
        rationale = f"Replanning itself was GOVERNANCE_BLOCKED: {replanning.reason}"
    elif replanning.decision == ReplanningDecision.HUMAN_REVIEW_REQUIRED:
        decision = GovernanceDecision.ACTION_DEFERRED_TO_HUMAN
        rationale = f"Replanning requires human review: {replanning.reason} No automated action is authorized; deferred to Human + Di."
    else:  # REPLAN_ALLOWED
        decision = GovernanceDecision.ACTION_DEFERRED_TO_HUMAN
        rationale = (
            "Replanning was evaluated as REPLAN_ALLOWED, but per this project's standing "
            "governance discipline (PROPOSE -> GOVERN -> AUTHORIZE -> IMPLEMENT), CP-07 itself "
            "never self-authorizes execution of a replan; final authorization is deferred to "
            "Human + Di."
        )

    return GovernanceRecord(
        governance_id=governance_id,
        rca_id=replanning.rca_id,
        replanning_id=replanning.replanning_id,
        execution_id=replanning.execution_id,
        decision=decision,
        cr002_status=cr002_status,
        prohibited_change_guard_passed=frozen_guard_result["passed"],
        prohibited_change_guard_detail=frozen_guard_result,
        rationale=rationale,
        generation_metadata={"generator": "deterministic-only (no LLM anywhere in CP-MVP2-07 governance)"},
    )
