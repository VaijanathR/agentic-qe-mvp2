"""
Multi-locator artifact assembly — additive only.

Builds a `MultiLocatorArtifact` from a real, already-persisted (Batch 1)
`GovernedPlaywrightArtifact` payload. Never mutates the source artifact
(read-only reference by ID); never regenerates the underlying testcase,
test data, or step structure. Only ADDS a per-step candidate list.

Governed by the same "no fabrication" principle as every other
checkpoint: a step whose frozen `locator` was `UNSUPPORTED` and for
which `automation.multi_locator.evidence` finds NO candidate either
remains unresolved here too (the artifact reports it, it does not
invent one) -- see `validate.py` for how that affects governance status.
"""
from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from automation.multi_locator.evidence import candidates_for_field, submit_candidates
from automation.multi_locator.schema import AutomationHealth, MultiLocatorArtifact, StepLocatorCandidateSet
from automation.persist import BASE_DIR as AUTOMATION_BASE_DIR
from automation.schema import ActionType, ELEMENT_TARGETING_ACTION_TYPES, LocatorStatus
from execution.persisted_lifecycle import discover_distinct_test_data_variants
from persistence.envelope import load_history, load_version


def resolve_source_automation_payload(source_automation_id: str, expected_test_data_set_id: Optional[str] = None) -> Dict:
    """Safely resolves the real, persisted CP-05 automation payload this
    multi-locator work should be built from -- reusing Batch 2's own
    `execution.persisted_lifecycle.discover_distinct_test_data_variants`
    collision-detection exactly, rather than calling `load_latest`
    directly (which would silently return "whichever version happens to
    be latest" for a colliding automation_id, per
    `AUTOMATION_ID_COLLISION_ADVISORY`). Per the "CONTINUE" instruction
    sec. 6: never silently overwrite/pick between distinct automation
    artifacts; if a collision exists and the caller has not explicitly
    disambiguated, raise rather than guess."""
    variants = discover_distinct_test_data_variants(source_automation_id)
    history = load_history(AUTOMATION_BASE_DIR, source_automation_id)
    if len(variants) <= 1:
        # No collision -- the single persisted version is unambiguous.
        latest_version = history[-1]["version"]
        return load_version(AUTOMATION_BASE_DIR, source_automation_id, latest_version)

    if expected_test_data_set_id is None:
        raise ValueError(
            f"automation_id {source_automation_id!r} has {len(variants)} distinct "
            f"persisted test_data_set_id values ({variants}) -- AUTOMATION_ID_COLLISION_ADVISORY. "
            "An expected_test_data_set_id must be supplied explicitly; refusing to guess a winner."
        )
    for h in history:
        vp = load_version(AUTOMATION_BASE_DIR, source_automation_id, h["version"])
        if vp and vp.get("test_data_set_id") == expected_test_data_set_id:
            return vp
    raise ValueError(
        f"expected_test_data_set_id={expected_test_data_set_id!r} not found among "
        f"persisted versions of {source_automation_id!r} ({variants})"
    )


def build_multi_locator_artifact(source_payload: Dict, ml_automation_id: str) -> MultiLocatorArtifact:
    """`source_payload` is the real persisted automation payload dict
    (as returned by `persistence.envelope.load_latest` against
    `automation/persist.py::BASE_DIR`) -- read-only input."""
    requirement_ids = list(source_payload["requirement_ids"])
    # This package only has real, verified evidence for REQ-ACO-03's
    # submit control; for every other requirement, `submit_candidates`
    # falls back to wrapping the frozen single-locator lookup exactly.
    primary_requirement = requirement_ids[0] if requirement_ids else None

    step_sets: List[StepLocatorCandidateSet] = []
    for step in source_payload["steps"]:
        action_type = step["action_type"]
        locator = step.get("locator")
        field_name = step.get("input_mapping")
        original_evidenced = bool(locator and locator.get("status") == LocatorStatus.EVIDENCED)

        if action_type not in ELEMENT_TARGETING_ACTION_TYPES:
            # NAVIGATE/WAIT/ASSERT steps carry no locator to resolve.
            continue

        if field_name:
            candidates = candidates_for_field(primary_requirement, field_name)
        else:
            # A page-level action with no field_name (this project's
            # existing convention for the submit/"Continue" control).
            candidates = submit_candidates(primary_requirement)

        step_sets.append(
            StepLocatorCandidateSet(
                step_order=step["step_order"],
                field_name=field_name,
                candidates=candidates,
                original_locator_was_evidenced=original_evidenced,
            )
        )

    if any(not s.candidates for s in step_sets):
        health = AutomationHealth.RED
    elif any(not s.original_locator_was_evidenced and s.candidates for s in step_sets):
        health = AutomationHealth.YELLOW
    else:
        health = AutomationHealth.GREEN

    return MultiLocatorArtifact(
        ml_automation_id=ml_automation_id,
        source_automation_id=source_payload["automation_id"],
        testcase_id=source_payload["testcase_id"],
        requirement_ids=requirement_ids,
        test_data_set_id=source_payload["test_data_set_id"],
        step_candidate_sets=step_sets,
        automation_health=health,
        source_attribution=list(source_payload.get("source_attribution", [])),
        generation_metadata={
            "generator": "deterministic-only (no LLM anywhere in multi-locator resolution)",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_automation_id": source_payload["automation_id"],
            "source_automation_governance_status": source_payload.get("validation_status"),
        },
    )
