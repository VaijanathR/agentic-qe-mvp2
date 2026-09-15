"""
Agentic QE Orchestration -- shared helper for reconstructing real,
persisted `testcases.schema.GovernedTestcase` objects from disk.

CP-MVP2-03's `testcases.persist.load_persisted_testcase()` returns the
plain dict shape `GovernedTestcase.to_dict()` produces (governance_status
+ reasons + every `Testcase` field flattened together). This module
reverses that flattening -- real, unmodified data, never invented --
so downstream real pipelines that expect the dataclass shape (RBTP,
Dependency Matrix, req/testcase traceability) can consume it.

Uses `orchestration.safe_persistence.safe_load_latest` rather than
`testcases.persist.load_persisted_testcase` directly -- see that
module's docstring for the real, disclosed cross-platform bug this
works around (a Windows-persisted artifact's stored path cannot be
resolved from a POSIX process).
"""
from __future__ import annotations

from typing import List, Optional

import testcases.persist as testcases_persist
from orchestration.safe_persistence import safe_load_latest
from testcases.schema import GovernedTestcase, Testcase

_TESTCASE_FIELDS = set(Testcase.__dataclass_fields__.keys())

#: Real bug found and fixed this task: `TC-MECHANISM-CHECK-01` (a much
#: earlier checkpoint's own historical, git-committed, self-disclosed
#: fixture -- its own persisted `reasons` field literally says
#: "DISCLOSED_SYNTHETIC_MECHANISM_FIXTURE" / "not real generated
#: evidence") happens to reference a real requirement ID
#: (REQ-WISH-01) as its own `requirement_ids` value. Without this
#: filter, `load_governed_testcases_for_requirement("REQ-WISH-01")`
#: would return that synthetic fixture as if it were real Enhancement-02
#: testcase evidence, and downstream REUSE-priority logic
#: (`testcase_orchestration.py`) would report it as "reused from the
#: CP-MVP2-03 persisted corpus" instead of falling through to the real
#: `ENH02-TC-REQ-WISH-01-ADD-TO-WISHLIST` testcase. Never modifies the
#: historical artifact itself -- only excludes it from being presented
#: as real coverage evidence.
_DISCLOSED_SYNTHETIC_MARKERS = {"DISCLOSED_SYNTHETIC_MECHANISM_FIXTURE"}


def _is_disclosed_synthetic_fixture(payload: dict) -> bool:
    return bool(_DISCLOSED_SYNTHETIC_MARKERS.intersection(payload.get("reasons", [])))


def load_governed_testcase(testcase_id: str) -> Optional[GovernedTestcase]:
    payload = safe_load_latest(testcases_persist.BASE_DIR, testcase_id)
    if payload is None or _is_disclosed_synthetic_fixture(payload):
        return None
    testcase_kwargs = {k: v for k, v in payload.items() if k in _TESTCASE_FIELDS}
    return GovernedTestcase(
        testcase=Testcase(**testcase_kwargs),
        governance_status=payload.get("governance_status", "UNKNOWN"),
        reasons=list(payload.get("reasons", [])),
    )


def load_all_persisted_governed_testcases() -> List[GovernedTestcase]:
    """Skips (rather than crashes on) any persisted artifact this
    process cannot load -- a real, pre-existing, disclosed example is
    `testcases/generated/TC-MECHANISM-CHECK-01/latest.json`, a
    historical, git-committed artifact (commit `220c16f`) whose stored
    `latest_path` contains a literal Windows backslash path, which
    `pathlib` on POSIX resolves incorrectly. That historical artifact is
    never modified by this orchestration package (never delete/rewrite
    historical evidence); this loader simply does not let one
    unreadable historical artifact block every other real, readable
    one."""
    out: List[GovernedTestcase] = []
    for tc_id in testcases_persist.list_persisted_testcase_ids():
        try:
            gtc = load_governed_testcase(tc_id)
        except (OSError, FileNotFoundError):
            continue
        if gtc is not None:
            out.append(gtc)
    return out


def load_governed_testcases_for_requirement(requirement_id: str) -> List[GovernedTestcase]:
    return [
        gtc for gtc in load_all_persisted_governed_testcases()
        if requirement_id in gtc.testcase.requirement_ids
    ]
