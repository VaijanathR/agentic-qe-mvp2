"""
Testcase-step <-> automation-step traceability — additive only.

Reuses the existing architecture rather than inventing a parallel one:
`PlaywrightStep.step_order` (frozen `automation.schema`) is the only
automation-step identity this project already has, and `Testcase.test_steps`
(frozen `testcases.schema`) is the only testcase-step identity it already
has (a plain, ordered list of strings — no per-step ID field exists in
the frozen schema; step *identity* is therefore its list index, the only
mechanism the frozen schema actually provides).

Deterministic mapping rule (disclosed, not a semantic/LLM interpretation
of business meaning):
  - If there is exactly one testcase step, every automation step
    (including the business-assertion evaluation) maps to it.
  - If there are 2+ testcase steps, the LAST testcase step is treated as
    the "observe the result" step and maps to the artifact's
    BUSINESS_REQUIRED assertion evaluation only (which, per the frozen
    CP-MVP2-06 contract, is evaluated after every action step
    completes — never interleaved). Every OTHER testcase step shares the
    automation's action steps (NAVIGATE/FILL/CLICK/SELECT/WAIT) in
    order, split as evenly as the step count allows, preserving
    automation `step_order` strictly ascending across the mapping.

This is a **structural allocation**, not a claim that automation step N
specifically implements the business *meaning* of testcase step M — it
only guarantees full coverage, no orphans, and order preservation. Today's
entire real, persisted testcase corpus uses the disclosed, deterministic
`StubLLMClient` narrative ("Perform the action described by the approved
requirement." / "Observe the resulting system behavior.") — exactly 2
generic steps — so in practice this always resolves to the simple
1-concrete-step + 1-observe-step case for every real artifact today. This
is a genuine, disclosed TESTCASE-content limitation (not a CP-05
automation-generation defect); see the accompanying execution report for
the full analysis. This module does not invent richer steps to compensate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from automation.schema import ActionType

#: Action types this module treats as automation "business actions"
#: eligible for step-mapping (mirrors automation.schema's own action
#: vocabulary; ASSERT is handled separately, mapped to the final
#: testcase step, never mixed into the action-step allocation).
_ACTION_STEP_TYPES = {ActionType.NAVIGATE, ActionType.FILL, ActionType.CLICK, ActionType.SELECT, ActionType.WAIT}


@dataclass
class TestcaseStepMapping:
    __test__ = False  # not a pytest test class; name follows this project's "testcase" vocabulary

    testcase_step_index: int
    testcase_step_text: str
    automation_step_orders: List[int] = field(default_factory=list)
    #: True for the (at most one) testcase step this mapping treats as
    #: "observe/verify the result" -- covered by the artifact's
    #: `assertions` list, which (per the frozen `automation.schema`)
    #: is a separate top-level field, not a `steps` entry with its own
    #: `step_order`. Kept as an explicit, disclosed flag rather than a
    #: fabricated step_order, since the frozen schema provides none.
    maps_to_assertions: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def build_step_mapping(test_steps: List[str], automation_steps: List[Dict], has_assertions: bool = True) -> List[TestcaseStepMapping]:
    """`automation_steps` is a list of raw step dicts (as persisted --
    each with `step_order`/`action_type`), never re-authored here."""
    action_orders = [s["step_order"] for s in automation_steps if s["action_type"] in _ACTION_STEP_TYPES]

    if len(test_steps) <= 1:
        text = test_steps[0] if test_steps else ""
        return [TestcaseStepMapping(0, text, sorted(action_orders), maps_to_assertions=has_assertions)]

    n_action_steps = len(test_steps) - 1  # all but the final "observe" step
    mappings: List[TestcaseStepMapping] = []
    if n_action_steps > 0 and action_orders:
        # Even, order-preserving split of the real action steps across
        # the non-final testcase steps.
        base, remainder = divmod(len(action_orders), n_action_steps)
        cursor = 0
        for i in range(n_action_steps):
            take = base + (1 if i < remainder else 0)
            chunk = action_orders[cursor:cursor + take]
            cursor += take
            mappings.append(TestcaseStepMapping(i, test_steps[i], chunk))
    else:
        for i in range(n_action_steps):
            mappings.append(TestcaseStepMapping(i, test_steps[i], []))

    mappings.append(TestcaseStepMapping(len(test_steps) - 1, test_steps[-1], [], maps_to_assertions=has_assertions))
    return mappings


def validate_full_coverage(mappings: List[TestcaseStepMapping], test_steps: List[str]) -> dict:
    covered_indices = {
        m.testcase_step_index for m in mappings
        if m.automation_step_orders or m.maps_to_assertions
    }
    all_indices = set(range(len(test_steps)))
    missing = sorted(all_indices - covered_indices)
    return {"check": "full_testcase_step_coverage", "passed": not missing, "detail": {"missing_testcase_steps": missing}}


def validate_no_orphan_automation_steps(mappings: List[TestcaseStepMapping], automation_steps: List[Dict]) -> dict:
    mapped_orders = {o for m in mappings for o in m.automation_step_orders}
    business_action_orders = {s["step_order"] for s in automation_steps if s["action_type"] in _ACTION_STEP_TYPES}
    orphans = sorted(business_action_orders - mapped_orders)
    return {"check": "no_orphan_automation_steps", "passed": not orphans, "detail": {"orphan_step_orders": orphans}}


def validate_order_preserved(mappings: List[TestcaseStepMapping]) -> dict:
    """The maximum automation step_order assigned to testcase step i
    must never exceed the minimum assigned to testcase step i+1 --
    i.e. mapped business order never regresses."""
    problems: List[str] = []
    prev_max = -1
    for m in sorted(mappings, key=lambda x: x.testcase_step_index):
        if not m.automation_step_orders:
            continue
        this_min = min(m.automation_step_orders)
        this_max = max(m.automation_step_orders)
        if this_min < prev_max:
            problems.append(f"testcase_step_{m.testcase_step_index}_out_of_order")
        prev_max = max(prev_max, this_max)
    return {"check": "testcase_step_order_preserved", "passed": not problems, "detail": problems}
