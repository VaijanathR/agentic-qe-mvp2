"""
CP-MVP2-07 — RCA / Replanning / Governance orchestration pipeline.

Wires together, by composition only (no frozen file modified):

  ExecutionResult (real, on-disk)
      -> Failure Detection / Classification  (rca.classify)
      -> Evidence Collection / RCA           (rca.analyze)
      -> Persist RCA                         (rca.persist)
      -> Replanning Decision                 (rca.replan)
      -> Persist Replanning                  (rca.persist)
      -> Governance Decision                 (rca.govern, incl. the
                                                prohibited-change guard
                                                and CR-002 re-affirmation)
      -> Persist Governance                  (rca.persist)
      -> Persisted Outcome (returned)

matching frozen `docs/CP-MVP2-07-SPECIFICATION-v1.0.md` sec. 2's
architecture diagram exactly. A missing execution_id produces a real,
governed BLOCKED outcome -- never a fabricated RCA (sec. 4).
"""
from __future__ import annotations

from typing import Dict, Optional

from rca.analyze import build_rca_record
from rca.govern import decide_governance, snapshot_frozen_artifacts, verify_frozen_artifacts_unchanged
from rca.ingest import load_execution_result
from rca.persist import persist_governance, persist_rca, persist_replanning
from rca.replan import decide_replanning
from rca.schema import GovernanceDecision, GovernanceRecord


def run_cp07_rca(execution_id: str) -> Dict:
    """Runs the full CP-07 pipeline for one real, persisted execution_id.
    Returns {"status": "BLOCKED", "reason": ...} if the execution
    evidence cannot be found (never fabricated), otherwise
    {"status": "COMPLETE", "rca": ..., "replanning": ..., "governance": ...,
    "persisted": {...}}."""
    frozen_baseline = snapshot_frozen_artifacts()

    execution_result = load_execution_result(execution_id)
    if execution_result is None:
        return {
            "status": "BLOCKED",
            "reason": f"No persisted ExecutionResult found for execution_id={execution_id!r}. "
                      "Per frozen CP-MVP2-07 spec sec. 4, RCA is never fabricated for evidence "
                      "that does not exist on disk.",
        }

    rca_id = f"RCA-{execution_id}"
    rca = build_rca_record(execution_id, rca_id)
    assert rca is not None  # execution_result was just confirmed present
    rca_persist_result = persist_rca(rca)

    replanning = decide_replanning(rca, execution_result["overall_status"])
    replanning_persist_result = persist_replanning(replanning)

    frozen_guard_result = verify_frozen_artifacts_unchanged(frozen_baseline)
    governance_id = f"GOV-{execution_id}"
    governance = decide_governance(replanning, governance_id, frozen_guard_result)
    governance_persist_result = persist_governance(governance)

    return {
        "status": "COMPLETE",
        "rca": rca.to_dict(),
        "replanning": replanning.to_dict(),
        "governance": governance.to_dict(),
        "persisted": {
            "rca": rca_persist_result,
            "replanning": replanning_persist_result,
            "governance": governance_persist_result,
        },
    }
