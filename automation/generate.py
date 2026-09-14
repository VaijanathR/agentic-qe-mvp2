"""
CP-MVP2-05 — Playwright artifact generation orchestration.

Implements the flow from the frozen specification (sec. 2/3):
    ACCEPTED CP-MVP2-03 TESTCASE + GOVERNED CP-MVP2-04 TEST DATA
    -> LLM (step-structure reasoning) -> STRUCTURED PLAYWRIGHT ARTIFACT

Reuses `testcases.generate.requirement_context()` (CP-MVP2-03,
unmodified, read-only import) for the real governed RAG attribution.
Locator values come exclusively from `automation.evidence.lookup_locator`/
`lookup_submit_locator` (real, disk-read evidence) — the LLM is only
ever shown field names and testcase narrative text; it never returns a
locator, and nothing here ever accepts one from it.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field as dc_field
from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from automation.evidence import lookup_locator, lookup_submit_locator
from automation.schema import (
    ALL_ACTION_TYPES,
    ALL_SYNC_STRATEGIES,
    ELEMENT_TARGETING_ACTION_TYPES,
    Assertion,
    AssertionType,
    LocatorSpec,
    LocatorStatus,
    LocatorStrategy,
    PlaywrightArtifact,
    PlaywrightStep,
    SyncStrategy,
)
from llm.automation_client import AutomationLLMClient
from testcases.generate import requirement_context as cp03_requirement_context
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import GovernedTestcase
from testdata.schema import DataGovernanceStatus, GovernedTestDataSet

ELIGIBLE_DATASET_STATUSES = {DataGovernanceStatus.ACCEPTED, DataGovernanceStatus.POSSIBLE_DUPLICATE}


@dataclass
class GenerationResult:
    testcase_id: str
    artifact: Optional[PlaywrightArtifact] = None
    unsupported: Optional[Dict] = None

    def to_dict(self) -> dict:
        return {
            "testcase_id": self.testcase_id,
            "artifact": self.artifact.to_dict() if self.artifact else None,
            "unsupported": self.unsupported,
        }


def build_artifact_context(testcase: GovernedTestcase, dataset: GovernedTestDataSet, requirement_id: str) -> Dict:
    return {
        "testcase_id": testcase.testcase.testcase_id,
        "requirement_id": requirement_id,
        "test_steps": list(testcase.testcase.test_steps),
        "expected_result": testcase.testcase.expected_result,
        "available_fields": [f.field_name for f in dataset.dataset.fields],
    }


def generate_for_testcase(
    kb: KnowledgeBase,
    testcase: GovernedTestcase,
    dataset: GovernedTestDataSet,
    llm: AutomationLLMClient,
) -> GenerationResult:
    testcase_id = testcase.testcase.testcase_id

    if testcase.governance_status != TestcaseGovernanceStatus.ACCEPTED:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "reason": "TESTCASE_NOT_ACCEPTED", "detail": f"governance_status={testcase.governance_status!r}"},
        )
    if dataset.governance_status not in ELIGIBLE_DATASET_STATUSES:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "reason": "DATASET_NOT_ELIGIBLE", "detail": f"dataset governance_status={dataset.governance_status!r}"},
        )
    if dataset.dataset.testcase_id != testcase_id:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "reason": "DATASET_TESTCASE_MISMATCH", "detail": f"dataset.testcase_id={dataset.dataset.testcase_id!r}"},
        )

    requirement_ids = testcase.testcase.requirement_ids
    if not requirement_ids:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "reason": "NO_REQUIREMENT_IDS", "detail": "testcase carries no requirement_ids"},
        )
    requirement_id = requirement_ids[0]

    rag_context = cp03_requirement_context(kb, requirement_id)
    if rag_context is None:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "requirement_id": requirement_id, "reason": "NO_APPROVED_REQUIREMENT_EVIDENCE", "detail": f"{requirement_id} did not resolve via governed RAG"},
        )

    available_field_names = {f.field_name for f in dataset.dataset.fields}
    context = build_artifact_context(testcase, dataset, requirement_id)
    raw_steps = llm.propose_steps(context)

    steps: List[PlaywrightStep] = []
    llm_assertion_conditions: List[str] = []
    for seq, raw in enumerate(raw_steps, start=1):
        action_type = raw.get("action_type")
        if action_type not in ALL_ACTION_TYPES:
            continue
        field_name = raw.get("field_name")
        sync = raw.get("synchronization_strategy")
        if sync not in ALL_SYNC_STRATEGIES:
            sync = SyncStrategy.NONE
        cond = raw.get("assertion_condition")
        if cond:
            llm_assertion_conditions.append(str(cond))

        locator: Optional[LocatorSpec] = None
        input_mapping: Optional[str] = None
        if action_type in ELEMENT_TARGETING_ACTION_TYPES:
            if field_name:
                evidence = lookup_locator(requirement_id, field_name)
                if field_name in available_field_names:
                    input_mapping = field_name
                # a field the LLM named that isn't in available_fields
                # is dropped as input_mapping (stays None) -- caught by
                # deterministic validation later, never trusted here.
            else:
                evidence = lookup_submit_locator(requirement_id)
            if evidence is not None:
                locator = LocatorSpec(evidence.strategy, evidence.value, evidence.evidence_source, LocatorStatus.EVIDENCED)
            else:
                locator = LocatorSpec(LocatorStrategy.UNSUPPORTED, None, None, LocatorStatus.UNSUPPORTED)

        steps.append(
            PlaywrightStep(
                step_order=seq,
                action_type=action_type,
                locator=locator,
                input_mapping=input_mapping,
                synchronization_strategy=sync,
            )
        )

    if not steps:
        return GenerationResult(
            testcase_id=testcase_id,
            unsupported={"testcase_id": testcase_id, "requirement_id": requirement_id, "reason": "NO_STEPS_PROPOSED", "detail": "LLM proposed no usable steps"},
        )

    # The one mandatory BUSINESS_REQUIRED assertion is always assembled
    # deterministically from the testcase's own governed expected_result
    # -- never contingent on the LLM remembering to propose one, and
    # never itself an LLM-authored string.
    assertions = [
        Assertion(
            assertion_type=AssertionType.BUSINESS_REQUIRED,
            condition=testcase.testcase.expected_result,
            source=f"testcase:{testcase_id}.expected_result",
            counts_toward_coverage=True,
        )
    ]
    for cond in llm_assertion_conditions:
        assertions.append(
            Assertion(
                assertion_type=AssertionType.TECHNICAL_USEFUL,
                condition=cond,
                source="llm_proposed_step_assertion",
                counts_toward_coverage=False,
            )
        )

    primary_chunk_id = rag_context["evidence"][0]["chunk_id"] if rag_context["evidence"] else None
    artifact = PlaywrightArtifact(
        automation_id=f"PW-{testcase_id}-01",
        testcase_id=testcase_id,
        requirement_ids=list(requirement_ids),
        test_data_set_id=dataset.dataset.data_set_id,
        journey_id=testcase.testcase.journey_id,
        scenario_type=testcase.testcase.scenario_type,
        browser_intent="chromium-headless",
        preconditions=list(testcase.testcase.preconditions),
        steps=steps,
        assertions=assertions,
        evidence_requirements=["screenshot", "dom_snapshot"],
        failure_handling_metadata={"retry": False, "escalate": True},
        source_attribution=[
            {
                "requirement_id": requirement_id,
                "source_document": rag_context["source_document"],
                "source_version": rag_context["source_version"],
                "chunk_id": primary_chunk_id,
            }
        ],
        generation_metadata={
            "generator": llm.model_name,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "test_data_set_id": dataset.dataset.data_set_id,
        },
    )
    return GenerationResult(testcase_id=testcase_id, artifact=artifact, unsupported=None)


def generate_for_testcases(
    kb: KnowledgeBase,
    testcase_dataset_pairs: List[tuple],
    llm: AutomationLLMClient,
) -> List[GenerationResult]:
    return [generate_for_testcase(kb, tc, ds, llm) for tc, ds in testcase_dataset_pairs]
