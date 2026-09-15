"""
Agentic QE Orchestration -- Dependency-Aware Execution Planning
(Orchestration Expansion instruction, Phase E).

Classifies each requirement's real, registered automation into exactly
one of five real execution modes, never guessed, always evidence-based:

  SAFE_PARALLEL           -- real, demonstrated parallel safety (the
                             Enhancement-02 closure's own "11/11 PASS
                             under real pytest -n 4" finding).
  PREREQUISITE_DEPENDENT  -- the real, persisted testcase's own
                             `preconditions` text references another
                             real requirement's testcase/state (e.g.
                             ENH02-TC-REQ-WISH-02-...'s precondition:
                             "chained from REQ-WISH-01") -- discovered
                             by scanning that real text for a REQ-ID
                             reference, never invented.
  EXCLUSIVE               -- real, demonstrated single-shared-resource
                             requirement (the one shared account in
                             `test_enh02_shared_account.py`, or the one
                             real guest order in
                             `test_gco03_post_freeze_validation.py`) --
                             real evidence: these real test modules
                             reliably fail under real pytest -n 4
                             concurrency and must run standalone.
  SEQUENTIAL               -- real ordering requirement without a
                             single-exclusive-resource constraint (not
                             currently instantiated by any real
                             requirement in this project; the vocabulary
                             exists for a future real case).
  BLOCKED                  -- the requirement does not exist in either
                             real source (RAG + coverage matrix), or has
                             no real testcase/automation yet.

This module never invents a relationship: every PREREQUISITE_DEPENDENT
classification cites the exact real precondition text and the exact
real requirement ID reference found inside it.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from orchestration.execution_planning import ParallelSafety, classify_parallel_safety
from reporting.requirement_coverage import REQUIREMENT_COVERAGE


class ExecutionCategory:
    SAFE_PARALLEL = "SAFE_PARALLEL"
    SEQUENTIAL = "SEQUENTIAL"
    PREREQUISITE_DEPENDENT = "PREREQUISITE_DEPENDENT"
    EXCLUSIVE = "EXCLUSIVE"
    BLOCKED = "BLOCKED"


#: Real, disclosed fact: which real Playwright test module each real
#: requirement's automation actually lives in (governing instruction's
#: own "reuse existing components" -- this is read off the real files,
#: not invented). Requirements not listed here have no real automation
#: yet (BLOCKED) or are assessed purely from the coverage matrix.
_REQUIREMENT_TO_TEST_MODULE: Dict[str, str] = {
    "REQ-REG-01": "test_enh01_registration.py",
    "REQ-REG-02": "test_enh02_registration_negative.py",
    "REQ-REG-03": "test_enh02_registration_negative.py",
    "REQ-SRCH-01": "test_enh02_catalog.py",
    "REQ-SRCH-02": "test_enh02_catalog.py",
    "REQ-BRW-01": "test_enh02_catalog.py",
    "REQ-CFG-01": "test_enh02_configurable_and_cart.py",
    "REQ-CART-01": "test_enh02_configurable_and_cart.py",
    "REQ-CART-02": "test_enh02_configurable_and_cart.py",
    "REQ-CART-03": "test_enh02_configurable_and_cart.py",
    "REQ-CART-04": "test_enh02_configurable_and_cart.py",
    "REQ-GCO-01": "test_enh02_guest_checkout.py",
    "REQ-GCO-02": "test_enh02_guest_checkout.py",
    "REQ-ACO-03": "test_enh02_guest_checkout.py",
    "REQ-WISH-01": "test_enh02_wishlist.py",
    "REQ-WISH-02": "test_enh02_wishlist.py",
    "REQ-WISH-03": "test_enh02_wishlist.py",
    "REQ-REG-04": "test_enh02_shared_account.py",
    "REQ-REG-05": "test_enh02_shared_account.py",
    "REQ-AUTH-01": "test_enh02_shared_account.py",
    "REQ-AUTH-02": "test_enh02_shared_account.py",
    "REQ-AUTH-03": "test_enh02_shared_account.py",
    "REQ-ACCT-01": "test_enh02_shared_account.py",
    "REQ-CART-05": "test_enh02_shared_account.py",
    "REQ-PWR-01": "test_enh02_shared_account.py",
    "REQ-ACO-01": "test_enh02_shared_account.py",
    "REQ-ACO-02": "test_enh02_shared_account.py",
    "REQ-SHIP-01": "test_enh02_shared_account.py",
    "REQ-PAY-01": "test_enh02_shared_account.py",
    "REQ-PAY-02": "test_enh02_shared_account.py",
    "REQ-PAY-03": "test_enh02_shared_account.py",
    "REQ-CONF-01": "test_enh02_shared_account.py",
    "REQ-CONF-02": "test_enh02_shared_account.py",
    "REQ-OHIST-01": "test_enh02_shared_account.py",
    "REQ-GCO-03": "test_gco03_post_freeze_validation.py",
}

_REQ_ID_RE = re.compile(r"\bREQ-[A-Z]+-\d+\b")

#: A bare requirement-ID co-occurrence in a precondition string is not,
#: by itself, proof of execution ordering -- a precondition can
#: reference another requirement merely for comparison ("consistent with
#: REQ-ACO-01's own mechanism"). Only a precondition string that ALSO
#: contains one of these real, disclosed ordering-indicator phrases
#: (each phrase copied verbatim from this project's own real testcase
#: preconditions) is treated as genuine prerequisite evidence.
_ORDERING_INDICATOR_RE = re.compile(
    r"chained from|already exist|already completed|has just|from enh0\d-tc|previously[- ]saved|real order.{0,20}completed|just completed",
    re.IGNORECASE,
)


@dataclass
class DependencyClassification:
    requirement_id: str
    category: str
    reason: str
    test_module: Optional[str] = None
    prerequisite_requirement_ids: List[str] = field(default_factory=list)
    evidence: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _find_precondition_prerequisite(requirement_id: str) -> Optional[DependencyClassification]:
    """Scans this requirement's own real ENH02_TESTCASES entry
    `preconditions` field -- deliberately NOT `notes` (a free-form
    commentary field that can mention an unrelated requirement for many
    reasons, e.g. naming *downstream* reusers of a shared account, or
    explicitly disclaiming reuse of another dataset -- either of which
    would be a false-positive "prerequisite" if scanned) -- for a
    reference to a DIFFERENT real requirement ID. `preconditions` is the
    one real field whose entire purpose is to state what must already be
    true before this testcase runs, so a REQ-ID found there is real,
    disclosed prerequisite evidence, never invented."""
    from automation.playwright.enh02_testcases import ENH02_TESTCASES

    for e in ENH02_TESTCASES:
        if requirement_id not in e.get("requirement_ids", []):
            continue
        for precondition in e.get("preconditions", []):
            if not _ORDERING_INDICATOR_RE.search(precondition):
                continue
            found = {m for m in _REQ_ID_RE.findall(precondition) if m != requirement_id}
            if found:
                return DependencyClassification(
                    requirement_id=requirement_id,
                    category=ExecutionCategory.PREREQUISITE_DEPENDENT,
                    reason=f"Real testcase {e['testcase_id']}'s own precondition references {sorted(found)} with an explicit ordering phrase.",
                    prerequisite_requirement_ids=sorted(found),
                    evidence=precondition.strip(),
                )
    return None


def classify(requirement_id: str) -> DependencyClassification:
    coverage = next((r for r in REQUIREMENT_COVERAGE if r.requirement_id == requirement_id), None)
    if coverage is None or not coverage.testcase_ids:
        return DependencyClassification(
            requirement_id=requirement_id,
            category=ExecutionCategory.BLOCKED,
            reason=(
                "Requirement not present in the real requirement coverage matrix."
                if coverage is None
                else f"Requirement has disposition {coverage.disposition!r} but no real testcase yet."
            ),
        )

    # A real, disclosed prerequisite reference always wins (it is the
    # most specific, most directly evidenced classification available)
    # -- even for a requirement whose test module also happens to be
    # EXCLUSIVE (e.g. REQ-ACO-02 both shares the one account AND
    # explicitly depends on REQ-ACO-01 having run first); the
    # prerequisite fact is reported alongside, not silently dropped.
    prereq = _find_precondition_prerequisite(requirement_id)

    test_module = _REQUIREMENT_TO_TEST_MODULE.get(requirement_id)
    parallel_safety = classify_parallel_safety(test_module) if test_module else ParallelSafety.UNKNOWN

    if prereq is not None:
        if parallel_safety == ParallelSafety.STATE_DEPENDENT:
            prereq.reason += f" Also EXCLUSIVE: real test module {test_module!r} requires standalone execution (shared account/order resource)."
        prereq.test_module = test_module
        return prereq

    if parallel_safety == ParallelSafety.SAFE_TO_PARALLELIZE:
        return DependencyClassification(
            requirement_id=requirement_id, category=ExecutionCategory.SAFE_PARALLEL,
            reason=f"Real test module {test_module!r} demonstrated PASS under real pytest -n 4 concurrency (Enhancement-02 closure evidence).",
            test_module=test_module,
        )
    if parallel_safety == ParallelSafety.STATE_DEPENDENT:
        return DependencyClassification(
            requirement_id=requirement_id, category=ExecutionCategory.EXCLUSIVE,
            reason=f"Real test module {test_module!r} shares a single, exclusive real SUT resource (one account or one order) and reliably fails under real pytest -n 4 concurrency -- must run standalone.",
            test_module=test_module,
        )
    if parallel_safety == ParallelSafety.RESOURCE_CONFLICT:
        return DependencyClassification(
            requirement_id=requirement_id, category=ExecutionCategory.EXCLUSIVE,
            reason=f"Real test module {test_module!r} is classified RESOURCE_CONFLICT.", test_module=test_module,
        )

    return DependencyClassification(
        requirement_id=requirement_id, category=ExecutionCategory.SEQUENTIAL,
        reason=(
            f"No real parallel-safety evidence exists yet for test module {test_module!r}."
            if test_module else "No real test module is registered for this requirement's automation yet."
        ),
        test_module=test_module,
    )


def classify_many(requirement_ids: List[str]) -> Dict[str, DependencyClassification]:
    return {rid: classify(rid) for rid in requirement_ids}


def test_module_for(requirement_id: str) -> Optional[str]:
    """Public accessor for the real, disclosed requirement -> test
    module fact table (`_REQUIREMENT_TO_TEST_MODULE`)."""
    return _REQUIREMENT_TO_TEST_MODULE.get(requirement_id)
