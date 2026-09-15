"""
Agentic QE Orchestration -- the orchestration journal (governing
instruction sec. 37, 52, 53).

A machine-readable, incrementally-persisted record of one orchestration
run: state transitions, decisions, tool invocations, results, evidence
references, and approval state. Persisted as a single, directly
overwritten JSON file per orchestration_id (NOT through
`persistence.envelope.persist_artifact`'s content-hash-versioned scheme
-- a journal is a single growing document for one run, not a family of
immutable artifact versions; this mirrors the same lighter-weight,
direct-JSON-write pattern `execution/persist.py` already uses for
per-execution records). Every `append()` call rewrites the file, so a
process interrupted mid-run leaves a real, readable, up-to-date journal
on disk (sec. 52/53 recovery requirement) rather than losing everything
still buffered in memory.

Never stores hidden chain-of-thought (sec. 37) -- only concise,
structured entries: state, decision, rationale, evidence references.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional

from persistence.envelope import REPO_ROOT

JOURNAL_ROOT = REPO_ROOT / "orchestration" / "generated" / "journal"


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class OrchestrationJournal:
    def __init__(self, orchestration_id: str, initiating_requirement_or_change: str):
        self.orchestration_id = orchestration_id
        self.initiating_requirement_or_change = initiating_requirement_or_change
        self.created_at = _now_iso()
        self.entries: List[Dict] = []
        self.current_state: Optional[str] = None
        self.approval_state: Dict = {}
        JOURNAL_ROOT.mkdir(parents=True, exist_ok=True)
        self._path = JOURNAL_ROOT / f"{orchestration_id}.json"
        self._persist()

    def _persist(self) -> None:
        payload = {
            "orchestration_id": self.orchestration_id,
            "initiating_requirement_or_change": self.initiating_requirement_or_change,
            "created_at": self.created_at,
            "updated_at": _now_iso(),
            "current_state": self.current_state,
            "approval_state": self.approval_state,
            "entries": self.entries,
        }
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    def record_transition(self, from_state: Optional[str], to_state: str, reason: str) -> None:
        self.current_state = to_state
        self.entries.append(
            {
                "kind": "STATE_TRANSITION",
                "timestamp": _now_iso(),
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
            }
        )
        self._persist()

    def record_decision(self, decision_dict: Dict) -> None:
        self.entries.append({"kind": "DECISION", "timestamp": _now_iso(), **decision_dict})
        self._persist()

    def record_tool_call(self, tool: str, input_summary: str, result_summary: str, evidence_references: Optional[List[str]] = None) -> None:
        self.entries.append(
            {
                "kind": "TOOL_CALL",
                "timestamp": _now_iso(),
                "tool": tool,
                "input_summary": input_summary,
                "result_summary": result_summary,
                "evidence_references": evidence_references or [],
            }
        )
        self._persist()

    def record_note(self, note: str) -> None:
        self.entries.append({"kind": "NOTE", "timestamp": _now_iso(), "note": note})
        self._persist()

    def record_approval(self, approval_dict: Dict) -> None:
        self.approval_state[approval_dict.get("approval_id", "UNKNOWN")] = approval_dict
        self.entries.append({"kind": "APPROVAL", "timestamp": _now_iso(), **approval_dict})
        self._persist()

    def to_dict(self) -> Dict:
        return {
            "orchestration_id": self.orchestration_id,
            "initiating_requirement_or_change": self.initiating_requirement_or_change,
            "created_at": self.created_at,
            "current_state": self.current_state,
            "approval_state": self.approval_state,
            "entries": self.entries,
        }


def load_journal(orchestration_id: str) -> Optional[Dict]:
    """Read-only reload of a persisted journal -- the basis for recovery
    (sec. 53): a caller can inspect `current_state`/`entries` to
    determine completed vs. pending stages without re-running anything."""
    path = JOURNAL_ROOT / f"{orchestration_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_journal_ids() -> List[str]:
    if not JOURNAL_ROOT.exists():
        return []
    return sorted(p.stem for p in JOURNAL_ROOT.glob("*.json"))
