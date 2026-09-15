# AGENTIC QE ORCHESTRATION — ARCHITECTURE

Companion diagram document to `docs/AGENTIC-QE-ORCHESTRATION-SPECIFICATION-v1.0.md`
(the specification is the authoritative, detailed description; this
document is diagrams + brief captions only, per governing instruction
§61 "avoid duplicate documents").

## System Architecture (governing instruction §62)

```text
                              User / CLI
                                  |
                    Agentic QE Orchestrator
                  (orchestration/orchestrator.py)
                                  |
                  Planning / Decision Layer
      state.py -- decisions.py -- journal.py -- governance.py
                                  |
              Specialized Stage Modules (plain Python,
                     no agent framework)
   requirement_intelligence -> risk -> impact -> test_strategy
   -> testcase_orchestration -> data_orchestration
   -> traceability_orchestration -> automation_orchestration
   -> execution_planning
                                  |
                    RAG + LLM + Tools (all reused)
   knowledge.lib.retrieval | llm.client/test_data_client/rbtp_client
   | testcases.pipeline | testdata.pipeline | rbtp.pipeline
   | dependencies.pipeline | automation/playwright Page Object Model
   | performance.pipeline
                                  |
          Functional / Performance Execution (REAL, non-mocked)
        Windows Chromium (Playwright)  |  Windows JMeter
        against https://demowebshop.tricentis.com/
                                  |
                             Evidence
   persistence.envelope | automation.playwright.logging_
   | execution.persist | performance.persist
                                  |
                        RCA / Replanning
        rca.pipeline.run_cp07_rca (CP-MVP2-07, reused, unmodified)
        via orchestration.execution_result_adapter
                                  |
                           Governance
        GREEN / YELLOW / RED  +  8 prohibited-action guards
        (orchestration/governance.py)
                                  |
                            Reporting
      7 coverage dimensions, Generated != Executable != Executed
                  != Passed != Fully Covered
```

## Traceability Chain

```text
Requirement
    |
Testcase          (reuse-first: CP-03 persisted corpus, then
    |               Enhancement-02 real corpus, then CP-03 pipeline
    |               generation as a last resort)
Dataset           (reuse-first: Enhancement-02 real corpus, then
    |               CP-04 persisted corpus, then CP-04 pipeline
    |               generation)
Automation        (real Playwright Page Object Model; readiness
    |               validated, never regenerated)
Execution         (real Windows Chromium / real Windows JMeter)
    |
Evidence          (execution log + screenshot / JMeter .jtl+.log)
    |
RCA               (CP-07, real, deterministic -- only on a real failure)
    |
Replan            (CP-07 + bounded retry policy)
    |
Final Result      (orchestration journal + final QE report)
```

## Orchestration State Flow

```text
RECEIVED -> UNDERSTANDING -> VALIDATED -> IMPACT_ANALYZED
   -> RISK_ASSESSED -> TEST_STRATEGY_READY -> TESTCASES_READY
   -> DATA_READY -> TRACEABILITY_VALID -> AUTOMATION_READY
   -> EXECUTION_PLANNED
        |
        +-- DRY_RUN: stop here (display-only, SUT never touched)
        |
        +-- REAL_EXECUTION -> EXECUTING -> EVIDENCE_COLLECTED
              -> RESULT_ANALYZED
                    |
                    +-- clean PASS --------------------> REGRESSION
                    |
                    +-- FAIL/ERROR -> RCA_REQUIRED -> RCA_COMPLETE
                          -> REPLAN_ASSESSED
                                |
                                +-- GREEN  -> ACTION_ALLOWED -> REGRESSION
                                +-- YELLOW -> HUMAN_REVIEW   -> REGRESSION
                                +-- RED    -> BLOCKED (terminal)
                    -> REGRESSION -> FINAL_REPORT

(any non-terminal state) -> BLOCKED   -- a governance conflict, frozen-spec
                                          conflict, or unsafe condition can
                                          surface at any stage
```

## Real, Demonstrated Runs (this task)

| Run | Mode | Result | Evidence |
|---|---|---|---|
| REQ-BRW-01 functional | REAL_EXECUTION | PASS | `automation/playwright/generated/executions/ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID-ORCH-20260915-194952-0001I7-main-1789501792949/` |
| REQ-BRW-01 performance | REAL_EXECUTION | PASS (capability), SLA INCONCLUSIVE | `performance/generated/records/PERF-RUN-20260915T195036Z/` |
| CONTROLLED TEST FAILURE | REAL_EXECUTION | ERROR -> RCA -> Replan (HUMAN_REVIEW_REQUIRED) -> Governance (YELLOW) | `automation/playwright/generated/executions/ORCH-PW-CONTROLLED-TEST-FAILURE-FIXTURE-ORCH-20260915-195201-0001Q0-main-1789501921681/`, `rca/generated/{rca,replanning,governance}/*ORCH-20260915-195201-0001Q0*` |

Full detail in `docs/claude-execution-reports/AGENTIC-QE-ORCHESTRATION/`.
