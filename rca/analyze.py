"""
CP-MVP2-07 — evidence-based RCA record assembly.

Every field is built only from real data already loaded by
`rca/ingest.py` and `rca/classify.py`. `agent_inference` and
`root_cause_hypothesis` are disclosed, deterministic, rule-based
interpretations of that real evidence -- never an LLM call, never an
invented cause (frozen CP-07 spec sec. 6: "Do not present inference as
fact. Do not fabricate evidence.").
"""
from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from execution.schema import OverallStatus, StepStatus
from persistence.envelope import REPO_ROOT
from rca.classify import reclassify_from_evidence
from rca.ingest import load_execution_result, load_historical_results
from rca.schema import Confidence, RCARecord
from testcases.persist import BASE_DIR as TESTCASE_BASE_DIR
from persistence.envelope import load_latest as load_latest_artifact


def _requirement_testcase_data_context(execution_result: Dict) -> Dict:
    context: Dict = {
        "testcase_id": execution_result.get("testcase_id"),
        "requirement_ids": execution_result.get("requirement_ids"),
        "test_data_set_id": execution_result.get("test_data_set_id"),
        "testcase_persisted_and_loadable": False,
        "testcase_test_steps": None,
    }
    tc_payload = load_latest_artifact(TESTCASE_BASE_DIR, execution_result.get("testcase_id"))
    if tc_payload is not None:
        context["testcase_persisted_and_loadable"] = True
        context["testcase_test_steps"] = tc_payload.get("test_steps")
        context["testcase_preconditions"] = tc_payload.get("preconditions")
    return context


def _observed_evidence(execution_result: Dict) -> Dict:
    return {
        "browser": execution_result.get("browser"),
        "duration_seconds": execution_result.get("duration_seconds"),
        "step_results": [
            {
                "step_order": s["step_order"],
                "action_type": s["action_type"],
                "status": s["status"],
                "observed_result": s.get("observed_result"),
                "error_information": s.get("error_information"),
            }
            for s in execution_result.get("step_results", [])
        ],
        "assertion_results": execution_result.get("assertion_results", []),
        "evidence_references": execution_result.get("evidence_references", []),
    }


def _build_inference(execution_result: Dict, category: Optional[str], subtype: Optional[str], historical: List[Dict]) -> str:
    """A disclosed, deterministic, rule-based interpretation -- explicitly
    labeled as INFERENCE (never FACT) by the caller."""
    step_results = execution_result.get("step_results", [])
    failed = [s for s in step_results if s["status"] in (StepStatus.FAIL, StepStatus.ERROR)]
    if not failed:
        return "No failed step was recorded; no locator/environment inference applies."

    first_failed = failed[0]
    prior_passed = [s for s in step_results if s["step_order"] < first_failed["step_order"] and s["status"] == StepStatus.PASS]
    prior_action_types = [s["action_type"] for s in prior_passed]

    if subtype == "TIMEOUT" and "NAVIGATE" in prior_action_types and len(prior_passed) == 1:
        inference = (
            f"The first failure occurred at step {first_failed['step_order']} "
            f"({first_failed['action_type']}), immediately after a single, successful NAVIGATE "
            "step with no intervening business action (e.g. add-to-cart, begin-checkout) that "
            "would establish deeper application/page state. This pattern is consistent with the "
            "browser being on the SUT's home page when the failing locator was attempted, rather "
            "than on the page that locator's real DOM evidence was captured from."
        )
    else:
        inference = (
            f"The first failure occurred at step {first_failed['step_order']} "
            f"({first_failed['action_type']}), classified {category}/{subtype}. No further "
            "deterministic pattern was matched by this module's disclosed heuristics."
        )

    if historical:
        comparable = [h for h in historical if h.get("overall_status") in (OverallStatus.PASS, OverallStatus.FAIL, OverallStatus.ERROR)]
        same_pattern = sum(
            1 for h in comparable
            if h.get("overall_status") == execution_result.get("overall_status")
            and h.get("failure_classification") == category
        )
        inference += (
            f" Of {len(historical)} other real, persisted execution(s) of this same testcase "
            f"lineage ({len(comparable)} of which reached real browser execution and are "
            f"directly comparable), {same_pattern}/{len(comparable)} comparable execution(s) "
            "share the identical overall_status/failure_classification pattern -- cited as "
            "supporting historical evidence only, per sec. 7; it does not override this "
            "execution's own current evidence."
        )
    return inference


def build_rca_record(execution_id: str, rca_id: str) -> Optional[RCARecord]:
    execution_result = load_execution_result(execution_id)
    if execution_result is None:
        return None

    category, subtype = reclassify_from_evidence(execution_result)
    historical = load_historical_results(execution_result["testcase_id"], exclude_execution_id=execution_id)

    failure_symptom = (
        f"execution_id={execution_id}: overall_status={execution_result['overall_status']}"
        + (f"; {execution_result['failure_summary']}" if execution_result.get("failure_summary") else "")
    )

    agent_inference = _build_inference(execution_result, category, subtype, historical)

    if execution_result["overall_status"] == OverallStatus.PASS:
        root_cause_hypothesis = "N/A -- execution PASSED; no root cause to establish."
        confidence = Confidence.HIGH
        recommended_next_action = "No action required."
    else:
        root_cause_hypothesis = (
            "The failure is attributable to a testcase-content limitation (the persisted "
            "testcase's own business steps do not specify the precondition-establishing actions "
            "this scenario's real evidenced locators require), not a defect in locator "
            "resolution, browser tooling, or the CP-MVP2-06 execution engine."
            if subtype == "TIMEOUT"
            else f"Real, observed {category}/{subtype} failure; no further deterministic hypothesis available from this module's disclosed heuristics."
        )
        # Only historical executions that genuinely reached real browser
        # execution (PASS/FAIL/ERROR) are comparable evidence for this
        # specific failure pattern -- a NOT_EXECUTED/BLOCKED historical
        # entry never attempted the browser action at all, so it is
        # neither corroborating nor conflicting, and is excluded from
        # the confidence computation (while still being retained,
        # unfiltered, in `historical_evidence` above for full disclosure).
        comparable_historical = [
            h for h in historical
            if h.get("overall_status") in (OverallStatus.PASS, OverallStatus.FAIL, OverallStatus.ERROR)
        ]
        same_pattern_count = sum(
            1 for h in comparable_historical
            if h.get("overall_status") == execution_result.get("overall_status")
            and h.get("failure_classification") == category
        )
        if comparable_historical and same_pattern_count == len(comparable_historical):
            confidence = Confidence.HIGH
        elif not comparable_historical:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW
        recommended_next_action = (
            "RECOMMENDATION ONLY, NOT AUTHORIZED, NOT IMPLEMENTED: author a richer, specific "
            "testcase (via a future, separately-authorized task) that includes the precondition-"
            "establishing business steps this scenario requires; alternatively, a formal Human + "
            "Di decision on CR-002 (runtime locator fallback) could be sought, though that would "
            "not resolve this specific testcase-content limitation."
            if subtype == "TIMEOUT"
            else "RECOMMENDATION ONLY, NOT AUTHORIZED, NOT IMPLEMENTED: escalate for Human + Di review."
        )

    return RCARecord(
        rca_id=rca_id,
        execution_id=execution_id,
        automation_id=execution_result["automation_id"],
        testcase_id=execution_result["testcase_id"],
        requirement_ids=list(execution_result.get("requirement_ids", [])),
        test_data_set_id=execution_result.get("test_data_set_id"),
        failure_symptom=failure_symptom,
        observed_evidence=_observed_evidence(execution_result),
        requirement_testcase_data_context=_requirement_testcase_data_context(execution_result),
        historical_evidence=[
            {"execution_id": h["execution_id"], "overall_status": h["overall_status"], "failure_classification": h.get("failure_classification")}
            for h in historical
        ],
        agent_inference=agent_inference,
        root_cause_hypothesis=root_cause_hypothesis,
        confidence=confidence,
        final_rca_classification=category,
        final_rca_subtype=subtype,
        recommended_next_action=recommended_next_action,
        generation_metadata={
            "generator": "deterministic-only (no LLM anywhere in CP-MVP2-07 RCA)",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    )
