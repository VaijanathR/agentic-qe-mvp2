"""
CP-MVP2-CR-001 Batch 1 — persisted Automation traceability
(REQ -> TC -> DATA -> AUTOMATION -> COMPONENT chain).

Reshapes/persists what CP-MVP2-05's own frozen governance already
decided, plus (optionally) which reusable components
(`automation.components`) each automation artifact consumes.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional

from automation.schema import GovernedPlaywrightArtifact
from persistence.envelope import REPO_ROOT, persist_artifact

BASE_DIR = REPO_ROOT / "traceability" / "automation"


def build_automation_traceability(
    governed_artifacts: List[GovernedPlaywrightArtifact],
    component_usage: Optional[Dict[str, List[str]]] = None,
) -> Dict:
    automation_to_testcase: Dict[str, str] = {}
    testcase_to_automation: Dict[str, List[str]] = defaultdict(list)
    automation_to_requirements: Dict[str, List[str]] = {}
    automation_to_testdata: Dict[str, str] = {}

    for g in governed_artifacts:
        a = g.artifact
        automation_to_testcase[a.automation_id] = a.testcase_id
        testcase_to_automation[a.testcase_id].append(a.automation_id)
        automation_to_requirements[a.automation_id] = list(a.requirement_ids)
        automation_to_testdata[a.automation_id] = a.test_data_set_id

    return {
        "automation_to_testcase": automation_to_testcase,
        "testcase_to_automation": {tcid: sorted(ids) for tcid, ids in testcase_to_automation.items()},
        "automation_to_requirements": automation_to_requirements,
        "automation_to_testdata": automation_to_testdata,
        "automation_to_components": component_usage or {},
        "automation_status": {g.artifact.automation_id: g.governance_status for g in governed_artifacts},
    }


def persist_automation_traceability(payload: Dict, generator: str, batch_id: str) -> Dict:
    return persist_artifact(
        BASE_DIR,
        artifact_id=batch_id,
        payload=payload,
        generator=generator,
        provenance={"checkpoint": "CP-MVP2-05", "kind": "automation_traceability"},
    )
