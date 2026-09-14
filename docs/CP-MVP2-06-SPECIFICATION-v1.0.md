# CP-MVP2-06 — Real Browser Execution

### Draft Specification — v1.0

> **Status:** APPROVED / FROZEN — self-reviewed (sec. 31: no blocking issue found) under this task's own batched SPECIFY → SELF-REVIEW → FREEZE authorization. See sec. 31/32 for the full self-review record.
> **Origin:** Authored from the frozen `docs/CP-MVP2-05-SPECIFICATION-v1.0.md` (commit `2a06b3f`, frozen `da10e89`) and its implementation (`automation/schema.py`, `automation/validate.py`, `automation/pipeline.py`, frozen `docs/CP-MVP2-05-FINAL-IMPLEMENTATION-FREEZE-CHECKPOINT.md`, implementation commit `dfc275a`), the CP-MVP2-04 specification/implementation, the Approved SRS (`requirements/MVP2_SRS_v1.0_APPROVED.md`), and README.md's MVP2 checkpoint list. Every schema field and governance vocabulary term cited from CP-MVP2-05 below was confirmed by direct inspection of the actual repository files, not assumed.
> **Important:** This document does not implement CP-MVP2-06, does not modify any frozen artifact, and does not authorize implementation. It defines the contract a future, separately authorized implementation task will build against.

---

## 1. Objective

CP-MVP2-06 owns **real browser execution** of `ACCEPTED`/`POSSIBLE_DUPLICATE` CP-MVP2-05 `PlaywrightArtifact` records, and production of trustworthy, evidence-backed execution results.

### 1.1 CP-MVP2-06 owns

* Loading and validating the execution-eligibility of a governed CP-MVP2-05 artifact.
* Launching and driving a real Playwright/Chromium browser session against the Demo Web Shop SUT.
* Executing each governed step in order, applying the exact locator/input mapping CP-MVP2-05 already resolved.
* Evaluating assertions and recording step- and artifact-level results.
* Capturing evidence (logs, screenshots, diagnostics) sufficient to substantiate every reported conclusion.
* Classifying failures deterministically.
* Producing a structured, traceable execution result.

### 1.2 CP-MVP2-06 does NOT own

* Requirement interpretation (Approved SRS / CP-MVP2-02 RAG).
* Testcase generation (CP-MVP2-03).
* Test-data generation (CP-MVP2-04).
* Playwright artifact generation or locator invention (CP-MVP2-05).
* Self-healing (prohibited — sec. 15).
* Requirement, testcase, or test-data modification.
* Browser-grid, multi-VM, or cloud-browser-farm orchestration (POST-MVP; not included unless a future, explicitly approved revision adds it — sec. 6).
* RCA, replanning (CP-MVP2-07), performance testing (CP-MVP2-08), or unified reporting (CP-MVP2-09).

## 2. Authoritative Architecture

```text
APPROVED SRS
      ↓
MVP2 KNOWLEDGE BASE / GOVERNED RAG
      ↓
ACCEPTED CP-MVP2-03 TESTCASE
      ↓
ACCEPTED / GOVERNED CP-MVP2-04 TEST DATA
      ↓
ACCEPTED / GOVERNED CP-MVP2-05 PLAYWRIGHT ARTIFACT
      ↓
CP-MVP2-06 REAL BROWSER EXECUTION
      ↓
EXECUTION EVIDENCE
      ↓
EXECUTION RESULT
      ↓
FAILURE CLASSIFICATION / GOVERNANCE
      ↓
CP-MVP2-06 RESULT
```

CP-MVP2-06 executes governed artifacts; it does not regenerate or reinterpret business intent. Every field it reads from a `PlaywrightArtifact` is treated as authoritative and immutable input — CP-MVP2-06 never redefines requirement meaning, testcase meaning, testcase coverage, test-data meaning, locator evidence, or CP-MVP2-05's own acceptance/governance decisions.

## 3. Frozen Upstream Contracts (verified by direct repository inspection)

| Checkpoint | Specification | Freeze commit | Implementation freeze commit |
|---|---|---|---|
| CP-MVP2-03 | `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` | `994338d` | `b20847a` (`docs/CP-MVP2-03-FINAL-FREEZE-CHECKPOINT.md`) |
| CP-MVP2-04 | `docs/CP-MVP2-04-SPECIFICATION-v1.0.md` | `2e77793` | `a5aa2b1` (`docs/CP-MVP2-04-FINAL-IMPLEMENTATION-FREEZE-CHECKPOINT.md`) |
| CP-MVP2-05 | `docs/CP-MVP2-05-SPECIFICATION-v1.0.md` | `2a06b3f`, frozen `da10e89` (`docs/CP-MVP2-05-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`) | `dfc275a`, frozen `076619f` (`docs/CP-MVP2-05-FINAL-IMPLEMENTATION-FREEZE-CHECKPOINT.md`) |

CP-MVP2-05's `automation/schema.py` (confirmed by direct inspection, not assumed) defines the exact `PlaywrightArtifact` field set CP-MVP2-06 must treat as authoritative input (sec. 4). CP-MVP2-06 must not redefine any of: `GovernanceStatus` vocabulary, `LocatorStrategy`/`LocatorStatus`, `AssertionType` (`BUSINESS_REQUIRED`/`TECHNICAL_USEFUL`/`DIAGNOSTIC_OPTIONAL`), `SyncStrategy`, or the load-bearing-locator acceptance rule (CP-MVP2-05 spec sec. 12.1).

## 4. Execution Eligibility

Deterministic, derived solely from the CP-MVP2-05 `GovernedPlaywrightArtifact.governance_status` already assigned upstream — CP-MVP2-06 never re-derives or second-guesses it:

| CP-MVP2-05 `governance_status` | CP-MVP2-06 eligibility |
|---|---|
| `ACCEPTED` | **ELIGIBLE** |
| `POSSIBLE_DUPLICATE` | **ELIGIBLE** (same rationale CP-MVP2-04/05 already apply: flagged, not proven duplicate, still a legitimate artifact) |
| `REJECTED` | **NOT ELIGIBLE** |
| `QUARANTINED` | **NOT ELIGIBLE** |
| `UNSUPPORTED_NEEDS_CLARIFICATION` | **NOT ELIGIBLE** |
| `DUPLICATE` | **NOT ELIGIBLE** (exact duplicate; its original already covers this case) |

An artifact CP-MVP2-06 determines is `NOT ELIGIBLE` must never be executed. Attempting to execute a `NOT ELIGIBLE` artifact is a governance violation, not a runtime failure — see sec. 18's design-time/runtime distinction. This directly satisfies the instruction's requirement that "the implementation must never silently execute an artifact that CP-05 has declared unsupported."

## 5. Browser Scope

* **In scope for MVP2:** `chromium-headless` only — the exact `browser_intent` value CP-MVP2-05's frozen specification already fixes (CP-MVP2-05 spec sec. 6/16), itself grounded in the Approved SRS's own disclosure that all CP-MVP2-01 discovery used headless Chromium via Playwright, single browser, single session (Approved SRS §11/§12).
* **Explicitly out of scope, not silently expanded:** Firefox, WebKit, browser grids, multiple VMs, cloud browser farms, parallel browser orchestration, multi-browser/cross-browser verification.
* **Future scope (documented, not designed or implemented here):** any of the above would require a new, explicitly approved MVP2 scope decision — mirroring exactly how the Approved SRS §9 treats NFR thresholds ("TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL") rather than inventing a default.
* CP-MVP2-06 must reject (`overall_status = BLOCKED`, sec. 9) any artifact whose `browser_intent` is not exactly `chromium-headless` — this should never occur given CP-MVP2-05's own fixed value, but the check exists as defense-in-depth, mirroring the "no fabricated data" defensive-filter precedent already used in `testdata/validate.py::calculate_coverage`.

## 6. Execution Input Contract

The CP-MVP2-05 `PlaywrightArtifact` (and its `PlaywrightStep`/`LocatorSpec`/`Assertion` children) is the **sole** authoritative input. CP-MVP2-06 must not consult CP-MVP2-01/02/03/04 directly for anything CP-MVP2-05 has already resolved — doing so would risk exactly the "reinterpretation" this specification prohibits.

| Field (from `automation/schema.py`) | Authoritative or metadata? |
|---|---|
| `automation_id` | Authoritative — the execution's own identity anchor. |
| `testcase_id`, `requirement_ids`, `test_data_set_id`, `journey_id` | Authoritative — traceability keys (sec. 19), never re-derived. |
| `scenario_type` | Authoritative — informs failure-severity framing only, never execution logic branching. |
| `browser_intent` | Authoritative — must equal `chromium-headless` (sec. 5). |
| `preconditions` | Authoritative — narrative text; CP-MVP2-06 applies what it can deterministically act on (e.g. "start from an anonymous session") and reports `BLOCKED` (sec. 9/16) for any precondition it cannot establish, never silently skipping it. |
| `steps` (ordered `PlaywrightStep` list: `step_order`, `action_type`, `locator`, `input_mapping`, `synchronization_strategy`) | Authoritative — executed exactly in order; `locator`/`input_mapping` are never re-resolved or substituted. |
| `assertions` (`assertion_type`, `condition`, `source`, `counts_toward_coverage`) | Authoritative for pass/fail determination (sec. 11). |
| `evidence_requirements` | Authoritative — the minimum evidence CP-MVP2-06 must capture. |
| `source_attribution` | Authoritative — copied verbatim into the execution result (sec. 19). |
| `generation_metadata` | Metadata — audit context only (which generator/model produced the artifact), never consulted for execution decisions. |
| `failure_handling_metadata` | Authoritative for CP-MVP2-06's own retry/escalation behavior (sec. 14) — e.g. CP-MVP2-05's own `{"retry": false, "escalate": true}` default must be honored, not overridden. |
| CP-MVP2-05 `validation_status` (i.e. `governance_status`) | Authoritative — the sole eligibility gate (sec. 4). |

## 7. Execution Engine (conceptual — not implemented by this specification)

1. Load the governed CP-MVP2-05 artifact (and its `GovernedPlaywrightArtifact` wrapper carrying `governance_status`).
2. Validate execution eligibility (sec. 4). Ineligible → `overall_status = NOT_EXECUTED`, stop here (design-time, sec. 18).
3. Resolve `browser_intent` (sec. 5). Mismatch → `overall_status = BLOCKED`, stop here.
4. Establish the browser/context/page (real Playwright Chromium, headless). Launch failure → `overall_status = ERROR`, category `BROWSER_LAUNCH_FAILURE` (sec. 13).
5. Apply preconditions to the extent deterministically actionable (sec. 6). An unestablishable precondition → `overall_status = BLOCKED`.
6. Execute each governed step in order (sec. 8/10), recording a `StepResult` per step. A load-bearing step failure (locator not found/interactable at runtime, navigation failure, timeout) stops step execution and drives `overall_status` toward `FAIL`/`ERROR`/`BLOCKED` per sec. 13's classification.
7. Evaluate assertions (sec. 11) against final page state.
8. Capture required evidence throughout (sec. 12), not only at the end.
9. Record the final `overall_status` (sec. 9) — never inferred after the fact from an incomplete run without evidence.
10. Classify any failure deterministically (sec. 13).
11. Produce the final `ExecutionResult` record (sec. 9), including traceability (sec. 19) and reproducibility metadata (sec. 20).

**This section is conceptual only — no engine, browser runner, or execution code is created by this specification task.**

## 8. Step Execution Semantics

For each `PlaywrightStep`, in `step_order`:

* `NAVIGATE`: go to the SUT's relevant URL (resolved from `environment_metadata`, sec. 16 — never hard-coded per-artifact).
* `FILL`/`SELECT`: resolve the real value from the CP-MVP2-04 dataset referenced by `test_data_set_id`, using the step's `input_mapping` field name (never a literal embedded in the CP-MVP2-05 artifact — CP-MVP2-05 intentionally never embeds concrete values, per its own implementation notes); interact using the step's `LocatorSpec.value`/`strategy` verbatim.
* `CLICK`: interact using the step's `LocatorSpec` verbatim (no field value involved).
* `WAIT`: apply the step's `synchronization_strategy` (`WAIT_FOR_VISIBLE`/`WAIT_FOR_NETWORK_IDLE`/`NONE`).
* `ASSERT`: evaluate the artifact-level `assertions` tied to this point in the sequence (sec. 11) — CP-MVP2-05's schema does not attach assertions to individual steps; assertion evaluation happens against the artifact's `assertions` list, at the point(s) the step sequence implies (typically after the load-bearing action sequence completes).

CP-MVP2-06 never invents a locator or a data value for a step CP-MVP2-05 already resolved. If a step's `locator.status` were somehow `UNSUPPORTED` on an artifact that reached CP-MVP2-06 (which should not happen, since CP-MVP2-05's own load-bearing rule already rejects such artifacts to `UNSUPPORTED_NEEDS_CLARIFICATION` before they could be `ACCEPTED`) — CP-MVP2-06 treats this as a design-time integrity violation (`overall_status = BLOCKED`, sec. 17/18), never as a runtime failure and never by fabricating a locator to proceed.

## 9. Execution Result Schema

```python
class OverallStatus:
    PASS = "PASS"                  # eligible, executed, all BUSINESS_REQUIRED assertions held
    FAIL = "FAIL"                  # eligible, executed, at least one BUSINESS_REQUIRED assertion or load-bearing step failed at runtime
    BLOCKED = "BLOCKED"            # eligible, but a precondition/environment/browser-scope issue prevented meaningful execution
    NOT_EXECUTED = "NOT_EXECUTED"  # design-time: artifact was not ELIGIBLE (sec. 4) — execution never attempted
    ERROR = "ERROR"                # an execution-engine-level failure occurred (crash, browser launch failure, unhandled exception) — not a business-logic outcome
```

| Field | Purpose |
|---|---|
| `execution_id` | Deterministic ID, e.g. `EXEC-<automation_id>-<seq>` — never LLM-assigned (no LLM participates in CP-MVP2-06 at all — see sec. 17). |
| `automation_id`, `testcase_id`, `requirement_ids`, `test_data_set_id`, `journey_id`, `scenario_type` | Copied verbatim from the CP-MVP2-05 artifact. |
| `browser` | The actual resolved browser/engine string (e.g. `"chromium-headless"`), confirmed against what was actually launched — never merely copied from `browser_intent` without confirmation. |
| `execution_start`, `execution_end`, `duration` | Real wall-clock timestamps/duration of the actual attempted execution; absent/null for `NOT_EXECUTED`. |
| `overall_status` | One of the five values above. |
| `step_results` | Ordered `List[StepResult]` (sec. 10). |
| `assertion_results` | Per-assertion outcome, each tagged with its source `Assertion.assertion_type` (sec. 11). |
| `evidence_references` | Pointers to captured evidence artifacts (sec. 12) — paths/IDs, never the raw binary embedded inline. |
| `failure_classification` | One of sec. 13's categories, or `null` for `PASS`. |
| `failure_summary` | Short, human-readable, evidence-grounded description — never speculation. |
| `source_attribution` | Copied verbatim from the CP-MVP2-05 artifact. |
| `environment_metadata` | SUT URL, Playwright/browser version, runtime version actually used (sec. 16/20). |
| `governance_status` | The CP-MVP2-05 eligibility status this execution was gated on (sec. 4) — retained for audit even though the decision was already made upstream. |
| `reproducibility_metadata` | sec. 20. |
| `notes` | Deterministic-code-authored reasoning trail. |

## 10. Step Result Model

| Field | Purpose |
|---|---|
| `step_order`, `action_type` | Copied from the source `PlaywrightStep`. |
| `target_locator_reference` | The actual `LocatorSpec.value`/`strategy` used (or `null` for steps with none). |
| `status` | `PASS`, `FAIL`, `SKIPPED`, `NOT_EXECUTED`, `ERROR` — the same vocabulary discipline as `overall_status`, scoped to one step. `SKIPPED` applies only when a prior step's failure makes a later step meaningless (e.g. cannot fill a field on a page that failed to load) — never used to silently omit a step that should have run. |
| `start_time`, `end_time`, `duration` | Real timestamps for this step's actual attempted execution. |
| `observed_result` | What was actually observed (e.g. resulting URL, a captured error message) — factual, never inferred beyond what was seen. |
| `expected_condition` | Populated for steps tied to an assertion; `null` otherwise. |
| `evidence_references` | Step-level evidence (e.g. a screenshot taken specifically at this step). |
| `error_information` | Present only on `FAIL`/`ERROR`; must never contain a secret/credential (sec. 21). |

## 11. Assertion Execution and Precedence

CP-MVP2-05's three-way assertion classification is preserved exactly:

* **`BUSINESS_REQUIRED`**: the **sole** determinant of whether `overall_status` can be `PASS`. Every `BUSINESS_REQUIRED` assertion (CP-MVP2-05 guarantees at least one exists on any `ACCEPTED`/`POSSIBLE_DUPLICATE` artifact, per its own `validate_assertions`) must hold for `overall_status = PASS`; any one failing drives `overall_status = FAIL`.
* **`TECHNICAL_USEFUL`**: evaluated and recorded in `assertion_results`, but its outcome **never** changes `overall_status` — it may inform `failure_summary`/diagnostics when a `BUSINESS_REQUIRED` assertion has already failed, but a `TECHNICAL_USEFUL` failure alone cannot produce `FAIL`, and a `TECHNICAL_USEFUL` pass can never mask a `BUSINESS_REQUIRED` failure.
* **`DIAGNOSTIC_OPTIONAL`**: evaluated (if practical) and recorded for diagnostic value only; never influences `overall_status` in either direction.

**Explicit precedence rule:** `overall_status` is determined solely by (a) design-time eligibility (sec. 4), (b) load-bearing step execution outcomes (sec. 8), and (c) `BUSINESS_REQUIRED` assertion outcomes. No other assertion type may override this. This directly satisfies the instruction's requirement that "a technical or diagnostic assertion must not silently override a business assertion."

## 12. Evidence Model

At minimum, CP-MVP2-06 must capture:

* An execution log (sequence of actions actually taken, with timestamps).
* Step-level logs (per `StepResult`).
* All assertion results (sec. 11), regardless of type.
* A screenshot on any `FAIL`/`ERROR`/`BLOCKED` outcome.
* A screenshot wherever an artifact's own `evidence_requirements` explicitly names one (CP-MVP2-05 always sets `["screenshot", "dom_snapshot"]` per its current implementation — CP-MVP2-06 must honor whatever the artifact actually declares, not a hard-coded assumption).
* Playwright/browser diagnostic output relevant to a failure (console errors, network failures).
* A final execution summary tying every conclusion back to the specific evidence that substantiates it.

**Every reported conclusion must be traceable to evidence actually captured during that specific execution.** Evidence must never be fabricated, reused from a different execution, or presented as having been captured when it was not. A `NOT_EXECUTED` or `BLOCKED` result legitimately has minimal-to-no browser-interaction evidence — this must be stated honestly, never papered over with a placeholder screenshot.

## 13. Failure Classification

Two-level taxonomy: the seven base categories (reusing the vocabulary the instruction supplies, kept consistent with CP-MVP2-04's own failure-category naming convention, sec. 18 of that spec), plus execution-specific **subtypes**, each mapped to exactly one base category — never a hidden, parallel taxonomy.

| Base category | Meaning | Execution-specific subtype(s) mapped to it |
|---|---|---|
| `REQUIREMENT_MISMATCH_AMBIGUITY` | The upstream requirement/testcase/artifact itself is ambiguous or inconsistent — discovered only at execution time (e.g. the real SUT behaves differently than the governed evidence implied). | — |
| `TEST_DATA_ISSUE` | The CP-MVP2-04 dataset's value was rejected or mishandled by the real SUT in a way the data itself explains (not a locator/tool problem). | — |
| `AUTHORIZATION_ISSUE` | An authentication/authorization precondition could not be established (sec. 16's disclosed limitation: no reusable authenticated-session fixture exists). | — |
| `TOOL_ISSUE` | Playwright/browser tooling itself failed, independent of the SUT or the artifact's business content. | `BROWSER_LAUNCH_FAILURE` (browser/context/page could not be started); `LOCATOR_FAILURE` (a locator CP-MVP2-05 marked `EVIDENCED` could not be resolved/interacted with by Playwright at runtime — e.g. the real page no longer matches the historical capture). |
| `ENVIRONMENT_ISSUE` | The execution environment (network, runtime, configuration) prevented meaningful execution. | `TIMEOUT` (a synchronization strategy's wait exceeded its bound without the expected condition). |
| `THIRD_PARTY_DEPENDENCY_ISSUE` | The shared, third-party Demo Web Shop SUT itself was unavailable, slow, or behaved unexpectedly for reasons outside MVP2's control (Approved SRS §11: no SLA, no uptime guarantee, no reset schedule on this shared public instance). | `NAVIGATION_FAILURE` (a `NAVIGATE` step could not reach the target URL/page). |
| `CONSTRAINT_VIOLATION` | A governed `BUSINESS_REQUIRED` assertion did not hold against real, observed SUT behavior. | `ASSERTION_FAILURE` (the direct, general case). |

An implementation-level defect in CP-MVP2-06 itself is classified `TOOL_ISSUE`, never miscategorized as a requirement, data, or SUT problem without actual evidence — mirroring the instruction's own explicit warning against misclassifying without evidence (also present verbatim in CP-MVP2-04 spec sec. 18).

## 14. Failure Governance

On any failure, CP-MVP2-06 must **not**:

* change the requirement, testcase, test data, or expected assertion condition;
* invent a locator to route around a `LOCATOR_FAILURE`;
* weaken, remove, or skip a failing `BUSINESS_REQUIRED` assertion;
* remove a failing step from the recorded sequence;
* retry indefinitely;
* classify a failure as `PASS` without evidence.

**Retry policy: automatic retry is explicitly PROHIBITED in CP-MVP2-06 v1.0.** No evidence yet exists in this project (no flakiness data, no established transient-failure pattern against this SUT) to justify a deterministic retry rule, and the instruction requires that retry be either justified by evidence or explicitly prohibited — since no such evidence exists, it is prohibited outright, not left ambiguous. A future revision may introduce a narrowly-scoped, evidence-justified retry policy only through the same formal Change Request process governing every other rule in this document.

## 15. Self-Healing Boundary

**Self-healing is explicitly PROHIBITED in CP-MVP2-06.** This is a firm decision, not a "limited" or vaguely deferred capability: CP-MVP2-06 must never mutate a frozen CP-MVP2-05 `PlaywrightArtifact`, propose a locator repair, or adjust an assertion in response to a runtime failure. Any future locator-repair/self-healing capability is a governance-controlled capability belonging to a later, explicitly authorized checkpoint (README.md's own MVP2 checkpoint list names this **CP-MVP2-07 — RCA + Replanning + Governance**) — CP-MVP2-06 only *records* the evidence (sec. 12/19) such a future checkpoint would need; it does not act on it.

## 16. Environment Handling

* **SUT URL:** `https://demowebshop.tricentis.com/` — the same third-party, publicly shared nopCommerce instance the Approved SRS's own discovery was performed against (Approved SRS §11). CP-MVP2-06 does not target any other environment.
* **Browser/runtime dependency:** Playwright with a Chromium browser, headless — already an existing project dependency (`playwright` is already installed in this project's Python environment; CP-MVP2-01's own discovery scripts already used it). CP-MVP2-06 reuses this existing foundation; it does not introduce a new browser-automation dependency.
* **Network dependency:** real, live network access to the public internet SUT is required for any attempted execution — CP-MVP2-06 cannot execute anything meaningful in a fully offline/sandboxed environment; an offline environment must yield `BLOCKED`/`ERROR` with an honest `ENVIRONMENT_ISSUE` classification, never a fabricated result.
* **Authentication/precondition assumptions — a genuine, disclosed limitation:** the Approved SRS explicitly forbids treating the CP-MVP2-01 discovery account as a reusable fixture (Approved SRS §10), and no later checkpoint has established a durable, reusable authenticated-session credential. Any CP-MVP2-05 artifact whose `preconditions` require a pre-existing authenticated account (e.g. `REQ-ACO-02`'s saved-address reuse) therefore cannot have that precondition established by CP-MVP2-06 today — it must report `overall_status = BLOCKED`, `failure_classification = AUTHORIZATION_ISSUE`, never a fabricated authenticated session. A scenario that itself *creates* a new account (e.g. `REQ-REG-01`) does not have this specific problem, but see the shared-instance data-pollution concern below.
* **No credentials are invented or embedded.** CP-MVP2-06 never hard-codes a production credential; where a scenario's own test data (CP-MVP2-04, always synthetic) includes a password-shaped value, that value is used only as literal UI input, never as a real credential for any system.
* **Timeout policy:** every `WAIT`/synchronization step and every browser action must have an explicit, configured timeout (no indefinite wait) — the exact numeric default is an implementation-time decision, not fixed by this specification, but the *requirement that one always exists* is fixed here.
* **Artifact/evidence output location:** a dedicated, non-committed evidence output directory (implementation detail; must not collide with or be confused with the governed `docs/claude-execution-reports/` evidence-report convention, which is for Claude's own task execution reports, not raw browser-execution artifacts).
* **Shared-instance data-pollution risk (new finding, disclosed here, not resolved):** the Demo Web Shop is a shared, public, third-party instance with **no known data-reset or isolation policy** (`DATA-OQ-01`, Approved SRS §13, still open — inherited unresolved through CP-MVP2-04/05). Any CP-MVP2-06 execution of a state-mutating scenario (e.g. actually registering a new account, actually placing an order) would leave real, persistent state on that shared instance, indistinguishable from any other user's activity, with no known way to clean it up afterward. **This specification does not resolve `DATA-OQ-01`.** It requires that CP-MVP2-06 implementation and any live-execution task treat this as an active risk needing explicit Human + Di acknowledgment before executing any state-mutating scenario for real — not merely a documentation footnote to be read past.

## 17. Deterministic Governance Validation

CP-MVP2-06 has **no LLM component at all** — unlike every prior checkpoint, there is no reasoning step here to bound; execution is purely mechanical, driven entirely by already-governed upstream data. Deterministic checks required before any browser action is attempted:

* Schema integrity of the loaded `PlaywrightArtifact` (already validated by CP-MVP2-05, but re-verified defensively — the same "never trust upstream blindly, re-check the invariant" precedent already used by `testdata.validate.calculate_coverage`'s applicable-ID filter).
* Execution eligibility (sec. 4).
* Required fields present (`automation_id`, `testcase_id`, `requirement_ids`, `test_data_set_id`, at least one step, at least one `BUSINESS_REQUIRED` assertion).
* Every element-targeting step's `locator.status == EVIDENCED` (defensive re-check; sec. 8).
* Action/browser-intent compatibility (sec. 5).
* Testcase/requirement traceability and test-data linkage (sec. 19) resolve to real, still-eligible upstream records — an upstream record's eligibility could theoretically change between CP-MVP2-05 generation time and CP-MVP2-06 execution time only if the repository's frozen state itself changed, which governance elsewhere in this project already prohibits; the check exists as defense-in-depth regardless.
* `evidence_requirements` is non-empty and each declared requirement is one CP-MVP2-06 actually knows how to satisfy.

**No part of this validation is an LLM decision.** This is a stronger statement than every prior checkpoint's "LLM proposes, deterministic code decides" — here there is no proposal step to bound at all.

## 18. Design-Time vs. Runtime Failures

* **Design-time failure:** the artifact was not `ELIGIBLE` (sec. 4), or failed a sec. 17 pre-execution check. `overall_status = NOT_EXECUTED`. Browser execution was never attempted. This must never be reported as a browser execution failure.
* **Runtime failure:** the artifact was `ELIGIBLE`, pre-execution checks passed, and execution began — but a failure occurred during or after that attempt (`FAIL`/`BLOCKED`/`ERROR`, sec. 9/13). This is visibly distinct in every report (sec. 22): a CP-MVP2-06 report must always show, for every artifact considered, which of these two categories applies, never blending them into one undifferentiated "failed" bucket.

## 19. Traceability

```text
EXECUTION ID
   ↓
AUTOMATION ID (CP-MVP2-05)
   ↓
TESTCASE ID (CP-MVP2-03)
   ↓
REQUIREMENT ID(s)
   ↓
APPROVED SRS
   ↓
SOURCE ATTRIBUTION (chunk_id / source_document / source_version)
```

and, separately:

```text
EXECUTION ID
   ↓
TEST DATA SET ID (CP-MVP2-04)
   ↓
TEST DATA FIELD(s) actually used (via each step's input_mapping)
```

No orphan execution result: an `ExecutionResult` whose `automation_id` does not resolve to a real, `ELIGIBLE` CP-MVP2-05 artifact must never be produced — it is a design-time integrity failure (sec. 17/18), reported as such, never silently discarded or silently accepted.

## 20. Reproducibility

Required `reproducibility_metadata` fields:

* `execution_id`, `timestamp` (real, not estimated).
* Browser/engine version actually launched (e.g. the installed Chromium build Playwright resolves) — read from the real runtime, never assumed.
* Playwright package version actually installed (already present in this project's environment — read it, don't hard-code an assumed version).
* Python/runtime version actually executing.
* `SUT URL` (sec. 16).
* The CP-MVP2-05 artifact's own identity (`automation_id`) and the CP-MVP2-04 `test_data_set_id` it consumed — together these already fix everything about *what* was executed; CP-MVP2-06 need not duplicate CP-MVP2-04/05's own generation metadata.
* Execution configuration actually in effect (timeout values, headless flag).

**Honesty constraint:** this is **audit-level** reproducibility (you can establish exactly what was run, against what, and with what tool versions) — it is **not** a claim that re-running the same artifact will deterministically produce an identical result, because the SUT is a shared, third-party, uncontrolled public instance (sec. 16) whose state MVP2 does not own. This specification does not claim more reproducibility than the environment can actually support.

## 21. Security / Data Handling

* No real PII, no real payment credentials, no secrets, no production credentials — inherited unchanged from CP-MVP2-04/05.
* All test-data values originate from CP-MVP2-04's governed, synthetic datasets (sec. 6) — CP-MVP2-06 never invents its own data.
* `error_information` (sec. 10) and any captured log/screenshot must never include a raw credential value, even a synthetic one that merely *looks* like a password — display/redact such fields consistently with how the value is already handled upstream (CP-MVP2-04 never fabricates a value that would need real secrecy, but redaction is still required as defense-in-depth, since a screenshot could visually expose a filled password field regardless of whether the underlying value is synthetic).
* Evidence artifacts (screenshots, logs) are stored in a location and retention policy appropriate for internal QE evidence, not published or exposed externally — an implementation detail deferred to the implementation task, bounded here only by the "no secrets, no unnecessary PII" rule.

## 22. Reporting

A CP-MVP2-06 execution report must state, at minimum:

* Execution summary (counts by `overall_status`: `PASS`/`FAIL`/`BLOCKED`/`NOT_EXECUTED`/`ERROR`).
* Total eligible artifacts (sec. 4) vs. total attempted vs. total for which execution actually began (distinguishing sec. 18's design-time/runtime line clearly).
* **Execution coverage** (sec. 23) — kept explicitly and visibly separate from **requirement/testcase coverage** (inherited from CP-MVP2-03/05, never redefined here).
* Requirement traceability (sec. 19) for every result.
* Evidence locations for every result.
- Failure classification breakdown (sec. 13).
* Governance findings (e.g. any artifact CP-MVP2-06's own sec. 17 checks rejected before execution, and why).
* Known limitations (sec. 29) restated for the specific run.
* Recommended next steps (e.g. "N artifacts BLOCKED on AUTHORIZATION_ISSUE — resolving this requires a Human + Di decision on a reusable test-account strategy, out of this specification's own authority to decide").

**A CP-MVP2-06 report must never claim that browser execution automatically increased requirement or testcase coverage** — those metrics remain owned by CP-MVP2-03/05's own governance, and a `PASS` execution result only confirms that one already-accepted artifact behaved as expected when actually run; it does not itself expand what is "covered" in the upstream sense.

## 23. Coverage

Three explicitly distinct metrics, never conflated:

1. **Eligible-artifact execution coverage** = (artifacts actually attempted) / (total `ELIGIBLE` CP-MVP2-05 artifacts). Measures how much of what *could* be executed *was* attempted.
2. **Successful execution rate** = (artifacts reaching `overall_status = PASS`) / (artifacts actually attempted, i.e. excluding `NOT_EXECUTED`). Measures execution reliability, not business coverage.
3. **Requirement/testcase coverage** — inherited unchanged from CP-MVP2-03 (`testcases.validate.calculate_coverage`) and CP-MVP2-05 (`automation.validate.calculate_coverage`). CP-MVP2-06 must not redefine, recompute, or "improve" this number by virtue of having executed something — a `PASS` execution result does not retroactively make an `UNSUPPORTED_NEEDS_CLARIFICATION` CP-MVP2-05 artifact become accepted, and does not change any upstream coverage percentage.

## 24. Live Execution Evidence

Valid evidence that a real browser execution occurred requires **all** of:

* An actual Playwright/browser process was launched (verifiable via the real, resolved browser/engine version — sec. 20 — not merely asserted).
* Actual network interaction with the real SUT occurred (observable via at least one real navigation/response, timestamped).
* Real execution timestamps (`execution_start`/`execution_end`, non-zero elapsed duration consistent with actual browser/network latency, not suspiciously instantaneous).
* At minimum the required evidence artifacts (sec. 12) actually exist and were actually produced during that specific run.
* A deterministic result record (sec. 9) consistent with the above.

**Never accepted as live execution evidence:** a mocked browser, a fabricated screenshot, a synthetic `PASS` record, or stub/test-double output presented as if it came from a real run. Unit/integration tests of CP-MVP2-06 itself (sec. 25) legitimately use mocks/stubs — but their output must always be labeled as such and must never be substituted for, or blended into, a report of genuine live execution, mirroring exactly the discipline this project has already applied at every prior checkpoint (e.g. `StubLLMClient`/`StubTestDataClient`/`StubAutomationClient` outputs are always clearly distinguished from real Claude invocations in every prior execution report).

## 25. Testing of CP-MVP2-06 Itself

A future implementation must provide, clearly labeled and never blended:

* **Unit tests** for deterministic components (eligibility checks, sec. 17 validation, failure classification mapping) — no browser involved.
* **Integration tests** for the execution pipeline's control flow (e.g. "an ineligible artifact never reaches the browser-launch step") — a mocked/stubbed browser layer is acceptable here, explicitly labeled as such.
* **Negative tests** for invalid/ineligible artifacts (every eligibility/governance rule in secs. 4/17 needs its own test, mirroring the exhaustive negative-path testing convention already established for CP-MVP2-03/04/05).
* **Governance tests** proving the prohibited behaviors in secs. 14/15 cannot occur (e.g. a test asserting no code path can mutate a `PlaywrightArtifact`'s locator).
* **Live browser verification:** at least one real, governed CP-MVP2-05 artifact should be exercised through a real Playwright/Chromium session, if and when the prerequisites in sec. 16 permit — this specification does not itself guarantee such an artifact currently exists in `ACCEPTED` status (see sec. 26).

## 26. Live Browser Test Policy

**The first live browser verification must use an existing, already-governed CP-MVP2-05 artifact — never a newly invented scenario created merely to make the test pass.**

As of this specification's authoring, direct inspection of the CP-MVP2-05 evidence (`docs/claude-execution-reports/CP-MVP2-05/CP-MVP2-05-EXEC-20260914-151910-5FAF88.md`) shows the one concretely demonstrated `REQ-ACO-03` artifact reached `UNSUPPORTED_NEEDS_CLARIFICATION`, not `ACCEPTED` — because its real submit-button locator evidence is genuinely ambiguous (CP-MVP2-05 spec sec. 20, implementation notes). **No currently-known `ACCEPTED`/`POSSIBLE_DUPLICATE` CP-MVP2-05 artifact has been demonstrated to exist as of this specification.** This is stated honestly, not concealed:

* A future CP-MVP2-06 implementation task must first check whether any `ACCEPTED`/`POSSIBLE_DUPLICATE` artifact exists (e.g. one might exist for a different requirement/category combination not yet exercised).
* If none exists, the correct, specification-compliant outcome is a governed `NOT_EXECUTED`/`BLOCKED` result for the live-verification step itself, honestly reported — **not** an artificially manufactured scenario, and **not** a CP-MVP2-05 specification/implementation change to force an artifact into `ACCEPTED` status.
* This specification does **not** authorize modifying CP-MVP2-04/05 to manufacture an executable artifact. That would be exactly the "change the specification to make the implementation pass" behavior every checkpoint's golden rule prohibits.

## 27. CP-MVP2-06 Output Artifacts (future implementation — not created by this specification)

Likely categories, named for a future implementation task's reference only — **no file listed here is created by this specification task**:

* `execution/schema.py` — execution-result/step-result schema (mirroring `automation/schema.py`'s dataclass convention).
* `execution/validate.py` — deterministic eligibility/pre-execution validators (sec. 17) and failure classifiers (sec. 13).
* `execution/engine.py` (or similar) — the actual Playwright-driving browser execution engine (sec. 7/8).
* `execution/evidence.py` — evidence capture/management (sec. 12).
* `execution/pipeline.py` — `run_cp_mvp2_06()` orchestrator, mirroring the `run_cp_mvp2_0N()` convention already established by every prior checkpoint.
* `tests/test_cp_mvp2_06_*.py` — unit/integration/negative/governance tests (sec. 25).
* `docs/CP-MVP2-06-IMPLEMENTATION.md`, execution reports/summaries under `docs/claude-execution-reports/CP-MVP2-06/`, and a final freeze checkpoint — mirroring the exact reporting convention already established by CP-MVP2-03/04/05.

Exact module boundaries/filenames are an implementation-time decision within this envelope; this specification fixes the *contract*, not the file layout, beyond this illustrative, non-binding list.

## 28. Downstream Contract

* **CP-MVP2-07 (RCA + Replanning + Governance):** may consume every `ExecutionResult` (sec. 9), especially `failure_classification`, `evidence_references`, and the full traceability chain (sec. 19), to perform root-cause analysis and (governed) replanning. CP-MVP2-06 does not implement any of that itself — it only ensures the evidence exists in a form CP-MVP2-07 can consume without re-deriving it. **NOT STARTED.**
* **CP-MVP2-08 (JMeter Performance Testing):** remains entirely separate — functional browser-execution results are not performance load data. **NOT STARTED.**
* **CP-MVP2-09 (Unified Final QE Reporting):** may consume CP-MVP2-06's `by_status`/coverage-shape output, kept structurally parallel to every prior checkpoint's own report shape for the same reason CP-MVP2-04/05 already state (reducing CP-09 redesign risk later). **NOT STARTED.**

## 29. Known Limitations (carried forward from direct repository inspection, none invented, none silently resolved)

1. **No currently-known `ACCEPTED`/`POSSIBLE_DUPLICATE` CP-MVP2-05 artifact has been demonstrated** (sec. 26) — the one concretely demonstrated `REQ-ACO-03` artifact is `UNSUPPORTED_NEEDS_CLARIFICATION` due to a genuinely ambiguous real submit-button locator.
2. **`REQ-REG-01` has zero locator evidence** (no `/register` capture exists) — inherited from CP-MVP2-05.
3. **`REQ-CART-03`'s cart-quantity locator pattern remains unresolved** (fragile, item-specific literal only) — inherited from CP-MVP2-05.
4. **`REQ-PAY-01`'s per-option payment-method locators remain unresolved** — inherited from CP-MVP2-05.
5. **`DATA-OQ-01`** (shared-instance data-reset/isolation policy) remains open — and CP-MVP2-06 specifically elevates this to an active *live-execution risk* (sec. 16), not merely an abstract open question, since CP-MVP2-06 is the first checkpoint that would actually mutate real state on the shared instance.
6. **`ACTION_TYPE_EVIDENCE_ADVISORY`** (CP-MVP2-05: `FILL` vs. `SELECT` action-type choice is not fully evidence-driven) — inherited unresolved.
7. **No reusable authenticated-session fixture exists** (sec. 16) — any precondition requiring a pre-existing account cannot currently be established by CP-MVP2-06.
8. **Browser/network environment prerequisites are not guaranteed** in every execution environment this repository might run in (e.g. a fully offline sandbox) — CP-MVP2-06 must report `BLOCKED`/`ERROR` honestly rather than claim execution occurred.
9. **DOM evidence boundary** (CP-MVP2-05 sec. 7.1, inherited): locator evidence lives outside the queryable RAG `KnowledgeBase` by CP-MVP2-02's own design; CP-MVP2-06 does not change this and continues to treat CP-MVP2-05's already-resolved `LocatorSpec` as the sole locator source — it does not re-read the raw discovery captures itself.

None of the above are resolved, invented around, or silently removed by this specification.

## 30. Acceptance Criteria

This specification is implementation-ready only when all of the following hold — each is satisfied by a specific section above:

* Scope is unambiguous (sec. 1).
* Upstream contracts are preserved, verified by direct inspection, not assumed (sec. 3).
* Executable eligibility is deterministic (sec. 4).
* Browser scope is explicit and not silently expanded (sec. 5).
* The execution result schema is fully defined, with named statuses and their exact semantics (sec. 9).
* Evidence requirements are defined and evidence is never allowed to be fabricated (sec. 12/24).
* The failure taxonomy is defined, with execution-specific subtypes explicitly mapped to base categories, never hidden (sec. 13).
* Governance behavior (prohibited actions, retry policy, self-healing boundary) is defined (secs. 14/15).
* Traceability is defined end-to-end (sec. 19).
* Reproducibility expectations are honest about what this environment can and cannot guarantee (sec. 20).
* Live execution evidence requirements are explicit, and the live-test policy forbids manufacturing a scenario to pass (secs. 24/26).
* Security/data-handling rules are explicit (sec. 21).
* Downstream boundaries (CP-MVP2-07/08/09) are explicit and marked not started (sec. 28).
* Known limitations are recorded, none invented around (sec. 29).
* No hidden CP-MVP2-07/08/09 functionality is introduced anywhere in this document.

---

## 31. Self-Review

Performed against: frozen CP-MVP2-01 through CP-MVP2-05 (specifications and implementation freeze checkpoints, all re-verified by direct `git log`/`git diff` inspection in this same task execution — see the accompanying execution report), the Approved SRS, README.md, the CP-MVP2-05 specification and implementation, this project's established governance principles (LLM proposes/deterministic governs; no fabrication; disclose, don't invent resolutions), and this task's own instruction.

**Findings:**

* No contradiction found between this specification and any frozen CP-MVP2-01–05 artifact's actual content (schema field names, governance vocabulary, and freeze commits cited above were all confirmed by direct inspection, not assumed).
* No requirement, testcase, test-data, or CP-MVP2-05 artifact meaning is redefined anywhere in this document.
* No hidden CP-MVP2-07/08/09 functionality was introduced — sec. 28 explicitly marks all three "NOT STARTED" and describes only what a *future* checkpoint *may* consume, never what it does.
* No browser scope expansion beyond CP-MVP2-05's existing `chromium-headless` fixed value was introduced; multi-browser/grid scenarios are explicitly deferred as documented future scope, not designed here.
* No self-healing capability or artifact-mutation path was introduced; sec. 15 is an explicit prohibition, not a soft deferral.
* No retry logic was introduced without justification; sec. 14 explicitly prohibits it in v1.0 for lack of evidence.
* No credential, secret, or real-PII handling was invented; sec. 21 inherits the existing project-wide rule unchanged.
* The `DATA-OQ-01` open question was not resolved by assumption — sec. 16 elevates it to an explicit, disclosed live-execution risk requiring a future Human + Di decision, consistent with how every prior checkpoint has handled it (disclose, never assume).
* The live-browser-test policy (sec. 26) was checked directly against the actual CP-MVP2-05 evidence file and found to accurately report that no `ACCEPTED` artifact currently exists — this is disclosed honestly rather than glossed over, and the specification explicitly forbids manufacturing one.
* No implementation code, browser runner, or execution engine was created by this task (verified in the accompanying execution report's "Absolute Implementation Boundary" check).

**No blocking issue was found.**

**Self-review result: PASS.** Specification status is updated below from DRAFT to **APPROVED / FROZEN**.

---

## 32. Versioning and Freeze

* Checkpoint: **CP-MVP2-06 — Real Browser Execution**
* Specification version: **1.0**
* **Status: APPROVED / FROZEN** (self-reviewed; see sec. 31 — this is a self-review freeze performed under this task's own explicit batched-governance authorization, not a substitute for independent Human + Di review of substance whenever they next choose to examine it).
* Any change after this freeze requires a formal, versioned Change Request — no silent modification permitted, mirroring the exact process already used for every prior checkpoint.
