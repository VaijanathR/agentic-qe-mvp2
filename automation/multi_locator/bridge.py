"""
Bridge: GovernedMultiLocatorArtifact -> a real, standard, frozen-schema
`GovernedPlaywrightArtifact` that the UNMODIFIED `execution.pipeline` /
`execution.persisted_lifecycle` can execute exactly as-is.

This is the deliberate boundary described in
`docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`: real CP-06
execution never sees a "candidate list" at all -- it only ever sees one
`LocatorSpec` per step, exactly like every other frozen CP-06 execution,
because this bridge selects the PRIMARY (priority-1) candidate for each
step, once, before execution begins. No runtime fallback is attempted;
`execution/{schema,validate,evidence,engine,pipeline}.py` remain
completely untouched and are not even aware this bridge exists.
"""
from __future__ import annotations

from typing import Dict, List

from automation.schema import (
    Assertion,
    GovernanceStatus,
    GovernedPlaywrightArtifact,
    LocatorSpec,
    LocatorStatus,
    PlaywrightArtifact,
    PlaywrightStep,
    SyncStrategy,
)
from automation.multi_locator.schema import GovernedMultiLocatorArtifact


def build_executable_artifact(
    ml_governed: GovernedMultiLocatorArtifact,
    source_payload: Dict,
) -> GovernedPlaywrightArtifact:
    """`source_payload` is the real, frozen, persisted automation
    payload this multi-locator artifact was derived from -- used only to
    copy over the non-locator step/assertion structure verbatim (never
    re-authored)."""
    ml_artifact = ml_governed.artifact
    candidate_by_step = {s.step_order: s for s in ml_artifact.step_candidate_sets}

    steps: List[PlaywrightStep] = []
    for raw_step in source_payload["steps"]:
        step_order = raw_step["step_order"]
        candidate_set = candidate_by_step.get(step_order)
        if candidate_set and candidate_set.candidates:
            primary = candidate_set.candidates[0]
            locator = LocatorSpec(
                strategy=primary.strategy,
                value=primary.locator,
                evidence_source=primary.evidence_source,
                status=LocatorStatus.EVIDENCED,
            )
        elif raw_step.get("locator"):
            locator = LocatorSpec(**raw_step["locator"])
        else:
            locator = None

        steps.append(
            PlaywrightStep(
                step_order=step_order,
                action_type=raw_step["action_type"],
                locator=locator,
                input_mapping=raw_step.get("input_mapping"),
                synchronization_strategy=raw_step.get("synchronization_strategy", SyncStrategy.NONE),
            )
        )

    assertions = [Assertion(**a) for a in source_payload["assertions"]]

    artifact = PlaywrightArtifact(
        automation_id=ml_artifact.ml_automation_id,
        testcase_id=ml_artifact.testcase_id,
        requirement_ids=list(ml_artifact.requirement_ids),
        test_data_set_id=ml_artifact.test_data_set_id,
        journey_id=source_payload.get("journey_id"),
        scenario_type=source_payload["scenario_type"],
        browser_intent=source_payload["browser_intent"],
        preconditions=list(source_payload.get("preconditions", [])),
        steps=steps,
        assertions=assertions,
        evidence_requirements=list(source_payload.get("evidence_requirements", [])),
        failure_handling_metadata=dict(source_payload.get("failure_handling_metadata", {})),
        source_attribution=list(ml_artifact.source_attribution),
        generation_metadata={
            **ml_artifact.generation_metadata,
            "bridge": "automation.multi_locator.bridge.build_executable_artifact",
            "note": (
                "Every LocatorSpec here is the PRIMARY (priority-1) candidate only; "
                "no runtime fallback is attempted by this artifact or by CP-06 "
                "execution -- see CP-MVP2-CR-002 proposal."
            ),
        },
    )

    # This artifact is only ever built from an ml_governed artifact whose
    # own governance already required every load-bearing step to have
    # >=1 real candidate (validate.py) -- ACCEPTED here mirrors that,
    # never independently re-decided or weakened.
    governance_status = (
        GovernanceStatus.ACCEPTED
        if ml_governed.governance_status == "ACCEPTED"
        else GovernanceStatus.UNSUPPORTED_NEEDS_CLARIFICATION
    )
    return GovernedPlaywrightArtifact(artifact=artifact, governance_status=governance_status, reasons=list(ml_governed.reasons))
