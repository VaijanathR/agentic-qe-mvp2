"""
CP-MVP2-CR-001 — shared, additive persistence primitives.

Implements the versioning/collision-control model from
docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md sec. 16/17: every new
`persist.py` module in this batch (testcases/, testdata/, automation/,
rbtp/, dependencies/, traceability/, execution/) is a thin, additive
wrapper around an existing frozen `to_dict()` representation, and every
one of them delegates the actual on-disk write/version/collision logic
to this single module rather than reimplementing it per checkpoint.

Design:
  - Every persisted artifact is IMMUTABLE once written: `persist_artifact`
    writes a new version file for a given `artifact_id`; an existing
    version file already on disk is NEVER edited, appended to, mutated,
    or deleted by this module.
  - A per-artifact, mutable POINTER file (`latest.json`) is the only
    thing this module ever rewrites — it only ever repoints to a version
    file's path plus an append-only `history` list; it never carries
    artifact content of its own.
  - Regeneration collision handling: the new payload is hashed after
    recursively stripping any key literally named `generated_at`
    (the one genuinely volatile field every frozen schema's
    `generation_metadata` already carries). If the stripped hash matches
    the current latest version's stripped hash, the payload is treated
    as "the same fact re-observed" — no new version is written, and the
    existing version is returned with `reused=True`. This is how a
    previously governed artifact is never silently overwritten with a
    byte-identical duplicate, while a genuinely different regeneration
    (e.g. a different real-LLM run) still gets its own new, distinct,
    permanently retained version.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _strip_volatile(obj: Any) -> Any:
    """Recursively removes any dict key literally named `generated_at`,
    so two payloads that differ only in when they were generated hash
    identically. Never mutates the caller's object."""
    if isinstance(obj, dict):
        return {k: _strip_volatile(v) for k, v in obj.items() if k != "generated_at"}
    if isinstance(obj, list):
        return [_strip_volatile(v) for v in obj]
    return obj


def _content_hash(payload: Dict) -> str:
    stripped = _strip_volatile(payload)
    canonical = json.dumps(stripped, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _artifact_dir(base_dir: Path, artifact_id: str) -> Path:
    return base_dir / artifact_id


def _version_path(base_dir: Path, artifact_id: str, version: int) -> Path:
    return _artifact_dir(base_dir, artifact_id) / f"v{version}.json"


def _pointer_path(base_dir: Path, artifact_id: str) -> Path:
    return _artifact_dir(base_dir, artifact_id) / "latest.json"


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def persist_artifact(
    base_dir: Path,
    artifact_id: str,
    payload: Dict,
    generator: str,
    provenance: Optional[Dict] = None,
) -> Dict:
    """Writes (or reuses) one immutable version of `payload` under
    `artifact_id`, updating the artifact's pointer file. Returns
    {"artifact_id", "version", "path", "reused", "content_hash"}.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    _artifact_dir(base_dir, artifact_id).mkdir(parents=True, exist_ok=True)

    new_hash = _content_hash(payload)
    pointer_file = _pointer_path(base_dir, artifact_id)
    pointer: Optional[Dict] = None
    if pointer_file.exists():
        pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
        if pointer.get("content_hash") == new_hash:
            return {
                "artifact_id": artifact_id,
                "version": pointer["latest_version"],
                "path": pointer["latest_path"],
                "reused": True,
                "content_hash": new_hash,
            }

    version = (pointer["latest_version"] + 1) if pointer else 1
    version_file = _version_path(base_dir, artifact_id, version)
    envelope = {
        "artifact_id": artifact_id,
        "artifact_version": version,
        "generated_at": _now(),
        "generator": generator,
        "provenance": provenance or {},
        "content_hash": new_hash,
        "payload": payload,
    }
    version_file.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")

    history: List[Dict] = list(pointer["history"]) if pointer else []
    history.append({"version": version, "path": _relative(version_file), "generated_at": envelope["generated_at"]})
    new_pointer = {
        "artifact_id": artifact_id,
        "latest_version": version,
        "latest_path": _relative(version_file),
        "content_hash": new_hash,
        "updated_at": envelope["generated_at"],
        "history": history,
    }
    pointer_file.write_text(json.dumps(new_pointer, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "artifact_id": artifact_id,
        "version": version,
        "path": _relative(version_file),
        "reused": False,
        "content_hash": new_hash,
    }


def load_latest(base_dir: Path, artifact_id: str) -> Optional[Dict]:
    """Returns the `payload` of the current latest version of
    `artifact_id`, or None if nothing has ever been persisted for it.
    Reads only immutable version-file content plus the pointer — never
    reconstructs or infers a payload."""
    pointer_file = _pointer_path(base_dir, artifact_id)
    if not pointer_file.exists():
        return None
    pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    version_file = REPO_ROOT / pointer["latest_path"]
    envelope = json.loads(version_file.read_text(encoding="utf-8"))
    return envelope["payload"]


def load_version(base_dir: Path, artifact_id: str, version: int) -> Optional[Dict]:
    version_file = _version_path(base_dir, artifact_id, version)
    if not version_file.exists():
        return None
    envelope = json.loads(version_file.read_text(encoding="utf-8"))
    return envelope["payload"]


def list_artifact_ids(base_dir: Path) -> List[str]:
    if not base_dir.exists():
        return []
    return sorted(p.name for p in base_dir.iterdir() if p.is_dir() and _pointer_path(base_dir, p.name).exists())


def load_history(base_dir: Path, artifact_id: str) -> List[Dict]:
    pointer_file = _pointer_path(base_dir, artifact_id)
    if not pointer_file.exists():
        return []
    pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    return pointer["history"]
