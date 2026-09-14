"""
CP-MVP2-04 — test-data requirement identification + generation
orchestration.

Implements the flow from the frozen specification (sec. 3):
    ACCEPTED CP-MVP2-03 TESTCASE -> TEST-DATA REQUIREMENT IDENTIFICATION
    -> LLM (field-value reasoning) -> STRUCTURED TEST DATA

Reuses `testcases.generate.requirement_context()` (CP-MVP2-03,
unmodified, read-only import) for the real governed RAG attribution —
this module never bypasses CP-MVP2-02's RAG and never independently
re-derives source attribution. `testdata.constraints.get_constraint_profile`
supplies the deterministic field list/rules; the LLM is only ever shown
that fixed list and asked for field VALUES (sec. 11) — everything else
on the assembled `TestDataSet`/`TestDataField` is assembled here,
deterministically, never trusted from the model.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field as dc_field
from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.test_data_client import TestDataLLMClient
from testcases.generate import requirement_context as cp03_requirement_context
from testcases.schema import GovernanceStatus, GovernedTestcase
from testdata.constraints import ConstraintProfile, get_constraint_profile
from testdata.schema import ALL_DATA_CATEGORIES, DataValidity, TestDataField, TestDataSet

DEFAULT_CATEGORIES = ["POSITIVE", "EXCEPTIONAL", "BOUNDARY", "ALTERNATE", "INVALID"]


@dataclass
class DataGenerationResult:
    testcase_id: str
    requirement_id: str
    datasets: List[TestDataSet] = dc_field(default_factory=list)
    unsupported: Optional[Dict] = None

    def to_dict(self) -> dict:
        return {
            "testcase_id": self.testcase_id,
            "requirement_id": self.requirement_id,
            "datasets": [d.to_dict() for d in self.datasets],
            "unsupported": self.unsupported,
        }


def _field_spec_dict(spec) -> Dict:
    return {
        "field_name": spec.field_name,
        "value_type": spec.value_type,
        "mandatory": spec.mandatory,
        "allowed_values": spec.allowed_values,
        "dependency_reference": spec.dependency_reference,
    }


def build_dataset_context(
    testcase: GovernedTestcase,
    requirement_id: str,
    profile: ConstraintProfile,
    requested_categories: List[str],
) -> Dict:
    """The governed context shown to the LLM: the fixed field list and
    any documented exceptional/boundary/alternate cases — nothing else.
    The LLM never sees, and cannot influence, testcase_id/requirement_ids/
    source_attribution."""
    return {
        "testcase_id": testcase.testcase.testcase_id,
        "requirement_id": requirement_id,
        "requested_categories": [c for c in requested_categories if c in ALL_DATA_CATEGORIES],
        "field_specs": [_field_spec_dict(s) for s in profile.field_specs],
        "documented_exceptional": profile.documented_exceptional,
        "documented_boundary": profile.documented_boundary,
        "documented_alternate": profile.documented_alternate,
        "evidence_note": profile.evidence_note,
    }


def generate_for_testcase(
    kb: KnowledgeBase,
    testcase: GovernedTestcase,
    llm: TestDataLLMClient,
    requested_categories: Optional[List[str]] = None,
) -> DataGenerationResult:
    """Generates candidate TestDataSets for one accepted CP-MVP2-03
    testcase. Returns datasets=[] and a populated `unsupported` dict
    whenever the testcase is not eligible or evidence is insufficient —
    never fabricates a dataset to make a testcase look served."""
    requested = [c for c in (requested_categories or DEFAULT_CATEGORIES) if c in ALL_DATA_CATEGORIES]
    testcase_id = testcase.testcase.testcase_id

    if testcase.governance_status != GovernanceStatus.ACCEPTED:
        return DataGenerationResult(
            testcase_id=testcase_id,
            requirement_id="",
            unsupported={
                "testcase_id": testcase_id,
                "reason": "TESTCASE_NOT_ACCEPTED",
                "detail": f"{testcase_id} has governance_status={testcase.governance_status!r}, not ACCEPTED.",
            },
        )

    requirement_ids = testcase.testcase.requirement_ids
    if not requirement_ids:
        return DataGenerationResult(
            testcase_id=testcase_id,
            requirement_id="",
            unsupported={
                "testcase_id": testcase_id,
                "reason": "NO_REQUIREMENT_IDS",
                "detail": f"{testcase_id} carries no requirement_ids to anchor data generation to.",
            },
        )
    requirement_id = requirement_ids[0]

    profile = get_constraint_profile(requirement_id)
    if profile is None:
        return DataGenerationResult(
            testcase_id=testcase_id,
            requirement_id=requirement_id,
            unsupported={
                "testcase_id": testcase_id,
                "requirement_id": requirement_id,
                "reason": "INSUFFICIENT_EVIDENCE",
                "detail": (
                    f"No deterministic constraint profile exists for {requirement_id}. "
                    "CP-MVP2-04 does not invent constraints for unprofiled requirements."
                ),
            },
        )

    rag_context = cp03_requirement_context(kb, requirement_id)
    if rag_context is None:
        return DataGenerationResult(
            testcase_id=testcase_id,
            requirement_id=requirement_id,
            unsupported={
                "testcase_id": testcase_id,
                "requirement_id": requirement_id,
                "reason": "NO_APPROVED_REQUIREMENT_EVIDENCE",
                "detail": f"{requirement_id} did not resolve to an APPROVED requirement chunk via the governed RAG layer.",
            },
        )

    dataset_context = build_dataset_context(testcase, requirement_id, profile, requested)
    raw_candidates = llm.propose_field_values(dataset_context)

    field_spec_by_name = {s.field_name: s for s in profile.field_specs}
    primary_chunk_id = rag_context["evidence"][0]["chunk_id"] if rag_context["evidence"] else None

    datasets: List[TestDataSet] = []
    for seq, candidate in enumerate(raw_candidates, start=1):
        data_category = candidate.get("data_category")
        if data_category not in requested:
            continue  # deterministic guard: never accept a category outside what was authorized

        fields: List[TestDataField] = []
        for raw_field in candidate.get("fields", []):
            field_name = raw_field.get("field_name")
            spec = field_spec_by_name.get(field_name)
            if spec is None:
                continue  # a field not in the deterministic spec is dropped, never trusted
            uniqueness = spec.uniqueness_requirement
            # documented_exceptional may override uniqueness for this
            # specific documented case (e.g. "duplicate_email" -> MAY_REUSE)
            for exc_spec in profile.documented_exceptional.values():
                override = exc_spec.get("uniqueness_override", {}).get(field_name)
                if override and data_category == "EXCEPTIONAL":
                    uniqueness = override
            boundary = (
                profile.documented_boundary["boundary_classification"]
                if profile.documented_boundary and profile.documented_boundary["field_name"] == field_name
                else "NOT_APPLICABLE"
            )
            fields.append(
                TestDataField(
                    field_name=field_name,
                    field_value=raw_field.get("field_value"),
                    value_type=spec.value_type,
                    boundary_classification=boundary,
                    uniqueness_requirement=uniqueness,
                    dependency_reference=spec.dependency_reference,
                )
            )

        validity = candidate.get("validity") if candidate.get("validity") in (DataValidity.VALID, DataValidity.INVALID) else DataValidity.VALID
        datasets.append(
            TestDataSet(
                data_set_id=f"TD-{testcase_id}-{seq:02d}",
                testcase_id=testcase_id,
                requirement_ids=list(requirement_ids),
                data_category=data_category,
                purpose=str(candidate.get("purpose", "")).strip(),
                validity=validity,
                fields=fields,
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
                    "retrieval_mode": "exact_id",
                    "categories_requested": requested,
                },
            )
        )

    unsupported = None
    if not datasets:
        unsupported = {
            "testcase_id": testcase_id,
            "requirement_id": requirement_id,
            "reason": "NO_JUSTIFIED_CATEGORY",
            "detail": f"No requested category in {requested} was justified by the constraint profile/evidence for {requirement_id}.",
        }
    return DataGenerationResult(testcase_id=testcase_id, requirement_id=requirement_id, datasets=datasets, unsupported=unsupported)


def generate_for_testcases(
    kb: KnowledgeBase,
    testcases: List[GovernedTestcase],
    llm: TestDataLLMClient,
    requested_categories: Optional[List[str]] = None,
) -> List[DataGenerationResult]:
    return [generate_for_testcase(kb, tc, llm, requested_categories) for tc in testcases]
