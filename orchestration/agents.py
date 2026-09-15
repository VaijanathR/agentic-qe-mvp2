"""
Agentic QE Orchestration -- meaningful agent specialization (Wave 2
instruction sec. 10, 32).

Each class below is a real coordination boundary, not a renamed
function: every one owns a distinct real decision (what to select, how
to prioritize, whether to generate, how to execute, why something
failed, what to do next, what to report) and every `decide()`/`act()`
call returns a real `DecisionRecord` (`orchestration/decisions.py`)
naming itself as `actor`. No agent here is created merely for
terminology -- each wraps a real, already-existing deterministic module
this package built across the two prior orchestration waves; none
reimplements logic.

**LLM usage boundary, explicit per agent** (Wave 2 sec. 10: "The
architecture must document why an LLM is or is not used at each
boundary."):

| Agent | Uses LLM? | Why |
|---|---|---|
| RequirementAnalysisAgent | No | Real RAG (`knowledge.lib.retrieval`) + the real, governed 35-requirement coverage matrix are sufficient, deterministic, and already-authoritative -- an LLM would only reintroduce uncertainty into a question the KB already answers exactly. |
| TestPlanningAgent | No | RBTP (CR-001) risk factors are either evidence-backed (deterministic functions in `rbtp.evidence`) or honestly `UNKNOWN` -- an LLM guess would violate "never invent historical probabilities" (sec. 8). |
| TestDataAgent | Optional, real | Dataset field-*value* proposal (not structure/governance) is exactly CP-MVP2-04's own approved LLM boundary (`llm.test_data_client`) -- used only when no real dataset already exists, and only ever through the frozen, deterministic `testdata.validate` gate. |
| AutomationAgent | Optional, real | Testcase scenario-content proposal (not acceptance) is CP-MVP2-03's own approved LLM boundary (`llm.client`) -- see `orchestration/llm_boundary.py` for the real, evidence-backed demonstration (including a real rejection). |
| ExecutionAgent | No | Real tool invocation (Playwright/JMeter/pytest-xdist) has no reasoning step -- it is pure, real, deterministic tool execution. |
| RCAAgent | No | CP-MVP2-07's RCA pipeline is deliberately, permanently deterministic-only ("no LLM anywhere in CP-MVP2-07 RCA" -- `rca/analyze.py`'s own generation_metadata) -- reused unmodified. |
| ReplanningAgent | No | Same deterministic-only discipline as RCA; replanning decisions must be reproducible and auditable, never a model's judgment call. |
| QEReportingAgent | No | Pure aggregation of already-real, already-governed facts -- no reasoning is needed to count and cross-reference existing records. |
"""
from __future__ import annotations

from typing import Dict, List, Optional

from orchestration import (
    automation_orchestration,
    consolidated_matrix,
    coverage as coverage_mod,
    data_orchestration,
    dependency_planning,
    failure_classification,
    impact,
    llm_boundary,
    rca_orchestration,
    replanning_orchestration,
    requirement_intelligence,
    risk as risk_mod,
    test_strategy,
    testcase_orchestration,
)
from orchestration.decisions import DecisionRecord, make_decision


class RequirementAnalysisAgent:
    """Understands one requirement's identity, relationships,
    dependencies, and execution eligibility. No LLM (see module
    docstring)."""

    def decide(self, orchestration_id: str, requirement_id: str) -> DecisionRecord:
        try:
            intel = requirement_intelligence.gather(requirement_id)
        except requirement_intelligence.RequirementNotFoundError as exc:
            return make_decision(
                orchestration_id=orchestration_id, stage="REQUIREMENT_ANALYSIS", actor=self.__class__.__name__,
                input_references=[requirement_id], decision="EXCLUDE", reason=str(exc),
                confidence="HIGH", governance_state="RED", alternatives=["INCLUDE (rejected -- no real evidence)"],
            )
        impact_result = impact.analyze(requirement_id)
        classification = dependency_planning.classify(requirement_id)
        eligible = classification.category not in (
            dependency_planning.ExecutionCategory.BLOCKED,
        )
        return make_decision(
            orchestration_id=orchestration_id, stage="REQUIREMENT_ANALYSIS", actor=self.__class__.__name__,
            input_references=[requirement_id],
            decision="INCLUDE" if eligible else "EXCLUDE",
            reason=f"disposition={intel.disposition}; dependency_category={classification.category}; {classification.reason}",
            evidence_references=[],
            confidence="HIGH" if intel.approval_status else "MEDIUM",
            governance_state="GREEN" if eligible else "YELLOW",
            alternatives=[c for c in ("INCLUDE", "EXCLUDE", "DEFER") if c != ("INCLUDE" if eligible else "EXCLUDE")],
        )


class TestPlanningAgent:
    """Selects/prioritizes testcases via real RBTP. No LLM (see module
    docstring)."""

    def decide(self, orchestration_id: str, requirement_id: str) -> DecisionRecord:
        strategy = test_strategy.determine_strategy(requirement_id)
        risk_result = risk_mod.assess(requirement_id)
        priority = risk_result["records"][0]["priority"] if risk_result.get("records") else "UNKNOWN"
        return make_decision(
            orchestration_id=orchestration_id, stage="TEST_PLANNING", actor=self.__class__.__name__,
            input_references=[requirement_id],
            decision=f"PRIORITY={priority}",
            reason=f"corpus_source={risk_result.get('corpus_source')}; covered_scenario_types={strategy['covered_scenario_types']}; missing={strategy['missing_scenario_types']}",
            risk=priority,
            confidence="HIGH" if risk_result.get("records") else "LOW",
        )


class TestDataAgent:
    """Selects, or (when genuinely required) proposes via the real,
    governed CP-MVP2-04 LLM boundary, test data. LLM used only on the
    generation path, never on reuse (see module docstring)."""

    def decide(self, orchestration_id: str, testcase_id: str, governed_testcase=None) -> DecisionRecord:
        result = data_orchestration.select_or_generate(testcase_id, governed_testcase=governed_testcase)
        used_llm = result["mode"] == "GENERATE"
        return make_decision(
            orchestration_id=orchestration_id, stage="TEST_DATA", actor=self.__class__.__name__,
            input_references=[testcase_id],
            decision=result["mode"], reason=f"corpus_source={result.get('corpus_source')}",
            confidence="HIGH" if result["mode"] in ("REUSE", "NOT_REQUIRED") else "MEDIUM",
            proposed_action="Real CP-MVP2-04 LLM generation invoked" if used_llm else None,
        )


class AutomationAgent:
    """Maps testcases to executable automation; may propose new testcase
    content via the real, governed CP-MVP2-03 LLM boundary
    (`orchestration/llm_boundary.py`) when no real testcase exists yet.
    LLM used only on the generation path (see module docstring)."""

    def decide(self, orchestration_id: str, requirement_id: str) -> DecisionRecord:
        automation = automation_orchestration.assess(requirement_id)
        return make_decision(
            orchestration_id=orchestration_id, stage="AUTOMATION", actor=self.__class__.__name__,
            input_references=[requirement_id],
            decision=automation["readiness"], reason=automation.get("note", ""),
            confidence="HIGH" if automation["readiness"] == automation_orchestration.AutomationReadiness.READY else "LOW",
        )

    def propose_missing_scenario_with_llm(self, orchestration_id: str, requirement_id: str, scenario_types: List[str], llm=None) -> DecisionRecord:
        record = llm_boundary.propose(requirement_id, scenario_types, llm=llm)
        return make_decision(
            orchestration_id=orchestration_id, stage="AUTOMATION_LLM_PROPOSAL", actor=self.__class__.__name__,
            input_references=[requirement_id],
            decision=record.final_governed_decision, reason=record.deterministic_validation_result,
            confidence=record.confidence, evidence_references=[f"orchestration/generated/llm_calls/{record.call_id}"],
            proposed_action=f"provider={record.provider_model}",
        )


class ExecutionAgent:
    """Controls real tool execution (Playwright/JMeter/pytest-xdist). No
    LLM (see module docstring) -- pure real tool invocation, wrapped
    elsewhere by `Orchestrator.run()`/`run_batch()`, which this class
    intentionally does not duplicate (avoids a second execution path)."""

    def decide_mode(self, orchestration_id: str, requirement_id: str, dry_run: bool) -> DecisionRecord:
        from orchestration import functional_execution

        has_driver = functional_execution.has_real_driver(requirement_id)
        decision = "DRY_RUN_PLANNED" if dry_run else ("REAL_EXECUTED" if has_driver else "BLOCKED_NO_DRIVER")
        return make_decision(
            orchestration_id=orchestration_id, stage="EXECUTION", actor=self.__class__.__name__,
            input_references=[requirement_id], decision=decision,
            reason="Real driver registered." if has_driver else "No real driver registered for this requirement in this orchestrator build.",
            governance_state="GREEN" if (dry_run or has_driver) else "YELLOW",
        )


class RCAAgent:
    """Analyzes real evidence and classifies real failures. No LLM (see
    module docstring) -- reuses CP-MVP2-07 unmodified."""

    def decide(self, orchestration_id: str, execution_id: str) -> DecisionRecord:
        result = rca_orchestration.run_rca_for_execution(execution_id)
        if result.get("status") != "COMPLETE":
            return make_decision(
                orchestration_id=orchestration_id, stage="RCA", actor=self.__class__.__name__,
                input_references=[execution_id], decision="BLOCKED", reason=result.get("reason", ""),
                governance_state="RED",
            )
        rca = result["rca"]
        return make_decision(
            orchestration_id=orchestration_id, stage="RCA", actor=self.__class__.__name__,
            input_references=[execution_id],
            decision=f"{rca['final_rca_classification']}/{rca['final_rca_subtype']}",
            reason=rca["root_cause_hypothesis"], confidence=rca["confidence"],
            evidence_references=[execution_id],
        )


class ReplanningAgent:
    """Produces the next authorized action within governance constraints.
    No LLM (see module docstring) -- combines CP-MVP2-07's real
    replanning decision with this package's own bounded retry policy."""

    def decide(self, orchestration_id: str, rca_result: Dict) -> DecisionRecord:
        replanning = rca_result.get("replanning", {})
        rca = rca_result.get("rca", {})
        action = replanning_orchestration.determine_replan_action(
            rca_replanning_decision=replanning.get("decision", "HUMAN_REVIEW_REQUIRED"),
            rca_confidence=rca.get("confidence", "LOW"),
            failure_classification=rca.get("final_rca_classification"),
        )
        return make_decision(
            orchestration_id=orchestration_id, stage="REPLANNING", actor=self.__class__.__name__,
            input_references=[rca.get("rca_id", "")],
            decision=action["action"], reason=action["why"],
            approval_required=action["approval_required"],
            proposed_action=action["what_changes"],
            alternatives=[a for a in ("RETRY", "HUMAN_REVIEW", "ACTION_DEFERRED", "TERMINAL_FAILURE") if a != action["action"]],
        )


class QEReportingAgent:
    """Builds consolidated, evidence-backed reporting. No LLM (see
    module docstring) -- pure aggregation of already-real records."""

    def decide(self, orchestration_id: str, orchestration_ids: List[str]) -> DecisionRecord:
        rows = consolidated_matrix.build_matrix(orchestration_ids)
        summary = consolidated_matrix.summarize(rows)
        return make_decision(
            orchestration_id=orchestration_id, stage="QE_REPORTING", actor=self.__class__.__name__,
            input_references=orchestration_ids,
            decision=f"{summary['executed_count']}/{summary['total_requirements']} EXECUTED, {summary['passed_count']} PASSED",
            reason="Consolidated matrix built from real, persisted orchestration journal(s) only.",
            confidence="HIGH",
        )
