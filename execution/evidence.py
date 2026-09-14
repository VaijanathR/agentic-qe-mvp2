"""
CP-MVP2-06 — evidence capture and management.

Per the frozen specification sec. 12: every reported conclusion must be
traceable to evidence actually captured during that specific execution.
This module writes real files to `runs/` (an existing, already-
`.gitignore`d project convention for runtime artifacts — see
`.gitignore`'s "Runtime artifacts: runs/, evidence/" entry) — it never
returns a path to something that was not actually written.

Per spec sec. 21: redaction is applied defensively to any logged field
value whose field NAME suggests a credential-shaped field (e.g.
"password"), regardless of whether the underlying value is synthetic —
a screenshot could visually expose a filled password field even when
the value itself is CP-MVP2-04 synthetic data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs" / "cp_mvp2_06"

_REDACT_FIELD_NAME_MARKERS = ("password", "token", "secret", "api_key", "apikey", "credential")


def redact_field_value(field_name: str, value) -> str:
    if field_name and any(marker in field_name.lower() for marker in _REDACT_FIELD_NAME_MARKERS):
        return "[REDACTED]"
    return str(value)


class EvidenceManager:
    """One instance per execution. Every method writes a real file and
    returns its path relative to the repo root — never a fabricated
    reference to a file that was not written."""

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.directory = RUNS_DIR / execution_id
        self.directory.mkdir(parents=True, exist_ok=True)
        self._log_lines: List[str] = []

    def _relative(self, path: Path) -> str:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")

    def log(self, line: str) -> None:
        self._log_lines.append(line)

    def flush_log(self) -> str:
        path = self.directory / "execution.log"
        path.write_text("\n".join(self._log_lines) + "\n", encoding="utf-8")
        return self._relative(path)

    def write_json(self, name: str, data: dict) -> str:
        path = self.directory / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return self._relative(path)

    def screenshot_path(self, name: str) -> Path:
        """Returns the real filesystem path a caller (the browser
        engine) should pass to Playwright's own page.screenshot(path=...)
        -- this module never fabricates the image bytes itself; only the
        actual Playwright call produces them."""
        return self.directory / name

    def screenshot_relative(self, name: str) -> str:
        return self._relative(self.directory / name)
