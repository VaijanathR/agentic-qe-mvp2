# CP-MVP2-07 — RCA, Replanning & Governance — Execution Report

Timestamp (UTC): 2026-09-15T09:17:07Z

## 1. Objective

Demonstrate that the Agentic QE system can consume real, persisted CP-MVP2-06 execution
evidence, determine what happened, classify the failure, perform evidence-based RCA,
determine whether replanning is appropriate, and produce a governed, persisted outcome —
per `docs/CP-MVP2-07-SPECIFICATION-v1.0.md`.

## 2. Frozen Specification Reference

- `docs/CP-MVP2-07-SPECIFICATION-v1.0.md` (self-authored this task; no prior CP-07
  specification existed anywhere in the repository — confirmed via `find . -iname "*CP*07*"`
  under `docs/`, zero results, before authoring). Frozen via
  `docs/CP-MVP2-07-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`,
  SHA-256 `c94521220ab926e7a52907db3a0b5bd13cda72f97ac589311af1e86db6f7bd79`.
- Faithfully derived from this task's own governing instruction sections 1–21
  (`ClaudeInstructions/CP-MVP2-07_instructions/inst-15092026-1433.md`), mirroring the exact
  SPECIFY → SELF-REVIEW → FREEZE → IMPLEMENT precedent already used for
  `docs/CP-MVP2-06-SPECIFICATION-v1.0.md`.

## 3. Starting HEAD

`9e122eaa00f08a05700aafc2d51b9a2d09ea3682` (CP-MVP2-06 governance closure commit — CP-06
GREEN WITH ADVISORIES, 38/38 focused + 300/300 full regression, frozen-artifact integrity
verified, fresh-clone verified).

## 4. CP-06 Evidence Consumed

Real, previously-persisted CP-MVP2-06 `ExecutionResult` artifacts on disk under `runs/`,
never regenerated, never fabricated:

| execution_id | testcase_id | overall_status | classification / subtype |
|---|---|---|---|
| `REALISM-SLICE-EXEC-D01` | `TC-REQ-ACO-03-01` | FAIL | ENVIRONMENT_ISSUE / TIMEOUT |
| `REALISM-SLICE-EXEC-D02` | `TC-REQ-ACO-03-01` | FAIL | ENVIRONMENT_ISSUE / TIMEOUT |
| `MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02` | `TC-REQ-ACO-03-01` | FAIL | ENVIRONMENT_ISSUE / TIMEOUT |
| `BATCH2-MECHANISM-CHECK-01` | `TC-MECHANISM-CHECK-01` | PASS | N/A |

`REALISM-SLICE-EXEC-D01` was used as the primary evidence for the full, end-to-end governed
decision walk demonstrated in this report; the other two real FAIL executions and the real
PASS execution were run through the same pipeline to prove the full decision space (FAIL →
HUMAN_REVIEW_REQUIRED/ACTION_DEFERRED_TO_HUMAN, PASS → REPLAN_NOT_ALLOWED/NO_ACTION_REQUIRED)
using only real, on-disk evidence — no synthetic ExecutionResult was ever constructed.

## 5. Failure Detected

`REALISM-SLICE-EXEC-D01`: Step 2 (FILL on `#BillingNewAddress_FirstName`) failed with
`TIMEOUT: Page.fill: Timeout 30000ms exceeded.` immediately after a single, successful
NAVIGATE step (home page), with no intervening business step establishing deeper
application/page state. All subsequent steps recorded `NOT_EXECUTED` (skipped: a prior
load-bearing step failed) per the frozen CP-06 engine's own load-bearing-step semantics.

## 6. Failure Classification

Deterministically re-derived by `rca/classify.py::reclassify_from_evidence()`, reusing
`execution.schema.FailureCategory`/`FailureSubtype`/`FAILURE_SUBTYPE_TO_CATEGORY` verbatim
(no new category invented, per frozen spec sec. 5):

- `final_rca_classification`: `ENVIRONMENT_ISSUE`
- `final_rca_subtype`: `TIMEOUT`

This matches the real, stored `failure_classification` already recorded by the frozen,
unmodified `execution.pipeline.run_cp_mvp2_06()` — independently re-verified here from raw
step-level evidence rather than merely trusted.

## 7. Evidence Reviewed

- Real `step_results` (13 steps; 1 PASS, 1 FAIL, 11 NOT_EXECUTED), real `error_information`
  (Playwright timeout call-log), real `assertion_results` (BUSINESS_REQUIRED, not evaluated),
  real `evidence_references`.
- Real, persisted testcase content for `TC-REQ-ACO-03-01` (`testcases/generated/`), confirming
  the testcase's own business steps contain no precondition-establishing action (e.g.
  add-to-cart, begin-checkout) before the billing-form FILL steps.
- Real historical evidence: 5 other persisted executions of the same `testcase_id` lineage
  (2 comparable — `REALISM-SLICE-EXEC-D02` and `MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02`, both
  real FAIL/ENVIRONMENT_ISSUE/TIMEOUT; 3 non-comparable `NOT_EXECUTED` pre-locator-resolution
  entries, correctly excluded from the confidence computation as neither corroborating nor
  conflicting).

## 8. RCA

Produced by `rca/analyze.py::build_rca_record()`, structurally separating:

- **FACT** — `failure_symptom` (the literal recorded status/error string).
- **EVIDENCE** — `observed_evidence` (real step/assertion/evidence-reference data),
  `requirement_testcase_data_context` (real, loaded testcase content),
  `historical_evidence` (5 real prior executions, unfiltered, fully disclosed).
- **INFERENCE** (explicitly labeled, never presented as fact) — `agent_inference`: "The
  first failure occurred at step 2 (FILL), immediately after a single, successful NAVIGATE
  step with no intervening business action... consistent with the browser being on the SUT's
  home page when the failing locator was attempted, rather than on the page that locator's
  real DOM evidence was captured from... Of 5 other real, persisted execution(s) of this same
  testcase lineage (2 of which reached real browser execution and are directly comparable),
  2/2 comparable execution(s) share the identical overall_status/failure_classification
  pattern — cited as supporting historical evidence only, per sec. 7; it does not override
  this execution's own current evidence."
- **CONCLUSION** — `root_cause_hypothesis`: "The failure is attributable to a testcase-content
  limitation (the persisted testcase's own business steps do not specify the
  precondition-establishing actions this scenario's real evidenced locators require), not a
  defect in locator resolution, browser tooling, or the CP-MVP2-06 execution engine."
- **RECOMMENDATION** (never self-executed) — `recommended_next_action`: "RECOMMENDATION ONLY,
  NOT AUTHORIZED, NOT IMPLEMENTED: author a richer, specific testcase (via a future,
  separately-authorized task) that includes the precondition-establishing business steps this
  scenario requires; alternatively, a formal Human + Di decision on CR-002 (runtime locator
  fallback) could be sought, though that would not resolve this specific testcase-content
  limitation."

## 9. Confidence

`HIGH` — 2/2 comparable (real, browser-reaching) historical executions share the identical
FAIL/ENVIRONMENT_ISSUE/TIMEOUT pattern with the current execution; non-comparable
`NOT_EXECUTED` historical entries are correctly excluded from this computation.

## 10. Replanning Analysis

`rca/replan.py::decide_replanning()` → **`HUMAN_REVIEW_REQUIRED`**. This is a real,
evidence-justified outcome, not an artificial one manufactured to exercise the vocabulary
(frozen spec sec. 11): a high-confidence root cause was established, but the only real
corrective action (authoring richer testcase content establishing the missing precondition)
requires inventing business-step content this checkpoint has no authority to invent (frozen
spec sec. 9). `proposed_change` is recorded as a recommendation only, never applied;
`human_approval_required=True`.

The real PASS execution (`BATCH2-MECHANISM-CHECK-01`) correctly produced `REPLAN_NOT_ALLOWED`
("Execution PASSED; there is nothing to replan.") — proving the vocabulary's negative branch
is also real, not merely asserted.

A synthetic `LOCATOR_FAILURE`-subtype RCA record (constructed only inside
`tests/test_cp07_rca.py`, never from real evidence, to exercise a decision branch this
project's real evidence does not currently exhibit) correctly produces `GOVERNANCE_BLOCKED`,
citing CR-002's unauthorized status.

## 11. Governance Decision

`rca/govern.py::decide_governance()` → **`ACTION_DEFERRED_TO_HUMAN`**, after:

1. The prohibited-change guard (`verify_frozen_artifacts_unchanged`, a real SHA-256
   content-hash comparison over 16 curated frozen paths, captured at pipeline start,
   re-verified at pipeline end) — **PASSED**, zero diffs.
2. The CR-002 live re-affirmation check (`check_cr002_status`, reading
   `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md` directly) — confirmed
   `PROPOSED` / `NOT AUTHORIZED` / `NOT IMPLEMENTED` still holds.

No automated action was authorized or executed; the outcome is fully deferred to Human + Di.

## 12. CR-002 Disposition

Remains **OPEN — FUTURE CHANGE, NOT AUTHORIZED**. CP-07 did not implement, self-authorize, or
recommend implementing runtime locator fallback as part of this task. Where CR-002 was
referenced (the LOCATOR_FAILURE replanning branch, and this RCA's own recommended_next_action
disclosure), it was recorded only as a non-binding, non-resolving mention for Human + Di —
never actioned.

## 13. Regression Results

- CP-07 focused suite (`tests/test_cp07_rca.py`): **31/31 passed**.
- Full regression (`tests/`): **331/331 passed** (300 pre-existing + 31 new CP-07 tests; zero
  existing test modified, weakened, or removed).

## 14. Frozen-Artifact Integrity

`git diff --stat HEAD` against the full CP-01–06 specification/implementation set, the
Approved SRS, and the CP-06 governance-closure report (the same list enumerated in
`docs/CP-MVP2-07-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`) is **empty** — zero drift,
re-verified after implementation.

## 15. Remaining Advisories

- **CR-002** remains open/unauthorized — carried forward unchanged from CP-06 closure; not
  resolved or required to be resolved by CP-07.
- **Testcase-content limitation** (disclosed at the prior testcase-step-fidelity task, and now
  formally root-caused by CP-07's RCA): the real testcases used for `REQ-ACO-03` do not
  specify precondition-establishing business steps for the billing-address form fields this
  scenario's locators target. This is CP-07's own real, current, high-confidence RCA
  conclusion — a disclosed advisory, not a defect in CP-06 or CP-07 themselves.
- Windows-path portability of `persistence.envelope.load_latest` (parked since CR-001) is
  unaffected by and unrelated to CP-07's scope.

## 16. Final CP-07 Gate Decision

# CP-MVP2-07 — GREEN WITH ADVISORIES

All frozen (self-authored, self-reviewed) CP-07 requirements are satisfied: real evidence
ingestion with a governed BLOCKED path for missing evidence; deterministic failure
classification reusing the frozen CP-06 taxonomy verbatim; evidence-based RCA with a real,
structural FACT/EVIDENCE/INFERENCE/CONCLUSION separation; historical evidence used only as
supporting, never overriding; a real, evidence-justified (non-artificial)
`HUMAN_REVIEW_REQUIRED` replanning outcome, plus a real `REPLAN_NOT_ALLOWED` outcome for a
real PASS case; a governed decision enforced by a real, tested prohibited-change guard and a
real CR-002 re-affirmation check; full persistence and reload via the unmodified
`persistence/envelope.py`; 31/31 focused + 331/331 full regression; zero frozen-artifact
drift. Only non-blocking advisories remain (above).

## 17. Recommended Next Checkpoint

**CP-MVP2-08** is authorized to begin, subject to Human + Di review of this report's
advisories (in particular, the testcase-content-limitation recommendation, which requires a
separately-authorized future task before any related replan could ever move from
`HUMAN_REVIEW_REQUIRED` toward `REPLAN_ALLOWED`).
