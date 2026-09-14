"""
CP-MVP2-CR-001 Batch 1 — reusable Playwright component identification.

Per CR-001 sec. 12: "Introduce reusable Playwright components only where
the Dependency/Reusability Matrix demonstrates real repetition ... Do
not over-engineer. Do not create speculative frameworks." This module
inspects real, persisted CP-05 automation artifacts for literal, exact
locator repetition across 2+ DISTINCT artifacts — one occurrence in one
artifact is never "repetition" and is never returned. No page object,
helper module, or other executable component is scaffolded by this
module itself; it only reports where the real evidence would justify
one, so a human/future implementation task can decide.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from automation.schema import GovernedPlaywrightArtifact


def identify_reusable_locator_candidates(governed_artifacts: List[GovernedPlaywrightArtifact]) -> List[Dict]:
    by_locator: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for g in governed_artifacts:
        a = g.artifact
        for step in a.steps:
            if step.locator and step.locator.value:
                key = (step.locator.strategy, step.locator.value)
                if a.automation_id not in by_locator[key]:
                    by_locator[key].append(a.automation_id)

    return [
        {"strategy": strategy, "value": value, "used_by_automation_ids": sorted(ids)}
        for (strategy, value), ids in by_locator.items()
        if len(ids) > 1
    ]


def build_component_usage_map(governed_artifacts: List[GovernedPlaywrightArtifact]) -> Dict[str, List[str]]:
    """Maps automation_id -> list of reusable-locator-candidate keys it
    participates in, for `traceability.automation.build_automation_traceability`'s
    `component_usage` parameter. Returns {} when fewer than 2 eligible
    artifacts exist to compare, or no repetition is found — an honest,
    empty result, never a fabricated component."""
    candidates = identify_reusable_locator_candidates(governed_artifacts)
    usage: Dict[str, List[str]] = defaultdict(list)
    for c in candidates:
        label = f"{c['strategy']}:{c['value']}"
        for automation_id in c["used_by_automation_ids"]:
            usage[automation_id].append(label)
    return {k: sorted(v) for k, v in usage.items()}
