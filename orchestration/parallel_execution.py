"""
Agentic QE Orchestration -- real, local multi-worker parallel execution
(Orchestration Expansion instruction, Phase G).

Genuinely invokes real `pytest -n <workers>` (pytest-xdist) as a real
subprocess against the real, existing Playwright test files whose
requirements were classified `SAFE_PARALLEL` by
`orchestration.dependency_planning` -- never a simulated or claimed
parallel run. This is LOCAL multi-worker parallelism only; distributed
(multi-machine) execution is not attempted and is never claimed (sec. 8:
"Never claim distributed execution without multiple execution
environments" -- `distributed_execution` is always reported as
`CONFIGURED / NOT_IMPLEMENTED`, per governing precedent).

This module never launches its own subprocess silently as a side effect
of import -- `run_real_parallel()` must be called explicitly, and it
always uses the project's own real Windows venv interpreter
(`sys.executable`, i.e. whatever interpreter this module itself is
running under -- the caller is responsible for running this under the
real Windows `.venv\\Scripts\\python.exe` for the result to count as a
real Windows execution).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from persistence.envelope import REPO_ROOT

DISTRIBUTED_EXECUTION_STATUS = "CONFIGURED / NOT_IMPLEMENTED"


def run_real_parallel(test_file_relative_paths: List[str], workers: int = 2, timeout_seconds: float = 300.0) -> Dict:
    """Runs `pytest -n <workers> <files>` for real, as a real subprocess,
    against the real SUT. Returns a real, parsed summary
    (`passed`/`failed`/`skipped`/`raw_tail`) -- never fabricates a
    result if the subprocess cannot be started or times out (reports
    `status: BLOCKED` instead, mirroring this project's own established
    CP-08 "never fabricate PASS" discipline)."""
    argv = [sys.executable, "-m", "pytest", "-n", str(workers), "-q", *test_file_relative_paths]
    try:
        completed = subprocess.run(
            argv, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "BLOCKED",
            "reason": f"Real pytest -n {workers} subprocess timed out after {timeout_seconds}s.",
            "command": argv,
        }
    except OSError as exc:
        return {"status": "BLOCKED", "reason": f"Failed to start real pytest subprocess: {exc}", "command": argv}

    stdout = completed.stdout or ""
    summary_line = next((l for l in reversed(stdout.splitlines()) if " passed" in l or " failed" in l or " error" in l), "")

    import re

    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", summary_line)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", summary_line)) else 0
    skipped = int(m.group(1)) if (m := re.search(r"(\d+) skipped", summary_line)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", summary_line)) else 0

    return {
        "status": "COMPLETE",
        "command": argv,
        "workers": workers,
        "returncode": completed.returncode,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "summary_line": summary_line.strip(),
        "distributed_execution": DISTRIBUTED_EXECUTION_STATUS,
    }
