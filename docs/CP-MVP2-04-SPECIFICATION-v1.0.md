# CP-MVP2-04 — LLM Test Data Generation

### Draft Specification — v1.0

> **Status:** DRAFT — pending Human + Di review. **NOT YET APPROVED. NOT YET FROZEN.**
> **Origin:** Authored for the CP-MVP2-04 — Specification Creation & Governance Review task, from the frozen `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` (governance conventions, scenario vocabulary, LLM/deterministic boundary), the Approved SRS (`requirements/MVP2_SRS_v1.0_APPROVED.md`, §10 "Data Requirements / Test Data Considerations" and §13's `DATA-OQ-01`), and the existing CP-MVP2-03 implementation (`testcases/schema.py`, `testcases/validate.py`) as design precedent.
> **Important:** This document does not implement CP-MVP2-04, does not modify any frozen artifact, and does not authorize implementation. It defines the contract a future, separately authorized implementation task will build against.

---

## 1. Objective

Generate governed, traceable **test data** for the testcases already produced and accepted by CP-MVP2-03, retrieved and reasoned about through the same governed MVP2 Knowledge Base/RAG layer and the same Approved-SRS-is-truth discipline.

The objective is to demonstrate that the Agentic QE system can:

1. Identify what test data an accepted CP-MVP2-03 testcase actually needs.
2. Derive data constraints from the Approved SRS and governed RAG evidence — never invent them.
3. Generate structured, categorized test data via LLM reasoning over that governed evidence.
4. Validate generated data deterministically (schema, constraints, uniqueness, traceability).
5. Prevent accidental duplicate business entities where the Approved SRS requires uniqueness (e.g. registration email).
6. Identify data that cannot be generated from available evidence, and report it rather than fabricate it.
7. Establish dataset-to-testcase-to-requirement-to-evidence traceability.
8. Calculate genuine, non-inflated data coverage against applicable testcases.
9. Produce a governed CP-MVP2-04 result that CP-MVP2-05 can consume without reinterpreting business requirements.

---

## 2. Scope

### 2.1 In Scope

* Test-data requirement identification from an accepted CP-MVP2-03 testcase (its `preconditions`, `test_steps`, `expected_result`, and linked `requirement_ids`).
* LLM-assisted test-data generation, constrained to governed evidence.
* Deterministic classification of generated data (category, boundary classification, validity).
* Dataset-to-testcase traceability and source attribution.
* Deterministic validation: schema, constraint conformance, requirement/testcase linkage, uniqueness, duplicate detection.
* Data governance (Approved-vs-Draft-equivalent discipline; no fabricated constraints presented as requirement-derived).
* Auditability of every accepted dataset.
* Reproducibility of a dataset's *identity and intent*, where practical, without over-engineering a full data-management subsystem for MVP2.

### 2.2 Explicitly Out of Scope

CP-MVP2-04 is **NOT responsible for**:

* Browser automation or real browser execution.
* Playwright test generation (CP-MVP2-05).
* Performance test execution (CP-MVP2-08).
* Security/penetration testing execution (POST-MVP, parked per the Approved SRS §3).
* Root-cause analysis, self-healing, or replanning (CP-MVP2-07).
* Final QE reporting (CP-MVP2-09).
* Git PR/merge automation.
* Modifying, reinterpreting, or resolving CP-MVP2-01/02/03 requirements or testcases.
* Establishing a general-purpose data-management/reset service for the shared Demo Web Shop instance (see §12 — `DATA-OQ-01` remains disclosed, not silently resolved).

---

## 3. Authoritative Architecture

```text
APPROVED SRS
     ↓
MVP2 KNOWLEDGE BASE
     ↓
GOVERNED RAG RETRIEVAL
     ↓
ACCEPTED CP-MVP2-03 TESTCASE
     ↓
TEST-DATA REQUIREMENT IDENTIFICATION
     ↓
LLM (TEST DATA REASONING)
     ↓
STRUCTURED TEST DATA OUTPUT
     ↓
DETERMINISTIC TEST DATA VALIDATORS
     ↓
UNIQUENESS / DUPLICATE / COVERAGE / GOVERNANCE
     ↓
CP-MVP2-04 RESULT
```

This extends, and does not replace, the CP-MVP2-03 pipeline:

```text
APPROVED SRS → GOVERNED RAG → LLM TESTCASE GENERATION → DETERMINISTIC TESTCASE VALIDATION
  → LLM TEST DATA GENERATION → DETERMINISTIC TEST DATA VALIDATION
```

CP-MVP2-04 consumes CP-MVP2-03's **accepted, governed output** (a `GovernedTestcase` with `governance_status == ACCEPTED`) as its own input's anchor — it does not re-derive or second-guess CP-MVP2-03's governance decision, and it does not consume rejected/quarantined/duplicate testcases as a basis for data generation.

---

## 4. Core Architectural Principle

Unchanged from CP-MVP2-03 (spec sec. 4), extended one stage further:

> **RAG supplies the evidence.
> The accepted CP-MVP2-03 testcase supplies the data need.
> LLM performs the data-value reasoning.
> Deterministic code decides whether the generated data complies.**

The LLM must not become the final authority for governance, constraint conformance, or uniqueness — exactly as in CP-MVP2-03. Deterministic validation is the sole acceptance authority for generated test data, exactly as it is for generated testcases.

---

## 5. Inputs

### 5.1 Required inputs

| Input | Source | Purpose |
|---|---|---|
| Accepted CP-MVP2-03 testcase (`GovernedTestcase` with `governance_status == ACCEPTED`) | `testcases.validate.build_report()` output | Anchors what data is needed: `test_steps`, `preconditions`, `expected_result`, `scenario_type` |
| `requirement_ids` | Same testcase | Anchors which Approved SRS requirement(s) govern the data's constraints |
| Governed requirement context | `testcases.generate.requirement_context()` (CP-MVP2-02 RAG, unchanged) | The requirement text and directly-linked evidence (business rules, negative cases) the constraints must be derived from |
| `source_document` / `source_version` / `approval_status` | Same requirement context | Attribution chain anchor; must be `approved_srs` / `APPROVED` |

### 5.2 Optional inputs

| Input | Source | Purpose |
|---|---|---|
| Explicitly supplied deterministic constraints | Caller-provided (e.g. a known field-length limit already validated elsewhere) | Allows a caller to supply a constraint that governed evidence alone does not state, without asking the LLM to invent it. Must itself be attributed to *something* (a prior governance decision, a system constant) — never anonymous. |
| Existing dataset registry (for uniqueness/duplicate checks) | Prior CP-MVP2-04 output for the same run/session | Enables the uniqueness/duplicate-detection layer (§10) to detect collisions across a batch, not just within one dataset. |

If neither the requirement context nor an explicitly supplied deterministic constraint establishes a needed value or rule, that data point is `UNSUPPORTED / NEEDS CLARIFICATION` (§9) — never filled from general LLM knowledge.

---

## 6. Test-Data Schema

### 6.1 Design decision (documented, per the task's "you may improve the schema" allowance)

A flat one-field-per-record schema cannot represent a realistic testcase need: `REQ-REG-01`, for example, requires **First name, Last name, Email, Password, and Confirm password together** to exercise one scenario — no single field value is independently testable for that testcase. CP-MVP2-04 therefore uses a **two-level schema**:

* **`TestDataSet`** — one governed unit of data for one testcase/scenario (the thing a testcase actually consumes).
* **`TestDataField`** — one named value within a `TestDataSet` (the thing constraints, boundary classification, and uniqueness rules actually apply to).

This mirrors the precedent already established in this project: CP-MVP2-02 keeps `approval_status` and `evidence_strength` as two independent axes on one `Chunk` (governance rule: collapsing them "would silently destroy exactly the distinction ... designed to preserve"); CP-MVP2-04 keeps dataset-level governance (`validity`, `data_category`, `validation_status`) and field-level governance (`boundary_classification`, `uniqueness_requirement`) as two independent, non-collapsed levels for the identical reason — a dataset can be overall `POSITIVE` while containing one field deliberately at a `BOUNDARY` value, and collapsing the two levels would hide that.

### 6.2 `TestDataSet`

| Field | Type | Purpose |
|---|---|---|
| `data_set_id` | `str` | Unique identifier, deterministically assigned (never LLM-assigned), analogous to `testcase_id`. |
| `testcase_id` | `str` | The CP-MVP2-03 testcase this dataset serves. |
| `requirement_ids` | `List[str]` | Copied from the anchor testcase — never independently re-derived or altered. |
| `data_category` | `str` | One of `POSITIVE, ALTERNATE, EXCEPTIONAL, BOUNDARY, INVALID` (§7). Orthogonal to the testcase's own `scenario_type` — see §6.1. |
| `purpose` | `str` | Short human-readable statement of why this dataset exists (e.g. "valid registration data satisfying all mandatory fields"). |
| `validity` | `str` | `VALID` or `INVALID` — whether the dataset is *intended* to satisfy the requirement's constraints (a deliberately `INVALID` dataset, e.g. for `NEG-03`'s malformed email, is not a defect — it is the point). |
| `source_attribution` | `List[Dict]` | Chain entries: `{requirement_id, source_document, source_version, chunk_id}` — built deterministically from the same retrieval CP-MVP2-03 already used for this testcase, never invented. |
| `generation_metadata` | `Dict` | `{generator, generated_at, retrieval_mode, ...}` — same discipline as CP-MVP2-03's `Testcase.generation_metadata`. |
| `validation_status` | `str` | Governance outcome (§11) — `ACCEPTED / REJECTED / QUARANTINED / UNSUPPORTED_NEEDS_CLARIFICATION / DUPLICATE / POSSIBLE_DUPLICATE`. Never set by the LLM. |
| `notes` | `str` (optional) | Deterministic-code-authored reasoning trail (e.g. which constraint rejected the dataset). Never an LLM justification presented as governance. |
| `fields` | `List[TestDataField]` | The actual data. |

### 6.3 `TestDataField`

| Field | Type | Purpose |
|---|---|---|
| `field_name` | `str` | e.g. `email`, `password`, `quantity`. |
| `field_value` | `str \| int \| float \| bool \| null` | The generated value. |
| `value_type` | `str` | `STRING, INTEGER, FLOAT, BOOLEAN, EMAIL, ENUM` (extensible; deterministic code validates against this, never the LLM). |
| `boundary_classification` | `str` | `NOMINAL, MIN_BOUNDARY, MAX_BOUNDARY, BELOW_MIN, ABOVE_MAX, EMPTY, NOT_APPLICABLE`. Only assignable where the Approved SRS/evidence actually states or implies a boundary (§7.4) — otherwise `NOT_APPLICABLE`, never guessed. |
| `uniqueness_requirement` | `str` | `MUST_BE_UNIQUE, MAY_REUSE, UNIQUENESS_UNKNOWN` (§10). |
| `dependency_reference` | `str \| null` | If this field's validity depends on another field/dataset (e.g. `confirm_password` depending on `password`), a reference to that dependency. `null` if none. |

### 6.4 Fixed vocabularies

```python
class DataCategory:
    POSITIVE = "POSITIVE"
    ALTERNATE = "ALTERNATE"
    EXCEPTIONAL = "EXCEPTIONAL"
    BOUNDARY = "BOUNDARY"
    INVALID = "INVALID"

class BoundaryClassification:
    NOMINAL = "NOMINAL"
    MIN_BOUNDARY = "MIN_BOUNDARY"
    MAX_BOUNDARY = "MAX_BOUNDARY"
    BELOW_MIN = "BELOW_MIN"
    ABOVE_MAX = "ABOVE_MAX"
    EMPTY = "EMPTY"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class UniquenessRequirement:
    MUST_BE_UNIQUE = "MUST_BE_UNIQUE"
    MAY_REUSE = "MAY_REUSE"
    UNIQUENESS_UNKNOWN = "UNIQUENESS_UNKNOWN"

class DataGovernanceStatus:   # deliberately the same vocabulary as testcases.schema.GovernanceStatus
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    UNSUPPORTED_NEEDS_CLARIFICATION = "UNSUPPORTED_NEEDS_CLARIFICATION"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
```

Reusing the CP-MVP2-03 `GovernanceStatus` vocabulary (rather than inventing a parallel one) is a deliberate consistency decision: every downstream consumer (evidence reports, future dashboards) already understands these five/six states.

---

## 7. Data Categories

A category is valid **only when justified by the anchor testcase and its governed requirement evidence** — never assigned merely to increase apparent thoroughness.

### 7.1 POSITIVE
Data that satisfies every stated constraint for a `POSITIVE`-scenario testcase. Example (grounded, not invented): for `REQ-REG-01` via `TC-REQ-REG-01-01`, a `POSITIVE` dataset supplies a syntactically valid, unique email, matching password/confirm-password, and non-blank first/last name.

### 7.2 ALTERNATE
Data exercising a valid-but-non-primary path the requirement evidence supports (e.g. a saved address selected via `REQ-ACO-02`'s reuse mechanism, rather than freshly entered).

### 7.3 EXCEPTIONAL
Data that deliberately violates a constraint the requirement/negative-case evidence documents as rejected. Example: `NEG-03`'s malformed email (`"not-an-email"` per direct system evidence), `NEG-02`'s mismatched password/confirm-password, `NEG-04`'s duplicate email.

### 7.4 BOUNDARY
Data at or adjacent to a stated limit. **CP-MVP2-04 must not invent a numeric boundary the Approved SRS/RAG evidence does not state.** Where the Approved SRS states a boundary explicitly (e.g. a quantity of exactly `0` per `REQ-CART-03`/`NEG-07`), `BOUNDARY` is justified. Where no such limit is evidenced (e.g. no maximum email length is documented anywhere in the Approved SRS), `BOUNDARY` must not be fabricated — the field's `boundary_classification` stays `NOT_APPLICABLE` and, if a boundary dataset was specifically requested for that field, the result is `UNSUPPORTED / NEEDS CLARIFICATION`, not an invented threshold.

### 7.5 INVALID
Data that violates basic type/format/required-ness constraints regardless of scenario (e.g. an empty required field, per `NEG-01`). Distinct from `EXCEPTIONAL` in that `INVALID` is a data-shape violation; `EXCEPTIONAL` is a business-rule violation. A dataset may legitimately be both (e.g. `NEG-01`'s all-blank submission is `INVALID` in category and also serves an `EXCEPTIONAL`-scenario testcase) — the two axes are not mutually exclusive, and this is intentional, not a modeling defect.

---

## 8. Requirement-Derived Constraints

Constraints are **extracted, never invented**, from:

1. The requirement's own `Statement` / `Acceptance Criteria` text (e.g. `REQ-ACO-03`: "shall require First name, Last name, Email, Country, City, Address 1, Zip/postal code, and Phone number; Company, Address 2, and Fax number shall be optional").
2. Directly linked `business_rule` chunks (e.g. Business Rule #1: "A registration email must be unique across accounts").
3. Directly linked `negative_case` chunks (journey-linked, exactly as CP-MVP2-03's `requirement_context` already gathers them — §5.1) — these establish what makes data *invalid*, which is itself a constraint.

Constraint categories to extract where present:

* **Mandatory / optional fields** — e.g. `REQ-REG-01`'s five mandatory fields; `REQ-ACO-03`'s mandatory-vs-optional address fields.
* **Field formats** — e.g. email must be a syntactically valid address (`REQ-REG-03`).
* **Field lengths / ranges** — extracted only where the Approved SRS or RAG evidence states one; **none currently exists** in the Approved SRS v1.0 for any field (disclosed, not silently assumed — see §17 limitations). This is why `BOUNDARY` (§7.4) is heavily evidence-gated.
* **Allowed value sets** — e.g. Payment Method: `Cash On Delivery, Check/Money Order, Credit Card, Purchase Order` (`REQ-PAY-01`); Shipping Method: multiple options, exact set not fixed by the SRS (only existence-of-choice is approved, per `REQ-SHIP-01`'s own "existence of the choice only" scope note — CP-MVP2-04 must not invent the specific method names as a business rule beyond what is documented).
* **Relationships between fields** — e.g. `password` must equal `confirm_password` (`REQ-REG-02`).
* **Dependencies** — e.g. cart quantity update depends on an existing cart line (`REQ-CART-02`/`03`).
* **Role-specific data** — Guest vs. Authenticated actor, where the requirement's `Actor` column differs (e.g. `REQ-ACO-02`'s saved-address reuse applies only to an authenticated actor with a prior order).
* **Country/region rules** — not evidenced anywhere in the Approved SRS v1.0; `Country` is a mandatory address field (`REQ-ACO-03`) with no stated allowed-value list or format rule beyond "required." CP-MVP2-04 must not invent a country-code standard as a business rule; it may use a self-evidently synthetic, clearly-labeled value and must not present the *choice* of that value as requirement-derived.
* **Business-rule constraints** — extracted only from `content_type == "business_rule"` chunks already ingested by CP-MVP2-02, exactly as CP-MVP2-03 already does for `ALTERNATE`-scenario justification (spec sec. 5/CP-MVP2-03-IMPLEMENTATION.md).

---

## 9. Unsupported / Clarification Behavior

If available evidence does not establish a value or rule needed to generate valid data, CP-MVP2-04 must report:

```text
UNSUPPORTED / NEEDS CLARIFICATION
```

with a reason, rather than fabricate a value. Examples grounded in this project's actual, disclosed gaps:

* Unspecified field format — e.g. no documented maximum length for any registration/address field.
* Unknown allowed value — e.g. the exact enumerated set of Shipping Method names is not fixed by the Approved SRS (`REQ-SHIP-01` approves only "existence of the choice").
* Unclear boundary — any numeric limit not stated in evidence.
* Conflicting approved information — none currently known in the Approved SRS v1.0; the mechanism must exist regardless.
* Missing dependency — e.g. generating `ALTERNATE` "saved address reuse" data (`REQ-ACO-02`) requires a prior order/address to exist; if the calling context supplies no such prior state, this is `UNSUPPORTED`, not fabricated.
* Requirement ambiguity — e.g. `DATA-OQ-01` (Approved SRS §13): "What is the shared-instance data-reset/isolation policy?" is explicitly parked and explicitly flagged in the Approved SRS itself as relevant to CP-MVP2-04. CP-MVP2-04 must report any data-isolation-dependent generation request against this open question as `UNSUPPORTED / NEEDS CLARIFICATION`, not silently assume an isolation policy.

---

## 10. Uniqueness and Duplicate Prevention

This is the most safety-critical section, per explicit task governance, and it is grounded directly in Business Rule #1 of the Approved SRS: *"A registration email must be unique across accounts."*

### 10.1 The distinction that must never collapse

* **Intentionally reused data** — e.g. the *same* malformed-email string may legitimately be reused across multiple `EXCEPTIONAL` datasets that all test "malformed email is rejected" — reuse here is correct, not a defect, because the requirement being tested (`REQ-REG-03`) does not depend on the email being unique; it depends on the email being *malformed*.
* **Accidentally duplicated data** — e.g. two `POSITIVE` registration datasets for two different testcases both generating `"test.user@example.com"` would create a real conflict, because `REQ-REG-04`/Business Rule #1 requires the email to be unique *across accounts*, and a real system exercised by both datasets would reject the second as a duplicate — not because the test wanted that, but because the generator failed to honor the constraint.
* **Data that must be unique** — any field a governed constraint (business rule or requirement statement) states must be unique (currently: registration/account email, per Business Rule #1). `uniqueness_requirement = MUST_BE_UNIQUE`.
* **Data that may be reused** — any field with no such constraint (e.g. `first_name`, a payment method selection, a malformed-email string used specifically *because* it's invalid). `uniqueness_requirement = MAY_REUSE`.
* **Data whose uniqueness cannot be established** — a field CP-MVP2-04 cannot yet classify from available evidence (e.g. a hypothetical future field with no documented rule either way). `uniqueness_requirement = UNIQUENESS_UNKNOWN` — this must never silently default to either `MUST_BE_UNIQUE` or `MAY_REUSE`; it is its own governed state, reported honestly.

### 10.2 Deterministic mechanism

* For every field classified `MUST_BE_UNIQUE`, the deterministic validator checks the generated value against every other **currently accepted** dataset's same-named field in the active run/session registry (§5.2). A collision is `REJECTED` (not silently regenerated by asking the LLM again) with a reason naming the colliding `data_set_id`.
* This check is per-field, not per-dataset: two datasets may share every other field value and differ only in the `MUST_BE_UNIQUE` field, and that is correct, not a duplicate.
* The system **must never alter the requirement to obtain a passing dataset** — e.g. it must never quietly redefine `email` as `MAY_REUSE` because generating a fresh unique value is harder. This is a hard, non-negotiable rule mirroring the CP-MVP2-03 Golden Rule.

---

## 11. Data Generation Model — LLM vs. Deterministic Responsibility

Identical boundary discipline to CP-MVP2-03 (spec sec. 15/16), applied to data:

**LLM may:**
* Propose concrete field values consistent with the governed constraints it is given (e.g. "a syntactically valid but clearly synthetic email").
* Reason about which `data_category` a proposed dataset serves, subject to deterministic confirmation.
* Propose `boundary_classification` candidates, subject to deterministic confirmation that a boundary actually exists in evidence.
* Assist in recognizing that a request is `UNSUPPORTED` (e.g. "I have no evidence of a maximum length").

**LLM must NOT:**
* Decide final `validation_status`.
* Decide final `uniqueness_requirement` classification (it may propose; deterministic code confirms against the actual governed business-rule set — currently a fixed, small, explicit list, not an LLM judgment call).
* Invent a business rule, format, or boundary not present in evidence.
* Assign `testcase_id`, `requirement_ids`, `data_set_id`, or `source_attribution` — these are always assembled deterministically from the anchor testcase and RAG retrieval, exactly as CP-MVP2-03 already does for `testcase_id`/`requirement_ids`/`source_attribution` on `Testcase`.
* Determine coverage.

**Deterministic code must:**
* Validate schema (both `TestDataSet` and `TestDataField` level).
* Validate every extracted constraint (§8) against the proposed value.
* Classify/confirm `uniqueness_requirement` and enforce §10.
* Detect duplicates (§13).
* Calculate coverage (§14).
* Assign final `validation_status` (§9/§11 vocabulary).

---

## 12. Traceability

```text
DATASET
   ↓
TESTCASE
   ↓
REQUIREMENT
   ↓
RAG EVIDENCE
   ↓
APPROVED SRS
```

Concretely, an accepted `TestDataSet` must carry:

* `testcase_id` → resolves to a real `GovernedTestcase` with `governance_status == ACCEPTED` from CP-MVP2-03's own output for the same run.
* `requirement_ids` → identical to that testcase's `requirement_ids` (never independently altered).
* `source_attribution` → the same `{requirement_id, source_document, source_version, chunk_id}` shape CP-MVP2-03 already uses, sourced from the same retrieval.

An orphan dataset (no resolvable `testcase_id`, or a `testcase_id` whose testcase is not `ACCEPTED`) must not be accepted — mirroring CP-MVP2-03's orphan-testcase rule exactly.

---

## 13. Duplicate Detection

Two independent checks, mirroring CP-MVP2-03's `check_duplicate_testcase_ids` / `detect_duplicates` split:

1. **`data_set_id` collision** — exact-ID check across the batch. Any collision is a hard defect (deterministic ID assignment should make this structurally impossible, but the check exists regardless, per the same defense-in-depth precedent as CP-MVP2-03's coverage-filter).
2. **Content-level classification** — `UNIQUE`, `DUPLICATE`, `POSSIBLE_DUPLICATE`:
   * `DUPLICATE`: same `testcase_id` + same `data_category` + every field's value identical (normalized) to an already-`ACCEPTED` dataset.
   * `POSSIBLE_DUPLICATE`: same `testcase_id` + same `data_category`, but at least one field differs — flagged for review, **never auto-deleted**, per the same explicit safeguard CP-MVP2-03 applies to testcases (spec sec. 13).
   * This check is independent of, and does not substitute for, the `MUST_BE_UNIQUE` field-level uniqueness check in §10 — a dataset can be a legitimate `POSSIBLE_DUPLICATE` at the content-classification level while still passing every `MUST_BE_UNIQUE` field check (e.g. two registration datasets differing only in `first_name`, both with distinct unique emails).

---

## 14. Coverage

```text
Test-Data Coverage =
Accepted CP-MVP2-03 testcases having ≥1 ACCEPTED dataset
------------------------------------------------------------
Total applicable ACCEPTED CP-MVP2-03 testcases
× 100
```

Rules, mirroring CP-MVP2-03 sec. 9/10 exactly, applied one layer down:

* Only `ACCEPTED` datasets count toward coverage (plus `POSSIBLE_DUPLICATE`, for the same reason CP-MVP2-03 counts it — a flagged-but-not-proven-duplicate is still a legitimate dataset).
* `REJECTED`, `QUARANTINED`, `UNSUPPORTED_NEEDS_CLARIFICATION`, and exact `DUPLICATE` datasets never inflate coverage.
* A testcase that is itself not `ACCEPTED` in CP-MVP2-03 is not part of the applicable denominator at all — CP-MVP2-04 coverage is scoped strictly to testcases CP-MVP2-03 already governed as acceptable.
* The report must state total applicable testcases, covered testcases, uncovered testcases, and coverage percentage — identical shape to `calculate_coverage()`'s existing output.

---

## 15. Reproducibility and Data Lifecycle

Deliberately minimal for MVP2 — no full data-management subsystem is being specified here:

* **Identification:** every dataset has a deterministic `data_set_id` (e.g. `TD-<testcase_id>-<seq>`, mirroring `TC-<requirement_id>-<seq>`'s convention).
* **Reproducibility where practical:** `generation_metadata` records the generator identity and timestamp, exactly as CP-MVP2-03 does — this supports *auditing* what produced a value, not deterministic regeneration of the identical value (an LLM-backed generator is not expected to be byte-reproducible; this is disclosed, not hidden).
* **Versioning:** tied to the CP-MVP2-03 testcase and CP-MVP2-04 specification versions it was generated under (`generation_metadata` should record which spec version governed the run).
* **Isolation:** a dataset is scoped to one testcase; nothing in this specification shares mutable state across testcases except the uniqueness registry (§10.2), which is explicitly, narrowly scoped to enforcing `MUST_BE_UNIQUE` collisions, not general shared fixtures.
* **Safe reuse:** governed by `uniqueness_requirement`, per §10 — `MAY_REUSE` data may be reused across runs; `MUST_BE_UNIQUE` data must not be.
* **Retirement:** out of scope for v1.0 — no automatic expiry/retirement mechanism is specified. This is disclosed as a limitation (§17), not a gap silently designed around.
* **`DATA-OQ-01` (Approved SRS §13):** the shared-instance data-reset/isolation policy remains genuinely unknown. CP-MVP2-04 does not resolve it; it only ensures that any generation request whose validity *depends* on that unknown policy is reported `UNSUPPORTED`, never silently assumed.

---

## 16. Security and Sensitive Data

* Generated data must be **clearly synthetic** — this is already an explicit Approved SRS rule (§10: "Any future test data must use clearly synthetic values, not real personal information") and CP-MVP2-04 inherits it as a hard constraint, not a suggestion.
* No real personal information, no real payment credentials, no real customer data may be generated or referenced.
* No external secrets, credentials, API keys, or tokens may ever appear as generated "test data," regardless of what a testcase's field name suggests (e.g. a "password" field value is a synthetic string for UI-level testing, never a real credential for any system).
* Discovery-session-specific values (the CP-MVP2-01 discovery account, its order number, sampled product IDs) must never be reused as generated data or fixtures — this is already an explicit, approved rule (Approved SRS §10) that CP-MVP2-04 must not violate.

---

## 17. Downstream Interface (CP-MVP2-05 Contract)

CP-MVP2-05 (Playwright E2E Generation) must be able to consume:

```text
VALIDATED TESTCASE (CP-MVP2-03) + VALIDATED TEST DATA (CP-MVP2-04)
```

and generate automation **without reinterpreting business requirements**. Concretely, CP-MVP2-04's output contract for one testcase must therefore expose, per `ACCEPTED` `TestDataSet`:

* Which `testcase_id` it serves (direct join key back to CP-MVP2-03's output — no re-derivation needed).
* A flat, ordered `fields` list with `field_name`/`field_value` pairs ready to drive form input, with no remaining ambiguity about which field maps to which UI control (that mapping is CP-MVP2-05's job, not CP-MVP2-04's, but the field *names* must be stable and testcase-step-aligned so CP-MVP2-05 does not have to guess).
* `data_category`/`validity` so CP-MVP2-05 knows whether an automation step should *expect* success or a specific rejection message, without CP-MVP2-05 having to re-read the Approved SRS itself.
* `source_attribution` so evidence remains traceable all the way through final QE reporting (CP-MVP2-09).

This is a **machine-readable, deterministic contract** — no natural-language interpretation is required downstream, matching the same discipline CP-MVP2-03's `Testcase` schema already provides to CP-MVP2-04 itself.

### 17.1 High-level compatibility review, CP-MVP2-05 through CP-MVP2-09

Performed as a design-time check only — none of these checkpoints are implemented, specified, or modified by this document.

* **CP-MVP2-05 (Playwright E2E Generation):** consumes the contract in §17 directly. No redesign risk identified — the two-level schema (§6.1) gives CP-05 exactly the field-level granularity it needs to drive form automation.
* **CP-MVP2-06 (Real Browser Execution):** consumes CP-05's output, not CP-04's directly; CP-04 has no direct contract with CP-06. No risk identified, provided CP-05 does not need to reach back into CP-04 for anything the §17 contract omits — flagged as an assumption (§18), not confirmed by implementation.
* **CP-MVP2-07 (RCA + Replanning + Governance):** will need to trace a browser-execution failure back through CP-05/04/03 to the originating requirement. The traceability chain in §12 (`DATASET → TESTCASE → REQUIREMENT → RAG EVIDENCE → APPROVED SRS`) is designed to support exactly this kind of backward trace; no redesign risk identified, but this is unverified until CP-07 exists.
* **CP-MVP2-08 (JMeter Performance Testing):** performance test data needs (load volume, concurrency shape) are structurally different from functional test data and are **not** addressed by this specification — flagged explicitly as a future scope decision for Human + Di, not assumed to be covered by this schema.
* **CP-MVP2-09 (Unified Final QE Reporting):** will aggregate governance/coverage results across all checkpoints. CP-MVP2-04's `validation_status`/coverage output shapes are deliberately kept structurally parallel to CP-MVP2-03's (`by_status`, `coverage` dict shape) specifically to make later aggregation straightforward — a design choice made now to reduce CP-09 redesign risk later.

---

## 18. Failure Classification

| Category | Meaning |
|---|---|
| `REQUIREMENT_AMBIGUITY` | The Approved SRS/RAG evidence does not clearly resolve what data is needed (e.g. an unstated field format). |
| `INSUFFICIENT_EVIDENCE` | A needed constraint or dependency simply has no governed evidence at all. |
| `INVALID_GENERATED_DATA` | The LLM proposed a value that fails deterministic schema/constraint validation. |
| `DUPLICATE_DATA` | A `MUST_BE_UNIQUE` collision, or an exact content-level `DUPLICATE` classification. |
| `DEPENDENCY_ISSUE` | A dataset requires prior state (e.g. a saved address) that was not supplied. |
| `ENVIRONMENT_DATA_STORE_ISSUE` | A future implementation-level failure interacting with wherever accepted datasets are persisted/registered for the uniqueness check — not applicable to this specification document itself, defined here so implementation has a category to use. |
| `TOOL_LLM_FAILURE` | The LLM backend itself failed (mirroring CP-MVP2-03's `LLMUnavailableError`/`ClaudeProviderError` precedent) — a provider/infrastructure failure, not a data-quality failure. |
| `SCHEMA_FAILURE` | A `TestDataSet`/`TestDataField` failed structural schema validation. |
| `GOVERNANCE_FAILURE` | A dataset violated a governance rule not covered by the above (e.g. attempted to alter a requirement to pass). |

An implementation defect (e.g. a bug in the deterministic validator) must never be classified as `REQUIREMENT_AMBIGUITY` or any other requirement-facing category without actual evidence that the requirement itself is the source of the ambiguity — mirroring this task's own explicit instruction not to misclassify without evidence.

---

## 19. Acceptance Criteria

### 19.1 Functional
* Test data is generated for at least one `ACCEPTED` CP-MVP2-03 testcase per supported `data_category`.
* Generated datasets are structurally valid per §6.

### 19.2 Governance
* Only `ACCEPTED` CP-MVP2-03 testcases are eligible anchors.
* No fabricated constraint is presented as requirement-derived.
* No fabricated boundary value is presented without evidence (§7.4).
* `UNSUPPORTED / NEEDS CLARIFICATION` is produced, with a reason, whenever evidence is insufficient.

### 19.3 Traceability
* Every `ACCEPTED` dataset resolves the full chain in §12.
* Source attribution is present and matches real, retrieved evidence.

### 19.4 Uniqueness / Quality
* Schema validation is enforced deterministically.
* `MUST_BE_UNIQUE` collisions are detected and rejected, never silently regenerated into a passing state by weakening the rule.
* Duplicate/possible-duplicate classification (§13) is applied without aggressively discarding legitimate variations.

### 19.5 Coverage
* Coverage is calculated per §14, deterministically, excluding non-`ACCEPTED`/`POSSIBLE_DUPLICATE` datasets.

### 19.6 Regression
* All existing CP-MVP2-01/02/03 tests continue to pass. No CP-MVP2-04 implementation may break a previously frozen checkpoint.

All of the above must be **testable** by a future implementation task's automated test suite — this specification intentionally defines vocabulary and rules precisely enough to be asserted against, not merely described qualitatively.

---

## 20. Governance

* The Approved SRS remains the ultimate source of truth. CP-MVP2-04 does not amend it, and every constraint it enforces must be traceable to it (or to an explicitly attributed supplied deterministic constraint, §5.2).
* RAG (CP-MVP2-02, unchanged) provides governed evidence; CP-MVP2-04 never bypasses it.
* The LLM reasons and proposes; deterministic validators govern acceptance (§11).
* No silent requirement changes, no fabricated constraints, no fabricated test data presented as requirement-derived, no silent baseline changes.
* Conflicts (e.g. a requested dataset whose validity depends on an unresolved open question such as `DATA-OQ-01`) become governance findings (`UNSUPPORTED`), not silent assumptions.
* Human approval remains available and required before this specification itself is treated as approved/frozen, and before any implementation begins.
* Evidence must support every conclusion — this specification cites the actual Approved SRS sections/business rules it draws from throughout, rather than asserting rules in the abstract.

Governed status vocabulary for a CP-MVP2-04 run's overall health (mirroring the project's existing GREEN/YELLOW/RED convention referenced in README.md's Core Principles):

* **GREEN** — all applicable testcases covered, no `REJECTED`/unexplained `QUARANTINED` datasets.
* **YELLOW** — coverage incomplete and/or `UNSUPPORTED`/`QUARANTINED` findings exist, but no governance rule was violated.
* **RED** — a governance rule was violated (e.g. a `MUST_BE_UNIQUE` collision reached `ACCEPTED`, or a fabricated constraint was detected) — this must never occur in a correct implementation and is a stop-the-line signal if observed.

---

## 21. Versioning and Freeze

* Checkpoint: **CP-MVP2-04 — LLM Test Data Generation**
* Specification version: **1.0**
* **Status: DRAFT — pending Human + Di review.**
* This document does not become authoritative until an explicit approval decision is recorded (mirroring the Approved SRS's own §15 "Approval Decision" convention and the CP-MVP2-03 specification's frozen-on-approval precedent).
* Any change after approval must go through a formal, versioned Change Request (mirroring CP-MVP2-03 spec sec. 22) — no silent modification is permitted once frozen.

---

## 22. Limitations / Assumptions (disclosed at specification time)

1. **No field-length/format boundary is documented anywhere in the Approved SRS v1.0** beyond "required" vs. "optional" and the email-format/duplicate-email rules already cited. This specification deliberately does not invent such boundaries — implementation will report most `BOUNDARY`-category requests as `UNSUPPORTED` until/unless a future SRS revision documents them. This is a real, disclosed limitation of the source-of-truth, not of this specification.
2. **`DATA-OQ-01` (shared-instance data-reset/isolation policy) remains open.** This specification defines how CP-MVP2-04 must *behave* in the presence of that open question (§9, §15) but does not resolve the question itself — resolving it is out of this specification's authority.
3. **The exact enumerated value sets for Shipping Method and Country are not fixed by the Approved SRS.** Implementation must treat these as `UNSUPPORTED` for exact-value generation unless a future SRS revision or explicitly-attributed supplied constraint (§5.2) provides them.
4. **Reproducibility is audit-level, not byte-for-byte**, per §15 — an LLM-backed generator is not assumed to produce identical values on repeated runs.
5. This specification assumes CP-MVP2-03's existing `Testcase`/`GovernedTestcase` schema and governance vocabulary remain unchanged; if a future CP-MVP2-03 revision changes them, this specification would need a corresponding revision before implementation.
6. High-level CP-05–CP-09 compatibility (§17.1) is a design-time review only, not a verified integration — each downstream checkpoint's actual needs may reveal a gap only once it is itself specified/implemented.
