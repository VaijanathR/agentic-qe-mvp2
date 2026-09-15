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
    execution_planning,
    failure_classification,
    functional_execution,
    governance,
    impact,
    performance_execution,
    rca_orchestration,
    regression as regression_mod,
    replanning_orchestration,
    requirement_intelligence,
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
            result.stages["replanning_governance"] = {"replanning": replanning, "governance": gov, "orchestration_governance_state": gstate}

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
        return result
