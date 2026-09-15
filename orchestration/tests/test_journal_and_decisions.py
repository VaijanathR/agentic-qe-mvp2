"""Tests for orchestration/journal.py and decisions.py."""
from __future__ import annotations

from orchestration.decisions import make_decision
from orchestration.ids import new_decision_id, new_orchestration_id
from orchestration.journal import OrchestrationJournal, load_journal


def test_orchestration_id_format():
    oid = new_orchestration_id()
    assert oid.startswith("ORCH-")
    parts = oid.split("-")
    assert len(parts) == 4  # ORCH, date, time, suffix


def test_two_ids_generated_immediately_are_unique():
    ids = {new_orchestration_id() for _ in range(20)}
    assert len(ids) == 20


def test_decision_record_round_trips():
    oid = new_orchestration_id()
    decision = make_decision(
        orchestration_id=oid, stage="RISK_ASSESSED", input_references=["REQ-BRW-01"],
        decision="RISK_ASSESSED", reason="test reason", confidence="HIGH", risk="P1",
    )
    d = decision.to_dict()
    assert d["orchestration_id"] == oid
    assert d["stage"] == "RISK_ASSESSED"
    assert d["decision_id"].startswith("DEC-")


def test_journal_persists_and_reloads():
    oid = new_orchestration_id()
    journal = OrchestrationJournal(oid, "REQ-BRW-01")
    journal.record_transition(None, "RECEIVED", "test start")
    journal.record_decision({"decision": "X", "reason": "Y"})
    journal.record_note("a note")

    reloaded = load_journal(oid)
    assert reloaded is not None
    assert reloaded["orchestration_id"] == oid
    assert reloaded["current_state"] == "RECEIVED"
    assert len(reloaded["entries"]) == 3


def test_journal_never_stores_hidden_chain_of_thought_field():
    """No entry kind in this module ever includes a
    'chain_of_thought'/'internal_reasoning' key -- only concise,
    structured fields (governing instruction sec. 37)."""
    oid = new_orchestration_id()
    journal = OrchestrationJournal(oid, "REQ-BRW-01")
    journal.record_decision({"decision": "X", "reason": "Y"})
    for entry in journal.entries:
        assert "chain_of_thought" not in entry
        assert "internal_reasoning" not in entry
