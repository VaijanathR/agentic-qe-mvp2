"""
Agentic QE Orchestration -- Resume / Recovery (Orchestration Expansion
instruction, Phase N).

A governed resume mechanism built entirely on the real, persisted
orchestration journal (`orchestration.journal`) -- never re-derives state
from scratch, never blindly restarts. `plan_resume()` is pure,
deterministic inspection: it never re-executes anything itself; the
caller (`Orchestrator.resume_batch()`) uses its output to decide what to
run next.

A completed requirement (one whose real execution log already shows a
terminal status: PASS, FAIL, or ERROR) is never re-executed by resume --
this is what "avoid duplicate unsafe execution" (Phase N) means in
practice: a requirement whose real, permanent SUT action (if any) already
ran is treated as done, not retried, regardless of PASS/FAIL.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from orchestration.journal import load_journal


class ResumeState:
    NOT_FOUND = "NOT_FOUND"
    ALREADY_COMPLETE = "ALREADY_COMPLETE"
    RESUMABLE = "RESUMABLE"
    NO_PENDING_WORK = "NO_PENDING_WORK"


@dataclass
class ResumePlan:
    orchestration_id: str
    resume_state: str
    selected_requirements: List[str] = field(default_factory=list)
    completed_requirement_ids: List[str] = field(default_factory=list)
    pending_requirement_ids: List[str] = field(default_factory=list)
    last_known_state: Optional[str] = None
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def plan_resume(orchestration_id: str) -> ResumePlan:
    journal = load_journal(orchestration_id)
    if journal is None:
        return ResumePlan(
            orchestration_id=orchestration_id, resume_state=ResumeState.NOT_FOUND,
            note=f"No persisted journal found for {orchestration_id!r} -- nothing to resume.",
        )

    summary = journal.get("summary") or {}
    selected = summary.get("selected_requirements") or []
    completed = summary.get("completed_requirement_ids") or []
    pending = [r for r in selected if r not in completed]

    if journal.get("current_state") == "FINAL_REPORT":
        return ResumePlan(
            orchestration_id=orchestration_id, resume_state=ResumeState.ALREADY_COMPLETE,
            selected_requirements=selected, completed_requirement_ids=completed, pending_requirement_ids=[],
            last_known_state=journal.get("current_state"),
            note="This orchestration already reached FINAL_REPORT -- resuming would duplicate real work; nothing to do.",
        )

    if not pending:
        return ResumePlan(
            orchestration_id=orchestration_id, resume_state=ResumeState.NO_PENDING_WORK,
            selected_requirements=selected, completed_requirement_ids=completed, pending_requirement_ids=[],
            last_known_state=journal.get("current_state"),
            note="Every selected requirement is already marked completed, but the orchestration did not reach "
                 "FINAL_REPORT -- likely interrupted during final reporting/regression; safe to re-run only the "
                 "reporting stage, not any requirement's real execution.",
        )

    return ResumePlan(
        orchestration_id=orchestration_id, resume_state=ResumeState.RESUMABLE,
        selected_requirements=selected, completed_requirement_ids=completed, pending_requirement_ids=pending,
        last_known_state=journal.get("current_state"),
        note=f"Interrupted at state {journal.get('current_state')!r} with {len(pending)} of {len(selected)} "
             f"requirement(s) still pending real completion: {pending}. Completed requirements "
             f"{completed} will NOT be re-executed.",
    )
