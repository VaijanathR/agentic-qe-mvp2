"""
CP-MVP2-07 — real execution-evidence ingestion. Read-only.

Loads a real, persisted CP-MVP2-06 `ExecutionResult` JSON from the
Batch-1/2 additive `runs/YYYY/MM/DD/<execution_id>/final_result.json`
path (`execution/persist.py`, unmodified). Never invokes CP-06, never
constructs a synthetic ExecutionResult, never regenerates anything --
if the requested execution_id cannot be found on disk, returns None
(the caller must produce a governed BLOCKED/ERROR disposition, per the
frozen CP-07 specification sec. 4, never a fabricated RCA).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT

RUNS_ROOT = REPO_ROOT / "runs"


def _find_final_result_path(execution_id: str) -> Optional[Path]:
    matches = sorted(RUNS_ROOT.glob(f"*/*/*/{execution_id}/final_result.json"))
    return matches[-1] if matches else None


def load_execution_result(execution_id: str) -> Optional[Dict]:
    path = _find_final_result_path(execution_id)
    if path is None:
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_historical_results(testcase_id: str, exclude_execution_id: Optional[str] = None) -> List[Dict]:
    """Every other real, persisted `ExecutionResult` on disk sharing the
    same `testcase_id` -- the real business-scenario "lineage" (per the
    frozen CP-07 spec sec. 4/7). `testcase_id`, not `automation_id`, is
    used as the lineage key: the multi-locator/multi-dataset work
    deliberately gives each dataset variant of the same testcase its own
    distinct `automation_id` (to avoid `AUTOMATION_ID_COLLISION_ADVISORY`),
    so `testcase_id` is the only real, stable identifier for "the same
    scenario, run again." Used strictly as historical, supporting
    evidence -- never overriding current evidence (sec. 7). Deterministic
    ordering (execution_start, falling back to execution_id) so repeated
    runs over the same on-disk evidence produce the same
    historical_evidence list."""
    results: List[Dict] = []
    for path in RUNS_ROOT.glob("*/*/*/*/final_result.json"):
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("testcase_id") != testcase_id:
            continue
        if exclude_execution_id and data.get("execution_id") == exclude_execution_id:
            continue
        results.append(data)
    results.sort(key=lambda d: (d.get("execution_start") or "", d.get("execution_id") or ""))
    return results
