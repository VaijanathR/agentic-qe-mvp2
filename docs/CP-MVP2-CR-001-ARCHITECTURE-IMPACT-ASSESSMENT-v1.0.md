# CP-MVP2-CR-001 — Architecture Impact Assessment

Companion to `docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md`. **Status:
PROPOSED — PENDING REVIEW. Design/analysis only; nothing in this document
has been implemented.**

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
RBTP  (pending definition approval — CR §4)
 ↓  (persisted)          → TRACEABILITY (REQ↔TC↔RBTP)
DEPENDENCY MATRIX
 ↓  (persisted)
DATA ─────────────→ TRACEABILITY (TC↔DATA)
 ↓  (persisted)
PLAYWRIGHT ───────→ TRACEABILITY (REQ↔TC↔DATA↔AUTOMATION↔COMPONENT)
 ↓  (persisted)
REUSABLE COMPONENTS  (page objects / utilities / fixtures)
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

Each row is a **proposed** contract. None of these artifacts exist yet;
none is created by this CR.

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
| Persistence location (proposed) | `testcases/generated/<testcase_id>.json` |

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
| Persistence location (proposed) | `traceability/req_to_testcase/<batch_id>.json` |

### C.3 RBTP Artifact (pending definition approval — CR §4)

| Field | Value |
|---|---|
| Purpose | Per-requirement test-planning/governance record (intent, priority/risk, scenario-coverage summary, dependencies, gaps, execution relevance) |
| Schema | **Not yet defined** — first requires the proposed definition in CR §4 to be approved |
| ID | Proposed: `RBTP-<requirement_id>` |
| Version | TBD |
| Owner | Proposed: CP-MVP2-03 (immediately after testcase persistence) or a new sub-stage |
| Inputs | Persisted Testcase Artifacts (C.1) + Requirement↔Testcase Traceability (C.2) |
| Outputs | One RBTP artifact per requirement |
| Traceability | REQ ↔ RBTP ↔ TC(s) |
| Consumer | Human review; dependency matrix (C.4); CP-MVP2-09 reporting |
| Persistence location (proposed) | `rbtp/<requirement_id>.json` |

### C.4 Dependency / Reusability Matrix

| Field | Value |
|---|---|
| Purpose | Identify shared preconditions, data reuse/uniqueness constraints, auth/session dependencies, reusable component candidates, before automation is generated |
| Schema | New |
| ID | Proposed: one artifact per CP-05 generation batch |
| Version | Schema version + reference to the CP-03/04 artifacts inspected |
| Owner | Proposed: a pre-CP-05 analysis stage |
| Inputs | Persisted Testcase Artifacts (C.1), Persisted Test Data Artifacts (C.6), RBTP (C.3, where available) |
| Outputs | One dependency matrix per batch |
| Traceability | TC ↔ shared setup/data/component candidates |
| Consumer | CP-MVP2-05 (automation generation), human review |
| Persistence location (proposed) | `dependencies/<batch_id>.json` |

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
| Persistence location (proposed) | `testdata/generated/<data_set_id>.json` |

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
| Persistence location (proposed) | `traceability/testcase_to_testdata/<batch_id>.json` |

### C.7 Persisted Automation Artifact

| Field | Value |
|---|---|
| Purpose | First-class record of one CP-05 Playwright artifact |
| Schema | Wraps existing `automation.schema.GovernedPlaywrightArtifact.to_dict()` unchanged; adds `artifact_version`, `baseline_reference` |
| ID | `automation_id` (existing) |
| Version | Persistence-format version |
| Owner | CP-MVP2-05 |
| Inputs | A `GovernedPlaywrightArtifact` from the existing, unmodified `automation.validate.govern_batch()` |
| Outputs | One artifact per generated automation |
| Traceability | `testcase_id`, `requirement_ids`, `test_data_set_id` (already present) |
| Consumer | Human review; CP-MVP2-06 |
| Persistence location (proposed) | `automation/generated/<automation_id>.json` |

### C.8 Reusable Component Artifact

| Field | Value |
|---|---|
| Purpose | A page object, utility, fixture, or helper shared across multiple automation artifacts, only where real evidence justifies reuse (CR §12 — no premature abstraction) |
| Schema | New — component ID, purpose, evidence justifying reuse, list of consuming `automation_id`s |
| ID | Proposed: `COMPONENT-<name>` |
| Version | Component-level version, since a change here can affect multiple automation artifacts |
| Owner | CP-MVP2-05 |
| Inputs | Recurring locator/workflow patterns identified via the Dependency Matrix (C.4) |
| Outputs | Reusable component source files (`automation/components/`, `automation/pages/`, `automation/utils/`) |
| Traceability | Component ↔ Automation(s) that use it |
| Consumer | CP-MVP2-05 generation; CP-MVP2-06 execution |
| Persistence location (proposed) | `automation/components/`, `automation/pages/`, `automation/utils/` |

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
| Persistence location (proposed) | `traceability/automation/<batch_id>.json` |

### C.10 Timestamped Execution Log

| Field | Value |
|---|---|
| Purpose | Real, per-execution evidence: step results, assertion results, errors, diagnostics, evidence file locations |
| Schema | Extends existing `execution.schema.ExecutionResult` (unchanged) with an explicit runtime-timestamp-derived path |
| ID | `execution_id` (existing) |
| Version | Execution-schema version (already exists) |
| Owner | CP-MVP2-06 |
| Inputs | A real `ExecutionResult` from the existing, unmodified `execution.pipeline.run_cp_mvp2_06()` |
| Outputs | `execution.log`, `step_results.json`, `assertions.json`, `screenshots/`, `traces/`, `final_result.json` |
| Traceability | `automation_id`, `testcase_id`, `requirement_ids`, `test_data_set_id` (already present) |
| Consumer | Human audit; Execution Summary (C.11); CP-MVP2-07 RCA |
| Persistence location (proposed) | `runs/<YYYY>/<MM>/<DD>/<execution_id>/...` — **a change to the existing frozen CP-06 convention (`runs/cp_mvp2_06/<execution_id>/...`); requires explicit approval, see CR §7/§8** |

### C.11 Execution Summary

| Field | Value |
|---|---|
| Purpose | Batch-level rollup distinguishing requirement coverage, testcase coverage, execution coverage, and pass/fail outcome |
| Schema | New |
| ID | One per execution batch |
| Version | Schema version + list of `execution_id`s included |
| Owner | CP-MVP2-06 (or CP-MVP2-07, TBD at implementation time) |
| Inputs | One or more Timestamped Execution Logs (C.10) |
| Outputs | One execution summary artifact |
| Traceability | Batch ↔ Execution(s) ↔ Automation(s) ↔ Testcase(s) ↔ Requirement(s) |
| Consumer | Human review; CP-MVP2-07 RCA; CP-MVP2-09 final reporting |
| Persistence location (proposed) | `reports/execution_summaries/<batch_id>.json` |

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
| CP-MVP2-03 | Frozen; generation+governance logic unchanged, output in-memory only | Add C.1 (Testcase Artifact) + C.2 (REQ↔TC Traceability) persistence as an additive layer around the existing, unmodified `run_cp_mvp2_03()` | **Requires a scoped Change Request/implementation task against the frozen CP-03 checkpoint** — additive only, no change to generation/governance semantics | Low (additive) |
| CP-MVP2-04 | Frozen; same in-memory pattern | Add C.5 (Test Data Artifact) + C.6 (TC↔Data Traceability); consume C.1 where available | **Requires a scoped CR/implementation task against frozen CP-04** — additive only | Low (additive) |
| CP-MVP2-05 | Frozen; same in-memory pattern | Add C.7 (Automation Artifact) + C.8 (Reusable Components) + C.9 (Automation Traceability); consume C.4/C.5/C.6 | **Requires a scoped CR/implementation task against frozen CP-05** — additive, plus a genuinely new capability (reusable-component extraction) that did not exist before | Medium (new capability, evidence-justification discipline needed to avoid over-engineering) |
| CP-MVP2-06 | Frozen; execution-evidence persistence already exists under `runs/cp_mvp2_06/<execution_id>/` | (a) Consume persisted C.7/C.5 artifacts instead of only in-memory ones — additive; (b) change the evidence directory convention to the timestamped `runs/YYYY/MM/DD/<execution_id>/` layout — **behavioral change to frozen output location**; (c) add C.11 (Execution Summary) | **Requires a scoped CR/implementation task against frozen CP-06; part (b) specifically requires explicit sign-off since it changes already-frozen, already-verified output paths referenced in CP-06's own freeze checkpoint** | Medium (part b touches frozen evidence paths already cited in a closed checkpoint) |
| CP-MVP2-07 | Not started (RCA + Replanning + Governance, per README) | This CR lays the artifact groundwork (C.2, C.6, C.9, C.11) CP-07 will consume; CP-07 itself remains out of scope for this CR | N/A — not yet started, not reopened | N/A |
| CP-MVP2-08 | Not started (JMeter Performance Testing, per README) | Same artifact/traceability *pattern* is reusable in principle; no direct persistence requirement imposed by this CR | N/A | N/A |
| CP-MVP2-09 | Not started (Unified Final QE Reporting, per README) | Depends on C.2/C.6/C.9/C.11 existing; this CR is a prerequisite, not an implementation | N/A | N/A |
| (Future) Security/Pentest | POST-MVP — PARKED (README, unchanged) | Design-only artifact contract proposed (C.12); parked status not lifted by this CR | N/A — no checkpoint exists to reopen | Governance risk if misread as scope change — mitigated by explicit Open Question §12.4 |

---

## E. Migration Strategy

The goal is to move from "in-memory only" to "persisted, traceable" **without corrupting or silently changing any frozen historical evidence**, and without reopening a frozen checkpoint's existing behavior except where explicitly approved (CP-06 directory convention, §D above).

1. **Additive-only code changes.** Exactly as this project already did for `llm/test_data_client.py` (CP-04) and `llm/automation_client.py` (CP-05) — new persistence modules are added alongside the existing frozen pipeline files, never edited in place. E.g., a new `testcases/persist.py` would read the `List[GovernedTestcase]` a caller already produced via the unmodified `testcases.pipeline.run_cp_mvp2_03()` and write C.1/C.2 artifacts — `testcases/generate.py`/`validate.py`/`pipeline.py`/`schema.py` remain byte-for-byte unchanged unless a specific, separately-justified change is proposed.
2. **No retroactive rewriting of existing evidence.** The one existing embedded testcase (`TC-REQ-REG-01-01`, inside the CP-03 live-pipeline-governance execution report) is **not** proposed to be extracted or converted into the new persisted format as part of this migration — that report remains exactly as frozen. Any future backfill would be its own explicitly-authorized, clearly-labeled action (Open Question §12.6 in the CR).
3. **Phased rollout, one checkpoint at a time**, mirroring how CP-04/05/06 were each implemented, verified, and frozen individually in this project:
   - Phase A: CP-03 persistence (C.1, C.2).
   - Phase B: RBTP (C.3) — only after its definition (CR §4) is approved.
   - Phase C: CP-04 persistence (C.5, C.6) + Dependency Matrix (C.4).
   - Phase D: CP-05 persistence (C.7, C.8, C.9).
   - Phase E: CP-06 persistence/consumption changes (C.10, C.11), including the explicitly-approved-or-rejected directory-convention change.
   - Each phase: full regression before/after, a scoped implementation report, and its own freeze checkpoint — the same discipline already used for every prior checkpoint in this project.
4. **Backward-compatible consumption.** Where a pipeline's signature must change to *consume* a persisted artifact (e.g., CP-04 optionally loading a specific persisted CP-03 testcase by ID instead of only receiving one in memory), the existing in-memory parameter path is preserved as a supported alternative, not removed — existing tests and existing call patterns continue to work unmodified.
5. **Versioning.** Every new persisted artifact carries an explicit `artifact_version`/schema-version field from its first implementation, so future format changes do not require guessing the shape of older files.
6. **Regression discipline unchanged.** Full `pytest -q` run before and after every phase, exactly as done for CP-03 through CP-06; the current 204-passed/0-failed baseline is the starting point for Phase A.

**No part of this migration strategy is executed by this CR.** It is provided so the human reviewer can evaluate feasibility and sequencing before authorizing any implementation phase.
