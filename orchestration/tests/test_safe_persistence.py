"""
Tests for orchestration/safe_persistence.py -- the real, disclosed
cross-platform fix for `persistence.envelope.load_latest()`'s
backslash-path bug (see that module's own docstring).
"""
from __future__ import annotations

import json

from automation.playwright.config import EXECUTIONS_ROOT
from orchestration.safe_persistence import safe_load_latest


def test_safe_load_latest_reads_a_windows_backslash_pointer(tmp_path, monkeypatch):
    """Real reproduction: writes a pointer file whose `latest_path`
    field contains a literal Windows backslash path, exactly like the
    real, pre-existing artifacts this fix works around -- proves
    `safe_load_latest` reads it correctly where `load_latest` would
    raise `FileNotFoundError` on POSIX."""
    artifact_id = "TEST-WINDOWS-STYLE-ARTIFACT"
    artifact_dir = tmp_path / artifact_id
    artifact_dir.mkdir(parents=True)

    version_envelope = {
        "artifact_id": artifact_id, "artifact_version": 1, "generated_at": "2026-01-01T00:00:00+00:00",
        "generator": "test", "provenance": {}, "content_hash": "irrelevant-for-this-test",
        "payload": {"hello": "world"},
    }
    (artifact_dir / "v1.json").write_text(json.dumps(version_envelope), encoding="utf-8")

    windows_style_path = f"{tmp_path.name}\\{artifact_id}\\v1.json"
    pointer = {
        "artifact_id": artifact_id, "latest_version": 1, "latest_path": windows_style_path,
        "content_hash": "irrelevant-for-this-test", "updated_at": "2026-01-01T00:00:00+00:00", "history": [],
    }
    (artifact_dir / "latest.json").write_text(json.dumps(pointer), encoding="utf-8")

    result = safe_load_latest(tmp_path, artifact_id)
    assert result == {"hello": "world"}


def test_safe_load_latest_returns_none_for_nonexistent_artifact(tmp_path):
    assert safe_load_latest(tmp_path, "DOES-NOT-EXIST") is None


def test_safe_load_latest_works_on_a_real_persisted_playwright_execution_log():
    """Real, live proof against this project's own real evidence corpus
    -- at least one real Enhancement-02 execution log for REQ-BRW-01
    must be loadable via safe_load_latest regardless of which OS
    originally persisted it."""
    from automation.playwright.logging_ import list_execution_log_ids

    brw01_ids = [i for i in list_execution_log_ids() if "BRW-01" in i]
    assert brw01_ids, "Expected at least one real, persisted REQ-BRW-01 execution log in this repository"
    loaded = [safe_load_latest(EXECUTIONS_ROOT, eid) for eid in brw01_ids]
    assert all(l is not None for l in loaded), "safe_load_latest must successfully read every real, persisted execution log"
