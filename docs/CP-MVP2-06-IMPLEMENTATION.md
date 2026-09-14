# CP-MVP2-06 — Real Browser Execution: Implementation Notes

Implements the frozen `docs/CP-MVP2-06-SPECIFICATION-v1.0.md`
(SHA-256 `acff2a219251e3343c94e971ce46787b2318605f27f88654c3626e459b14571d`)
on top of the unmodified CP-MVP2-01–05 layers. This document explains the
implementation; it does not redefine or extend the specification.

## Architecture

```text
ACCEPTED/POSSIBLE_DUPLICATE CP-MVP2-05 PLAYWRIGHT ARTIFACT + its linked CP-MVP2-04 dataset
      |
DETERMINISTIC ELIGIBILITY CHECK        (execution/validate.py::check_eligibility)
      |
DEFENSIVE PRE-EXECUTION RE-VALIDATION  (execution/validate.py::validate_pre_execution,
      |                                 validate_data_field_availability)
      |
AUTHORIZATION / DATA-OQ-01 GATES       (execution/validate.py::check_authorization_precondition,
      |                                 assess_data_oq_01)
      |
REAL CHROMIUM-HEADLESS EXECUTION       (execution/engine.py::BrowserExecutor — genuine
      |                                 Playwright automation, never mocked in this module)
      |
DETERMINISTIC ASSERTION EVALUATION + EVIDENCE CAPTURE  (execution/evidence.py, execution/engine.py)
      |
EXECUTION RESULT + FAILURE CLASSIFICATION + GOVERNANCE  (execution/schema.py, execution/pipeline.py)
      |
CP-MVP2-06 RESULT  (execution/pipeline.py::run_cp_mvp2_06())
```

| Path | Role |
|---|---|
| `execution/schema.py` | `OverallStatus`/`StepStatus`/`FailureCategory`/`FailureSubtype` vocabularies, `FAILURE_SUBTYPE_TO_CATEGORY` mapping, `StepResult`/`AssertionResult`/`ExecutionResult` dataclasses. |
| `execution/validate.py` | Deterministic, LLM-free eligibility + pre-execution + authorization + DATA-OQ-01 + data-field-availability checks. |
| `execution/evidence.py` | `EvidenceManager` — real file I/O under `runs/cp_mvp2_06/<execution_id>/`, plus `redact_field_value()`. |
| `execution/engine.py` | `BrowserExecutor` — the only module that touches Playwright; genuine Chromium-headless automation, never a stub code path. |
| `execution/pipeline.py` | `run_cp_mvp2_06()` — the single orchestration entry point; sequences the gates above and derives the final governed result. |

## Design decision — no new LLM client is introduced

Unlike CP-MVP2-04/05, CP-MVP2-06 introduces **no** LLM component at all
(frozen spec secs. 4/17: "there is no LLM component anywhere in
CP-MVP2-06"). `execution/validate.py` performs only plain
equality/membership/lookup checks against the CP-MVP2-05 artifact's own
already-governed fields. `llm/client.py` is unmodified (confirmed by
`git diff` throughout this task, exactly as at every prior checkpoint).

## CP-05 is the execution contract, not a target for repair

`execution/validate.py::check_eligibility()` performs a pure membership
check against the artifact's existing `GovernanceStatus`
(`ACCEPTED`/`POSSIBLE_DUPLICATE` eligible, every other value —
`REJECTED`/`QUARANTINED`/`UNSUPPORTED_NEEDS_CLARIFICATION`/`DUPLICATE`
— not). It never re-derives, second-guesses, or "fixes" the upstream
CP-MVP2-05 decision. `execution/engine.py` uses each step's `locator`
and `input_mapping` **verbatim** — on any step failure the engine
records the failure and stops; it never searches for an alternative
locator, rewrites a selector, or regenerates the artifact (frozen spec's
explicit "NO SELF-HEALING" requirement).

## Gate order (`execution/pipeline.py::run_cp_mvp2_06`)

1. `check_eligibility` — ineligible → **NOT_EXECUTED** (design-time, spec sec. 18).
2. `validate_pre_execution` — schema/locator/traceability defects → **NOT_EXECUTED** (design-time).
3. `validate_data_field_availability` — unresolvable `input_mapping` → **NOT_EXECUTED** (design-time).
4. `check_authorization_precondition` — a precondition names an authenticated session/existing account that no reusable fixture can establish → **BLOCKED** / `AUTHORIZATION_ISSUE` (runtime-eligible, environment-blocked).
5. `assess_data_oq_01` — the artifact's requirement IDs intersect `STATE_MUTATING_REQUIREMENT_IDS` → **BLOCKED** / `ENVIRONMENT_ISSUE` / subtype `DATA_OQ_01_UNRESOLVED`.
6. Only if all five gates pass: real `BrowserExecutor.run_steps()` — a `BrowserLaunchError` → **ERROR** / `TOOL_ISSUE` / `BROWSER_LAUNCH_FAILURE`; otherwise step results plus assertion evaluation determine `PASS`/`FAIL`.

Gates 1–3 are strictly design-time (the artifact was never eligible to
run); gates 4–5 are genuine runtime-eligible artifacts blocked by an
environment/precondition limitation; only step 6 performs real browser
work. This mirrors the frozen spec's design-time-vs-runtime distinction
(sec. 18) exactly, and is asserted directly in the test suite (mocked
`BrowserExecutor.assert_not_called()` for every gate-1–5 outcome).

## Disclosed simplification — `BUSINESS_REQUIRED` assertion evaluation

The frozen CP-MVP2-05 `Assertion.condition` field is free narrative text
(e.g. "the new address is saved and checkout proceeds to the shipping
method step"). CP-MVP2-06 v1.0 has no NLP/DOM condition-matching
component specified, and none is introduced here. The implemented
proxy — disclosed, not hidden — is: **a `BUSINESS_REQUIRED` assertion is
recorded `passed=True` iff every step in the artifact reached
`StepStatus.PASS`.** This is a documented limitation, not a governance
decision: it means CP-MVP2-06 v1.0 can detect that the scripted step
sequence completed without error, but cannot yet independently verify
that the *narrative* business condition was actually satisfied by the
resulting page state. `TECHNICAL_USEFUL`/`DIAGNOSTIC_OPTIONAL`
assertions are recorded identically but never influence `overall_status`
(frozen spec sec. 11), verified directly in
`tests/test_cp_mvp2_06_execution.py`.

## Real evidence produced this task

1. **Infrastructure capability check** (`BrowserExecutor.check_infrastructure`,
   never tied to any artifact, spec sec. 16/26): a genuine Chromium
   `151.0.7922.34` headless launch, real navigation to
   `https://demowebshop.tricentis.com/`, HTTP 200, a real 99,518-byte
   1280×720 PNG screenshot at
   `runs/cp_mvp2_06/INFRA-CHECK-01/infrastructure_check.png`, ~12.3s
   elapsed. This demonstrates the environment *can* run a real browser
   against the real SUT; it is explicitly not an artifact execution.
2. **Live-verification decision-tree exercise** (spec sec. 26, task
   instruction's "LIVE BROWSER VERIFICATION" section): the real
   CP-03→CP-04→CP-05 stub pipelines were re-run for all four previously
   profiled requirements (`REQ-REG-01`, `REQ-ACO-03`, `REQ-PAY-01`,
   `REQ-CART-03`), producing **22 real CP-MVP2-05 `PlaywrightArtifact`s
   — every one governed `UNSUPPORTED_NEEDS_CLARIFICATION`**. Each of the
   22 was fed through the real `run_cp_mvp2_06()`; every one correctly
   and deterministically returned `NOT_EXECUTED` with note
   `INELIGIBLE: {'governance_status': 'UNSUPPORTED_NEEDS_CLARIFICATION'}`
   — no browser was launched for any of them (by construction: gate 1
   runs before `BrowserExecutor` is ever instantiated). Full raw result
   set: `runs/cp_mvp2_06/VERIFY-ALL-01/results.json`.
3. Question 1 of the decision tree ("Is there an ACCEPTED or
   POSSIBLE_DUPLICATE CP-MVP2-05 artifact that is actually executable?")
   is therefore answered **NO, by direct re-derivation, not by
   assumption** — carrying forward, and now formally re-confirming as
   this task's own evidence, the same finding already disclosed at the
   CP-MVP2-05 and CP-MVP2-06-specification checkpoints. Per the
   instruction's own decision tree, this is "an acceptable and
   potentially valuable CP-MVP2-06 governance result" — the correct
   action is a governed `NOT_EXECUTED`, not manufacturing an executable
   artifact.
4. A single earlier manual smoke exercise of `run_cp_mvp2_06()`'s
   step-execution path against a synthetic single-`NAVIGATE`-step
   artifact (disclosed as synthetic, used only to prove
   `BrowserExecutor.run_steps()` itself performs genuine Playwright
   automation end-to-end) produced real evidence at
   `runs/cp_mvp2_06/EXEC-PW-TEST-01-01/execution.log` (`step 1 [NAVIGATE]
   -> PASS`). This is a mechanism check, not a business-scenario
   execution, and is reported as such.

## DATA-OQ-01 — implementation-time disposition

`STATE_MUTATING_REQUIREMENT_IDS` (`execution/validate.py`) is a fixed,
evidence-cited (Approved SRS §6.1/§6.9/§6.10/§6.13) set: `REQ-REG-01`,
`REQ-GCO-01/02/03`, `REQ-ACO-01`, `REQ-CONF-01/02`. Any artifact whose
`requirement_ids` intersects this set is blocked at gate 5 regardless of
how "safe-looking" its CP-MVP2-04 data is — synthetic field values alone
never establish a data-reset/isolation policy. This is a deliberate,
conservative implementation of the frozen spec's DATA-OQ-01 elevation;
no attempt was made to weaken it to obtain a PASS.

## Known limitations / advisories (carried forward + new)

* No `ACCEPTED`/`POSSIBLE_DUPLICATE` CP-MVP2-05 artifact currently
  exists for any of the four profiled requirements — a pre-existing
  CP-MVP2-05-layer condition (locator ambiguity / zero evidence), not a
  CP-MVP2-06 defect. Re-confirmed by this task's own evidence (see above).
  Because none is eligible, this task's live-browser exercise of a real
  *business* scenario is a governed `NOT_EXECUTED`, not a `PASS`/`FAIL`.
* `BUSINESS_REQUIRED` assertion evaluation is a step-success proxy, not
  narrative-condition verification (see above) — disclosed, not hidden.
* No reusable authenticated-session fixture exists; `check_authorization_precondition`
  will `BLOCKED` any artifact whose precondition text names one.
* DATA-OQ-01 remains genuinely unresolved at the SRS level; CP-MVP2-06
  never attempts to resolve it — it only detects and blocks the risk.
* Retry and self-healing are both absent by design (frozen spec v1.0
  explicitly prohibits both).
* CP-MVP2-07 (self-healing) is the disclosed downstream consumer of a
  `LOCATOR_FAILURE`/`ASSERTION_FAILURE` result; it is **not started**
  by this task.
