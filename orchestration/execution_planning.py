"""
Agentic QE Orchestration -- Execution Planning (governing instruction
sec. 26, 27, 28, 50, 51).

Parallel-safety classification (sec. 27) is not guessed: it reflects
real, demonstrated behavior already discovered and disclosed in the
Enhancement-02 closure work --
`docs/claude-execution-reports/ENHANCEMENT-02/ENHANCEMENT-02-FINAL-FREEZE-REPORT-20260915-181704.md`'s
own Defect #2 documents that the sequential, real-account-creating chain
(`test_enh02_shared_account.py`) reliably fails under real `pytest -n 4`
concurrency (a real, reproduced finding, not a hypothesis), while every
other Enhancement-02 test file is real, demonstrated `SAFE_TO_PARALLELIZE`
(the same report's own "11/11 PASS under pytest -n 4" evidence). Anything
this module has not real-evidence for is honestly UNKNOWN, never guessed
SAFE.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


class ParallelSafety:
    SAFE_TO_PARALLELIZE = "SAFE_TO_PARALLELIZE"
    STATE_DEPENDENT = "STATE_DEPENDENT"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    UNKNOWN = "UNKNOWN"


class ExecutionMode:
    DRY_RUN = "DRY_RUN"
    REAL_EXECUTION = "REAL_EXECUTION"


#: Real, demonstrated classification (Enhancement-02 evidence, see module
#: docstring) -- keyed by the real Playwright test module basename.
_KNOWN_PARALLEL_SAFETY = {
    "test_enh01_registration.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_catalog.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_configurable_and_cart.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_guest_checkout.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_registration_negative.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_wishlist.py": ParallelSafety.SAFE_TO_PARALLELIZE,
    "test_enh02_shared_account.py": ParallelSafety.STATE_DEPENDENT,
    "test_gco03_post_freeze_validation.py": ParallelSafety.STATE_DEPENDENT,
}


def classify_parallel_safety(test_module_basename: str) -> str:
    return _KNOWN_PARALLEL_SAFETY.get(test_module_basename, ParallelSafety.UNKNOWN)


@dataclass
class ExecutionPlan:
    requirement_id: str
    mode: str
    testcase_ids: List[str]
    automation_ids: List[str]
    dataset_ids: List[str]
    parallel_safety: str
    creates_permanent_state: bool
    permanent_state_authorization_reference: Optional[str]
    governance_gates: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def build_plan(
    requirement_id: str,
    testcase_ids: List[str],
    automation_ids: List[str],
    dataset_ids: List[str],
    mode: str,
    test_module_basename: Optional[str] = None,
    creates_permanent_state: bool = False,
    permanent_state_authorization_reference: Optional[str] = None,
) -> ExecutionPlan:
    parallel_safety = (
        classify_parallel_safety(test_module_basename) if test_module_basename else ParallelSafety.UNKNOWN
    )
    governance_gates = ["valid_state_transition", "evidence_not_fabricated"]
    if creates_permanent_state:
        governance_gates.append("permanent_state_authorization")

    steps = [
        f"Select automation: {automation_ids or '(none -- generation required first)'}",
        f"Select dataset(s): {dataset_ids or '(none required)'}",
        f"Execution mode: {mode}",
        f"Parallel safety: {parallel_safety}"
        + (" -- run standalone, not combined with other files under pytest -n 4" if parallel_safety == ParallelSafety.STATE_DEPENDENT else ""),
    ]
    if mode == ExecutionMode.REAL_EXECUTION:
        steps.append("REAL_EXECUTION: will invoke real Windows Playwright Chromium against the real SUT.")
    else:
        steps.append("DRY_RUN: no SUT interaction will occur; this plan is display-only.")

    return ExecutionPlan(
        requirement_id=requirement_id,
        mode=mode,
        testcase_ids=list(testcase_ids),
        automation_ids=list(automation_ids),
        dataset_ids=list(dataset_ids),
        parallel_safety=parallel_safety,
        creates_permanent_state=creates_permanent_state,
        permanent_state_authorization_reference=permanent_state_authorization_reference,
        governance_gates=governance_gates,
        steps=steps,
    )
