"""
Agentic QE Orchestration -- adapter from the Enhancement-02 real testcase
corpus (`automation/playwright/enh02_testcases.py`) to CP-MVP2-03's
`testcases.schema.GovernedTestcase` shape.

Why this exists: CP-MVP2-03's real, persisted testcase corpus
(`testcases/generated/`) only covers 4 requirements from the original
MVP2 vertical slice (REQ-REG-01, REQ-ACO-03, REQ-CART-03, REQ-PAY-01).
Enhancement-02's own, separate, real, 27-testcase corpus is not persisted
through `testcases.persist` (a deliberate, disclosed scope boundary --
Enhancement-02 has its own dataset/coverage-matrix conventions). For the
orchestrator's Risk/Impact/Test-Strategy stages to work for an
Enhancement-02-era requirement (this project's real majority, 32/35), this
module performs a structural, field-preserving adaptation -- no content is
invented; every field maps 1:1 from the real, governed
`ENH02_TESTCASES`/`ENH02-TC-*` entries.

`test_type` mapping: Enhancement-02 uses this project's four-way
POSITIVE/NEGATIVE/ALTERNATE/EXCEPTIONAL vocabulary (CP-03's testcase
schema, sec. established by `testcases/schema.py::ScenarioType`, extended
informally); CP-03's own `ScenarioType` enum only defines
POSITIVE/ALTERNATE/EXCEPTIONAL. NEGATIVE maps to EXCEPTIONAL here (the
closest existing concept -- a negative/exceptional path), a disclosed,
one-line mapping, never silently redefining either vocabulary.
"""
from __future__ import annotations

from typing import List, Optional

from automation.playwright.enh02_testcases import ENH02_TESTCASES
from testcases.schema import GovernanceStatus, GovernedTestcase, ScenarioType, Testcase

_TEST_TYPE_TO_SCENARIO_TYPE = {
    "POSITIVE": ScenarioType.POSITIVE,
    "ALTERNATE": ScenarioType.ALTERNATE,
    "EXCEPTIONAL": ScenarioType.EXCEPTIONAL,
    "NEGATIVE": ScenarioType.EXCEPTIONAL,
}


def _to_governed_testcase(entry: dict) -> GovernedTestcase:
    testcase = Testcase(
        testcase_id=entry["testcase_id"],
        title=entry["title"],
        requirement_ids=list(entry["requirement_ids"]),
        scenario_type=_TEST_TYPE_TO_SCENARIO_TYPE.get(entry["test_type"], ScenarioType.POSITIVE),
        preconditions=list(entry.get("preconditions", [])),
        test_steps=list(entry.get("business_steps", [])),
        expected_result=entry.get("expected_result", ""),
        priority=entry.get("priority", "MEDIUM"),
        journey_id=None,
        test_data_reference=entry["dataset_ids"][0] if entry.get("dataset_ids") else None,
        source_attribution=[{"source": "automation/playwright/enh02_testcases.py", "objective": entry.get("objective", "")}],
        generation_metadata={"generator": "Post-MVP2 Enhancement 02 real testcase corpus (adapted, not regenerated)"},
    )
    # Every Enhancement-02 testcase is already real, evidence-backed, and
    # (per the requirement coverage matrix) automated -- ACCEPTED is the
    # accurate governance status, never re-derived by this adapter.
    return GovernedTestcase(testcase=testcase, governance_status=GovernanceStatus.ACCEPTED, reasons=[])


def governed_testcases_for_requirement(requirement_id: str) -> List[GovernedTestcase]:
    return [
        _to_governed_testcase(e) for e in ENH02_TESTCASES
        if requirement_id in e.get("requirement_ids", [])
    ]


def governed_testcase_by_id(testcase_id: str) -> Optional[GovernedTestcase]:
    for e in ENH02_TESTCASES:
        if e["testcase_id"] == testcase_id:
            return _to_governed_testcase(e)
    return None


def all_governed_testcases() -> List[GovernedTestcase]:
    return [_to_governed_testcase(e) for e in ENH02_TESTCASES]
