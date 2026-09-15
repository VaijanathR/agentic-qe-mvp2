"""
Tests for rca/ — the new, additive CP-MVP2-07 RCA/Replanning/Governance
package (docs/CP-MVP2-07-SPECIFICATION-v1.0.md).

Categories: INGEST (real, on-disk evidence loading, incl. the
missing-execution-id case), CLASSIFY (deterministic re-derivation
reusing execution.schema verbatim), ANALYZE (FACT/EVIDENCE/INFERENCE/
CONCLUSION separation, historical-evidence precedence), REPLAN
(governed vocabulary incl. a real, non-artificial HUMAN_REVIEW_REQUIRED
case), GOVERN (enforcement, incl. a dedicated tampering-detection test
and CR-002 re-affirmation), PERSIST (roundtrip via the unmodified
persistence/envelope.py), PIPELINE (end-to-end, deterministic re-run).

All tests use real, previously-persisted CP-MVP2-06 execution evidence
already on disk in this repository (REALISM-SLICE-EXEC-D01/-D02,
MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02, BATCH2-MECHANISM-CHECK-01) --
never a synthetic ExecutionResult, per frozen spec sec. 4.
"""
from __future__ import annotations

import copy

import pytest

from execution.schema import FailureCategory, FailureSubtype
from rca.analyze import build_rca_record
from rca.classify import reclassify_from_evidence
from rca.govern import (
    CR002_DOC_PATH,
    check_cr002_status,
    decide_governance,
    snapshot_frozen_artifacts,
    verify_frozen_artifacts_unchanged,
)
from rca.ingest import load_execution_result, load_historical_results
from rca.persist import (
    load_persisted_governance,
    load_persisted_rca,
    load_persisted_replanning,
)
from rca.pipeline import run_cp07_rca
from rca.replan import decide_replanning
from rca.schema import (
    ALL_GOVERNANCE_DECISIONS,
    ALL_REPLANNING_DECISIONS,
    Confidence,
    GovernanceDecision,
    ReplanningDecision,
)

REAL_FAIL_EXECUTION_ID = "REALISM-SLICE-EXEC-D01"
REAL_FAIL_EXECUTION_ID_2 = "REALISM-SLICE-EXEC-D02"
REAL_FAIL_EXECUTION_ID_3 = "MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02"
REAL_PASS_EXECUTION_ID = "BATCH2-MECHANISM-CHECK-01"


def _require_real_evidence(execution_id: str) -> dict:
    result = load_execution_result(execution_id)
    if result is None:
        pytest.skip(f"Real, persisted execution evidence {execution_id!r} not present on disk in this environment")
    return result


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

def test_load_execution_result_loads_real_persisted_evidence():
    result = _require_real_evidence(REAL_FAIL_EXECUTION_ID)
    assert result["execution_id"] == REAL_FAIL_EXECUTION_ID
    assert result["testcase_id"] == "TC-REQ-ACO-03-01"
    assert result["overall_status"] == "FAIL"


def test_load_execution_result_missing_execution_id_returns_none_never_fabricated():
    assert load_execution_result("NO-SUCH-EXECUTION-ID-EVER-EXISTED") is None


def test_load_historical_results_uses_testcase_id_lineage_and_excludes_self():
    _require_real_evidence(REAL_FAIL_EXECUTION_ID)
    historical = load_historical_results("TC-REQ-ACO-03-01", exclude_execution_id=REAL_FAIL_EXECUTION_ID)
    assert all(h["execution_id"] != REAL_FAIL_EXECUTION_ID for h in historical)
    assert all(h["testcase_id"] == "TC-REQ-ACO-03-01" for h in historical)


def test_load_historical_results_deterministic_ordering():
    a = load_historical_results("TC-REQ-ACO-03-01", exclude_execution_id=REAL_FAIL_EXECUTION_ID)
    b = load_historical_results("TC-REQ-ACO-03-01", exclude_execution_id=REAL_FAIL_EXECUTION_ID)
    assert [h["execution_id"] for h in a] == [h["execution_id"] for h in b]


# ---------------------------------------------------------------------------
# Classify
# ---------------------------------------------------------------------------

def test_reclassify_from_evidence_reuses_frozen_taxonomy_verbatim():
    result = _require_real_evidence(REAL_FAIL_EXECUTION_ID)
    category, subtype = reclassify_from_evidence(result)
    assert category in vars(FailureCategory).values() or category is None
    assert subtype in vars(FailureSubtype).values() or subtype is None


def test_reclassify_from_evidence_real_timeout_case():
    result = _require_real_evidence(REAL_FAIL_EXECUTION_ID)
    category, subtype = reclassify_from_evidence(result)
    assert subtype == FailureSubtype.TIMEOUT
    assert category == FailureCategory.ENVIRONMENT_ISSUE


def test_reclassify_from_evidence_pass_returns_none_none():
    result = _require_real_evidence(REAL_PASS_EXECUTION_ID)
    assert reclassify_from_evidence(result) == (None, None)


# ---------------------------------------------------------------------------
# Analyze — FACT / EVIDENCE / INFERENCE / CONCLUSION separation
# ---------------------------------------------------------------------------

def test_build_rca_record_missing_execution_returns_none():
    assert build_rca_record("NO-SUCH-EXECUTION-ID-EVER-EXISTED", "RCA-DOES-NOT-MATTER") is None


def test_build_rca_record_separates_fact_evidence_inference_conclusion():
    _require_real_evidence(REAL_FAIL_EXECUTION_ID)
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-SEPARATION")
    assert rca is not None
    # FACT
    assert REAL_FAIL_EXECUTION_ID in rca.failure_symptom
    # EVIDENCE — real, structured, never a free-text blob
    assert isinstance(rca.observed_evidence, dict)
    assert "step_results" in rca.observed_evidence
    assert isinstance(rca.requirement_testcase_data_context, dict)
    assert isinstance(rca.historical_evidence, list)
    # INFERENCE — explicitly a distinct field, non-empty, never called a "fact"
    assert rca.agent_inference
    assert "fact" not in rca.agent_inference.lower()
    # CONCLUSION
    assert rca.root_cause_hypothesis
    assert rca.confidence in {Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW}
    # RECOMMENDATION — never self-executed, always disclosed as such
    assert "RECOMMENDATION" in rca.recommended_next_action or rca.recommended_next_action == "No action required."


def test_build_rca_record_never_presents_inference_as_fact_for_real_timeout_case():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-INFERENCE")
    assert rca is not None
    assert "testcase-content limitation" in rca.root_cause_hypothesis
    assert "not a defect in locator resolution" in rca.root_cause_hypothesis


def test_build_rca_record_pass_case_has_na_hypothesis_and_high_confidence():
    _require_real_evidence(REAL_PASS_EXECUTION_ID)
    rca = build_rca_record(REAL_PASS_EXECUTION_ID, "RCA-TEST-PASS")
    assert rca is not None
    assert rca.root_cause_hypothesis.startswith("N/A")
    assert rca.confidence == Confidence.HIGH
    assert rca.final_rca_classification is None
    assert rca.recommended_next_action == "No action required."


def test_build_rca_record_historical_evidence_present_and_does_not_override_current():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-HISTORICAL")
    assert rca is not None
    assert len(rca.historical_evidence) >= 1
    # current evidence (a real FAIL) is authoritative regardless of any historical mix
    assert rca.final_rca_classification == "ENVIRONMENT_ISSUE"
    assert "does not override this execution's own current evidence" in rca.agent_inference


def test_build_rca_record_confidence_high_when_comparable_history_corroborates():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-CONFIDENCE")
    assert rca is not None
    assert rca.confidence == Confidence.HIGH


# ---------------------------------------------------------------------------
# Replan
# ---------------------------------------------------------------------------

def test_decide_replanning_pass_case_is_replan_not_allowed():
    rca = build_rca_record(REAL_PASS_EXECUTION_ID, "RCA-TEST-REPLAN-PASS")
    assert rca is not None
    replanning = decide_replanning(rca, "PASS")
    assert replanning.decision == ReplanningDecision.REPLAN_NOT_ALLOWED
    assert replanning.human_approval_required is False


def test_decide_replanning_real_fail_case_is_human_review_required_not_artificial():
    """The real, current CP-07 case: a high-confidence root cause exists,
    but its only corrective action requires content this checkpoint has
    no authority to author -- a genuine HUMAN_REVIEW_REQUIRED outcome,
    not one manufactured merely to exercise the vocabulary (sec. 11)."""
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-REPLAN-FAIL")
    assert rca is not None
    replanning = decide_replanning(rca, "FAIL")
    assert replanning.decision == ReplanningDecision.HUMAN_REVIEW_REQUIRED
    assert replanning.human_approval_required is True
    assert replanning.proposed_change is not None
    assert "NOT APPLIED" in replanning.proposed_change


def test_decide_replanning_locator_failure_is_governance_blocked():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-REPLAN-LOCATOR")
    assert rca is not None
    forced = copy.deepcopy(rca)
    forced.final_rca_subtype = FailureSubtype.LOCATOR_FAILURE
    replanning = decide_replanning(forced, "FAIL")
    assert replanning.decision == ReplanningDecision.GOVERNANCE_BLOCKED
    assert "CR-002" in replanning.reason


def test_decide_replanning_low_confidence_is_human_review_required():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-REPLAN-LOWCONF")
    assert rca is not None
    forced = copy.deepcopy(rca)
    forced.confidence = Confidence.LOW
    forced.final_rca_subtype = FailureSubtype.ASSERTION_FAILURE
    replanning = decide_replanning(forced, "FAIL")
    assert replanning.decision == ReplanningDecision.HUMAN_REVIEW_REQUIRED


def test_all_replanning_decisions_are_governed_vocabulary_only():
    for value in (ReplanningDecision.REPLAN_ALLOWED, ReplanningDecision.REPLAN_NOT_ALLOWED,
                  ReplanningDecision.HUMAN_REVIEW_REQUIRED, ReplanningDecision.GOVERNANCE_BLOCKED):
        assert value in ALL_REPLANNING_DECISIONS


# ---------------------------------------------------------------------------
# Govern — enforcement, tampering detection, CR-002 re-affirmation
# ---------------------------------------------------------------------------

def test_snapshot_and_verify_frozen_artifacts_unchanged_passes_when_untouched():
    baseline = snapshot_frozen_artifacts()
    result = verify_frozen_artifacts_unchanged(baseline)
    assert result["passed"] is True
    assert result["diffs"] == {}


def test_verify_frozen_artifacts_unchanged_detects_real_tampering():
    """A dedicated tampering-detection test: simulates a baseline captured
    before a (hypothetical) frozen-file edit by tampering with the
    baseline dict itself -- proves the guard actually compares hashes and
    fails closed, without ever touching a real frozen file on disk."""
    baseline = snapshot_frozen_artifacts()
    tampered_baseline = dict(baseline)
    some_path = next(iter(tampered_baseline))
    tampered_baseline[some_path] = "0" * 64  # a hash that cannot match real content
    result = verify_frozen_artifacts_unchanged(tampered_baseline)
    assert result["passed"] is False
    assert some_path in result["diffs"]


def test_check_cr002_status_reads_live_document_and_is_still_unauthorized():
    status = check_cr002_status()
    assert status["found"] is True
    assert status["still_unauthorized"] is True


def test_decide_governance_blocks_on_failed_frozen_guard():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-GOV-GUARD")
    assert rca is not None
    replanning = decide_replanning(rca, "FAIL")
    failed_guard = {"passed": False, "checked_paths": [], "diffs": {"some/frozen/file.py": {"baseline": "a", "current": "b"}}}
    governance = decide_governance(replanning, "GOV-TEST-GUARD", failed_guard)
    assert governance.decision == GovernanceDecision.GOVERNANCE_BLOCKED
    assert governance.prohibited_change_guard_passed is False


def test_decide_governance_real_case_defers_to_human():
    rca = build_rca_record(REAL_FAIL_EXECUTION_ID, "RCA-TEST-GOV-REAL")
    assert rca is not None
    replanning = decide_replanning(rca, "FAIL")
    passing_guard = verify_frozen_artifacts_unchanged(snapshot_frozen_artifacts())
    governance = decide_governance(replanning, "GOV-TEST-REAL", passing_guard)
    assert governance.decision == GovernanceDecision.ACTION_DEFERRED_TO_HUMAN
    assert governance.cr002_status == "OPEN_NOT_AUTHORIZED"


def test_decide_governance_pass_case_is_no_action_required():
    rca = build_rca_record(REAL_PASS_EXECUTION_ID, "RCA-TEST-GOV-PASS")
    assert rca is not None
    replanning = decide_replanning(rca, "PASS")
    passing_guard = verify_frozen_artifacts_unchanged(snapshot_frozen_artifacts())
    governance = decide_governance(replanning, "GOV-TEST-PASS", passing_guard)
    assert governance.decision == GovernanceDecision.NO_ACTION_REQUIRED


def test_all_governance_decisions_are_governed_vocabulary_only():
    for value in (GovernanceDecision.ACTION_AUTHORIZED, GovernanceDecision.ACTION_DEFERRED_TO_HUMAN,
                  GovernanceDecision.NO_ACTION_REQUIRED, GovernanceDecision.GOVERNANCE_BLOCKED):
        assert value in ALL_GOVERNANCE_DECISIONS


# ---------------------------------------------------------------------------
# Persist — roundtrip via the unmodified persistence/envelope.py
# ---------------------------------------------------------------------------

def test_pipeline_persists_reloadable_rca_replanning_governance_artifacts():
    result = run_cp07_rca(REAL_FAIL_EXECUTION_ID)
    assert result["status"] == "COMPLETE"

    rca_id = result["rca"]["rca_id"]
    replanning_id = result["replanning"]["replanning_id"]
    governance_id = result["governance"]["governance_id"]

    reloaded_rca = load_persisted_rca(rca_id)
    reloaded_replanning = load_persisted_replanning(replanning_id)
    reloaded_governance = load_persisted_governance(governance_id)

    assert reloaded_rca is not None and reloaded_rca["rca_id"] == rca_id
    assert reloaded_replanning is not None and reloaded_replanning["replanning_id"] == replanning_id
    assert reloaded_governance is not None and reloaded_governance["governance_id"] == governance_id


# ---------------------------------------------------------------------------
# Pipeline — end-to-end, deterministic, missing-evidence BLOCKED
# ---------------------------------------------------------------------------

def test_run_cp07_rca_end_to_end_real_fail_case():
    result = run_cp07_rca(REAL_FAIL_EXECUTION_ID)
    assert result["status"] == "COMPLETE"
    assert result["rca"]["confidence"] == Confidence.HIGH
    assert result["replanning"]["decision"] == ReplanningDecision.HUMAN_REVIEW_REQUIRED
    assert result["governance"]["decision"] == GovernanceDecision.ACTION_DEFERRED_TO_HUMAN


def test_run_cp07_rca_end_to_end_real_pass_case():
    result = run_cp07_rca(REAL_PASS_EXECUTION_ID)
    assert result["status"] == "COMPLETE"
    assert result["replanning"]["decision"] == ReplanningDecision.REPLAN_NOT_ALLOWED
    assert result["governance"]["decision"] == GovernanceDecision.NO_ACTION_REQUIRED


def test_run_cp07_rca_missing_execution_is_blocked_never_fabricated():
    result = run_cp07_rca("NO-SUCH-EXECUTION-ID-EVER-EXISTED")
    assert result["status"] == "BLOCKED"
    assert "never fabricated" in result["reason"]


def test_run_cp07_rca_is_deterministic_on_repeated_runs():
    first = run_cp07_rca(REAL_FAIL_EXECUTION_ID_2)
    second = run_cp07_rca(REAL_FAIL_EXECUTION_ID_2)
    assert first["rca"]["confidence"] == second["rca"]["confidence"]
    assert first["rca"]["final_rca_classification"] == second["rca"]["final_rca_classification"]
    assert first["replanning"]["decision"] == second["replanning"]["decision"]
    assert first["governance"]["decision"] == second["governance"]["decision"]
    # byte-identical content -> the persistence envelope reuses version 1 both times
    assert second["persisted"]["rca"]["reused"] is True


def test_run_cp07_rca_third_real_fail_case_also_completes():
    result = run_cp07_rca(REAL_FAIL_EXECUTION_ID_3)
    assert result["status"] == "COMPLETE"
    assert result["rca"]["final_rca_classification"] == "ENVIRONMENT_ISSUE"
