"""
CP-MVP2-CR-001 Batch 1 — additive, timestamped persistence for a real
CP-MVP2-06 `ExecutionResult`, WITHOUT modifying the frozen
`execution/pipeline.py`, `engine.py`, or `evidence.py`.

**Design decision (CR-001 sec. 13's own fallback instruction: "If
changing the existing frozen CP-06 directory convention creates a
compatibility concern, implement the safest backward-compatible
approach ... rather than silently breaking existing consumers").** The
frozen CP-MVP2-06 final-implementation-freeze checkpoint already cites
real evidence paths under `runs/cp_mvp2_06/<execution_id>/...`; changing
that default would retroactively invalidate paths a CLOSED checkpoint
already cites as evidence. This module therefore does not touch
`execution.evidence.EvidenceManager` or its default `RUNS_DIR` at all —
it adds a SEPARATE, purely additive step that any caller may invoke, by
composition, immediately after the unmodified `run_cp_mvp2_06()`,
writing the requested `runs/YYYY/MM/DD/<execution_id>/` layout as an
additional, parallel record of the same real `ExecutionResult` — never a
replacement for, and never mutating, CP-06's own frozen evidence.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict

from execution.schema import ExecutionResult
from persistence.envelope import REPO_ROOT

RUNS_ROOT = REPO_ROOT / "runs"


def _execution_date(result: ExecutionResult) -> datetime.datetime:
    if result.execution_start:
        try:
            return datetime.datetime.fromisoformat(result.execution_start)
        except ValueError:
            pass
    return datetime.datetime.now(datetime.timezone.utc)


def timestamped_dir(result: ExecutionResult) -> Path:
    dt = _execution_date(result)
    return RUNS_ROOT / f"{dt.year:04d}" / f"{dt.month:02d}" / f"{dt.day:02d}" / result.execution_id


def persist_execution_result(result: ExecutionResult) -> Dict:
    """Writes `final_result.json`/`step_results.json`/`assertions.json`
    under the timestamped directory. Purely additive real-evidence
    mirroring of an `ExecutionResult` that has ALREADY been produced by
    the unmodified, frozen `run_cp_mvp2_06()` — this function performs
    no browser action itself and fabricates nothing."""
    out_dir = timestamped_dir(result)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "final_result.json").write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    (out_dir / "step_results.json").write_text(
        json.dumps([s.to_dict() for s in result.step_results], indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    (out_dir / "assertions.json").write_text(
        json.dumps([a.to_dict() for a in result.assertion_results], indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )

    try:
        relative = str(out_dir.relative_to(REPO_ROOT))
    except ValueError:
        relative = str(out_dir)
    return {"execution_id": result.execution_id, "path": relative}
