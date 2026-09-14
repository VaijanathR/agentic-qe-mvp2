"""
CP-MVP2 Batch 2 — CP-06 persisted-lifecycle input contract.

Additive only. This module is the sole new integration surface between
Batch 1's persisted artifacts (`testcases/persist.py`, `testdata/persist.py`,
`automation/persist.py`, all built on `persistence/envelope.py`) and the
frozen, unmodified CP-MVP2-06 implementation
(`execution/{schema,validate,engine,pipeline,evidence}.py`). It never
constructs a synthetic/fabricated artifact and never bypasses a single
frozen CP-06 gate — every candidate that reaches "ready" here is still
run through the real, untouched `execution.pipeline.run_cp_mvp2_06()`.

Implements the 12-step persisted-input contract (Batch 2 instruction
sec. 7):
    1. load persisted automation artifact
    2. validate persistence envelope (required keys present)
    3. validate artifact schema (deserialize into the frozen dataclasses)
    4. validate automation ID (incl. AUTOMATION_ID_COLLISION_ADVISORY detection)
    5. validate testcase ID
    6. validate requirement IDs
    7. validate test-data reference
    8. resolve persisted testcase
    9. resolve persisted test data
    10. validate traceability
    11. validate CP-06 execution eligibility — delegated entirely to the
        frozen `execution.validate` module (never reimplemented)
    12. execute only if eligible — delegated entirely to the frozen
        `execution.pipeline.run_cp_mvp2_06()`

AUTOMATION_ID_COLLISION_ADVISORY handling (Batch 2 instruction sec. 13):
the frozen CP-05 `automation_id` convention (`PW-{testcase_id}-01`) does
not incorporate the paired dataset's ID, so a testcase with multiple
eligible CP-04 datasets produces multiple, genuinely distinct persisted
`PlaywrightArtifact`s that collide on one `automation_id`. This module
never guesses a "winner": if a caller does not supply
`expected_test_data_set_id` to disambiguate, a collision is reported and
execution is BLOCKED. The batch-level runner below never disambiguates
by silently picking one either — it enumerates every distinct variant
explicitly and attempts each one separately.
"""
from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from automation.persist import BASE_DIR as AUTOMATION_BASE_DIR
from automation.schema import Assertion, GovernedPlaywrightArtifact, LocatorSpec, PlaywrightArtifact, PlaywrightStep, SyncStrategy
from execution.persist import persist_execution_result
from execution.pipeline import run_cp_mvp2_06
from execution.schema import ExecutionResult, FailureCategory, OverallStatus
from execution.summary import build_execution_summary, persist_execution_summary
from persistence.envelope import list_artifact_ids, load_history, load_latest, load_version
from testcases.persist import BASE_DIR as TESTCASE_BASE_DIR
from testcases.schema import GovernedTestcase, Priority, Testcase
from testdata.persist import BASE_DIR as TESTDATA_BASE_DIR
from testdata.schema import GovernedTestDataSet, TestDataField, TestDataSet

REQUIRED_AUTOMATION_KEYS = {
    "automation_id", "testcase_id", "requirement_ids", "test_data_set_id",
    "validation_status", "steps", "assertions",
}


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Deserialization — reconstructs the exact frozen dataclasses from a
# persisted payload dict. No field is invented; a missing/mistyped
# required key raises KeyError/TypeError, which callers treat as a real
# schema-validation failure (never silently patched).
# ---------------------------------------------------------------------------

def deserialize_testcase(payload: Dict) -> GovernedTestcase:
    tc = Testcase(
        testcase_id=payload["testcase_id"],
        title=payload["title"],
        requirement_ids=list(payload["requirement_ids"]),
        scenario_type=payload["scenario_type"],
        preconditions=list(payload.get("preconditions", [])),
        test_steps=list(payload.get("test_steps", [])),
        expected_result=payload["expected_result"],
        priority=payload.get("priority", Priority.MEDIUM),
        journey_id=payload.get("journey_id"),
        test_data_reference=payload.get("test_data_reference"),
        source_attribution=list(payload.get("source_attribution", [])),
        generation_metadata=dict(payload.get("generation_metadata", {})),
    )
    return GovernedTestcase(
        testcase=tc,
        governance_status=payload["governance_status"],
        reasons=list(payload.get("reasons", [])),
    )


def deserialize_dataset(payload: Dict) -> GovernedTestDataSet:
    fields = [TestDataField(**f) for f in payload.get("fields", [])]
    ds = TestDataSet(
        data_set_id=payload["data_set_id"],
        testcase_id=payload["testcase_id"],
        requirement_ids=list(payload["requirement_ids"]),
        data_category=payload["data_category"],
        purpose=payload["purpose"],
        validity=payload["validity"],
        fields=fields,
        source_attribution=list(payload.get("source_attribution", [])),
        generation_metadata=dict(payload.get("generation_metadata", {})),
    )
    return GovernedTestDataSet(
        dataset=ds,
        governance_status=payload["validation_status"],
        reasons=list(payload.get("notes", [])),
    )


def deserialize_automation(payload: Dict) -> GovernedPlaywrightArtifact:
    steps: List[PlaywrightStep] = []
    for s in payload["steps"]:
        locator = LocatorSpec(**s["locator"]) if s.get("locator") else None
        steps.append(PlaywrightStep(
            step_order=s["step_order"],
            action_type=s["action_type"],
            locator=locator,
            input_mapping=s.get("input_mapping"),
            synchronization_strategy=s.get("synchronization_strategy", SyncStrategy.NONE),
        ))
    assertions = [Assertion(**a) for a in payload["assertions"]]
    artifact = PlaywrightArtifact(
        automation_id=payload["automation_id"],
        testcase_id=payload["testcase_id"],
        requirement_ids=list(payload["requirement_ids"]),
        test_data_set_id=payload["test_data_set_id"],
        journey_id=payload.get("journey_id"),
        scenario_type=payload["scenario_type"],
        browser_intent=payload["browser_intent"],
        preconditions=list(payload.get("preconditions", [])),
        steps=steps,
        assertions=assertions,
        evidence_requirements=list(payload.get("evidence_requirements", [])),
        failure_handling_metadata=dict(payload.get("failure_handling_metadata", {})),
        source_attribution=list(payload.get("source_attribution", [])),
        generation_metadata=dict(payload.get("generation_metadata", {})),
    )
    return GovernedPlaywrightArtifact(
        artifact=artifact,
        governance_status=payload["validation_status"],
        reasons=list(payload.get("notes", [])),
    )


def discover_distinct_test_data_variants(automation_id: str) -> List[str]:
    """Every distinct `test_data_set_id` found across all persisted
    versions of `automation_id`. More than one entry is the real,
    on-disk signature of AUTOMATION_ID_COLLISION_ADVISORY."""
    history = load_history(AUTOMATION_BASE_DIR, automation_id)
    seen: List[str] = []
    for h in history:
        vp = load_version(AUTOMATION_BASE_DIR, automation_id, h["version"])
        data_id = vp.get("test_data_set_id") if vp else None
        if data_id and data_id not in seen:
            seen.append(data_id)
    return seen


def _early_result(
    execution_id: str,
    automation_id: str,
    reason: str,
    detail: str,
    status: str = OverallStatus.NOT_EXECUTED,
    failure_classification: Optional[str] = None,
    testcase_id: Optional[str] = None,
    requirement_ids: Optional[List[str]] = None,
    test_data_set_id: Optional[str] = None,
    governance_status: str = "UNKNOWN",
) -> ExecutionResult:
    return ExecutionResult(
        execution_id=execution_id,
        automation_id=automation_id,
        testcase_id=testcase_id or "UNKNOWN",
        requirement_ids=list(requirement_ids or []),
        test_data_set_id=test_data_set_id or "UNKNOWN",
        journey_id=None,
        scenario_type="UNKNOWN",
        browser=None,
        execution_start=None,
        execution_end=None,
        duration_seconds=None,
        overall_status=status,
        failure_classification=failure_classification,
        failure_summary=(f"{reason}: {detail}" if status != OverallStatus.NOT_EXECUTED else None),
        governance_status=governance_status,
        reproducibility_metadata={"execution_id": execution_id, "timestamp": _now_iso()},
        notes=[f"{reason}: {detail}"],
    )


def resolve_persisted_execution_candidate(
    automation_id: str,
    expected_test_data_set_id: Optional[str] = None,
    execution_id: Optional[str] = None,
) -> Dict:
    """Implements the 12-step contract (steps 1-10 here; 11-12 are left
    entirely to the frozen execution.validate/execution.pipeline
    modules). Never raises — every failure path is captured as
    structured stage evidence plus, where blocking, an honest
    ExecutionResult. Returns:
        {"ready": bool, "stages": {...}, "governed_artifact": ..., "governed_dataset": ..., "early_result": ...}
    """
    execution_id = execution_id or f"EXEC-LIFECYCLE-{automation_id}"
    stages: Dict[str, Dict] = {}

    # Stage 1: load persisted automation artifact.
    automation_payload = load_latest(AUTOMATION_BASE_DIR, automation_id)
    stages["persisted_automation_discovered"] = {
        "passed": automation_payload is not None,
        "automation_id": automation_id,
    }
    if automation_payload is None:
        result = _early_result(execution_id, automation_id, "PERSISTED_AUTOMATION_NOT_FOUND",
                                f"no persisted artifact exists for automation_id={automation_id!r}")
        return {"ready": False, "stages": stages, "governed_artifact": None, "governed_dataset": None, "early_result": result}

    # Stage 2: validate persistence envelope (structural — required keys present).
    missing_keys = REQUIRED_AUTOMATION_KEYS - set(automation_payload.keys())
    stages["envelope_validated"] = {"passed": not missing_keys, "missing_keys": sorted(missing_keys)}
    if missing_keys:
        result = _early_result(execution_id, automation_id, "MALFORMED_PERSISTED_ENVELOPE",
                                f"missing required keys: {sorted(missing_keys)}")
        return {"ready": False, "stages": stages, "governed_artifact": None, "governed_dataset": None, "early_result": result}

    # Stage 3: validate artifact schema (deserialize into the frozen dataclasses).
    try:
        governed_artifact = deserialize_automation(automation_payload)
    except (KeyError, TypeError) as exc:
        result = _early_result(execution_id, automation_id, "AUTOMATION_SCHEMA_DESERIALIZATION_FAILURE", str(exc))
        return {"ready": False, "stages": stages, "governed_artifact": None, "governed_dataset": None, "early_result": result}
    stages["artifact_schema_validated"] = {"passed": True, "governance_status": governed_artifact.governance_status}

    # Stage 4: validate automation ID — AUTOMATION_ID_COLLISION_ADVISORY detection.
    variants = discover_distinct_test_data_variants(automation_id)
    collision = len(variants) > 1
    stages["automation_id_validated"] = {
        "passed": True,
        "automation_id_collision_advisory": collision,
        "distinct_test_data_set_ids": variants,
        "version_count": len(load_history(AUTOMATION_BASE_DIR, automation_id)),
    }
    if collision:
        if expected_test_data_set_id is None:
            result = _early_result(
                execution_id, automation_id, "AUTOMATION_ID_COLLISION_DETECTED",
                f"automation_id {automation_id!r} has {len(variants)} distinct test_data_set_id values "
                f"across its persisted versions ({variants}) -- AUTOMATION_ID_COLLISION_ADVISORY "
                "(pre-existing CP-05 finding, not fixed here). No test_data_set_id was supplied to "
                "disambiguate; refusing to guess a winner.",
                status=OverallStatus.BLOCKED, failure_classification=FailureCategory.TOOL_ISSUE,
                testcase_id=governed_artifact.artifact.testcase_id,
                requirement_ids=governed_artifact.artifact.requirement_ids,
                governance_status=governed_artifact.governance_status,
            )
            return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}
        matching_payload = None
        for h in load_history(AUTOMATION_BASE_DIR, automation_id):
            vp = load_version(AUTOMATION_BASE_DIR, automation_id, h["version"])
            if vp and vp.get("test_data_set_id") == expected_test_data_set_id:
                matching_payload = vp
        if matching_payload is None:
            result = _early_result(
                execution_id, automation_id, "AUTOMATION_ID_COLLISION_UNRESOLVED",
                f"expected test_data_set_id={expected_test_data_set_id!r} not found among "
                f"persisted versions of {automation_id!r} ({variants})",
                status=OverallStatus.BLOCKED, failure_classification=FailureCategory.TOOL_ISSUE,
                governance_status=governed_artifact.governance_status,
            )
            return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}
        governed_artifact = deserialize_automation(matching_payload)
        stages["automation_id_validated"]["resolved_via_expected_test_data_set_id"] = expected_test_data_set_id

    artifact = governed_artifact.artifact

    # Stage 5: validate testcase ID.
    testcase_payload = load_latest(TESTCASE_BASE_DIR, artifact.testcase_id)
    stages["testcase_id_validated"] = {"passed": testcase_payload is not None, "testcase_id": artifact.testcase_id}
    if testcase_payload is None:
        result = _early_result(execution_id, automation_id, "PERSISTED_TESTCASE_NOT_FOUND",
                                f"no persisted testcase for testcase_id={artifact.testcase_id!r}",
                                testcase_id=artifact.testcase_id, requirement_ids=artifact.requirement_ids,
                                test_data_set_id=artifact.test_data_set_id, governance_status=governed_artifact.governance_status)
        return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}
    governed_testcase = deserialize_testcase(testcase_payload)
    stages["testcase_resolved"] = {"passed": True, "governance_status": governed_testcase.governance_status}

    # Stage 6: validate requirement IDs (automation vs. resolved testcase — no invention).
    req_match = set(artifact.requirement_ids) == set(governed_testcase.testcase.requirement_ids)
    stages["requirement_ids_validated"] = {
        "passed": req_match,
        "automation_requirement_ids": sorted(artifact.requirement_ids),
        "testcase_requirement_ids": sorted(governed_testcase.testcase.requirement_ids),
    }
    if not req_match:
        result = _early_result(execution_id, automation_id, "REQUIREMENT_ID_TRACEABILITY_MISMATCH",
                                f"automation requirement_ids {sorted(artifact.requirement_ids)} != "
                                f"testcase requirement_ids {sorted(governed_testcase.testcase.requirement_ids)}",
                                testcase_id=artifact.testcase_id, requirement_ids=artifact.requirement_ids,
                                test_data_set_id=artifact.test_data_set_id, governance_status=governed_artifact.governance_status)
        return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}

    # Stage 7: validate test-data reference (non-empty).
    stages["test_data_reference_validated"] = {"passed": bool(artifact.test_data_set_id), "test_data_set_id": artifact.test_data_set_id}
    if not artifact.test_data_set_id:
        result = _early_result(execution_id, automation_id, "MISSING_TEST_DATA_REFERENCE",
                                "artifact.test_data_set_id is empty",
                                testcase_id=artifact.testcase_id, requirement_ids=artifact.requirement_ids,
                                governance_status=governed_artifact.governance_status)
        return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}

    # Stage 9 (data half of 8/9): resolve persisted test data.
    dataset_payload = load_latest(TESTDATA_BASE_DIR, artifact.test_data_set_id)
    stages["test_data_resolved"] = {"passed": dataset_payload is not None, "test_data_set_id": artifact.test_data_set_id}
    if dataset_payload is None:
        result = _early_result(execution_id, automation_id, "PERSISTED_TEST_DATA_NOT_FOUND",
                                f"no persisted dataset for test_data_set_id={artifact.test_data_set_id!r}",
                                testcase_id=artifact.testcase_id, requirement_ids=artifact.requirement_ids,
                                test_data_set_id=artifact.test_data_set_id, governance_status=governed_artifact.governance_status)
        return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": None, "early_result": result}
    governed_dataset = deserialize_dataset(dataset_payload)

    # Stage 10: validate traceability (dataset.testcase_id must match artifact.testcase_id).
    trace_ok = governed_dataset.dataset.testcase_id == artifact.testcase_id
    stages["traceability_validated"] = {
        "passed": trace_ok,
        "dataset_testcase_id": governed_dataset.dataset.testcase_id,
        "artifact_testcase_id": artifact.testcase_id,
    }
    if not trace_ok:
        result = _early_result(execution_id, automation_id, "TESTDATA_TESTCASE_TRACEABILITY_MISMATCH",
                                f"dataset.testcase_id={governed_dataset.dataset.testcase_id!r} != "
                                f"artifact.testcase_id={artifact.testcase_id!r}",
                                testcase_id=artifact.testcase_id, requirement_ids=artifact.requirement_ids,
                                test_data_set_id=artifact.test_data_set_id, governance_status=governed_artifact.governance_status)
        return {"ready": False, "stages": stages, "governed_artifact": governed_artifact, "governed_dataset": governed_dataset, "early_result": result}

    # Stages 11-12 belong entirely to the frozen execution.validate /
    # execution.pipeline modules -- not duplicated or second-guessed here.
    stages["ready_for_frozen_cp06_gates"] = {"passed": True}

    return {
        "ready": True,
        "stages": stages,
        "governed_artifact": governed_artifact,
        "governed_dataset": governed_dataset,
        "early_result": None,
    }


def execute_persisted_candidate(
    automation_id: str,
    sut_base_url: str,
    expected_test_data_set_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    timeout_ms: int = 30000,
) -> Dict:
    """Resolves+validates a persisted candidate, then — only if ready —
    executes it through the real, unmodified `run_cp_mvp2_06()`. Always
    persists the resulting `ExecutionResult` through Batch 1's additive,
    timestamped `execution/persist.py` path; the frozen
    `execution/evidence.py` legacy path is untouched and still written
    to by `run_cp_mvp2_06()` itself whenever a real browser step runs."""
    execution_id = execution_id or f"EXEC-LIFECYCLE-{automation_id}"
    resolution = resolve_persisted_execution_candidate(automation_id, expected_test_data_set_id, execution_id)

    if resolution["ready"]:
        result = run_cp_mvp2_06(
            resolution["governed_artifact"], resolution["governed_dataset"], sut_base_url,
            timeout_ms=timeout_ms, execution_id=execution_id,
        )
    else:
        result = resolution["early_result"]

    persisted = persist_execution_result(result)
    return {"result": result, "stages": resolution["stages"], "persisted_path": persisted["path"]}


def run_batch2_persisted_execution(sut_base_url: str, batch_id: str) -> Dict:
    """Batch-level runner (Batch 2 instruction secs. 19-21): attempts a
    real, governed execution for every persisted automation_id. A
    colliding automation_id (AUTOMATION_ID_COLLISION_ADVISORY) is never
    resolved by picking a winner — every distinct test_data_set_id
    variant under it is attempted as its own separate, explicitly
    disambiguated execution."""
    automation_ids = list_artifact_ids(AUTOMATION_BASE_DIR)
    executions: List[Dict] = []
    candidates_examined = 0
    by_governance_status: Dict[str, int] = {}

    for aid in automation_ids:
        variants = discover_distinct_test_data_variants(aid)
        collision = len(variants) > 1
        targets = variants if collision else [None]
        for target in targets:
            candidates_examined += 1
            suffix = f"-{target}" if collision and target else ""
            execution_id = f"{batch_id}-{aid}{suffix}"
            outcome = execute_persisted_candidate(aid, sut_base_url, expected_test_data_set_id=target, execution_id=execution_id)
            executions.append(outcome)
            gs = outcome["result"].governance_status
            by_governance_status[gs] = by_governance_status.get(gs, 0) + 1

    summary = build_execution_summary([o["result"] for o in executions], batch_id=batch_id)
    summary_persisted = persist_execution_summary(summary, generator="deterministic-only")

    return {
        "executions": executions,
        "summary": summary,
        "summary_persisted": summary_persisted,
        "automation_ids_examined": automation_ids,
        "candidates_examined": candidates_examined,
        "by_governance_status": by_governance_status,
    }
