"""Multi-locator artifact governance — additive, deterministic only."""
from __future__ import annotations

from typing import List

from automation.multi_locator.schema import GovernedMultiLocatorArtifact, MultiLocatorArtifact, MultiLocatorGovernanceStatus
from automation.multi_locator.step_mapping import TestcaseStepMapping, validate_full_coverage, validate_order_preserved


def govern_multi_locator_artifact(artifact: MultiLocatorArtifact) -> GovernedMultiLocatorArtifact:
    problems: List[str] = []

    if not artifact.step_candidate_sets:
        problems.append("NO_ELEMENT_TARGETING_STEPS")

    unresolved = [s.step_order for s in artifact.step_candidate_sets if not s.candidates]
    if unresolved:
        problems.append(f"UNRESOLVED_STEPS:{unresolved}")

    for s in artifact.step_candidate_sets:
        priorities = [c.priority for c in s.candidates]
        if priorities != sorted(priorities):
            problems.append(f"STEP_{s.step_order}_CANDIDATES_NOT_PRIORITY_ORDERED")
        for c in s.candidates:
            if not c.evidence_source or not c.locator:
                problems.append(f"STEP_{s.step_order}_CANDIDATE_MISSING_EVIDENCE")

    if artifact.testcase_step_mappings:
        mappings = [TestcaseStepMapping(**m) for m in artifact.testcase_step_mappings]
        expected_indices = set(range(len(mappings)))
        actual_indices = {m.testcase_step_index for m in mappings}
        if actual_indices != expected_indices:
            problems.append(f"TESTCASE_STEP_MAPPING_INDEX_GAP:{sorted(expected_indices - actual_indices)}")
        coverage = validate_full_coverage(mappings, [m.testcase_step_text for m in mappings])
        if not coverage["passed"]:
            problems.append(f"TESTCASE_STEP_MAPPING_INCOMPLETE:{coverage['detail']['missing_testcase_steps']}")
        order = validate_order_preserved(mappings)
        if not order["passed"]:
            problems.append(f"TESTCASE_STEP_MAPPING_OUT_OF_ORDER:{order['detail']}")

    if problems:
        # Any unresolved load-bearing step means this artifact cannot
        # yet be executed for real -- exactly mirroring the frozen
        # CP-05 UNSUPPORTED_NEEDS_CLARIFICATION disposition, never
        # silently downgraded to REJECTED nor upgraded to ACCEPTED.
        status = (
            MultiLocatorGovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION
            if any(p.startswith("UNRESOLVED_STEPS") for p in problems)
            else MultiLocatorGovernanceStatus.REJECTED
        )
        return GovernedMultiLocatorArtifact(artifact, status, problems)

    return GovernedMultiLocatorArtifact(artifact, MultiLocatorGovernanceStatus.ACCEPTED, [])
