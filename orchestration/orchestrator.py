"""
Agentic QE Orchestration -- the central Orchestrator (governing
instruction sec. 10).

Coordinates every stage module in this package through the explicit
state machine (`orchestration/state.py`), recording a `DecisionRecord`
(`orchestration/decisions.py`) and a journal entry
(`orchestration/journal.py`) at every stage. This class performs no
reasoning, no RAG retrieval, no RCA, and no governance decision itself --
it only sequences the real, existing capability modules and enforces
that every transition and every prohibited action is checked (sec. 9:
"Deterministic Code = validation / policy / state / traceability /
enforcement").

DRY_RUN mode never touches the real SUT: it stops at EXECUTION_PLANNED
with a display-only plan (sec. 50). REAL_EXECUTION mode requires a real
Playwright `(page, browser_version)` pair (the same shape
`automation/playwright/tests/conftest.py::browser_page` yields) --
this class never launches its own browser silently (sec. 51).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from orchestration import (
    automation_orchestration,
    coverage as coverage_mod,
    data_orchestration,
    dependency_planning,
    execution_planning,
    failure_classification,
    functional_execution,
    governance,
    impact,
    parallel_execution,
    performance_execution,
    rca_orchestration,
    regression as regression_mod,
    replanning_orchestration,
    requirement_intelligence,
    resume as resume_mod,
    risk as risk_mod,
    test_strategy,
    testcase_orchestration,
    traceability_orchestration,
)
from orchestration.decisions import make_decision
from orchestration.execution_planning import ExecutionMode
from orchestration.governance import GovernanceState
from orchestration.ids import new_orchestration_id
from orchestration.journal import OrchestrationJournal
from orchestration.state import OrchestrationState, validate_transition


class OrchestrationResult:
    def __init__(self, orchestration_id: str, journal: OrchestrationJournal):
        self.orchestration_id = orchestration_id
        self.journal = journal
        self.final_state: Optional[str] = None
        self.final_status: Optional[str] = None  # PASS / FAIL / BLOCKED / DRY_RUN_COMPLETE
        self.stages: Dict[str, Dict] = {}

    def to_dict(self) -> Dict:
        return {
            "orchestration_id": self.orchestration_id,
            "final_state": self.final_state,
            "final_status": self.final_status,
            "stages": self.stages,
        }


class Orchestrator:
    def __init__(self, kb: Optional[KnowledgeBase] = None):
        self.kb = kb or KnowledgeBase.load()

    def _transition(self, journal: OrchestrationJournal, current: str, target: str, reason: str) -> str:
        guard = governance.guard_valid_state_transition(current, target)
        if not guard["passed"]:
            journal.record_note(f"GOVERNANCE: {guard['rationale']}")
            validate_transition(current, target)  # raises, since the guard already failed
        journal.record_transition(current, target, reason)
        return target

    def run(
        self,
        requirement_id: str,
        mode: str = ExecutionMode.DRY_RUN,
        page=None,
        browser_version: Optional[str] = None,
        worker_id: str = "main",
        controlled_failure: bool = False,
        run_performance: bool = False,
        force_full_regression: bool = False,
    ) -> OrchestrationResult:
        orchestration_id = new_orchestration_id()
        journal = OrchestrationJournal(orchestration_id, requirement_id)
        result = OrchestrationResult(orchestration_id, journal)
        journal.update_summary(selected_requirements=[requirement_id], completed_requirement_ids=[], pending_requirement_ids=[requirement_id])

        srs_baseline_hash = governance.snapshot_srs_hash()

        state = OrchestrationState.RECEIVED
        journal.record_transition(None, state, f"Orchestration received for {requirement_id} (mode={mode}).")

        # --- UNDERSTANDING ---
        state = self._transition(journal, state, OrchestrationState.UNDERSTANDING, "Gathering requirement intelligence.")
        intel = requirement_intelligence.gather(requirement_id, self.kb)
        result.stages["requirement_intelligence"] = intel.to_dict()
        journal.record_decision(make_decision(
            orchestration_id=orchestration_id, stage=state, input_references=[requirement_id],
            decision="REQUIREMENT_UNDERSTOOD", reason=f"Disposition={intel.disposition}, source={intel.source}",
            evidence_references=[], confidence="HIGH" if intel.approval_status else "MEDIUM",
            governance_state=GovernanceState.GREEN,
        ).to_dict())

        # --- VALIDATED ---
        state = self._transition(journal, state, OrchestrationState.VALIDATED, "Requirement exists in a real, governed source.")

        # --- IMPACT_ANALYZED ---
        state = self._transition(journal, state, OrchestrationState.IMPACT_ANALYZED, "Running dependency/reusability impact analysis.")
        impact_result = impact.analyze(requirement_id)
        result.stages["impact"] = impact_result

        # --- RISK_ASSESSED ---
        state = self._transition(journal, state, OrchestrationState.RISK_ASSESSED, "Running RBTP risk assessment (deterministic).")
        risk_result = risk_mod.assess(requirement_id, self.kb)
        result.stages["risk"] = risk_result
        journal.record_decision(make_decision(
            orchestration_id=orchestration_id, stage=state, input_references=[requirement_id],
            decision="RISK_ASSESSED", reason=f"corpus_source={risk_result.get('corpus_source')}",
            confidence="HIGH" if risk_result.get("records") else "UNKNOWN",
            risk=(risk_result["records"][0]["priority"] if risk_result.get("records") else "UNKNOWN"),
            governance_state=GovernanceState.GREEN,
        ).to_dict())

        # --- TEST_STRATEGY_READY ---
        state = self._transition(journal, state, OrchestrationState.TEST_STRATEGY_READY, "Determining test strategy (covered vs. missing scenario types).")
        strategy_result = test_strategy.determine_strategy(requirement_id)
        result.stages["test_strategy"] = strategy_result

        # --- TESTCASES_READY ---
        state = self._transition(journal, state, OrchestrationState.TESTCASES_READY, "Selecting/generating testcases.")
        testcase_result = testcase_orchestration.select_or_generate(requirement_id, self.kb)
        result.stages["testcases"] = testcase_result
        journal.record_decision(make_decision(
            orchestration_id=orchestration_id, stage=state, input_references=[requirement_id],
            decision=testcase_result["mode"], reason=f"corpus_source={testcase_result.get('corpus_source')}",
            governance_state=GovernanceState.GREEN,
        ).to_dict())

        # --- DATA_READY ---
        state = self._transition(journal, state, OrchestrationState.DATA_READY, "Selecting/generating test data.")
        data_results = []
        for tc in testcase_result["testcases"]:
            data_results.append(data_orchestration.select_or_generate(tc["testcase_id"], self.kb))
        result.stages["test_data"] = data_results

        # --- TRACEABILITY_VALID ---
        state = self._transition(journal, state, OrchestrationState.TRACEABILITY_VALID, "Validating Requirement->Testcase->Dataset->Automation->Execution chain.")
        chain = traceability_orchestration.build_chain(requirement_id)
        trace_validation = traceability_orchestration.validate(chain)
        result.stages["traceability"] = {"chain": chain, "validation": trace_validation}
        if not trace_validation["valid"]:
            journal.record_note(f"Traceability orphans found: {trace_validation}")

        # --- AUTOMATION_READY ---
        state = self._transition(journal, state, OrchestrationState.AUTOMATION_READY, "Assessing automation readiness.")
        automation_result = automation_orchestration.assess(requirement_id)
        result.stages["automation"] = automation_result

        # --- EXECUTION_PLANNED ---
        state = self._transition(journal, state, OrchestrationState.EXECUTION_PLANNED, "Building execution plan.")
        test_module = "test_enh02_catalog.py" if requirement_id == "REQ-BRW-01" else None
        plan = execution_planning.build_plan(
            requirement_id=requirement_id,
            testcase_ids=automation_result.get("testcase_ids", []),
            automation_ids=automation_result.get("automation_ids", []),
            dataset_ids=intel.dataset_coverage,
            mode=mode,
            test_module_basename=test_module,
            creates_permanent_state=False,
        )
        result.stages["execution_plan"] = plan.to_dict()

        if mode == ExecutionMode.DRY_RUN:
            journal.record_note("DRY_RUN: stopping before EXECUTING -- no SUT interaction performed.")
            result.final_state = state
            result.final_status = "DRY_RUN_COMPLETE"
            return result

        # --- EXECUTING (REAL_EXECUTION only) ---
        if page is None or browser_version is None:
            journal.record_note("BLOCKED: REAL_EXECUTION mode requires a real (page, browser_version) pair.")
            state = self._transition(journal, state, OrchestrationState.BLOCKED, "REAL_EXECUTION requested without a real browser page.")
            result.final_state = state
            result.final_status = "BLOCKED"
            return result

        state = self._transition(journal, state, OrchestrationState.EXECUTING, "Real Windows Playwright execution.")
        if requirement_id != "REQ-BRW-01" and not controlled_failure:
            journal.record_note(f"BLOCKED: no real functional-execution driver registered for {requirement_id} in this orchestrator build.")
            state = self._transition(journal, state, OrchestrationState.BLOCKED, "No real execution driver for this requirement.")
            result.final_state = state
            result.final_status = "BLOCKED"
            return result

        try:
            if controlled_failure:
                exec_ref = functional_execution.execute_controlled_failure(page, browser_version, worker_id, orchestration_id)
            else:
                exec_ref = functional_execution.execute_real_brw01(page, browser_version, worker_id, orchestration_id)
        except AssertionError as exc:
            # A real business assertion genuinely not holding is an
            # expected, legitimate outcome this orchestrator must carry
            # forward into RCA/Replanning/Governance -- never a process
            # crash. `real_execution()` (enh02_helpers.py) has already
            # persisted the real ExecutionLogRecord (status ERROR) before
            # re-raising; this is that same, established project
            # convention (see the Enhancement-02 closure work's own
            # totals-parsing-bug execution log, which shows the identical
            # pattern) -- the orchestrator now simply continues instead
            # of letting the exception propagate to the caller.
            journal.record_note(f"Real execution raised (expected, carried forward to RESULT_ANALYZED/RCA): {exc}")
            exec_ref = {
                "testcase_id": "ORCH-CONTROLLED-TEST-FAILURE-FIXTURE" if controlled_failure else "ENH02-TC-REQ-BRW-01-CATEGORY-GRID",
                "automation_id": "ORCH-PW-CONTROLLED-TEST-FAILURE-FIXTURE" if controlled_failure else "ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID",
            }

        from automation.playwright.logging_ import list_execution_log_ids, load_execution_log

        matching = sorted(
            (eid for eid in list_execution_log_ids() if eid.startswith(exec_ref["automation_id"] + "-") and orchestration_id in eid),
            reverse=True,
        )
        execution_id = matching[0] if matching else None
        execution_log = load_execution_log(execution_id) if execution_id else None
        result.stages["execution"] = {"execution_id": execution_id, "execution_log": execution_log}

        performance_result = None
        if run_performance and performance_execution.is_performance_relevant(requirement_id):
            performance_result = performance_execution.execute_real(requirement_id, run_id=f"PERF-{orchestration_id}")
            result.stages["performance"] = performance_result

            if performance_result.get("status") == "BLOCKED":
                # Sec. 18: a real JMeter/Java-unavailable (or subprocess-
                # failed) disposition is a real execution failure this
                # orchestration must carry into the SAME RCA-derived
                # replanning/governance vocabulary the functional path
                # uses -- but CP-07's own RCA pipeline is schema-scoped to
                # Playwright `ExecutionLogRecord`s (rca_orchestration.py's
                # own docstring), so it is never invoked here on a
                # `PerformanceRunRecord`; instead this orchestrator
                # classifies the real, disclosed `capability_result_detail`
                # deterministically (an unresolved JAVA_HOME/JMETER_EXECUTABLE
                # or a failed subprocess is always an ENVIRONMENT_ISSUE --
                # never a fabricated hypothesis) and derives the SAME
                # bounded replan action a functional ENVIRONMENT_ISSUE
                # failure would get.
                perf_replan_action = replanning_orchestration.determine_replan_action(
                    rca_replanning_decision="HUMAN_REVIEW_REQUIRED",
                    rca_confidence="HIGH",
                    failure_classification="ENVIRONMENT_ISSUE",
                )
                result.stages["performance_replanning"] = {
                    "failure_classification": "ENVIRONMENT_ISSUE",
                    "rationale": performance_result["record"].get("capability_result_detail"),
                    "replan_action": perf_replan_action,
                }
                journal.record_decision(make_decision(
                    orchestration_id=orchestration_id, stage=state, input_references=[performance_result["record"]["run_id"]],
                    decision=perf_replan_action["action"], reason=perf_replan_action["why"],
                    governance_state=GovernanceState.YELLOW, actor="RCAAgent",
                ).to_dict())

        # --- EVIDENCE_COLLECTED ---
        state = self._transition(journal, state, OrchestrationState.EVIDENCE_COLLECTED, "Real evidence persisted.")
        evidence_refs = (execution_log or {}).get("evidence_references", [])
        guard = governance.guard_evidence_not_fabricated(evidence_refs)
        journal.record_note(guard["rationale"])

        # --- RESULT_ANALYZED ---
        state = self._transition(journal, state, OrchestrationState.RESULT_ANALYZED, "Analyzing real execution result.")
        overall_status = (execution_log or {}).get("final_status", "NOT_EXECUTED")

        if overall_status == "PASS":
            journal.record_decision(make_decision(
                orchestration_id=orchestration_id, stage=state, input_references=[execution_id or ""],
                decision="NO_RCA_REQUIRED", reason="Execution PASSED; RCA/replanning stages skipped per sec. 11 branch model.",
                governance_state=GovernanceState.GREEN,
            ).to_dict())
            journal.update_summary(completed_requirement_ids=[requirement_id], pending_requirement_ids=[], execution_ids=[execution_id] if execution_id else [])
            state = self._transition(journal, state, OrchestrationState.REGRESSION, "Clean PASS -- proceeding to regression.")
        else:
            state = self._transition(journal, state, OrchestrationState.RCA_REQUIRED, f"Real execution status={overall_status} -- RCA required.")
            rca_result = rca_orchestration.run_rca_for_execution(execution_id)
            result.stages["rca"] = rca_result
            state = self._transition(journal, state, OrchestrationState.RCA_COMPLETE, "RCA pipeline complete.")

            state = self._transition(journal, state, OrchestrationState.REPLAN_ASSESSED, "Interpreting replanning + governance outcome.")
            replanning = rca_result.get("replanning", {})
            gov = rca_result.get("governance", {})
            gstate = governance.classify_governance_decision(gov.get("decision", "GOVERNANCE_BLOCKED"))
            replan_action = replanning_orchestration.determine_replan_action(
                rca_replanning_decision=replanning.get("decision", "HUMAN_REVIEW_REQUIRED"),
                rca_confidence=rca_result.get("rca", {}).get("confidence", "LOW"),
                failure_classification=rca_result.get("rca", {}).get("final_rca_classification"),
            )
            result.stages["replanning_governance"] = {"replanning": replanning, "governance": gov, "orchestration_governance_state": gstate, "replan_action": replan_action}
            journal.update_summary(
                completed_requirement_ids=[requirement_id], pending_requirement_ids=[],
                execution_ids=[execution_id] if execution_id else [],
                failures={requirement_id: overall_status},
                rca={requirement_id: rca_result.get("rca", {}).get("final_rca_classification")},
                replan={requirement_id: replan_action["action"]},
                governance_decision={requirement_id: gstate},
            )

            if gstate == GovernanceState.RED:
                state = self._transition(journal, state, OrchestrationState.BLOCKED, f"Governance RED: {gov.get('rationale')}")
                result.final_state = state
                result.final_status = "BLOCKED"
                return result
            elif gstate == GovernanceState.YELLOW:
                state = self._transition(journal, state, OrchestrationState.HUMAN_REVIEW, f"Governance YELLOW: {gov.get('rationale')}")
                journal.record_note("No reexecution authorized without explicit Human + Di approval; proceeding to regression with this failure disclosed.")
                state = self._transition(journal, state, OrchestrationState.REGRESSION, "Human review noted; proceeding to regression (no auto-reexecution).")
            else:
                state = self._transition(journal, state, OrchestrationState.ACTION_ALLOWED, f"Governance GREEN: {gov.get('rationale')}")
                state = self._transition(journal, state, OrchestrationState.REGRESSION, "No action required; proceeding to regression.")

        # --- REGRESSION (selection only -- see orchestration/regression.py; actual pytest invocation is external) ---
        regression_selection = regression_mod.select_scope(impact_result, risk_result, force_full=force_full_regression)
        result.stages["regression_selection"] = regression_selection

        # --- Frozen-integrity re-check before FINAL_REPORT ---
        srs_guard = governance.guard_srs_immutable(srs_baseline_hash)
        result.stages["srs_immutability_guard"] = srs_guard
        if not srs_guard["passed"]:
            state = self._transition(journal, state, OrchestrationState.BLOCKED, srs_guard["rationale"])
            result.final_state = state
            result.final_status = "BLOCKED"
            return result

        # --- FINAL_REPORT ---
        state = self._transition(journal, state, OrchestrationState.FINAL_REPORT, "Orchestration complete.")
        result.stages["coverage"] = coverage_mod.build_coverage_report()
        result.final_state = state
        result.final_status = overall_status if mode == ExecutionMode.REAL_EXECUTION else "DRY_RUN_COMPLETE"
        journal.update_summary(final_status=result.final_status)
        return result

    def run_batch(
        self,
        requirement_ids: List[str],
        mode: str = ExecutionMode.DRY_RUN,
        real_parallel_workers: int = 2,
        force_full_regression: bool = False,
    ) -> OrchestrationResult:
        """Multi-requirement orchestration (Orchestration Expansion
        instruction, Phase A/F). Unlike `run()`, this method owns its own
        real-execution lifecycle for REAL_EXECUTION mode (it invokes real
        `pytest -n <workers>` itself, via `orchestration.parallel_execution`,
        rather than requiring a caller-supplied `page` -- multiple real
        Chromium sessions genuinely need multiple real subprocess workers,
        which only pytest-xdist can provide safely). Never claims
        distributed (multi-machine) execution; local multi-worker
        parallelism only."""
        orchestration_id = new_orchestration_id()
        journal = OrchestrationJournal(orchestration_id, ",".join(requirement_ids))
        result = OrchestrationResult(orchestration_id, journal)
        journal.update_summary(
            selected_requirements=list(requirement_ids),
            completed_requirement_ids=[], pending_requirement_ids=list(requirement_ids),
        )

        srs_baseline_hash = governance.snapshot_srs_hash()
        state = OrchestrationState.RECEIVED
        journal.record_transition(None, state, f"Batch orchestration received for {requirement_ids} (mode={mode}).")

        # --- UNDERSTANDING / VALIDATED ---
        state = self._transition(journal, state, OrchestrationState.UNDERSTANDING, "Gathering requirement intelligence for every selected requirement.")
        intel_by_req: Dict[str, Dict] = {}
        for rid in requirement_ids:
            try:
                intel_by_req[rid] = requirement_intelligence.gather(rid, self.kb).to_dict()
            except requirement_intelligence.RequirementNotFoundError as exc:
                intel_by_req[rid] = {"error": str(exc)}
        result.stages["requirement_intelligence"] = intel_by_req
        state = self._transition(journal, state, OrchestrationState.VALIDATED, "Every selected requirement checked against real RAG + coverage-matrix sources.")

        # --- IMPACT_ANALYZED ---
        state = self._transition(journal, state, OrchestrationState.IMPACT_ANALYZED, "Running dependency/reusability impact analysis for every requirement.")
        impact_by_req = {rid: impact.analyze(rid) for rid in requirement_ids}
        result.stages["impact"] = impact_by_req

        # --- RISK_ASSESSED ---
        state = self._transition(journal, state, OrchestrationState.RISK_ASSESSED, "Running RBTP risk assessment for every requirement (deterministic).")
        risk_by_req = {rid: risk_mod.assess(rid, self.kb) for rid in requirement_ids}
        result.stages["risk"] = risk_by_req
        journal.update_summary(risk={rid: [r.get("priority") for r in rr.get("records", [])] for rid, rr in risk_by_req.items()})

        # --- TEST_STRATEGY_READY / TESTCASES_READY / DATA_READY ---
        state = self._transition(journal, state, OrchestrationState.TEST_STRATEGY_READY, "Determining test strategy for every requirement.")
        strategy_by_req = {rid: test_strategy.determine_strategy(rid) for rid in requirement_ids}
        result.stages["test_strategy"] = strategy_by_req

        state = self._transition(journal, state, OrchestrationState.TESTCASES_READY, "Selecting/generating testcases for every requirement.")
        testcase_by_req = {rid: testcase_orchestration.select_or_generate(rid, self.kb) for rid in requirement_ids}
        result.stages["testcases"] = testcase_by_req
        all_testcase_ids = sorted({tc["testcase_id"] for r in testcase_by_req.values() for tc in r["testcases"]})
        journal.update_summary(testcase_ids=all_testcase_ids)

        state = self._transition(journal, state, OrchestrationState.DATA_READY, "Selecting/generating test data for every testcase.")
        data_by_testcase = {tc_id: data_orchestration.select_or_generate(tc_id, self.kb) for tc_id in all_testcase_ids}
        result.stages["test_data"] = data_by_testcase
        all_dataset_ids = sorted({d for r in data_by_testcase.values() for d in r.get("dataset_ids", [])})
        journal.update_summary(dataset_ids=all_dataset_ids)

        # --- TRACEABILITY_VALID / AUTOMATION_READY ---
        state = self._transition(journal, state, OrchestrationState.TRACEABILITY_VALID, "Validating traceability chain for every requirement.")
        chain_by_req = {rid: traceability_orchestration.build_chain(rid) for rid in requirement_ids}
        validation_by_req = {rid: traceability_orchestration.validate(c) for rid, c in chain_by_req.items()}
        result.stages["traceability"] = {rid: {"chain": chain_by_req[rid], "validation": validation_by_req[rid]} for rid in requirement_ids}

        state = self._transition(journal, state, OrchestrationState.AUTOMATION_READY, "Assessing automation readiness for every requirement.")
        automation_by_req = {rid: automation_orchestration.assess(rid) for rid in requirement_ids}
        result.stages["automation"] = automation_by_req
        all_automation_ids = sorted({a for r in automation_by_req.values() for a in r.get("automation_ids", [])})
        journal.update_summary(automation_ids=all_automation_ids)

        # --- EXECUTION_PLANNED (Phase E: dependency-aware) ---
        state = self._transition(journal, state, OrchestrationState.EXECUTION_PLANNED, "Building dependency-aware, multi-requirement execution plan.")
        classifications = dependency_planning.classify_many(requirement_ids)
        by_category: Dict[str, List[str]] = {}
        for rid, c in classifications.items():
            by_category.setdefault(c.category, []).append(rid)
        result.stages["dependency_plan"] = {rid: c.to_dict() for rid, c in classifications.items()}
        result.stages["execution_plan_by_category"] = by_category
        journal.update_summary(execution_plan=by_category)

        if mode == ExecutionMode.DRY_RUN:
            journal.record_note("DRY_RUN: stopping before EXECUTING -- no SUT interaction performed. Plan (PLANNED, not EXECUTED) is fully computed above.")

            # Sec. 17: dry-run must EXPLICITLY produce every item in this
            # checklist -- never leave a reader to reconstruct it from
            # scattered per-stage fields.
            has_driver_by_req = {rid: functional_execution.has_real_driver(rid) for rid in requirement_ids}
            excluded_deferred = []
            for rid in requirement_ids:
                c = classifications[rid]
                if c.category == dependency_planning.ExecutionCategory.EXCLUSIVE:
                    excluded_deferred.append({"requirement_id": rid, "status": "EXCLUSIVE", "reason": c.reason})
                elif c.category == dependency_planning.ExecutionCategory.BLOCKED:
                    excluded_deferred.append({"requirement_id": rid, "status": "BLOCKED", "reason": c.reason})
                elif not has_driver_by_req[rid]:
                    excluded_deferred.append({
                        "requirement_id": rid, "status": "DEFERRED",
                        "reason": "No real execution driver registered for this requirement in this orchestrator build.",
                    })
            cr002 = governance.guard_cr002_not_implemented()
            result.stages["dry_run_summary"] = {
                "selected_requirements": list(requirement_ids),
                "selected_testcases": all_testcase_ids,
                "datasets": all_dataset_ids,
                "dependencies": {rid: c.to_dict() for rid, c in classifications.items()},
                "planned_execution_order": [rid for rid in requirement_ids if rid not in [e["requirement_id"] for e in excluded_deferred]],
                "parallel_groups": by_category,
                "expected_resources": {
                    "automation_ids": all_automation_ids,
                    "real_drivers_available_for": [rid for rid, has in has_driver_by_req.items() if has],
                },
                "excluded_or_deferred": excluded_deferred,
                "governance_constraints": {
                    "srs_content_hash": srs_baseline_hash,
                    "cr002_status": cr002["rationale"],
                    "performance_threshold_policy": "No approved numeric threshold -- SLA always reported INCONCLUSIVE (Approved SRS sec. 9.2).",
                },
            }

            result.final_state = state
            result.final_status = "DRY_RUN_COMPLETE"
            journal.update_summary(final_status=result.final_status, pending_requirement_ids=list(requirement_ids))
            return result

        # --- EXECUTING (REAL_EXECUTION) ---
        state = self._transition(journal, state, OrchestrationState.EXECUTING, "Real, local multi-worker Playwright execution for every requirement with a registered real driver.")

        executable_now = [
            rid for rid in requirement_ids
            if classifications[rid].category in (dependency_planning.ExecutionCategory.SAFE_PARALLEL, dependency_planning.ExecutionCategory.PREREQUISITE_DEPENDENT)
            and functional_execution.has_real_driver(rid)
        ]
        exclusive_not_run = [rid for rid in requirement_ids if classifications[rid].category == dependency_planning.ExecutionCategory.EXCLUSIVE]
        blocked = [rid for rid in requirement_ids if classifications[rid].category == dependency_planning.ExecutionCategory.BLOCKED]
        no_driver = [rid for rid in requirement_ids if rid not in executable_now and rid not in exclusive_not_run and rid not in blocked]

        if exclusive_not_run:
            journal.record_note(
                f"PLANNED, NOT EXECUTED this run: {exclusive_not_run} are classified EXCLUSIVE (single shared "
                "real SUT resource) -- real evidence for these already exists from prior, separately-authorized "
                "runs (Enhancement-02 closure, REQ-GCO-03 closure); not re-executed here to honor 'minimum "
                "necessary permanent state creation' and avoid unnecessary duplicate real accounts/orders."
            )
        if blocked:
            journal.record_note(f"BLOCKED, NOT EXECUTED: {blocked} -- {[classifications[r].reason for r in blocked]}")
        if no_driver:
            journal.record_note(f"PLANNED, NOT EXECUTED: {no_driver} have no real execution driver registered in this orchestrator build.")

        test_files = sorted({
            f"automation/playwright/tests/{dependency_planning.test_module_for(rid)}"
            for rid in executable_now if dependency_planning.test_module_for(rid)
        })

        parallel_result: Dict = {"status": "NOT_RUN", "reason": "No real execution driver was applicable."}
        new_execution_logs: Dict[str, Dict] = {}
        if test_files:
            from automation.playwright.logging_ import list_execution_log_ids, load_execution_log

            before_ids = set(list_execution_log_ids())
            parallel_result = parallel_execution.run_real_parallel(test_files, workers=real_parallel_workers)
            after_ids = set(list_execution_log_ids())
            for eid in sorted(after_ids - before_ids):
                record = load_execution_log(eid)
                if record:
                    new_execution_logs[eid] = record
        result.stages["real_parallel_execution"] = parallel_result
        result.stages["new_execution_logs"] = new_execution_logs

        # Attribute each fresh execution back to its requirement.
        completed: List[str] = []
        per_requirement_result: Dict[str, Dict] = {}
        for rid in executable_now:
            match = next(
                (eid for eid, rec in new_execution_logs.items() if rid in rec.get("requirement_ids", [])),
                None,
            )
            if match:
                per_requirement_result[rid] = {"execution_id": match, "final_status": new_execution_logs[match]["final_status"]}
                completed.append(rid)
            else:
                per_requirement_result[rid] = {"execution_id": None, "final_status": "NOT_EXECUTED", "note": "Real parallel run completed but no matching fresh execution log was found for this requirement."}
        result.stages["per_requirement_execution"] = per_requirement_result
        journal.update_summary(
            execution_ids=[v["execution_id"] for v in per_requirement_result.values() if v["execution_id"]],
            completed_requirement_ids=completed,
            pending_requirement_ids=[r for r in requirement_ids if r not in completed],
        )

        # --- EVIDENCE_COLLECTED ---
        state = self._transition(journal, state, OrchestrationState.EVIDENCE_COLLECTED, "Real evidence persisted for every completed requirement.")
        all_evidence_refs = [ref for rec in new_execution_logs.values() for ref in rec.get("evidence_references", [])]
        evidence_guard = governance.guard_evidence_not_fabricated(all_evidence_refs)
        journal.record_note(evidence_guard["rationale"])
        journal.update_summary(evidence_references=all_evidence_refs)

        # --- RESULT_ANALYZED -> RCA for any real failure ---
        state = self._transition(journal, state, OrchestrationState.RESULT_ANALYZED, "Analyzing real execution results for every completed requirement.")
        failures = {rid: v for rid, v in per_requirement_result.items() if v.get("final_status") not in ("PASS", "NOT_EXECUTED")}
        journal.update_summary(failures={rid: v["final_status"] for rid, v in failures.items()})

        rca_by_req: Dict[str, Dict] = {}
        replan_by_req: Dict[str, Dict] = {}
        governance_states: List[str] = []
        if failures:
            state = self._transition(journal, state, OrchestrationState.RCA_REQUIRED, f"Real failures found for {list(failures)} -- RCA required.")
            for rid, v in failures.items():
                rca_result = rca_orchestration.run_rca_for_execution(v["execution_id"])
                rca_by_req[rid] = rca_result
                replanning = rca_result.get("replanning", {})
                gov = rca_result.get("governance", {})
                gstate = governance.classify_governance_decision(gov.get("decision", "GOVERNANCE_BLOCKED"))
                governance_states.append(gstate)
                replan_action = replanning_orchestration.determine_replan_action(
                    rca_replanning_decision=replanning.get("decision", "HUMAN_REVIEW_REQUIRED"),
                    rca_confidence=rca_result.get("rca", {}).get("confidence", "LOW"),
                    failure_classification=rca_result.get("rca", {}).get("final_rca_classification"),
                )
                replan_by_req[rid] = {"replanning": replanning, "governance": gov, "governance_state": gstate, "replan_action": replan_action}
            state = self._transition(journal, state, OrchestrationState.RCA_COMPLETE, "RCA pipeline complete for every real failure.")
            state = self._transition(journal, state, OrchestrationState.REPLAN_ASSESSED, "Replanning + governance assessed for every real failure.")
            journal.update_summary(rca={rid: r.get("rca", {}).get("final_rca_classification") for rid, r in rca_by_req.items()}, replan={rid: r["replan_action"]["action"] for rid, r in replan_by_req.items()}, governance_decision={rid: r["governance_state"] for rid, r in replan_by_req.items()})
            result.stages["rca"] = rca_by_req
            result.stages["replan"] = replan_by_req

            if "RED" in governance_states:
                state = self._transition(journal, state, OrchestrationState.BLOCKED, f"At least one real failure is GOVERNANCE_BLOCKED (RED): {[rid for rid, r in replan_by_req.items() if r['governance_state'] == 'RED']}")
                result.final_state = state
                result.final_status = "BLOCKED"
                journal.update_summary(final_status=result.final_status)
                return result
            elif "YELLOW" in governance_states:
                state = self._transition(journal, state, OrchestrationState.HUMAN_REVIEW, "At least one real failure requires human review.")
                state = self._transition(journal, state, OrchestrationState.REGRESSION, "Human review noted for the affected requirement(s); proceeding to regression for the rest.")
            else:
                state = self._transition(journal, state, OrchestrationState.ACTION_ALLOWED, "No governance block found among real failures.")
                state = self._transition(journal, state, OrchestrationState.REGRESSION, "Proceeding to regression.")
        else:
            journal.record_note("No real failures in this batch -- RCA/Replanning/Governance stages skipped per sec. 11 branch model.")
            state = self._transition(journal, state, OrchestrationState.REGRESSION, "Clean batch (no real failures) -- proceeding to regression.")

        # --- REGRESSION (intelligent selection, aggregated across the whole batch) ---
        aggregate_impact = {
            "directly_impacted_testcase_ids": sorted({tc for r in impact_by_req.values() for tc in r.get("directly_impacted_testcase_ids", [])}),
            "indirectly_impacted_testcase_ids": sorted({tc for r in impact_by_req.values() for tc in r.get("indirectly_impacted_testcase_ids", [])}),
        }
        aggregate_risk = {"records": [rec for r in risk_by_req.values() for rec in r.get("records", [])]}
        regression_selection = regression_mod.select_scope(aggregate_impact, aggregate_risk, force_full=force_full_regression)
        result.stages["regression_selection"] = regression_selection

        # --- Frozen-integrity re-check before FINAL_REPORT ---
        srs_guard = governance.guard_srs_immutable(srs_baseline_hash)
        result.stages["srs_immutability_guard"] = srs_guard
        if not srs_guard["passed"]:
            state = self._transition(journal, state, OrchestrationState.BLOCKED, srs_guard["rationale"])
            result.final_state = state
            result.final_status = "BLOCKED"
            journal.update_summary(final_status=result.final_status)
            return result

        # --- FINAL_REPORT ---
        state = self._transition(journal, state, OrchestrationState.FINAL_REPORT, "Batch orchestration complete.")
        result.stages["coverage"] = coverage_mod.build_coverage_report()
        result.final_state = state
        overall_pass = completed and not failures
        result.final_status = "PASS" if overall_pass else ("PASS_WITH_FAILURES" if completed else "BLOCKED")
        journal.update_summary(
            final_status=result.final_status,
            completed_requirement_ids=completed,
            pending_requirement_ids=[r for r in requirement_ids if r not in completed],
        )
        return result

    def resume_batch(self, orchestration_id: str, mode: str = ExecutionMode.DRY_RUN, **kwargs) -> Dict:
        """Governed resume (Phase N): inspects the real, persisted
        journal via `orchestration.resume.plan_resume()` and, if genuine
        pending work exists, re-invokes `run_batch()` for ONLY the
        pending requirement_ids -- a completed requirement (real
        execution already produced a terminal status) is never
        re-executed. Returns the `ResumePlan` alone (never re-executes)
        when there is nothing safe/necessary to resume."""
        plan = resume_mod.plan_resume(orchestration_id)
        if plan.resume_state != resume_mod.ResumeState.RESUMABLE:
            return {"resumed": False, "plan": plan.to_dict()}

        new_result = self.run_batch(plan.pending_requirement_ids, mode=mode, **kwargs)
        return {
            "resumed": True,
            "plan": plan.to_dict(),
            "new_orchestration_result": new_result.to_dict(),
        }
