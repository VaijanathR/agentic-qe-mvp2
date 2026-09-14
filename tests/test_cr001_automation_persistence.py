"""
CP-MVP2-CR-001 Batch 1 — automation persistence (automation/persist.py),
automation traceability (traceability/automation.py), and reusable
component candidate identification (automation/components.py).

Real ACCEPTED CP-05 artifacts do not currently exist against real
locator evidence (the submit-button locator for REQ-ACO-03 is genuinely
ambiguous — see docs/CP-MVP2-05-IMPLEMENTATION.md). This file reuses the
project's own established DISCLOSED SYNTHETIC MECHANISM TEST precedent
(tests/test_cp_mvp2_05_automation_generation.py::test_valid_artifact_reaches_accepted_with_synthetic_unambiguous_evidence)
— a mocked, unambiguous locator lookup — to obtain a real ACCEPTED
artifact whose PERSISTENCE mechanism can then be genuinely exercised.
This is disclosed, not presented as real end-to-end CP-05 evidence.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

import automation.persist as auto_persist
from automation.components import build_component_usage_map, identify_reusable_locator_candidates
from automation.evidence import LocatorEvidence
from automation.generate import generate_for_testcase
from automation.schema import GovernanceStatus, LocatorStrategy
from automation.validate import govern_artifact
from knowledge.lib.retrieval import KnowledgeBase
from llm.automation_client import StubAutomationClient
from llm.client import StubLLMClient
from llm.test_data_client import StubTestDataClient
from testcases.generate import generate_for_requirement
from testcases.schema import GovernanceStatus as TestcaseGovernanceStatus
from testcases.schema import ScenarioType
from testcases.validate import govern_batch as govern_testcases
from testdata.generate import generate_for_testcases as td_generate_for_testcases
from testdata.schema import DataGovernanceStatus
from testdata.validate import govern_batch as govern_datasets
from traceability.automation import build_automation_traceability


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


def _accepted_aco03_pair(kb):
    cp03_stub = StubLLMClient()
    td_stub = StubTestDataClient()
    gen = generate_for_requirement(kb, "REQ-ACO-03", cp03_stub, scenario_types=[ScenarioType.POSITIVE])
    governed_tcs = govern_testcases(gen.testcases, kb)
    accepted_tc = next(g for g in governed_tcs if g.governance_status == TestcaseGovernanceStatus.ACCEPTED)
    gen_results = td_generate_for_testcases(kb, [accepted_tc], td_stub, requested_categories=[ScenarioType.POSITIVE])
    all_datasets = [d for r in gen_results for d in r.datasets]
    governed_datasets = govern_datasets(all_datasets, {accepted_tc.testcase.testcase_id: accepted_tc})
    accepted_ds = next(g for g in governed_datasets if g.governance_status == DataGovernanceStatus.ACCEPTED)
    return accepted_tc, accepted_ds


def _accepted_artifact(kb, tc, ds, submit_locator="#fake_submit"):
    def fake_lookup(requirement_id, field_name):
        return LocatorEvidence(LocatorStrategy.STABLE_ATTRIBUTE, f"#fake_{field_name}", "synthetic_test_fixture")

    def fake_submit(requirement_id):
        return LocatorEvidence(LocatorStrategy.STABLE_ATTRIBUTE, submit_locator, "synthetic_test_fixture")

    with patch("automation.generate.lookup_locator", side_effect=fake_lookup), \
         patch("automation.generate.lookup_submit_locator", side_effect=fake_submit):
        result = generate_for_testcase(kb, tc, ds, StubAutomationClient())
    governed = govern_artifact(result.artifact, {tc.testcase.testcase_id: tc}, {ds.dataset.data_set_id: ds})
    assert governed.governance_status == GovernanceStatus.ACCEPTED, governed.reasons
    return governed


def test_persist_accepted_automation_roundtrips(tmp_path, monkeypatch, kb):
    monkeypatch.setattr(auto_persist, "BASE_DIR", tmp_path)
    tc, ds = _accepted_aco03_pair(kb)
    governed = _accepted_artifact(kb, tc, ds)

    result = auto_persist.persist_governed_artifact(governed, generator="stub-deterministic-v1", batch_id="B1")
    assert result["reused"] is False
    loaded = auto_persist.load_persisted_artifact(governed.artifact.automation_id)
    assert loaded == governed.to_dict()
    assert loaded["testcase_id"] == tc.testcase.testcase_id


def test_automation_traceability_chain(kb):
    tc, ds = _accepted_aco03_pair(kb)
    governed = _accepted_artifact(kb, tc, ds)
    payload = build_automation_traceability([governed])
    aid = governed.artifact.automation_id
    assert payload["automation_to_testcase"][aid] == tc.testcase.testcase_id
    assert aid in payload["testcase_to_automation"][tc.testcase.testcase_id]
    assert payload["automation_to_requirements"][aid] == governed.artifact.requirement_ids
    assert payload["automation_to_testdata"][aid] == ds.dataset.data_set_id


def test_no_reusable_candidate_with_fewer_than_two_artifacts(kb):
    tc, ds = _accepted_aco03_pair(kb)
    governed = _accepted_artifact(kb, tc, ds)
    assert identify_reusable_locator_candidates([governed]) == []
    assert build_component_usage_map([governed]) == {}


def test_reusable_candidate_appears_with_two_artifacts_sharing_a_locator(kb):
    tc, ds = _accepted_aco03_pair(kb)
    governed_a = _accepted_artifact(kb, tc, ds, submit_locator="#shared_submit")
    # a second, distinctly-IDed artifact reusing the SAME submit locator
    governed_b = _accepted_artifact(kb, tc, ds, submit_locator="#shared_submit")
    object.__setattr__(governed_b.artifact, "automation_id", governed_b.artifact.automation_id + "-B")

    candidates = identify_reusable_locator_candidates([governed_a, governed_b])
    assert any(c["value"] == "#shared_submit" and len(c["used_by_automation_ids"]) == 2 for c in candidates)

    usage = build_component_usage_map([governed_a, governed_b])
    assert usage[governed_a.artifact.automation_id]
    assert usage[governed_b.artifact.automation_id]


def test_automation_traceability_includes_component_usage_when_supplied(kb):
    tc, ds = _accepted_aco03_pair(kb)
    governed = _accepted_artifact(kb, tc, ds)
    usage = {governed.artifact.automation_id: ["STABLE_ATTRIBUTE:#fake_submit"]}
    payload = build_automation_traceability([governed], component_usage=usage)
    assert payload["automation_to_components"] == usage
