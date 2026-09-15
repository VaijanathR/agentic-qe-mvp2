"""
Agentic QE Orchestration -- a real, cross-platform-safe substitute for
`persistence.envelope.load_latest()`.

**Real bug found and worked around (never fixed in the frozen file
itself):** `persistence.envelope.load_latest()` resolves
`REPO_ROOT / pointer["latest_path"]`, trusting the `latest_path` string
stored inside the pointer file at write time. When an artifact was
persisted by a Windows-native Python process (`.venv\\Scripts\\python.exe`
-- the required acceptance-execution environment for this whole project,
per every prior governing instruction's Windows-execution gate),
`pathlib.Path.relative_to()`/`str()` renders that path with backslash
separators. Reading it back from a POSIX process (this orchestration
package's own WSL-side analysis/coordination work, per this project's
established WSL-orchestration/Windows-execution split) then fails with
`FileNotFoundError`, because POSIX treats the literal backslash as an
ordinary filename character, not a path separator.

This affects the *majority* of this project's real execution-log/testcase/
testdata evidence, since nearly all of it was legitimately persisted via
the Windows venv. It is a real, pre-existing, disclosed defect in frozen,
shared infrastructure (`persistence/envelope.py`) this orchestration
package must not modify (governing instruction sec. 4: protected
historical asset). The fix implemented here is additive and equivalent:
`persistence.envelope.load_version()` builds its file path itself, via
plain `pathlib` joins (`base_dir / artifact_id / f"v{version}.json"`),
never from a stored string -- so it is unaffected by the bug. This module
reads the pointer file directly (itself a safe, freshly-joined path) for
`latest_version` (a plain int, no path-separator concern), then calls the
frozen, unmodified `load_version()` -- reusing existing infrastructure,
never reimplementing the persistence format.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from persistence.envelope import load_version


def safe_load_latest(base_dir: Path, artifact_id: str) -> Optional[Dict]:
    pointer_file = base_dir / artifact_id / "latest.json"
    if not pointer_file.exists():
        return None
    try:
        pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    latest_version = pointer.get("latest_version")
    if latest_version is None:
        return None
    return load_version(base_dir, artifact_id, latest_version)


def safe_list_artifact_ids(base_dir: Path) -> List[str]:
    """Equivalent to `persistence.envelope.list_artifact_ids()`, reused
    unmodified -- listing directory names never touches the buggy stored
    path field, so no replacement is needed there; re-exported here only
    so callers can import both list/load helpers from one place."""
    from persistence.envelope import list_artifact_ids

    return list_artifact_ids(base_dir)
