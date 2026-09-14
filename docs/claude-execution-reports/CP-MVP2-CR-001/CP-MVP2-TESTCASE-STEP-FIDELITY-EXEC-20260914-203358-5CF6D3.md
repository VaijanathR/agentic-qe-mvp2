# CP-MVP2 — Testcase-Step Fidelity + Multi-Dataset Vertical Slice: Execution Report

**Mode: governed implementation. No Human + Di final gate is declared here.**

## A. Governance Preflight

* Starting HEAD: `220c16fccf040468c40f1120f6dc937685afc9b6` — inspected, then re-verified current HEAD `5a68c92c45564d143b254927b2a79063bf42651d` (== `origin/main`) before any change.
* Inspected before implementation: frozen `docs/CP-MVP2-{05,06}-SPECIFICATION-v1.0.md`; current `automation/{schema,generate,validate,pipeline,evidence,persist}.py`; the entire `automation/multi_locator/` package and its committed `ML-PW-TC-REQ-ACO-03-01-01` artifact from the immediately preceding task; the real execution failure evidence from that task (`runs/cp_mvp2_06/MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02/`); the real persisted `TC-REQ-ACO-03-01` and `TD-TC-REQ-ACO-03-01-{01,02}` artifacts; `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`; and the real Demo Web Shop DOM evidence already established.
* **CR-002 status:** inspected, remains PROPOSED / NOT AUTHORIZED. Not self-authorized. This task performed no runtime-fallback work and did not need to — the new requirement (exact testcase-step fidelity) is a generation-time/traceability concern, not a CP-06 execution-behavior concern.
* No frozen CP-01–06 specification, freeze checkpoint, the Approved SRS, or any prior implementation file was modified — `git diff --stat` empty against every one of them, both before and after.

## B. Root-Cause Finding — the "CP-05 Realism Gap" Reclassified

The previous task's real execution FAIL (TIMEOUT at the first `FILL` step) was provisionally attributed to "a CP-05 realism gap" (missing add-to-cart/checkout-navigation steps). Direct inspection this task, as required by governance step 1/§7, found the actual root cause is **upstream of CP-05 entirely**:

`llm/client.py::StubLLMClient.propose_testcases()` (frozen CP-03's disclosed, deterministic, offline reasoning stand-in) always proposes, for **every** requirement, the identical two generic steps:

```text
"Perform the action described by the approved requirement."
"Observe the resulting system behavior."
```

Confirmed by direct inspection of all 9 real persisted testcases (`testcases/generated/*/v1.json`) — every one carries this exact, identical pair, verbatim, differing only in `expected_result` (which is the requirement's own text). **There is no requirement anywhere in the real, persisted testcase corpus that specifies "add product to cart" / "begin checkout" as a business step** — the stub was never designed to produce a realistic, specific business flow; it is explicitly documented (in `llm/client.py`'s own docstring) as a mechanics stand-in.

Per this task's own explicit rule (§7): *"If the testcase itself is insufficient to establish the required state: STOP → classify as TESTCASE / REQUIREMENT insufficiency rather than silently adding steps."* **This finding is classified exactly that way.** No step was invented in automation to compensate; the real, honest FAIL from the previous task (and the two re-confirmed FAILs in this task, §I) stands as correct, disclosed evidence of this testcase-content limitation — not a CP-05 or CP-06 defect, and not something this task attempted to silently patch.

## C. Implementation

**Files added:**
* `automation/multi_locator/step_mapping.py` — `TestcaseStepMapping`, `build_step_mapping()`, `validate_full_coverage()`, `validate_no_orphan_automation_steps()`, `validate_order_preserved()`.
* `tests/test_multi_locator_step_mapping.py` — 11 tests.

**Files modified (all within the previous task's own, not-yet-frozen additive package — never a frozen CP-01–06 file):**
* `automation/multi_locator/schema.py` — added one new, backward-compatible field, `testcase_step_mappings: List[Dict] = field(default_factory=list)`, to `MultiLocatorArtifact`.
* `automation/multi_locator/generate.py` — `build_multi_locator_artifact()` now accepts an optional `testcase_payload` and populates the new field via `build_step_mapping()`.
* `automation/multi_locator/validate.py` — governance now also checks stored step-mapping internal consistency (index-gap, coverage, order).

**Files deliberately untouched:** every frozen CP-01–06 file; `persistence/envelope.py`; `execution/*`; `testcases/*`; `testdata/*`; `llm/client.py`; `tests/test_multi_locator.py` (all 15 pre-existing tests pass unmodified).

## D. Business Step vs. Technical Step — How the Existing Architecture Was Reused

Per §3/§4's explicit instruction not to invent a parallel business-step model: this implementation reuses **only** identity mechanisms the frozen schemas already provide — `Testcase.test_steps`' own list index (the frozen schema has no separate step-ID field, so the index *is* the step identity) and `PlaywrightStep.step_order` (already the automation-step identity everywhere else in this project). No new ID scheme was introduced for either side.

## E. Selected Testcase / Test Data (unchanged from the prior slice — re-validated, still correct)

* **Testcase:** `TC-REQ-ACO-03-01` — `ACCEPTED`, `REQ-ACO-03` (`APPROVED — BASELINED v1.0`, SRS line 184).
* **Test data:** both real, distinct, `ACCEPTED` variants used — `TD-TC-REQ-ACO-03-01-01` (POSITIVE) and `TD-TC-REQ-ACO-03-01-02` (EXCEPTIONAL), explicitly disambiguated via `resolve_source_automation_payload()` (never a silent "latest" pick).

## F. Testcase Business Steps (verbatim, from the real persisted artifact)

```text
1. Perform the action described by the approved requirement.
2. Observe the resulting system behavior.
```

## G. Automation Business Steps (verbatim, from the real persisted `ML-PW-TC-REQ-ACO-03-01-01-D01` artifact)

```text
1  NAVIGATE
2-12 FILL (first_name, last_name, email, country, city, address1,
     zip_postal_code, phone_number, company, address2, fax_number)
13 CLICK (submit)
+ 1 BUSINESS_REQUIRED assertion (artifact-level, not a `steps` entry)
```

## H. Exact Testcase-Step ↔ Automation-Step Mapping (real, persisted, identical for both datasets)

| Testcase Step | Text | Mapped Automation Steps | Maps to Assertions |
|---|---|---|---|
| 0 | "Perform the action described by the approved requirement." | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 | No |
| 1 | "Observe the resulting system behavior." | (none — assertions have no `step_order` in the frozen schema) | **Yes** |

**Proof of fidelity (all three deterministic checks, real result):**
* `validate_full_coverage` → **PASS** (every testcase step index 0 and 1 has content or `maps_to_assertions=True`).
* `validate_no_orphan_automation_steps` → **PASS** (every automation action step 1–13 appears in some mapping; zero orphans).
* `validate_order_preserved` → **PASS** (step 0's automation orders `[1..13]` all precede step 1's assertion-only mapping).

No business step was omitted, invented, reordered, or replaced. The mapping is a disclosed **structural allocation** (§ step_mapping.py docstring), not a claim of semantic understanding — honestly scoped given the testcase's own generic content (§B).

## I. Multiple Test Data Sets — Proven, Not Merely Asserted

The same testcase (`TC-REQ-ACO-03-01`) was used with **two real, distinct, differently-categorized** datasets:

| Dataset | Category | Automation ID | Field order | Step mapping |
|---|---|---|---|---|
| `TD-TC-REQ-ACO-03-01-01` | POSITIVE | `ML-PW-TC-REQ-ACO-03-01-01-D01` | `[first_name, last_name, email, country, city, address1, zip_postal_code, phone_number, company, address2, fax_number]` | identical to D02 |
| `TD-TC-REQ-ACO-03-01-02` | EXCEPTIONAL | `ML-PW-TC-REQ-ACO-03-01-01-D02` | identical to D01 | identical to D01 |

`artifact_d1.testcase_step_mappings == artifact_d2.testcase_step_mappings` → **True** (real, asserted in `tests/test_multi_locator_step_mapping.py::test_same_testcase_two_datasets_identical_business_steps_distinct_ids`). Only `test_data_set_id` and `ml_automation_id` differ. **The `AUTOMATION_ID_COLLISION_ADVISORY` was avoided for these two new artifacts** — each dataset variant received its own distinct, non-colliding ID (`-D01`/`-D02`), rather than repeating the frozen `automation/generate.py` collision pattern.

## J. Locator Candidates and Evidence (unchanged from the prior task, re-confirmed)

Submit control: 2 real, independently-verified candidates (`#billing-buttons-container .new-address-next-step-button`, HIGH; `input[onclick="Billing.save()"]`, MEDIUM). Address fields: 1 candidate each (original frozen evidence). `automation_health = YELLOW` for both dataset variants (identical reason: the submit step needed this package's resolution; every other step's original locator was already evidenced).

## K. Automation Identity

* `ML-PW-TC-REQ-ACO-03-01-01-D01` and `-D02` — both new, unique, non-colliding, version-1-only.
* The prior task's un-suffixed `ML-PW-TC-REQ-ACO-03-01-01` (from commit `b0dec2e`) remains, unmodified, as its own historical artifact — **not deleted, not overwritten** — now superseded in practice by `-D01` (which adds the step-mapping layer), but no historical evidence was rewritten.

## L. Real Browser Execution Result (both datasets)

| Dataset | Browser | Result | Failure |
|---|---|---|---|
| D01 | `chromium/151.0.7922.34` | `FAIL` | `ENVIRONMENT_ISSUE` — TIMEOUT on `#BillingNewAddress_FirstName` |
| D02 | `chromium/151.0.7922.34` | `FAIL` | `ENVIRONMENT_ISSUE` — TIMEOUT on `#BillingNewAddress_FirstName` (identical root cause) |

Both real, both honest, neither fabricated. The identical failure mode across both datasets is itself further proof of §I's business-step independence: the failure occurs before any dataset-specific value is ever used (the browser never reaches a fillable page), confirming the FAIL is about page state, not data content.

## M. Execution Evidence Locations

* `runs/cp_mvp2_06/REALISM-SLICE-EXEC-D01/{execution.log,step_2_failure.png}` and `runs/cp_mvp2_06/REALISM-SLICE-EXEC-D02/{execution.log,step_2_failure.png}` (legacy path, real files, verified on disk).
* `runs/2026/09/14/REALISM-SLICE-EXEC-D01/` and `.../REALISM-SLICE-EXEC-D02/` (new additive timestamped path, real files, verified on disk).

## N. Traceability

`Automation → Testcase → Requirement → Test Data` resolves deterministically for both variants: `ExecutionResult.testcase_id = "TC-REQ-ACO-03-01"`, `requirement_ids = ["REQ-ACO-03"]` (SRS line 184), `test_data_set_id` = the correct, explicitly-disambiguated dataset per variant.

## O. Tests

* Focused: `tests/test_multi_locator_step_mapping.py` (11, new) + `tests/test_multi_locator.py` (15, pre-existing, unmodified) → **26 passed.**
* Full regression: **300 passed, 0 failed** (289 pre-existing + 11 new).

## P. Fresh-Process Verification

Two independent Python processes (this session) and, separately, a genuinely fresh `git clone` of `origin/main` (outside the working tree, deleted after use) each loaded `ML-PW-TC-REQ-ACO-03-01-01-D01` from disk (`persistence.envelope`-style direct read, no regeneration) and produced the **identical** SHA-256 (`7538fb3ea25d8aafd966e3feaf28fafa9ee6bf9a64f9fe9c0a58462dd2159c25`). The fresh clone's `TC-REQ-ACO-03-01` load also matched.

## Q. CR-002 Status

Unchanged: **PROPOSED, NOT AUTHORIZED.** No runtime-fallback code was added or needed in this task.

## R. Advisories

1. The testcase-content limitation in §B is systemic across the entire real corpus (all 9 testcases share the identical generic 2-step pattern) — a future, richer vertical slice would require either real live-LLM testcase generation (a separate, explicitly-scoped task) or a deliberately-crafted, disclosed test fixture; neither was done here, per this task's own prohibition on inventing business steps.
2. `AUTOMATION_ID_COLLISION_ADVISORY` remains open at the source (frozen `automation/generate.py`); this task avoided it for its own two new artifacts via an explicit `-D01`/`-D02` suffix convention, but did not fix the underlying frozen ID scheme.
3. `reports/execution_summaries/BATCH2-TEST(2)/` test-pollution and the original 9 `automation/generated/PW-*` artifacts remain untracked, carried forward unchanged from prior tasks, still pending a Human/Di decision.
4. The step-mapping heuristic (§step_mapping.py) is validated against the real corpus's simple 2-step case and a synthetic richer-case unit test (`test_richer_multi_step_testcase_splits_action_steps_in_order`); it has not been exercised against a real, richer testcase, because none currently exists in the persisted corpus.

## S. Blockers

None.
