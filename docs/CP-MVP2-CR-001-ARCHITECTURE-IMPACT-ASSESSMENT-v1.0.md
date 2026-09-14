# CP-MVP2-CR-001 — Architecture Impact Assessment

Companion to `docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md`. **Status:
BATCH 1 IMPLEMENTATION AUTHORIZED AND COMPLETE — AWAITING DI FINAL GATE.**
RBTP corrected to Risk-Based Test Prioritization (see companion §4).
Di's independent engineering review of the Batch 1 implementation: PASS
with advisories. **Di has NOT yet issued the final CR-001 governance
gate** — see the governance reconciliation report under
`docs/claude-execution-reports/CP-MVP2-CR-001/`. **Batch 2** (persisted-
lifecycle integration with CP-06, commits `53a4f38`/`b33f5c9`) is
implemented and evidenced, **awaiting independent Human + Di final
gate** — not self-declared approved or closed.

---

## B. Architecture — Current vs. Proposed

### B.1 Current (verified by direct code inspection)

```text
SRS  →  RAG  →  TC (in-memory)  →  DATA (in-memory)  →  PLAYWRIGHT (in-memory)  →  EXECUTION (persisted)
```

Only the Knowledge Base/RAG corpus (CP-02) and CP-06's own execution
evidence are durable. Every testcase, dataset, and automation object is
discarded the moment the process that generated it exits, unless a human
happens to transcribe it into a report (as occurred once, for
`TC-REQ-REG-01-01`).

### B.2 Proposed

```text
SRS
 ↓
TC ───────────────→ TRACEABILITY (REQ↔TC)
 ↓  (persisted)
RBTP  (Risk-Based Test Prioritization — corrected definition, CR §4)
 ↓  (persisted)          → TRACEABILITY (REQ↔TC↔RBTP)
DEPENDENCY MATRIX
 ↓  (persisted)
DATA ─────────────→ TRACEABILITY (TC↔DATA)
 ↓  (persisted)
PLAYWRIGHT ───────→ TRACEABILITY (REQ↔TC↔DATA↔AUTOMATION↔COMPONENT)
 ↓  (persisted)
REUSABLE COMPONENT CANDIDATES  (identification only — see §C.8; no page-object/utility source-file scaffolding was built)
 ↓  (persisted)
EXECUTION
 ↓  (persisted, timestamped)
LOGS
 ↓  (persisted)
SUMMARY
 ↓  (persisted)
EVIDENCE / RCA / GOVERNANCE  →  CP-MVP2-07 (not started; out of this CR's scope)
```

Every stage in B.1 is preserved unchanged (same LLM boundary, same
deterministic-governance boundary, same "LLM proposes, code decides"
principle) — B.2 only adds a persistence + traceability layer *around*
each existing stage. No existing reasoning/governance logic is proposed to
be replaced.

---

## C. Artifact Contract

**All contracts below are implemented (Batch 1, commit `415038c`).**
Each "Persistence location" now names the actual, real path produced by
the implementation — an artifact's own directory containing an
immutable `v<N>.json` per version plus a mutable `latest.json` pointer
(`persistence/envelope.py`), not a single flat `.json` file as this
document's earlier draft anticipated.

### C.1 Persisted Testcase Artifact

| Field | Value |
|---|---|
| Purpose | First-class, independently-readable record of one accepted CP-03 testcase |
| Schema | Wraps existing `testcases.schema.GovernedTestcase.to_dict()` unchanged; adds `artifact_version`, `baseline_reference` |
| ID | `testcase_id` (existing, deterministic: `TC-<requirement_id>-<seq>`) |
| Version | New field: schema/persistence-format version, independent of testcase content |
| Owner | CP-MVP2-03 |
| Inputs | A `GovernedTestcase` already produced by the existing, unmodified `testcases.validate.govern_batch()` |
| Outputs | One artifact file per accepted testcase |
| Traceability | `requirement_ids`, `source_attribution` (already present, unchanged) |
| Consumer | Human review; CP-MVP2-04; CP-MVP2-05; CP-MVP2-07 reporting |
| Persistence location (actual) | `testcases/generated/<testcase_id>/v<N>.json` + `latest.json` |

### C.2 Requirement ↔ Testcase Traceability Artifact

| Field | Value |
|---|---|
| Purpose | Deterministic coverage/traceability matrix: covered/uncovered requirements, 1:many mappings, orphans, duplicates |
| Schema | New — derived entirely from existing `calculate_coverage()`/`detect_duplicates()` output, restructured for persistence |
| ID | One artifact per generation batch, keyed by requirement-set + timestamp |
| Version | Schema version + reference to the CP-03 run that produced it |
| Owner | CP-MVP2-03 |
| Inputs | The full `List[GovernedTestcase]` from one `run_cp_mvp2_03()` call |
| Outputs | One traceability artifact |
| Traceability | REQ → TC(s); TC → REQ |
| Consumer | Human audit; RBTP generation; CP-MVP2-09 reporting |
| Persistence location (actual) | `traceability/req_to_testcase/<batch_id>/v<N>.json` + `latest.json` |

### C.3 RBTP Artifact — Risk-Based Test Prioritization (corrected definition, CR §4)

| Field | Value |
|---|---|
| Purpose | Per-testcase, explainable prioritization record answering "which testcases should be executed first, and why" — evidence-backed risk factors, deterministic priority, execution recommendation, rationale |
| Schema | `rbtp/schema.py::RBTPRecord`/`GovernedRBTPRecord` (this batch) |
| ID | `RBTP-<testcase_id>` |
| Version | Persistence-format version (via `persistence.envelope`) |
| Owner | A new sub-stage, run immediately after Requirement↔Testcase Traceability and before the Dependency/Reusability Matrix |
| Inputs | Persisted Testcase Artifacts (C.1) + Requirement↔Testcase Traceability (C.2) + real KB evidence (journey membership, requirement text) |
| Outputs | One RBTP artifact per accepted testcase |
| Traceability | REQ ↔ TC ↔ RBTP |
| Consumer | Human review; execution planning; CP-MVP2-09 reporting |
| Persistence location (actual) | `rbtp/generated/<rbtp_id>/v<N>.json` + `latest.json` |

### C.4 Dependency / Reusability Matrix

| Field | Value |
|---|---|
| Purpose | Identify shared preconditions, data reuse/uniqueness constraints, auth/session dependencies, reusable component candidates, before automation is generated |
| Schema | `dependencies/schema.py::DependencyMatrix`/`DependencyEdge` (this batch) |
| ID | `matrix_id` (one per batch) |
| Version | Persistence-format version (via `persistence.envelope`) |
| Owner | `dependencies/pipeline.py::run_dependency_matrix`, a deterministic, LLM-free analysis stage run after RBTP, before CP-04/CP-05 consumption |
| Inputs | Persisted Testcase Artifacts (C.1) only, as actually implemented — edges are computed from each testcase's own `journey_id`/`preconditions`/`requirement_ids`/CP-03 duplicate-detection reasons; Test Data Artifacts (C.6) and RBTP (C.3) are NOT inputs (RBTP is a parallel, independent prioritization concern) |
| Outputs | One dependency matrix per batch: pairwise edges (`SHARED_JOURNEY`/`SHARED_PRECONDITION`/`SHARED_REQUIREMENT`/`POSSIBLE_DUPLICATE_TESTING`) plus `reusable_component_candidates` requiring literal repetition across 2+ testcases |
| Traceability | TC ↔ shared setup/requirement/possible-duplicate relationships |
| Consumer | CP-MVP2-05 (automation generation), human review |
| Persistence location (actual) | `dependencies/generated/<matrix_id>/v<N>.json` + `latest.json` |

### C.5 Persisted Test Data Artifact

| Field | Value |
|---|---|
| Purpose | First-class record of one accepted CP-04 dataset |
| Schema | Wraps existing `testdata.schema.GovernedTestDataSet.to_dict()` unchanged; adds `artifact_version`, `baseline_reference` |
| ID | `data_set_id` (existing) |
| Version | Persistence-format version |
| Owner | CP-MVP2-04 |
| Inputs | A `GovernedTestDataSet` from the existing, unmodified `testdata.validate.govern_batch()` |
| Outputs | One artifact per accepted dataset |
| Traceability | `testcase_id`, `requirement_ids` (already present) |
| Consumer | Human review; CP-MVP2-05; CP-MVP2-06 |
| Persistence location (actual) | `testdata/generated/<data_set_id>/v<N>.json` + `latest.json` |

### C.6 Testcase ↔ Test Data Traceability Artifact

| Field | Value |
|---|---|
| Purpose | Answer "which data does this testcase need" / "which testcases use this data"; detect missing/orphan/incompatible/duplicate data |
| Schema | New — derived from existing CP-04 governance/coverage output |
| ID | One per CP-04 batch |
| Version | Schema version + CP-04 run reference |
| Owner | CP-MVP2-04 |
| Inputs | Persisted Test Data Artifacts (C.5), Persisted Testcase Artifacts (C.1) |
| Outputs | One traceability artifact |
| Traceability | TC ↔ Data |
| Consumer | Human audit; CP-MVP2-05; CP-MVP2-09 |
| Persistence location (actual) | `traceability/testcase_to_testdata/<batch_id>/v<N>.json` + `latest.json` |

### C.7 Persisted Automation Artifact

| Field | Value |
|---|---|
| Purpose | First-class record of one CP-05 Playwright artifact |
| Schema | Wraps existing `automation.schema.GovernedPlaywrightArtifact.to_dict()` unchanged; adds `artifact_version`, `baseline_reference` |
| ID | `automation_id` (existing) — **known limitation:** `f"PW-{testcase_id}-01"` does not incorporate the paired `test_data_set_id`, so a testcase with N eligible datasets produces N distinct artifacts sharing one `automation_id` (`AUTOMATION_ID_COLLISION_ADVISORY`, discovered by this batch; see the Batch 1 implementation report). Persistence handled this safely (every distinct artifact retained as its own immutable version, no data lost) but `latest.json` for such an ID does not mean "the current version of one logical automation." |
| Version | Persistence-format version |
| Owner | CP-MVP2-05 |
| Inputs | A `GovernedPlaywrightArtifact` from the existing, unmodified `automation.validate.govern_batch()` |
| Outputs | One artifact per generated automation |
| Traceability | `testcase_id`, `requirement_ids`, `test_data_set_id` (already present) |
| Consumer | Human review; CP-MVP2-06 |
| Persistence location (actual) | `automation/generated/<automation_id>/v<N>.json` + `latest.json` |

### C.8 Reusable Component Candidate (implemented as identification only — not a persisted artifact family, not source-file extraction)

**Corrected scope.** Batch 1 implements real, evidence-backed **candidate
identification** (`automation/components.py::identify_reusable_locator_candidates`),
not the page-object/utility/fixture source-file scaffolding this row's
earlier draft anticipated. No `automation/components/`, `automation/pages/`,
or `automation/utils/` source directory was created.

| Field | Value |
|---|---|
| Purpose | Report where 2+ **distinct** automation artifacts literally share the same locator (`strategy`+`value`) — real, evidence-backed reuse potential, never a fabricated or speculative one |
| Schema | Plain dict: `{strategy, value, used_by_automation_ids}` — no dataclass, no independent persistence; folded into C.9's `automation_to_components` field |
| ID | None — not independently ID-addressed or versioned |
| Owner | `automation/components.py` (Batch 1) |
| Inputs | Real, persisted CP-05 automation artifacts (any governance status — candidates are computed over ALL generated artifacts, not only `ACCEPTED` ones, per §12's "identify reuse wherever real repetition exists") |
| Outputs | A list of candidates (empty when fewer than 2 artifacts share a locator — an honest empty result, not an error) |
| Traceability | Folded into Automation Traceability (C.9)'s `automation_to_components` map |
| Consumer | Human review; a future task deciding whether to actually extract a page object/helper |
| Persistence location | Not independently persisted; see C.9 |

### C.9 Automation Traceability Artifact

| Field | Value |
|---|---|
| Purpose | Persist REQ→TC→Data→Automation→Component chain; answer "which automation implements this testcase," "which requirements does this automation cover," "which components does it use" |
| Schema | New |
| ID | One per CP-05 batch |
| Version | Schema version + CP-05 run reference |
| Owner | CP-MVP2-05 |
| Inputs | C.1, C.5, C.7, C.8 |
| Outputs | One traceability artifact |
| Traceability | Full REQ→TC→Data→Automation→Component chain |
| Consumer | Human audit; CP-MVP2-06; CP-MVP2-09 |
| Persistence location (actual) | `traceability/automation/<batch_id>/v<N>.json` + `latest.json` |

### C.10 Timestamped Execution Log

| Field | Value |
|---|---|
| Purpose | Real, per-execution evidence: step results, assertion results, errors, diagnostics, evidence file locations |
| Schema | Extends existing `execution.schema.ExecutionResult` (unchanged) with an explicit runtime-timestamp-derived path |
| ID | `execution_id` (existing) |
| Version | Execution-schema version (already exists) |
| Owner | CP-MVP2-06 |
| Inputs | A real `ExecutionResult` from the existing, unmodified `execution.pipeline.run_cp_mvp2_06()` |
| Outputs | `final_result.json`, `step_results.json`, `assertions.json` written by the NEW additive path (`execution/persist.py`); `execution.log`/screenshots continue to be written, unchanged, by the frozen `execution/evidence.py::EvidenceManager` under the original `runs/cp_mvp2_06/<execution_id>/` path — the two paths coexist, neither replaces the other |
| Traceability | `automation_id`, `testcase_id`, `requirement_ids`, `test_data_set_id` (already present) |
| Consumer | Human audit; Execution Summary (C.11); CP-MVP2-07 RCA |
| Persistence location (actual) | **Additive, resolved:** `runs/<YYYY>/<MM>/<DD>/<execution_id>/...` was added as a SEPARATE, parallel path. The frozen `runs/cp_mvp2_06/<execution_id>/...` convention was left completely untouched (`git diff` on `execution/evidence.py` empty) — no approval-requiring breaking change was made. |

### C.11 Execution Summary

| Field | Value |
|---|---|
| Purpose | Batch-level rollup distinguishing requirement coverage, testcase coverage, execution coverage, and pass/fail outcome |
| Schema | New |
| ID | One per execution batch |
| Version | Schema version + list of `execution_id`s included |
| Owner | Implemented as a standalone, additive module (`execution/summary.py`) — not owned by frozen CP-06 itself; consumed by future CP-MVP2-07/09 |
| Inputs | One or more real `ExecutionResult`s from the unmodified, frozen `run_cp_mvp2_06()` |
| Outputs | One execution summary artifact: counts by status, execution/testcase/requirement coverage kept distinct (a requirement counts only via a PASS execution) |
| Traceability | Batch ↔ Execution(s) ↔ Automation(s) ↔ Testcase(s) ↔ Requirement(s) |
| Consumer | Human review; CP-MVP2-07 RCA; CP-MVP2-09 final reporting |
| Persistence location (actual) | `reports/execution_summaries/<batch_id>/v<N>.json` + `latest.json` |

### C.12 (Future, design-only) Security Test Scenario / Evidence / Finding

| Field | Value |
|---|---|
| Purpose | Same governed shape (Requirement → Security Test Scenario → Security Test Data/Config → Security Test Automation/Tool → Execution → Evidence → Finding → Severity → Traceability → Report) for a future, separately-authorized security-testing checkpoint |
| Schema | Not defined — design placeholder only |
| Status | **Design-only. Does not un-park the README's POST-MVP/PARKED security-testing scope. See CR §9, Open Question §12.4.** |

---

## D. Checkpoint Impact Matrix

| Checkpoint | Current state (verified) | Required change | Frozen-status impact | Risk |
|---|---|---|---|---|
| CP-MVP2-01 | Frozen; Approved SRS + discovery evidence, already durable | None | None — not reopened | None |
| CP-MVP2-02 | Frozen; Knowledge Base/RAG corpus, already durable | None | None — not reopened | None |
| CP-MVP2-03 | Frozen; generation+governance logic unchanged | **IMPLEMENTED (Batch 1):** C.1 (Testcase Artifact) + C.2 (REQ↔TC Traceability) added as an additive layer around the existing, unmodified `run_cp_mvp2_03()` | Frozen checkpoint itself not reopened — `testcases/{schema,generate,validate,pipeline}.py` byte-for-byte unchanged (`git diff` empty) | Realized: Low (additive, confirmed) |
| CP-MVP2-04 | Frozen; same prior in-memory pattern | **IMPLEMENTED (Batch 1):** C.5 (Test Data Artifact) + C.6 (TC↔Data Traceability) | Frozen checkpoint itself not reopened — `testdata/{schema,generate,validate,pipeline,constraints}.py` byte-for-byte unchanged | Realized: Low (additive, confirmed) |
| CP-MVP2-05 | Frozen; same prior in-memory pattern | **IMPLEMENTED (Batch 1):** C.7 (Automation Artifact) + C.8 (reusable-component candidate identification, corrected scope) + C.9 (Automation Traceability) | Frozen checkpoint itself not reopened — `automation/{schema,generate,validate,pipeline,evidence}.py` byte-for-byte unchanged. **New finding surfaced (not a checkpoint reopening):** `AUTOMATION_ID_COLLISION_ADVISORY` — see C.7 | Realized: Medium — new capability implemented within evidence-justification discipline (11 real candidates found, 0 fabricated); one advisory discovered, not fixed |
| CP-MVP2-06 | Frozen; execution-evidence persistence already existed under `runs/cp_mvp2_06/<execution_id>/` | **IMPLEMENTED (Batch 1), additive only:** (a) `execution/persist.py`/`execution/summary.py` consume real `ExecutionResult`s from the unmodified `run_cp_mvp2_06()`; (b) the timestamped `runs/YYYY/MM/DD/<execution_id>/` layout was added as a SEPARATE path — the original convention was NOT changed | Frozen checkpoint itself not reopened — `execution/{schema,validate,evidence,engine,pipeline}.py` byte-for-byte unchanged; no output path a closed checkpoint cites was altered | Realized: Low (additive-only path chosen specifically to avoid the Medium risk originally flagged here) |
| CP-MVP2-07 | Not started (RCA + Replanning + Governance, per README) | This CR lays the artifact groundwork (C.2, C.6, C.9, C.11) CP-07 will consume; CP-07 itself remains out of scope for this CR | N/A — not yet started, not reopened | N/A |
| CP-MVP2-08 | Not started (JMeter Performance Testing, per README) | Same artifact/traceability *pattern* is reusable in principle; no direct persistence requirement imposed by this CR | N/A | N/A |
| CP-MVP2-09 | Not started (Unified Final QE Reporting, per README) | Depends on C.2/C.6/C.9/C.11 existing; this CR is a prerequisite, not an implementation | N/A | N/A |
| (Future) Security/Pentest | POST-MVP — PARKED (README, unchanged) | Design-only artifact contract proposed (C.12); parked status not lifted by this CR | N/A — no checkpoint exists to reopen | Governance risk if misread as scope change — mitigated by explicit Open Question §12.4 |

---

## E. Migration Strategy

The goal is to move from "in-memory only" to "persisted, traceable" **without corrupting or silently changing any frozen historical evidence**, and without reopening a frozen checkpoint's existing behavior except where explicitly approved (CP-06 directory convention, §D above).

1. **Additive-only code changes, confirmed.** Exactly as this project already did for `llm/test_data_client.py` (CP-04) and `llm/automation_client.py` (CP-05) — new persistence modules were added alongside the existing frozen pipeline files, never edited in place. `testcases/persist.py` reads the `List[GovernedTestcase]` a caller already produced via the unmodified `testcases.pipeline.run_cp_mvp2_03()` and writes C.1/C.2 artifacts — `testcases/generate.py`/`validate.py`/`pipeline.py`/`schema.py` remain byte-for-byte unchanged (confirmed by `git diff`).
2. **No retroactive rewriting of existing evidence, confirmed.** The one existing embedded testcase (`TC-REQ-REG-01-01`, inside the CP-03 live-pipeline-governance execution report) was **not** extracted or converted into the new persisted format as part of Batch 1 — that report remains exactly as frozen. Any future backfill would be its own explicitly-authorized, clearly-labeled action (Open Question §12.6 in the CR — still open, not decided by Batch 1).
3. **Rollout, as actually authorized and executed:** this document originally proposed a phased, per-checkpoint rollout (Phase A: CP-03; B: RBTP; C: CP-04 + Dependency Matrix; D: CP-05; E: CP-06), each with its own freeze checkpoint. The Human/Di-authorized Batch 1 instruction explicitly directed all five phases (A–E) to be implemented together in **one controlled batch**, with one full regression run, one comprehensive implementation report, and one governance reconciliation — not five separate freeze checkpoints. This was a deliberate, explicit authorization decision, recorded here rather than silently substituted for the originally-proposed sequencing.
4. **Backward-compatible consumption, confirmed.** No frozen pipeline (`run_cp_mvp2_03/04/05/06`) signature changed; every persistence/traceability/RBTP/dependency-matrix call is a separate step the caller makes after the frozen pipeline returns. Existing tests and call patterns work unmodified (204 pre-existing tests still pass).
5. **Versioning, implemented.** `persistence/envelope.py` gives every persisted artifact an immutable `v<N>.json` + mutable `latest.json` pointer from its first write; a byte-identical regeneration (ignoring the volatile `generated_at` field) is reused rather than reversioned.
6. **Regression discipline, confirmed.** Full `pytest -q` run before and after Batch 1: **204 passed, 0 failed → 249 passed, 0 failed** (45 new tests).

**This migration strategy has been executed as Batch 1**, per the deviation recorded in point 3 above. This section now records what was actually done, not merely what was proposed.
