"""
CP-MVP2-CR-001 Batch 1 — unit tests for `persistence/envelope.py`, the
shared versioning/collision-control primitive every new persist.py
module in this batch delegates to.
"""
from __future__ import annotations

from persistence.envelope import list_artifact_ids, load_history, load_latest, load_version, persist_artifact


def test_first_persist_creates_version_1(tmp_path):
    result = persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test")
    assert result["version"] == 1
    assert result["reused"] is False
    assert load_latest(tmp_path, "A-1") == {"x": 1}


def test_identical_payload_is_reused_not_versioned(tmp_path):
    persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test")
    second = persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test")
    assert second["reused"] is True
    assert second["version"] == 1
    assert len(load_history(tmp_path, "A-1")) == 1


def test_payload_differing_only_in_generated_at_is_still_reused(tmp_path):
    """generation_metadata.generated_at is the one genuinely volatile
    field every frozen schema already carries -- two otherwise-identical
    regenerations must not be treated as a real change."""
    persist_artifact(tmp_path, "A-1", {"x": 1, "generation_metadata": {"generated_at": "T1"}}, generator="test")
    second = persist_artifact(tmp_path, "A-1", {"x": 1, "generation_metadata": {"generated_at": "T2"}}, generator="test")
    assert second["reused"] is True
    assert second["version"] == 1


def test_different_payload_creates_a_new_immutable_version(tmp_path):
    persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test")
    second = persist_artifact(tmp_path, "A-1", {"x": 2}, generator="test")
    assert second["reused"] is False
    assert second["version"] == 2
    # the first version file is never mutated
    assert load_version(tmp_path, "A-1", 1) == {"x": 1}
    assert load_version(tmp_path, "A-1", 2) == {"x": 2}
    assert load_latest(tmp_path, "A-1") == {"x": 2}
    assert [h["version"] for h in load_history(tmp_path, "A-1")] == [1, 2]


def test_load_latest_returns_none_when_never_persisted(tmp_path):
    assert load_latest(tmp_path, "NEVER-WRITTEN") is None


def test_list_artifact_ids_lists_only_persisted_artifacts(tmp_path):
    persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test")
    persist_artifact(tmp_path, "A-2", {"x": 1}, generator="test")
    assert list_artifact_ids(tmp_path) == ["A-1", "A-2"]


def test_provenance_is_persisted_verbatim(tmp_path):
    persist_artifact(tmp_path, "A-1", {"x": 1}, generator="test-gen", provenance={"batch_id": "B1"})
    version_files = list((tmp_path / "A-1").glob("v*.json"))
    assert len(version_files) == 1
    import json
    envelope = json.loads(version_files[0].read_text())
    assert envelope["generator"] == "test-gen"
    assert envelope["provenance"] == {"batch_id": "B1"}
    assert envelope["artifact_id"] == "A-1"
    assert envelope["artifact_version"] == 1
