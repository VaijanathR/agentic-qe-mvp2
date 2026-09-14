# CP-MVP2 — Multi-Locator Candidate Resolution + Real Vertical Slice: Execution Report

**Mode: governed implementation. No Human + Di final gate is declared here.**

## A. Governance Preflight

* Starting HEAD: `220c16fccf040468c40f1120f6dc937685afc9b6` (== `origin/main`).
* Inspected before implementation: frozen `docs/CP-MVP2-{03,04,05,06}-SPECIFICATION-v1.0.md`, current `automation/{schema,generate,validate,pipeline,evidence,persist,components}.py`, current `execution/{schema,validate,evidence,engine,pipeline,persist,summary,persisted_lifecycle}.py`, current `persistence/envelope.py`, the real, committed `automation/generated/*` corpus (from the immediately preceding task's commit), the `AUTOMATION_ID_COLLISION_ADVISORY`, and the real Demo Web Shop DOM evidence (`knowledge/historical/discovery_evidence/captures/checkout_00.html`).
* **Conflict found and resolved per governance (not silently worked around):** the Human's requested *runtime* fallback-on-failure behavior directly conflicts with the frozen `docs/CP-MVP2-06-SPECIFICATION-v1.0.md` sec. 14 ("automatic retry is explicitly PROHIBITED ... prohibited outright") and sec. 15 ("self-healing ... belongs to a later, explicitly authorized checkpoint ... CP-MVP2-07"). Per this task's own instruction ("if a frozen specification or contract must change: STOP implementation, produce a formal CR"), this half of the request was **not implemented**. A proposal was produced instead: `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md` (status: PROPOSED, NOT AUTHORIZED).
* The **generation-time / persistence-time** half of the request (a deterministic, evidence-backed, priority-ordered candidate set per load-bearing step) does not conflict with any frozen rule and was implemented.
* No frozen CP-01–06 specification, freeze checkpoint, the Approved SRS, or any prior Batch-1/2 implementation file was modified — confirmed by `git diff --stat` against every one of them, both before and after implementation (empty).

## B. Implementation

**Files added** (all new, none modify an existing file):
* `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`
* `automation/multi_locator/__init__.py`, `schema.py`, `evidence.py`, `generate.py`, `validate.py`, `persist.py`, `pipeline.py`, `bridge.py`
* `tests/test_multi_locator.py`
* `automation/generated/ML-PW-TC-REQ-ACO-03-01-01/{latest,v1}.json` (the real, executable, resolved artifact)
* `automation/multi_locator/generated/ML-PW-TC-REQ-ACO-03-01-01/{latest,v1}.json` (the real multi-locator candidate artifact)
* `ClaudeInstructions/CP-MVP2-CR001_instructions/Inst-15092026-0132_CR Automation FIxes.md` (Human-authored note for this task, committed verbatim per the established convention from the immediately preceding task)

**Files modified:** none.

**Files deliberately untouched:** `automation/{schema,generate,validate,pipeline,evidence,persist,components}.py`, `execution/{schema,validate,evidence,engine,pipeline,persist,summary,persisted_lifecycle}.py`, `persistence/envelope.py`, `testcases/`, `testdata/`, `llm/client.py`, the Approved SRS, every CP-01–06 specification/freeze checkpoint.

## C. Design: how the new capability fits the frozen contracts

* **Schema:** no new field was added to the frozen `automation.schema.LocatorSpec`/`PlaywrightStep`. A wholly separate, additive dataclass family (`LocatorCandidate`, `StepLocatorCandidateSet`, `MultiLocatorArtifact`) lives in a new package and references the frozen `PlaywrightArtifact` only by ID (`source_automation_id`), never by mutation.
* **Priority order:** `TEST_ID(1) > ROLE(2) > LABEL(3) > STABLE_ATTRIBUTE(4)`, fixed and deterministic, matching the Human's own stated preference — no LLM involvement anywhere in this package.
* **Confidence:** `HIGH`/`MEDIUM`/`LOW`, assigned deterministically per candidate at generation time (the container-scoped selector is `HIGH`; the attribute-based alternate is `MEDIUM`, since it depends on the `onclick` handler name remaining stable — a judgment recorded, not computed by any formula, and disclosed as such).
* **Automation health:** `GREEN`/`YELLOW`/`RED`, computed deterministically from whether every step's original frozen locator was already `EVIDENCED` (`GREEN`), some step needed this package's new resolution (`YELLOW`), or some step has zero candidates even after this package's search (`RED`). This vocabulary is recorded only in this new package's own artifacts — it is never written into any frozen `execution.schema.ExecutionResult` field.
* **Execution:** `automation/multi_locator/bridge.py::build_executable_artifact()` selects only the priority-1 candidate per step and constructs a real, standard `automation.schema.GovernedPlaywrightArtifact` — the object the frozen, unmodified `execution.pipeline.run_cp_mvp2_06()` already knows how to execute, unchanged. No runtime candidate list, no fallback attempt, no retry.

## D. Automation ID Collision — investigated and actively defended against, not just noted

Before generating anything, `automation/multi_locator/generate.py::resolve_source_automation_payload()` was built specifically to answer this task's own §6 question ("is the current identity model sufficient?"). Answer, demonstrated live: **no** — `PW-TC-REQ-ACO-03-01-01` itself has 2 persisted versions with different `test_data_set_id` values (`TD-TC-REQ-ACO-03-01-01` POSITIVE, `TD-TC-REQ-ACO-03-01-02` EXCEPTIONAL). An early, uncorrected draft of this task's own vertical-slice script called `load_latest()` directly and silently got version 2 (EXCEPTIONAL) — caught during test-writing (`test_bridge_produces_a_standard_artifact_with_only_primary_locators` failed on a hardcoded assumption), root-caused, and corrected: `resolve_source_automation_payload()` now reuses Batch 2's own `execution.persisted_lifecycle.discover_distinct_test_data_variants()` collision detector and **raises** if the caller does not explicitly supply `expected_test_data_set_id` — it never silently picks a "latest" winner. The corrected vertical slice explicitly requested `TD-TC-REQ-ACO-03-01-01` (POSITIVE, matching the anchor testcase's own `scenario_type`). No new automation-identity collision was introduced: `ML-PW-TC-REQ-ACO-03-01-01` is a brand-new, unique `automation_id`, created once, version 1 only.

## E. First Vertical Slice — Selection and Rationale

**Selected: `TC-REQ-ACO-03-01` + `TD-TC-REQ-ACO-03-01-01` (REQ-ACO-03).**

Why: REQ-ACO-03 is an APPROVED, BASELINED requirement (`requirements/MVP2_SRS_v1.0_APPROVED.md` line 184); `TC-REQ-ACO-03-01` is `ACCEPTED`; `TD-TC-REQ-ACO-03-01-01` is `ACCEPTED`; real Demo Web Shop DOM evidence exists for every address field (`knowledge/historical/discovery_evidence/captures/checkout_00.html`); and it is the **exact, real, previously-documented case** of a governance-blocking locator ambiguity (the shared `.new-address-next-step-button` class) — making it the most meaningful, non-trivial demonstration of the new capability, rather than a case chosen because it was already easy.

## F. Real Chain Demonstrated

```text
Approved Requirement (REQ-ACO-03, SRS line 184)
        ↓
Persisted Testcase (TC-REQ-ACO-03-01, real file, git-committed)
        ↓
Persisted Test Data (TD-TC-REQ-ACO-03-01-01, real file, git-committed, explicitly disambiguated)
        ↓
Multi-Locator Resolution (2 real, independently-verified candidates for the submit control)
        ↓
Persisted Multi-Locator Artifact (ML-PW-TC-REQ-ACO-03-01-01 under automation/multi_locator/generated/, real file, git-committed)
        ↓
Bridged Executable Artifact (ML-PW-TC-REQ-ACO-03-01-01 under automation/generated/, real file, git-committed, governance ACCEPTED)
        ↓
Real Chromium Browser (151.0.7922.34, real 34.0s session)
        ↓
Execution Evidence (real screenshot + log at runs/cp_mvp2_06/..., real JSON at runs/2026/09/14/...)
        ↓
Execution Result (FAIL / ENVIRONMENT_ISSUE — genuine, not fabricated)
        ↓
Requirement/Testcase Traceability (ExecutionResult.testcase_id=TC-REQ-ACO-03-01, requirement_ids=[REQ-ACO-03])
```

## G. Locator Candidates and Their Evidence

| Step | Field | Priority | Strategy | Locator | Confidence | Evidence |
|---|---|---|---|---|---|---|
| 2–12 | first_name…fax_number | 4 | STABLE_ATTRIBUTE | `#BillingNewAddress_*` | HIGH | `checkout_00.html` — unchanged from the frozen CP-05 lookup (already evidenced, `original_locator_was_evidenced=True`) |
| 13 | (submit) | 4 | STABLE_ATTRIBUTE | `#billing-buttons-container .new-address-next-step-button` | HIGH | `checkout_00.html` — real parent-container-scoped selector, verified unique via regex against the live file at call time |
| 13 | (submit, fallback candidate — NOT executed) | 5 | STABLE_ATTRIBUTE | `input[onclick="Billing.save()"]` | MEDIUM | `checkout_00.html` — real, independently-verified attribute selector; persisted as metadata only, never attempted at runtime (no CR-002 authorization) |

`automation_health = YELLOW` (step 13 required this package's new resolution; every other step's original frozen locator was already evidenced).

## H. Automation ID / Identity Result

* Source (frozen CP-05): `PW-TC-REQ-ACO-03-01-01` — unchanged, un-mutated, still `UNSUPPORTED_NEEDS_CLARIFICATION` in its own right.
* New multi-locator artifact: `ML-PW-TC-REQ-ACO-03-01-01` (under `automation/multi_locator/generated/`) — `ACCEPTED`.
* New executable artifact: `ML-PW-TC-REQ-ACO-03-01-01` (under `automation/generated/`, standard frozen schema) — `ACCEPTED`.
* No duplicate/ambiguous identity was created; both new artifacts use a single, distinct ID, created once (version 1 only), with `source_automation_id` preserved for full backward traceability to the untouched frozen artifact.

## I. Real Browser Execution Result

* Execution ID: `MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02`.
* Browser: `chromium/151.0.7922.34` (real).
* Start/end: `2026-09-14T20:12:01.120111+00:00` → `2026-09-14T20:12:35.124194+00:00` (real, 34.004s).
* Step 1 (NAVIGATE): `PASS` — real navigation to `https://demowebshop.tricentis.com/`.
* Step 2 (FILL `#BillingNewAddress_FirstName`): `FAIL` — real `TIMEOUT: Page.fill: Timeout 30000ms exceeded`.
* Steps 3–13: `NOT_EXECUTED` (load-bearing failure upstream — matches frozen CP-06 sec. 14's "stop at first load-bearing failure" behavior, unmodified).
* **Overall: `FAIL` / `ENVIRONMENT_ISSUE`.**
* **Root cause (disclosed, not fabricated, not fixed by this task):** the CP-05-generated step sequence's `NAVIGATE` step targets only `sut_base_url` (the site's home page) — there are no "add to cart, begin checkout" steps establishing the real precondition ("user is on the Billing/Shipping address step"), because the CP-05 stub generator never produced them. The multi-locator resolution work in this task correctly resolved the *locator* ambiguity (proven: the artifact reached `ACCEPTED` and real browser execution, which it could not do before); the FAIL is a **separate, pre-existing, honestly-disclosed limitation** of the generated step sequence's realism, not a defect introduced by this task. No PASS was fabricated to hide this.

## J. Execution Evidence Locations

* Legacy (frozen) path: `runs/cp_mvp2_06/MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02/execution.log`, `.../step_2_failure.png` (real, 143,650-byte screenshot, verified on disk).
* New additive path: `runs/2026/09/14/MULTI-LOCATOR-VERTICAL-SLICE-EXEC-02/{final_result,step_results,assertions}.json` (real, verified on disk).
* Both coexist; neither was overwritten or deleted; consistent with the backward-compatibility design already established in the prior Batch-2 task.

## K. Traceability

* **Testcase → Requirement:** `TC-REQ-ACO-03-01.requirement_ids = ["REQ-ACO-03"]`; `REQ-ACO-03` confirmed present, `APPROVED — BASELINED v1.0`, in `requirements/MVP2_SRS_v1.0_APPROVED.md` line 184.
* **Automation → Testcase:** `ExecutionResult.testcase_id = "TC-REQ-ACO-03-01"` (real, from the real execution above).
* **Automation → Test Data:** `ExecutionResult.test_data_set_id = "TD-TC-REQ-ACO-03-01-01"` (real, explicitly disambiguated, not the collision's other variant).
* **Automation → Source (frozen) Automation:** `ML-PW-TC-REQ-ACO-03-01-01`'s `generation_metadata.source_automation_id = "PW-TC-REQ-ACO-03-01-01"`.

## L. Tests

* Focused: `tests/test_multi_locator.py` — 15 tests (schema/evidence/generate/validate/persist/bridge/mocked-integration), all passing.
* Full regression: `.venv/Scripts/python.exe -m pytest -q` → **289 passed, 0 failed** (274 pre-existing + 15 new).
* No frozen or Batch-1/2 test file was modified.

## M. Fresh-Process Verification

Two genuinely separate Python processes (PIDs `19872` and `15416`) each loaded `ML-PW-TC-REQ-ACO-03-01-01` from `automation/generated/` strictly from disk (`persistence.envelope.load_latest`, no regeneration) and computed the identical SHA-256 hash (`a65d6bbc7626fb249650c41f3cda06cbf2d8e3cc2050a8eed5f0cdf4e0e6c983`) — confirming genuine, stable, repository-grade persistence. The corresponding multi-locator candidate artifact (`automation/multi_locator/generated/`) was verified the same way.

## N. Known Advisories

1. **`AUTOMATION_ID_COLLISION_ADVISORY`** — re-confirmed, and this time actively worked around (not silently), via `resolve_source_automation_payload()`'s explicit-disambiguation requirement. Still not fixed at the source (frozen `automation/generate.py`); still a future CP-05-scoped CR candidate.
2. **CP-05 step-sequence realism gap (new observation, this task):** the stub-generated `NAVIGATE` step never encodes "reach the actual page this scenario needs" (e.g., add-to-cart + begin-checkout for REQ-ACO-03) — a real, disclosed limitation of the existing CP-05 generation logic's realism, surfaced concretely by this task's real execution attempt, not previously exercised end-to-end. Not fixed here (would require modifying frozen `automation/generate.py`/CP-05 generation logic).
3. **CR-002 (runtime locator fallback) remains unauthorized** — no runtime fallback-retry code exists anywhere in this repository.
4. `reports/execution_summaries/BATCH2-TEST(2)/` test-pollution (carried forward from the prior task) remains untracked, not fixed, not committed.
5. `automation/generated/PW-*` (the original 9 real, frozen-governed artifacts) remain untracked pending the still-open Human/Di decision from the prior task; only the NEW `ML-PW-TC-REQ-ACO-03-01-01` artifacts were committed in this task, per this task's own explicit persistence requirement (§9).

## O. Blockers

None. The one genuine frozen-specification conflict found (runtime fallback/self-healing) was handled correctly per governance: STOP on that specific sub-capability, CR proposal produced, everything else proceeded.
