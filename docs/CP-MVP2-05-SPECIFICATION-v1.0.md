# CP-MVP2-05 — Playwright E2E Generation

### Draft Specification — v1.0

> **Status:** DRAFT — pending Human + Di review. **NOT YET APPROVED. NOT YET FROZEN.**
> **Origin:** Authored from the frozen `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` and `docs/CP-MVP2-04-SPECIFICATION-v1.0.md` (governance conventions, LLM/deterministic boundary, two-level schema precedent), the Approved SRS (`requirements/MVP2_SRS_v1.0_APPROVED.md`), and — critically for this checkpoint — the **actual raw DOM evidence already captured during CP-MVP2-01 discovery** (`knowledge/historical/discovery_evidence/captures/*.html`), inspected directly for this specification rather than assumed.
> **Important:** This document does not implement CP-MVP2-05, does not modify any frozen artifact, and does not authorize implementation. It defines the contract a future, separately authorized implementation task will build against.

---

## 1. Objective

Define a governed transformation:

```text
Approved SRS -> governed RAG evidence -> accepted CP-MVP2-03 testcase
  -> accepted/governed CP-MVP2-04 test data -> Playwright E2E artifact
```

The objective is **not** "generate Playwright code." The objective is to
establish that an already-accepted testcase and its already-governed
test data can be transformed into a browser-automation artifact **without
reinterpreting or changing the business requirement, testcase intent, or
test data** they came from — mirroring exactly the discipline CP-MVP2-03
established for testcases and CP-MVP2-04 established for test data, one
layer further downstream.

---

## 2. Authoritative Architecture

```text
APPROVED SRS
      ↓
MVP2 KNOWLEDGE BASE
      ↓
GOVERNED RAG
      ↓
ACCEPTED CP-MVP2-03 TESTCASE
      ↓
ACCEPTED / GOVERNED CP-MVP2-04 TEST DATA
      ↓
PLAYWRIGHT TEST DESIGN
      ↓
DETERMINISTIC VALIDATION
      ↓
TRACEABILITY / GOVERNANCE
      ↓
CP-MVP2-05 RESULT
```

## 3. Core Architectural Principle

> RAG supplies evidence.
> CP-MVP2-03 supplies the governed testcase.
> CP-MVP2-04 supplies governed test data.
> LLM may reason/generate Playwright artifacts.
> Deterministic code decides structural and governance compliance.

The LLM must not become the final authority for requirements, testcase
validity, test-data validity, locator correctness, or governance —
identical in kind to CP-MVP2-03 sec. 4 and CP-MVP2-04 sec. 4/11, applied
one layer further downstream.

---

## 4. Scope

### 4.1 In Scope

* Consuming an accepted CP-MVP2-03 `GovernedTestcase` and its accepted CP-MVP2-04 `TestDataSet`(s) as anchors.
* Deriving a structured Playwright artifact (navigation, actions, locators, assertions) from them.
* Deterministic locator-evidence lookup against the existing, already-captured DOM evidence (sec. 7).
* Deterministic validation of the generated artifact (schema, traceability, locator/assertion integrity, governance).
* Coverage calculation scoped to applicable accepted CP-MVP2-03 testcases.
* Recording evidence sufficient for a future CP-MVP2-07 RCA/replanning pass, without implementing RCA itself.

### 4.2 Explicitly Out of Scope

* Real browser execution — **CP-MVP2-06.**
* RCA / replanning / self-healing — **CP-MVP2-07.**
* Performance testing — **CP-MVP2-08.**
* Unified final QE reporting — **CP-MVP2-09.**
* CI/CD, browser grids, multi-VM execution, production deployment, enterprise-scale orchestration — POST-MVP, per the Approved SRS §3 / README.md's existing project governance.
* Multi-browser execution — the Approved SRS §11 discloses that **all CP-MVP2-01 discovery used headless Chromium only**; this specification does not expand browser scope beyond what has ever actually been evidenced against this SUT.
* Modifying CP-MVP2-01/02/03/04 or the Approved SRS to make CP-MVP2-05 easier to implement.

---

## 5. Input Contract

### 5.1 Required inputs

| Input | Source | Purpose |
|---|---|---|
| Accepted CP-MVP2-03 `GovernedTestcase` (`governance_status == ACCEPTED`) | `testcases.validate` output | Anchors scenario intent: `test_steps`, `preconditions`, `expected_result`, `scenario_type`, `journey_id`. |
| Its `requirement_ids` | Same testcase | Anchors the requirement(s) that govern locator/assertion evidence. |
| Accepted CP-MVP2-04 `TestDataSet`(s) (`validation_status` in `{ACCEPTED, POSSIBLE_DUPLICATE}`) whose `testcase_id` matches | `testdata.validate` output | Supplies the concrete input values — CP-MVP2-05 never invents an input value. |
| Governed requirement context / RAG attribution | `testcases.generate.requirement_context()` (CP-MVP2-02, unchanged) | Same attribution chain CP-MVP2-03/04 already use. |
| DOM/locator evidence, where it exists (sec. 7) | `knowledge/historical/discovery_evidence/captures/*.html` (read directly, not via `KnowledgeBase` — see sec. 7.1) | The only legitimate source of a locator value for MVP2; never invented. |

### 5.2 Explicit non-reinterpretation rule

CP-MVP2-05 must **not**:

* silently repair an upstream `REJECTED`/`QUARANTINED` testcase or dataset by substituting its own values;
* generate an artifact anchored on a testcase or dataset that is not `ACCEPTED`/`POSSIBLE_DUPLICATE` — such a testcase/dataset is simply not eligible, mirroring CP-MVP2-04 sec. 3/12's "only `ACCEPTED` anchors are eligible" rule one layer further;
* reinterpret a testcase's `expected_result` text to invent a different assertion than what it states.

---

## 6. Playwright Artifact Contract

### 6.1 Design decision: three logical levels, not one

Mirroring CP-MVP2-04 sec. 6.1's reasoning (a flat schema cannot represent
a real testcase's need): a single Playwright "record" cannot represent
an E2E scenario, because a scenario is an **ordered sequence of actions**,
each of which may need its own locator and, in some cases, an
assertion. CP-MVP2-05 therefore uses:

* **`PlaywrightArtifact`** — one governed automation unit for one testcase (+ one of its datasets).
* **`PlaywrightStep`** — one ordered action within the artifact (navigate, fill, click, select, wait, assert).
* **`LocatorSpec`** — the evidence-graded locator for a step that targets a UI element (not every step needs one, e.g. a pure `WAIT`).
* **`Assertion`** — a check tied to a step or to the artifact's overall expected result, explicitly classified (sec. 10).

### 6.2 `PlaywrightArtifact`

| Field | Purpose |
|---|---|
| `automation_id` | Deterministic ID, e.g. `PW-<testcase_id>-<seq>` — never LLM-assigned. |
| `testcase_id` | The CP-MVP2-03 testcase this artifact serves. |
| `requirement_ids` | Copied verbatim from the anchor testcase. |
| `test_data_set_id` | The CP-MVP2-04 dataset supplying this artifact's inputs. |
| `journey_id` | Copied from the anchor testcase. |
| `scenario_type` | Copied from the anchor testcase (`POSITIVE`/`ALTERNATE`/`EXCEPTIONAL`). |
| `browser_intent` | Fixed to `"chromium-headless"` for MVP2 — the only browser configuration ever evidenced against this SUT (Approved SRS §11); not a free-text or LLM-chosen value. |
| `preconditions` | Copied/derived from the anchor testcase's `preconditions`. |
| `steps` | Ordered `List[PlaywrightStep]`. |
| `evidence_requirements` | What evidence (screenshot, DOM snapshot, network log) a future CP-MVP2-06 execution should capture for this artifact — declared here, captured there. |
| `failure_handling_metadata` | Declares what a future CP-MVP2-06/07 should do on failure (e.g. "capture screenshot + DOM snapshot; do not retry silently") — metadata only, no self-healing logic (sec. 14). |
| `source_attribution` | `{requirement_id, source_document, source_version, chunk_id}` — identical shape to CP-MVP2-03/04. |
| `generation_metadata` | `{generator, generated_at, ...}`. |
| `validation_status` | Governance outcome (sec. 12) — never LLM-assigned. |
| `notes` | Deterministic-code-authored reasoning trail. |

### 6.3 `PlaywrightStep`

| Field | Purpose |
|---|---|
| `step_order` | Integer, defines execution order. |
| `action_type` | `NAVIGATE, FILL, CLICK, SELECT, WAIT, ASSERT`. |
| `locator` | A `LocatorSpec`, or `null` for actions that do not target an element (`NAVIGATE`, some `WAIT`). |
| `input_mapping` | For `FILL`/`SELECT`: the exact CP-MVP2-04 `TestDataField.field_name` this step's value comes from. `null` for actions with no input. Never a hard-coded literal — always a reference. |
| `synchronization_strategy` | e.g. `WAIT_FOR_VISIBLE`, `WAIT_FOR_NETWORK_IDLE`, `NONE` — declared, not left implicit, because the checkout flow's step transitions are AJAX-driven within one URL (per `knowledge/technical/application_notes.md`, itself sourced from the real discovery captures), which is exactly the kind of behavior a naive "wait for navigation" strategy would get wrong. |

### 6.4 `LocatorSpec`

| Field | Purpose |
|---|---|
| `strategy` | `TEST_ID, ROLE, STABLE_ATTRIBUTE, LABEL, UNSUPPORTED` (sec. 7). |
| `value` | The actual locator string (e.g. a CSS `#id` selector), or `null` if `strategy == UNSUPPORTED`. |
| `evidence_source` | Which file/capture this locator's value was read from (e.g. `knowledge/historical/discovery_evidence/captures/checkout_00.html`) — never unattributed. |
| `status` | `EVIDENCED` or `UNSUPPORTED` — deterministic, never an LLM claim of confidence. |

### 6.5 `Assertion`

| Field | Purpose |
|---|---|
| `assertion_type` | `BUSINESS_REQUIRED, TECHNICAL_USEFUL, DIAGNOSTIC_OPTIONAL` (sec. 10). |
| `condition` | What is checked (e.g. "success message text equals X", "URL matches pattern"). |
| `source` | Where the expectation comes from: the anchor testcase's `expected_result`, or a specific Approved SRS requirement/acceptance-criterion. |
| `counts_toward_coverage` | `true` only for `BUSINESS_REQUIRED` — sec. 10/18. |

---

## 7. Application / DOM Evidence

### 7.1 What is actually available now (inspected directly for this specification, not assumed)

CP-MVP2-01's discovery session produced **raw HTML captures** at
`knowledge/historical/discovery_evidence/captures/` — 14 files covering
the checkout flow (`checkout_00.html` through `checkout_final.html`,
`checkout_00_filled.html`), guest-checkout entry (`anon_checkout.html`,
`guest_checkout_step1.html`), cart state (`cart_with_item.html`), and
wishlist confirmation (`wishlist_confirm.html`).

**These captures are real DOM evidence, but they are NOT part of the
governed, queryable RAG corpus.** CP-MVP2-02's own governance
deliberately excludes them: `knowledge/lib/validate.py`'s
`check_historical_vs_approved_conflict` asserts zero historical-discovery
chunks ever enter the queryable `KnowledgeBase`. This is a real,
load-bearing architectural fact CP-MVP2-05 must respect, not route
around: a future implementation must read these capture files **directly
from disk**, tagged as `CURRENT_TESTING_ARTIFACT`/historical-tier
evidence (per `knowledge/historical/discovery_evidence/MANIFEST.json`),
never via `KnowledgeBase.query()`/`by_id()` — those methods do not, and
per CP-MVP2-02 governance must not, surface this content.

**Concretely, inspecting the actual captures for this specification found:**

* The Billing/Shipping address form (`checkout_00.html`) uses a
  **stable, deterministic locator pattern**: ASP.NET MVC model-binding
  IDs of the exact shape `{Model}_{Property}`, e.g.
  `id="BillingNewAddress_FirstName"`, `id="BillingNewAddress_Email"`,
  `id="BillingNewAddress_ZipPostalCode"` — one per `REQ-ACO-03` mandatory/
  optional field. This is real, evidenced, genuinely stable (framework
  convention, not an ad hoc generated string) locator evidence.
* The cart quantity control (`cart_with_item.html`) uses
  `name="itemquantity7079994"` — the numeric suffix is that specific
  product's internal item ID from that one discovery session. This is a
  **documented example of a fragile/non-generalizable selector**: using
  this literal name for a different product or a different discovery
  session would be wrong. CP-MVP2-05 must not treat a captured value like
  this as a stable, reusable locator without re-deriving the ID pattern
  (e.g. `input[name^="itemquantity"]` scoped to the correct cart row) —
  and where the pattern itself is not confidently evidenced, the correct
  disposition is `UNSUPPORTED`, not a guess.
* **No registration-page (`/register`) capture exists anywhere in the
  discovery evidence** — only an outbound link to `/register` appears
  (in `guest_checkout_step1.html`). This means `REQ-REG-01`, despite
  already having both an accepted CP-MVP2-03 testcase and accepted
  CP-MVP2-04 test data (this project's own prior checkpoints), has **zero
  locator evidence** available today. A CP-MVP2-05 artifact for it must
  report every element-targeting step as `UNSUPPORTED`, not fabricate
  plausible-looking IDs by analogy to the address form's naming
  convention. This is a genuine, disclosed limitation (sec. 20), not
  something this specification resolves.
* Payment-method **page-level presence** is evidenced (the Payment
  Method step exists in every `checkout_0N.html` capture, matching
  `REQ-PAY-01`), but this inspection did **not** confirm stable
  per-option locator attributes (only a "Continue" button was found in
  the specific file sampled) — disclosed as **partially evidenced**,
  not claimed as fully evidenced, and not to be treated as such by a
  future implementation without re-inspecting more of the captures.

### 7.2 What requires CP-MVP2-06

Any evidence that requires interacting with a *live* browser instance —
confirming a locator still resolves today, observing dynamic content,
inspecting an area no capture covers — belongs to CP-MVP2-06 ("Real
Browser Execution"), not CP-MVP2-05. CP-MVP2-05 does not perform, and
must not silently assume the results of, live browser inspection.

### 7.3 Boundary: test generation vs. real execution

CP-MVP2-05 generates a structured artifact describing *intended*
actions/locators/assertions. It does not launch a browser, does not
execute Playwright, and does not confirm a locator resolves against the
live SUT. That confirmation is CP-MVP2-06's job, operating on CP-MVP2-05's
governed output.

---

## 8. Playwright Generation Boundary

CP-MVP2-05 may generate Playwright-shaped artifacts (sec. 6). It must
**not** execute them. `docs/CP-MVP2-05-SPECIFICATION-v1.0.md` and any
future implementation of it stop at producing `PlaywrightArtifact`
records; CP-MVP2-06 consumes them and drives a real browser.

---

## 9. Test-Data Mapping

Every `FILL`/`SELECT` step's `input_mapping` must name an existing
`field_name` on the linked CP-MVP2-04 `TestDataSet`. Concretely, for a
`REQ-REG-01` `POSITIVE` artifact: the step filling the email field maps
`input_mapping = "email"`, which resolves at artifact-build time to that
dataset's actual `email` field value (e.g. a real accepted value like
`priya.sharma@example.com`, per this project's own CP-MVP2-04 live
verification evidence) — never a value invented independently of that
dataset.

If a UI field a testcase's `test_steps` describes has **no corresponding
field** on the linked dataset, the artifact reports:

```text
UNSUPPORTED / NEEDS CLARIFICATION
```

with the missing field named explicitly. The generator must never
silently substitute an invented value to "complete" the mapping.

---

## 10. Assertion Governance

Every artifact must carry at least one `BUSINESS_REQUIRED` assertion,
grounded in one of:

* the anchor testcase's own `expected_result` text (always eligible — it
  is itself already a governed, accepted statement);
* a specific Approved SRS acceptance criterion for one of the artifact's
  `requirement_ids`.

`TECHNICAL_USEFUL` assertions (e.g. "the page did not throw a JS
console error") and `DIAGNOSTIC_OPTIONAL` assertions (e.g. "capture a
screenshot regardless of outcome") may additionally be attached, but
**never** count toward requirement coverage (`counts_toward_coverage =
false`) — this is the explicit safeguard sec. 18/21 requires: an LLM
adding a dozen "useful" technical checks must never make a testcase look
more thoroughly covered than its actual governed business assertion
count justifies.

An LLM proposing an assertion the deterministic layer cannot trace to
either source above is rejected at that assertion's level, not silently
kept.

---

## 11. Traceability

Two chains, mirroring CP-MVP2-04 sec. 12 exactly one layer further:

```text
PLAYWRIGHT ARTIFACT
   ↓
CP-MVP2-03 TESTCASE
   ↓
REQUIREMENT ID
   ↓
APPROVED SRS
   ↓
RAG EVIDENCE
```

```text
PLAYWRIGHT INPUT (a step's input_mapping)
   ↓
CP-MVP2-04 DATASET
   ↓
TEST-DATA FIELD
```

No orphan automation artifacts (unresolvable `testcase_id`); no unknown
requirement IDs; no unknown testcase IDs; no unknown dataset IDs. A
violation of any of these is `REJECTED` or `QUARANTINED` exactly as
CP-MVP2-03/04 already define for their own analogous cases (unknown =
`QUARANTINED`, known-but-ineligible = `REJECTED`).

---

## 12. Governance States

Reused, not reinvented, from the project's existing vocabulary (per this
task's own instruction to avoid unnecessary parallel terminology):

```python
class GovernanceStatus:  # identical vocabulary to testcases/testdata
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    UNSUPPORTED_NEEDS_CLARIFICATION = "UNSUPPORTED_NEEDS_CLARIFICATION"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
```

Applied per-artifact (an artifact overall) and per-step/locator (a step
whose locator is `UNSUPPORTED` does not necessarily reject the whole
artifact — see sec. 13's "partial artifact" disposition). The LLM never
self-authorizes any of these; deterministic validation always makes the
final call (sec. 17), exactly as in CP-MVP2-03/04.

### 12.1 Partial-artifact disposition (new nuance for this checkpoint)

Because an artifact is a *sequence* of steps, a single step's
`UNSUPPORTED` locator does not automatically make every other step
meaningless. This specification requires:

* If **any** step required to reach or verify the testcase's core
  `expected_result` is `UNSUPPORTED`, the **whole artifact** is
  `UNSUPPORTED_NEEDS_CLARIFICATION` (the scenario cannot be completed).
* An artifact is never partially `ACCEPTED` — governance status is
  artifact-level for acceptance purposes, even though individual step/
  locator statuses are retained in the record for diagnostic and future
  RCA purposes (sec. 14).

---

## 13. Failure / Ambiguity Handling

| Condition | Disposition |
|---|---|
| Missing locator evidence | Step's `LocatorSpec.status = UNSUPPORTED`; artifact becomes `UNSUPPORTED_NEEDS_CLARIFICATION` if that step is load-bearing (sec. 12.1). |
| Ambiguous UI element (evidence suggests more than one plausible locator) | `UNSUPPORTED` — never resolved by LLM guess. |
| Missing test-data field | `UNSUPPORTED / NEEDS CLARIFICATION` (sec. 9). |
| Testcase/data mismatch (dataset's `requirement_ids` don't match testcase's) | `REJECTED` — mirrors CP-MVP2-04 sec. 12's requirement-ID-mismatch rule. |
| Unsupported browser interaction (an action Playwright/Chromium cannot represent as evidenced) | `UNSUPPORTED`, with the specific interaction named. |
| Requirement ambiguity | `UNSUPPORTED` — never resolved by reinterpreting the requirement. |
| Conflicting evidence (two captures disagree on a locator) | `UNSUPPORTED` — flagged for human/Di review, never auto-resolved by preference. |
| Unstable selector evidence (e.g. the `itemquantity<id>` pattern, sec. 7.1) | `UNSUPPORTED` unless the stable *pattern* (not the literal captured value) can itself be evidenced and generalized — a future implementation decision, not assumed here. |
| Unsupported control/widget (no evidenced interaction pattern exists) | `UNSUPPORTED`. |
| Dependency unavailable (e.g. artifact needs a prior order to exist) | `UNSUPPORTED`, mirroring CP-MVP2-04's `DEPENDENCY_ISSUE` category. |
| Application evidence unavailable entirely (e.g. `REQ-REG-01`, sec. 7.1) | `UNSUPPORTED_NEEDS_CLARIFICATION` for every element-targeting step. |

In every case: **report the problem; never invent a solution that
changes the business requirement, testcase intent, or test data.**

---

## 14. Self-Healing Boundary

CP-MVP2-05 does **not** implement self-healing. It does, however, record
the evidence a future CP-MVP2-07 would need to reason about a failure
without re-deriving it from scratch:

* `evidence_requirements` (sec. 6.2) declares what CP-MVP2-06 should
  capture on failure (screenshot, DOM snapshot, network log) — CP-MVP2-05
  declares the requirement; it does not capture anything itself (no
  browser is run here).
* `failure_handling_metadata` declares the *intended* failure response
  (e.g. "do not retry silently; escalate") as data, not as executable
  logic.

Nothing in this specification permits a future self-healing mechanism to
silently alter requirements, testcase intent, test data, or expected
results — any such change remains subject to the same formal Change
Request process already governing every other checkpoint.

---

## 15. Security / Data Governance

* No real PII, payment credentials, secrets, or production credentials
  — inherited directly from CP-MVP2-04 sec. 16 and the Approved SRS §10.
* Generated automation must not hard-code secrets. Any credential-shaped
  value (e.g. a login password) comes exclusively from a governed
  CP-MVP2-04 dataset field, itself already synthetic per CP-MVP2-04's own
  governance — never a literal invented by this checkpoint.
* Environment-specific configuration (base URL, timeout values) should
  be represented as named configuration references in
  `generation_metadata`, not hard-coded literals scattered through
  `steps` — without prematurely designing a CI/CD or production
  configuration system, which remains out of scope (sec. 4.2).

---

## 16. Browser Scope

* **Browser-independent generation:** the `PlaywrightArtifact` schema
  itself (sec. 6) is browser-agnostic structured data.
* **Browser-specific execution:** deferred entirely to CP-MVP2-06.
* **Multi-browser execution:** out of scope for MVP2 — the Approved SRS
  explicitly discloses headless-Chromium-only discovery and no
  cross-browser verification (Approved SRS §11/§12). `browser_intent`
  (sec. 6.2) is fixed accordingly; this specification does not invent a
  multi-browser requirement the frozen SRS never established.

---

## 17. Deterministic Validation

Deterministic code (never the LLM) must validate:

* **Schema validity** — required fields present on `PlaywrightArtifact`/`PlaywrightStep`/`LocatorSpec`/`Assertion`; fixed vocabularies respected.
* **Testcase traceability** — `testcase_id` resolves to a real, `ACCEPTED` `GovernedTestcase`.
* **Requirement traceability** — `requirement_ids` match that testcase's exactly.
* **Test-data traceability** — `test_data_set_id` resolves to a real, `ACCEPTED`/`POSSIBLE_DUPLICATE` `TestDataSet` whose `testcase_id` matches.
* **Locator validity/structure** — every non-null `LocatorSpec` cites a real `evidence_source`; a `strategy` other than `UNSUPPORTED` must have a non-null `value`.
* **Action/field mapping** — every `input_mapping` names a field that actually exists on the linked dataset (sec. 9).
* **Assertion presence** — at least one `BUSINESS_REQUIRED` assertion exists and is traceable (sec. 10).
* **Governance status** — final `ACCEPTED`/`REJECTED`/`QUARANTINED`/`UNSUPPORTED`/`DUPLICATE`/`POSSIBLE_DUPLICATE` assignment (sec. 12).
* **Unsupported conditions** — every condition in sec. 13's table is checked, not merely documented.
* **Duplicate detection** — same `(testcase_id, test_data_set_id)` producing structurally identical artifacts is content-level duplicate handling, mirroring CP-MVP2-03/04's exact-vs-possible-duplicate split.
* **Coverage calculation** — sec. 18.

Coverage must never be inflated by invalid, orphaned, `REJECTED`, or
`QUARANTINED` artifacts — identical rule to CP-MVP2-03/04, applied here.

---

## 18. Coverage

```text
CP-MVP2-05 Coverage =
Accepted CP-MVP2-03 testcases having ≥1 ACCEPTED PlaywrightArtifact
--------------------------------------------------------------------
Total applicable ACCEPTED CP-MVP2-03 testcases
× 100
```

* The denominator is CP-MVP2-03's own `ACCEPTED` testcase set — identical
  scoping discipline to CP-MVP2-04 sec. 14 (a testcase CP-MVP2-03 itself
  did not accept is excluded from the denominator entirely).
* The numerator counts only `ACCEPTED` (and `POSSIBLE_DUPLICATE`, for the
  same reason CP-MVP2-03/04 count it) artifacts.
* **An LLM generating *some* output for every testcase does not mean
  100% coverage.** Coverage requires deterministic acceptance, not mere
  attempted generation — this is the explicit rule this task's sec. 18
  demands, and it is enforced by the same `COVERAGE_COUNTING_STATUSES`-
  style filter already proven in `testcases/schema.py` and
  `testdata/schema.py`.

---

## 19. Downstream Contract

### 19.1 CP-MVP2-06 (Real Browser Execution)

Must be able to consume exactly the `ACCEPTED` `PlaywrightArtifact`
records CP-MVP2-05 produces, and execute them against a real browser
**without reinterpreting business requirements** — every action, locator,
input value, and assertion it needs is already resolved, attributed,
and governed. CP-MVP2-06's own job is purely mechanical execution plus
evidence capture per `evidence_requirements`/`failure_handling_metadata`.

### 19.2 CP-MVP2-07 (RCA + Replanning + Governance)

May consume: the full traceability chain (sec. 11) to walk backward from
an execution failure to the originating requirement; `failure_handling_metadata`
and `evidence_requirements` to know what evidence should already exist;
per-step/locator status detail (sec. 12.1) to localize *which* step
failed, not just that the artifact did. CP-MVP2-07 is not implemented,
specified, or modified by this document.

### 19.3 CP-MVP2-08 (JMeter Performance Testing)

Functional Playwright artifacts are not performance test plans; CP-MVP2-08
is expected to have its own, separate input contract (analogous to how
CP-MVP2-04 sec. 17.1 already flagged this same distinction). Not
addressed further here.

### 19.4 CP-MVP2-09 (Unified Final QE Reporting)

May consume CP-MVP2-05's `by_status`/coverage output shapes, deliberately
kept structurally parallel to CP-MVP2-03/04's for the same reason
CP-MVP2-04 sec. 17.1 already gives: reducing CP-09 redesign risk later.

---

## 20. Known Limitations / Open Questions (disclosed at specification time)

1. **`REQ-REG-01` has zero locator evidence** despite already having an
   accepted CP-MVP2-03 testcase and accepted CP-MVP2-04 data (sec. 7.1).
   Disposition: `UNSUPPORTED_NEEDS_CLARIFICATION` for any registration
   artifact, until a future discovery pass captures the `/register` page.
   Not solved by assumption here.
2. **Exact per-option payment-method locators are not confirmed** (sec.
   7.1) — only page-level step presence is evidenced. Disposition:
   `UNSUPPORTED` for the specific option-selection step until a future
   evidence pass confirms it; the page-level navigation step itself may
   still be evidenced separately.
3. **The cart-quantity locator pattern is evidenced only as a fragile,
   item-specific literal** (`itemquantity7079994`) — whether the
   generalized pattern (`input[name^="itemquantity"]` scoped to the
   correct row) is reliable is genuinely unresolved without further,
   real evidence (ideally from CP-MVP2-06-era live inspection).
   Disposition: `UNSUPPORTED` unless/until a future task establishes and
   evidences the generalized pattern.
4. **DOM/locator evidence lives outside the governed RAG corpus by
   design** (sec. 7.1) — this is an existing, correct CP-MVP2-02
   governance decision, not a gap to be closed by CP-MVP2-05. A future
   implementation must read `knowledge/historical/discovery_evidence/`
   directly, tagged at its own historical-tier authority, never conflated
   with the Approved-SRS-tier evidence CP-MVP2-03/04 consume.
5. **`DATA-OQ-01`** (shared-instance data-reset/isolation policy,
   Approved SRS §13) remains unresolved, inherited unchanged from
   CP-MVP2-04 — any CP-MVP2-05 artifact whose validity would depend on an
   isolation assumption (e.g. "this order must not already exist") must
   report `UNSUPPORTED`, not assume a policy.
6. **Multi-step/AJAX synchronization strategy is declared as a
   requirement, not yet validated against a live instance** — the
   `synchronization_strategy` field (sec. 6.3) exists because the
   checkout flow is known (from real evidence) to be AJAX-driven within
   one URL, but the *correct* strategy per step is a CP-MVP2-06-era
   empirical question, not resolved by this specification.

---

## 21. Acceptance Criteria

### 21.1 Functional
Generated `PlaywrightArtifact` correctly represents the accepted
testcase's `test_steps`/`expected_result` in structured form.

### 21.2 Traceability
Every artifact resolves the full chain in sec. 11 — no orphan artifact,
no unknown requirement/testcase/dataset ID.

### 21.3 Governance
No requirement/testcase/test-data reinterpretation anywhere in the
pipeline; governance status always deterministically assigned.

### 21.4 Locator integrity
Every locator is either evidence-based (`EVIDENCED`, with a cited
`evidence_source`) or explicitly `UNSUPPORTED` — never a plausible-looking
invented value.

### 21.5 Assertion integrity
At least one `BUSINESS_REQUIRED` assertion per accepted artifact,
traceable to the testcase's `expected_result` or an Approved SRS
acceptance criterion; `TECHNICAL_USEFUL`/`DIAGNOSTIC_OPTIONAL` assertions
never count toward coverage.

### 21.6 Data integrity
Every input value traces to a named field on an accepted CP-MVP2-04
dataset — never an independently invented literal.

### 21.7 Deterministic validation
An artifact failing any check in sec. 17 cannot reach `ACCEPTED`.

### 21.8 Coverage
Computed per sec. 18, deterministically, excluding non-`ACCEPTED`/
non-`POSSIBLE_DUPLICATE` artifacts and out-of-universe testcases.

### 21.9 Regression
CP-MVP2-01 through CP-MVP2-04 behavior (all existing tests) remains
unchanged and passing.

---

## 22. Governance

* The Approved SRS remains the ultimate source of truth; CP-MVP2-03's
  accepted testcases and CP-MVP2-04's accepted datasets remain the
  immediate, non-reinterpretable anchors for this checkpoint.
* RAG (unchanged) and the historical discovery captures (read directly,
  at their own correct authority tier — sec. 7.1) provide governed
  evidence; CP-MVP2-05 never bypasses either or conflates their authority.
* The LLM reasons and proposes structure/locator candidates/assertions;
  deterministic validators govern acceptance (sec. 17).
* No silent requirement, testcase, or test-data change; no fabricated
  locator; no assertion invented without a traceable source; no silent
  baseline change.
* Conflicts (ambiguous evidence, missing evidence, an upstream
  testcase/dataset defect) become governance findings (`UNSUPPORTED`/
  `REJECTED`/`QUARANTINED`), never silent assumptions or repairs.
* Human approval remains required before this specification is treated
  as approved/frozen, and before any implementation begins.

Governed run-health vocabulary (mirroring CP-MVP2-04 sec. 20 and the
project's existing GREEN/YELLOW/RED convention):

* **GREEN** — all applicable testcases have an `ACCEPTED` artifact, no
  unexplained `QUARANTINED`/`REJECTED` findings.
* **YELLOW** — coverage incomplete and/or `UNSUPPORTED` findings exist
  (e.g. the known `REQ-REG-01` locator gap), but no governance rule was
  violated.
* **RED** — a governance rule was violated (e.g. a fabricated locator
  reached `ACCEPTED`, or an assertion with no traceable source was
  counted toward coverage) — must never occur in a correct
  implementation; a stop-the-line signal if observed.

---

## 23. Versioning and Freeze

* Checkpoint: **CP-MVP2-05 — Playwright E2E Generation**
* Specification version: **1.0**
* **Status: DRAFT — pending Human + Di review.**
* This document does not become authoritative until an explicit approval
  decision is recorded, mirroring the exact process already used for
  CP-MVP2-03 and CP-MVP2-04.
* Any change after approval requires a formal, versioned Change Request
  — no silent modification permitted once frozen.
