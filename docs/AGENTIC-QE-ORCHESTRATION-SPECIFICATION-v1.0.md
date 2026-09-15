# AGENTIC QE ORCHESTRATION — SPECIFICATION v1.0

**Status:** APPROVED — BASELINED v1.0 (this task)
**Starting baseline:** `905c1cb`
**Historical baselines:** MVP2 mechanism `33b9946`, Enhancement 01 `85dc6ab`, Enhancement 02 `521b155`, REQ-GCO-03 closure `905c1cb`

**Disclosed authoring note:** this specification was authored concurrently
with a real repository-discovery pass and the early implementation
iterations, rather than strictly before any code existed. The governing
instruction's own §7 ("First task — repository discovery... reuse
existing components, do not reinvent working infrastructure") made
discovery a genuine precondition for writing an accurate architecture
section — an architecture written before discovering that CR-001's real
RBTP and Dependency Matrix pipelines already exist, for example, would
have specified reinventing them. This document reflects the real,
implemented architecture, not a speculative one; per §8 it is frozen as
of this commit — no further substantial implementation changes are made
without a corresponding specification update.

---

## 1. Objectives

Evolve MVP2/Enhancement-01/Enhancement-02/CR-001's demonstrated QE
capabilities (RAG, LLM-boundary reasoning, testcase/testdata generation,
risk-based prioritization, dependency analysis, real Playwright
automation, real JMeter performance, RCA, replanning, governance,
reporting) from a **collection** of capabilities into a **governed,
evidence-driven, end-to-end orchestration system** that coordinates them
through an explicit lifecycle, with deterministic decision contracts,
a persisted orchestration journal, and a governance layer that can never
be bypassed by an LLM.

## 2. Scope

**In scope:** a central Orchestrator; an explicit state machine; decision
contracts; an orchestration journal; a governance layer (GREEN/YELLOW/RED
plus 8 explicit prohibited-action guards); Requirement Intelligence; Risk
Assessment (real RBTP reuse); Impact Analysis (real Dependency Matrix
reuse); Test Strategy; Testcase/Test Data selection-then-generation;
Traceability validation; Automation readiness assessment; Execution
Planning (dry-run/real, parallel-safety classification); real Functional
(Playwright) and Performance (JMeter) execution wrappers; a structural
adapter bridging Enhancement-01/02's execution-log schema into CP-06/07's
schema so CP-07's real RCA/Replanning/Governance pipeline can be reused
unmodified; bounded retry policy; regression-scope selection; multi-
dimension coverage reporting; a CLI entry point.

**Out of scope (explicitly deferred, per the governing instruction):**
CR-002 (runtime locator self-healing) implementation; Docker/CI-CD/
distributed execution implementation (extension points only, §14);
generalizing the CP-08 JMeter pipeline beyond its existing, committed
REQ-BRW-01 scenario; any modification of a frozen MVP2/CP01-09/
Enhancement-01/Enhancement-02/REQ-GCO-03-closure artifact.

## 3. Architecture

```text
User / CLI (orchestration/cli.py)
        |
Agentic QE Orchestrator (orchestration/orchestrator.py)
        |
Planning / Decision Layer
  - state machine (orchestration/state.py)
  - decision contract (orchestration/decisions.py)
  - orchestration journal (orchestration/journal.py)
  - governance layer (orchestration/governance.py)
        |
Specialized Stage Modules ("agents" -- plain, focused Python modules,
no framework; see sec. 5)
  requirement_intelligence -> risk -> impact -> test_strategy ->
  testcase_orchestration -> data_orchestration ->
  traceability_orchestration -> automation_orchestration ->
  execution_planning -> functional_execution / performance_execution ->
  execution_result_adapter -> rca_orchestration ->
  replanning_orchestration -> regression -> coverage
        |
RAG + LLM + Tools (all REUSED, not reimplemented)
  - knowledge.lib.retrieval.KnowledgeBase (CP-MVP2-02, real RAG)
  - llm.client / llm.test_data_client / llm.rbtp_client
    (CP-MVP2-03/04/CR-001, real provider abstraction: Stub/OpenAI/Claude)
  - testcases.pipeline / testdata.pipeline (CP-MVP2-03/04)
  - rbtp.pipeline / dependencies.pipeline (CR-001)
  - automation/playwright/* Page Object Model (Enhancement-01/02, real
    Windows Playwright)
  - performance.pipeline (CP-MVP2-08, real Windows JMeter)
        |
Functional / Performance Execution (real, non-mocked, against
https://demowebshop.tricentis.com/)
        |
Evidence (persistence.envelope, automation.playwright.logging_,
execution.persist, performance.persist -- all reused, unmodified)
        |
RCA / Replanning (rca.pipeline.run_cp07_rca -- CP-MVP2-07, real,
deterministic, reused unmodified via orchestration.execution_result_adapter)
        |
Governance (orchestration.governance -- GREEN/YELLOW/RED classification
of CP-07's own decision + 8 orchestration-level prohibited-action guards)
        |
Reporting (orchestration.coverage -- 7 separate coverage dimensions,
Generated != Executable != Executed != Passed != Fully Covered)
```

**Traceability and state flow** (governing instruction §21):

```text
Requirement -> Testcase -> Dataset -> Automation -> Execution -> Evidence
    -> RCA -> Replan -> Final Result
```

Every stage's output carries the IDs needed to reconstruct this chain;
`orchestration.traceability_orchestration.validate()` checks for orphaned
automation (declared but never really executed) on every run.

## 4. Core Architectural Principle (governing instruction §9)

| Layer | Responsibility | Real implementation |
|---|---|---|
| RAG | Authoritative knowledge | `knowledge.lib.retrieval.KnowledgeBase` (unmodified) |
| LLM | Reasoning / interpretation / planning / generation | `llm.client.LLMClient` implementations (unmodified); defaults to `StubLLMClient`/`StubTestDataClient` (deterministic, non-fabricating) unless a real provider is explicitly supplied |
| Deterministic Code | Validation / policy / state / traceability / enforcement | Every module in `orchestration/` except the LLM-client parameter itself |
| Agents | Specialized reasoning/action responsibilities | Plain Python modules (sec. 5) — no agent framework |
| Orchestrator | Workflow coordination | `orchestration.orchestrator.Orchestrator` |
| Tools | Actual system interaction | Real Windows Playwright / real Windows JMeter, invoked through the existing, unmodified Enhancement-01/02/CP-08 mechanisms |
| Evidence | Proof | `persistence.envelope`, `automation.playwright.logging_`, `execution.persist`, `performance.persist` — all real, all unmodified |
| Human | Governance authority | `orchestration.approval` — no approval can be self-synthesized (`record_decision()` requires a real `approved_by` string) |

The LLM is never the final authority: every governance guard, every
state transition, every coverage computation in this package is plain,
deterministic Python — verified explicitly in
`orchestration/tests/test_governance.py`.

## 5. Components / "Agents"

No agent framework was introduced (governing instruction §42, §64: "Do
not create artificial agents merely for terminology... unnecessary agent
frameworks... unless justified"). Each stage is a plain Python module
with a small, typed function-based interface, matching the established
style of every prior CP checkpoint in this repository:

| Module | Responsibility |
|---|---|
| `requirement_intelligence.py` | Consolidates RAG + coverage-matrix facts for one requirement |
| `risk.py` | Real RBTP risk assessment (CR-001, reused, deterministic-only) |
| `impact.py` | Real Dependency/Reusability Matrix impact analysis (CR-001, reused) |
| `test_strategy.py` | Covered vs. missing scenario types |
| `testcase_orchestration.py` | Select-then-generate testcases (CP-03 pipeline reused) |
| `data_orchestration.py` | Select-then-generate test data (CP-04 pipeline reused) |
| `traceability_orchestration.py` | Builds and validates the full chain |
| `automation_orchestration.py` | Assesses real automation readiness |
| `execution_planning.py` | Builds a dry-run/real execution plan; parallel-safety classification |
| `functional_execution.py` | Drives real Playwright business actions + the CONTROLLED TEST FAILURE fixture |
| `performance_execution.py` | Wraps the real, unmodified CP-08 JMeter pipeline |
| `execution_result_adapter.py` | Structural bridge: Enhancement-01/02 `ExecutionLogRecord` -> CP-06 `ExecutionResult` |
| `rca_orchestration.py` | Thin wrapper over the real, unmodified CP-07 RCA pipeline |
| `replanning_orchestration.py` | Bounded retry policy + replanning-prohibition guard |
| `failure_classification.py` | Extended (superset) failure taxonomy, mapped onto the frozen CP-06 base taxonomy |
| `regression.py` | Deterministic regression-scope selection |
| `coverage.py` | 7-dimension coverage report |
| `governance.py` | GREEN/YELLOW/RED + the 8 prohibited-action guards |
| `approval.py` | Structured human approval records |
| `journal.py` | Incrementally-persisted orchestration journal |
| `decisions.py` | The decision contract |
| `state.py` | The explicit lifecycle state machine |
| `safe_persistence.py` | Cross-platform-safe substitute for a real, disclosed bug in `persistence.envelope.load_latest()` (sec. 16) |
| `enh02_adapter.py` / `testcase_loader.py` | Structural adapters onto the two real testcase corpora this project has (CP-03 persisted, Enhancement-02 real) |
| `orchestrator.py` | The central coordinator |
| `cli.py` | Entry point |

## 6. State Machine

The baseline model from the governing instruction §11, implemented
verbatim in `orchestration/state.py::VALID_TRANSITIONS`, plus one
implementation-time addition (`BLOCKED`, reachable from every non-
terminal state) and two explicitly-justified branch points:
`RESULT_ANALYZED` may go straight to `REGRESSION` on a clean PASS
(skipping the RCA/Replan states entirely — "not every requirement needs
every stage," §10), and `REPLAN_ASSESSED`/`HUMAN_REVIEW` may proceed
directly to `REGRESSION` without a `REEXECUTION` when no reexecution is
authorized. Every transition is checked by
`orchestration.governance.guard_valid_state_transition()` before it is
applied; an unlisted transition raises `InvalidTransitionError`
deterministically (`orchestration/tests/test_state.py`).

## 7. Orchestration

`Orchestrator.run(requirement_id, mode, ...)` sequences every stage
module, recording a `DecisionRecord` and a journal entry at each one.
`DRY_RUN` mode stops at `EXECUTION_PLANNED` and never imports Playwright
(proven by `test_dry_run_without_page_never_imports_playwright`).
`REAL_EXECUTION` mode requires a real `(page, browser_version)` pair
(the same shape `automation/playwright/tests/conftest.py` already
provides) — this class never launches its own browser silently.

## 8. Decisions

Every major decision is a `DecisionRecord`
(`decision_id, orchestration_id, stage, input_references, decision,
reason, evidence_references, confidence, risk, governance_state,
proposed_action, approval_required, next_state`) — concise rationale and
evidence references only, never a hidden chain-of-thought (§37).

## 9. Traceability

See §3's diagram. `traceability_orchestration.build_chain()` cross-
references the real requirement coverage matrix against real, live-
verified execution logs (not merely the coverage matrix's own possibly-
stale `execution_ids` field) — `validate()` reports any orphaned
automation explicitly.

## 10. Evidence

No new evidence format was introduced. This package writes to the same,
existing, real, persisted stores every prior checkpoint uses
(`persistence.envelope`, `automation/playwright/generated/`,
`runs/` via `execution.persist`, `performance/generated/`,
`rca/generated/`, `rbtp/generated/`, `dependencies/generated/`), plus its
own new, additive `orchestration/generated/journal/` for the
orchestration journal itself.

## 11. Governance

`orchestration.governance` implements:
- `classify_governance_decision()` — maps CP-07's real
  `GovernanceDecision` (`NO_ACTION_REQUIRED` / `ACTION_DEFERRED_TO_HUMAN`
  / `GOVERNANCE_BLOCKED`, plus the never-actually-assigned
  `ACTION_AUTHORIZED`) onto this package's `GREEN`/`YELLOW`/`RED`.
- 8 independent `guard_*` functions, one per prohibited action in the
  governing instruction §58 (SRS immutability, expected-result
  immutability, permanent-state authorization, CR-002 non-
  implementation, evidence non-fabrication, human-approval presence,
  valid state transitions, approved performance threshold) — each
  covered by an explicit negative test in
  `orchestration/tests/test_governance.py`.
- `enforce()` — raises `GovernanceViolation` for a failed guard; never
  silently downgraded to a PASS anywhere in this package.

## 12. Execution

**Functional:** `functional_execution.py` reuses the existing
Enhancement-02 Page Object Model verbatim (no new locators, no new page
objects). It provides one real, demonstrated business action
(REQ-BRW-01: navigate to Books, observe the product grid) and one
CLEARLY-MARKED `CONTROLLED TEST FAILURE` fixture (a real page load, a
deliberately-missing locator assertion).

**Performance:** `performance_execution.py` wraps the real, unmodified
CP-MVP2-08 JMeter pipeline (`performance.pipeline.run_cp08_performance_scenario`),
scoped to its own existing, committed REQ-BRW-01 `.jmx` scenario —
never generalized or modified.

## 13. RCA / Replanning

`rca_orchestration.run_rca_for_execution(execution_id)` adapts a real
`ExecutionLogRecord` into CP-06's `ExecutionResult` shape
(`execution_result_adapter.py` — see §16 for the real cross-platform bug
this also had to work around) and invokes CP-07's real, unmodified,
fully deterministic pipeline
(`Observed Evidence -> Candidate Causes -> Evidence Comparison -> Most
Supported Cause -> Confidence -> Recommended Action`). No RCA logic is
reimplemented. `replanning_orchestration.py` layers a bounded retry
policy (§33: `ENVIRONMENT_ISSUE`/`TOOL_ISSUE` retryable, bounded to
`MAX_RETRIES=1`; everything else not retryable) and a defense-in-depth
scan for prohibited replanning phrases (§32) on top of CP-07's own
replanning decision.

## 14. Reporting

`coverage.py` reports 7 separate dimensions (requirement/testcase/
automation/execution/evidence/performance coverage, plus a "fully
covered" composite) and preserves Generated != Executable != Executed !=
Passed != Fully Covered at the per-requirement-row level — never
collapsed into one number.

## 15. Extension Points (governing instruction §65, §6)

- **Docker:** `functional_execution.py`/`performance_execution.py` take
  an already-constructed `page`/environment — a future Docker-packaged
  execution worker could satisfy that same interface without touching
  the orchestrator itself.
- **CI/CD:** `cli.py`'s subcommands are already scriptable
  (`orchestrate-requirement --real`, exit code 0/1) — a CI pipeline can
  invoke them directly.
- **Distributed execution:** `execution_planning.ParallelSafety` already
  distinguishes `SAFE_TO_PARALLELIZE` from `STATE_DEPENDENT`; a future
  distributed executor can read that classification. No distributed
  execution is claimed or implemented here (`CONFIGURED / NOT_IMPLEMENTED`,
  §28).
- **CR-002:** `orchestration.governance.guard_cr002_not_implemented()` is
  the explicit re-affirmation point; implementing CR-002 would mean
  changing that guard's expected outcome, which is exactly the kind of
  change this package is designed to make loud and impossible to do
  silently.
- **Additional LLM providers / SUTs / performance tools / security
  testing:** every stage module accepts its collaborator (KB, LLM
  client, page) as a parameter, never a hard-coded global.

## 16. Real Defect Found and Worked Around (disclosed)

`persistence.envelope.load_latest()` resolves a path string stored
inside an artifact's pointer file at write time. When an artifact was
persisted by a Windows-native Python process (this project's required
real-execution environment), that string is backslash-separated; reading
it back from a POSIX process (this package's own WSL-side orchestration
work) then fails with `FileNotFoundError`. This affects the majority of
this project's real evidence, since nearly all of it was legitimately
persisted via the Windows venv. `persistence/envelope.py` is a protected,
frozen, shared file and was not modified. `orchestration/safe_persistence.py`
works around it additively, by reusing the frozen, unaffected
`load_version()` (which builds its file path itself via plain
`pathlib` joins) instead of trusting the stored string — see that
module's own docstring for the full account, and
`orchestration/tests/test_safe_persistence.py` for a real reproduction
plus a live proof against this project's own real evidence corpus.

## 17. Acceptance Criteria

See the governing instruction §66 verbatim; every listed criterion is
demonstrated in the final execution report
(`docs/claude-execution-reports/AGENTIC-QE-ORCHESTRATION/`).

## 18. Limitations (disclosed, not hidden)

- Real functional/performance execution drivers are currently registered
  for exactly one requirement, `REQ-BRW-01` (chosen deliberately: real,
  read-only, zero new permanent SUT state, already
  `FUNCTIONAL_AND_PERFORMANCE`-dispositioned). Extending real-execution
  coverage to every one of the 35 requirements is a real, separate,
  larger task, not attempted here.
- `data_orchestration.py`'s generation path (CP-04 pipeline) is
  implemented and unit-tested but not exercised against the real SUT in
  this task's own real E2E demonstration, since REQ-BRW-01's real
  testcase declares zero required datasets by design.
- The CP-08 JMeter pipeline remains scoped to its own existing
  REQ-BRW-01 scenario; this package does not generalize it to other
  performance-relevant requirements (e.g. REQ-SRCH-01's own separate,
  pre-existing `.jmx`), per governing instruction §4's protected-asset
  rule.
- `execution_result_adapter.py`'s `action_type` inference is a small,
  disclosed keyword heuristic over free-text step descriptions (no
  structured `action_type` field exists on `ExecutionLogRecord`); for a
  synthetic step description like "Unhandled exception" (added by
  `real_execution()`'s own exception handler) it can produce a
  misleadingly-specific RCA subtype (`BROWSER_LAUNCH_FAILURE`) — real,
  disclosed, and visible in the controlled-failure demonstration's own
  evidence; never silently corrected to look more accurate than it is.
- Distributed execution and Docker packaging remain `CONFIGURED /
  NOT_IMPLEMENTED` — no second machine or container runtime was used.
