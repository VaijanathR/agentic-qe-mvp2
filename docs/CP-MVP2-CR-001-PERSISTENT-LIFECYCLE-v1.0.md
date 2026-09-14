# CP-MVP2-CR-001 — Persistent, Traceable, Evidence-Driven End-to-End Agentic QE Lifecycle

## Formal Change Request

* **CR ID:** CP-MVP2-CR-001
* **Status:** **BATCH 1 IMPLEMENTATION AUTHORIZED AND COMPLETE** (RBTP corrected to Risk-Based Test Prioritization; see §4). Di's independent engineering review: PASS with advisories. **This status describes implementation completion, not a final CR-001 governance gate — that determination remains Di's separate, independent responsibility** (see the governance reconciliation report under `docs/claude-execution-reports/CP-MVP2-CR-001/`).
* **Raised against:** CP-MVP2-03, CP-MVP2-04, CP-MVP2-05, CP-MVP2-06 (all currently **FROZEN/CLOSED**), and the not-yet-started CP-MVP2-07/08/09.
* **Trigger evidence:** `docs/claude-execution-reports/CP-MVP2-03/CP-MVP2-03-TESTCASE-PERSISTENCE-INVESTIGATION-20260914-173808-FAE651.md` (commit `21ce740`) — a read-only forensic investigation that established, by direct code inspection, that CP-03-generated testcase instances are **not** persisted as first-class artifacts (governance classification **RED**).
* **Companion document:** `docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md` (current-vs-proposed architecture, per-artifact contract, checkpoint impact matrix, migration strategy).
* **Batch 1 implementation commits:** `415038c` (implementation), `546c568` (evidence report). Implemented additively — no frozen CP-01–06 specification, freeze checkpoint, or `llm/client.py` was edited (verified by `git diff`).

---

## 1. Change Requested

Introduce persistent, first-class, independently-auditable artifacts and deterministic, bidirectionally-navigable traceability across the full Agentic QE lifecycle:

```text
Requirements → Testcases → RBTP → Dependency Matrix → Test Data →
Playwright Automation → Reusable Components → Execution Logs →
Execution Summary → Evidence/RCA/Governance → (future) Security/Penetration Testing
```

Concretely, this CR requests:

1. A persisted, canonical, first-class testcase artifact per accepted CP-03 testcase (closing the RED finding above).
2. A persisted Requirement ↔ Testcase traceability artifact.
3. The corrected RBTP (Risk-Based Test Prioritization, see §4) artifact and its persistence.
4. A persisted dependency/reusability matrix, produced before automation generation.
5. Persisted CP-04 test-data artifacts, with an explicit Testcase ↔ Test Data traceability artifact.
6. Persisted CP-05 Playwright automation artifacts, with an explicit Testcase ↔ Automation traceability artifact.
7. A reusable Playwright component architecture (page objects / utilities / fixtures) so automation is not one fully independent script per testcase where reuse is justified by real evidence.
8. Persisted, timestamped CP-06 execution logs/evidence and a persisted execution summary, distinguishing requirement coverage from testcase coverage from execution coverage.
9. An explicitly-scoped, non-destructive future pattern for security/penetration testing following the same governance shape — **without silently lifting the existing POST-MVP/PARKED scope decision** (see §9).
10. A repository structure for all of the above (see companion Architecture Impact Assessment §C/§D) — **implemented in Batch 1** (`persistence/`, `testcases/generated/`, `testdata/generated/`, `automation/generated/`, `rbtp/generated/`, `dependencies/generated/`, `traceability/*/`, `reports/execution_summaries/`; the generated-data directories are real, locally-produced evidence, left untracked in git per this repo's existing `runs/`/`evidence/` convention — see the Batch 1 implementation report).

## 2. Reason

Established by direct, read-only code inspection (not assumption):

* `testcases/pipeline.py::run_cp_mvp2_03()` returns a plain in-memory `dict`; no function anywhere in `testcases/` or `llm/client.py` performs `json.dump`, `write_text`, `open(..., "w")`, or any equivalent persistence call.
* `testdata/pipeline.py::run_cp_mvp2_04()` and `automation/pipeline.py::run_cp_mvp2_05()` both accept `cp03_governed_testcases: List[GovernedTestcase]` as a plain Python parameter — an in-memory handoff from whatever object the caller currently holds, never a file read.
* The only real, live-generated CP-03 testcase in the repository (`TC-REQ-REG-01-01`) survives only because a human manually transcribed its JSON into a Markdown execution report — not because of any system persistence mechanism.
* Consequence: a human cannot open a first-class testcase artifact and review exactly what CP-03 generated; CP-04/CP-05 cannot be pointed at a specific, previously-governed CP-03 output; reproducibility of a specific generated instance depends on re-reading a report, not re-fetching an artifact.
* This pattern — real objects living only inside one process's memory, with governance and coverage computed correctly in that moment but nothing durable left behind — was, by inspection, never contradicted anywhere in CP-04/05/06 either: each stage's `Governed*` objects are equally transient unless *this* CR's persistence layer is added.
* The intended Agentic QE lifecycle (per the CR's own stated objective) requires artifacts that are **persistent, traceable, reusable, and evidence-driven** end-to-end — the current implementation satisfies "traceable" and "evidence-driven" only within a single process's lifetime, not durably.

## 3. Current Architecture (verified)

```text
APPROVED SRS
     ↓
MVP2 KNOWLEDGE BASE (persisted — CP-02, chunks.jsonl/manifest.json)
     ↓
GOVERNED RAG RETRIEVAL (KnowledgeBase.by_id(), in-memory query over persisted chunks)
     ↓
LLM (ClaudeLLMClient / StubLLMClient — llm/client.py)
     ↓
STRUCTURED TESTCASE OUTPUT (testcases.schema.Testcase — in-memory dataclass)
     ↓
DETERMINISTIC VALIDATORS (testcases.validate — in-memory GovernedTestcase)
     ↓
CP-MVP2-03 RESULT (a Python dict returned to the caller — IN MEMORY ONLY)
     ↓  (in-memory List[GovernedTestcase] parameter, same process or a freshly-regenerated equivalent)
CP-MVP2-04 (testdata.pipeline.run_cp_mvp2_04 — same in-memory pattern, IN MEMORY ONLY)
     ↓  (in-memory List[GovernedTestDataSet] parameter)
CP-MVP2-05 (automation.pipeline.run_cp_mvp2_05 — same in-memory pattern, IN MEMORY ONLY)
     ↓  (in-memory GovernedPlaywrightArtifact + GovernedTestDataSet parameters)
CP-MVP2-06 (execution.pipeline.run_cp_mvp2_06 — the ONE stage that does persist, but only
     ↓       execution-time evidence: runs/cp_mvp2_06/<execution_id>/*, never the upstream
     ↓       testcase/data/automation artifacts themselves)
CP-MVP2-06 RESULT
```

Only two things are durably persisted anywhere in today's implementation: (a) the CP-02 Knowledge Base/RAG corpus itself (requirements, business rules, negative cases, historical discovery evidence), and (b) CP-06's own execution-time evidence (logs, screenshots, `ExecutionResult` JSON). Every testcase, dataset, and automation artifact in between exists only as long as one Python process holds a reference to it.

## 4. RBTP — Corrected Definition (approved via the Batch 1 implementation instruction)

**CORRECTION.** A repository-wide search (code, every Markdown document under `docs/`, `README.md`, `ClaudeInstructions/`, and the two `ChatGPT_MVP3_RelatedChat...` reference documents at the repository root) found **zero** existing occurrences of "RBTP" anywhere in this project prior to this CR — it was not a term this project had previously defined. This CR's original text proposed reading it as "Requirement-Based Test Plan"; that reading has been **explicitly superseded and corrected** by the Human/Di-authorized Batch 1 implementation instruction. The governing definition, effective from that instruction forward, is:

> **RBTP = Risk-Based Test Prioritization.** A persisted, per-testcase, explainable artifact answering: *"which testcases should be executed first, and why?"* It operates on already-persisted testcases (§5) and records, per testcase: evidence-backed risk factors (`business_criticality`, `risk_likelihood`, `change_impact`, `defect_history`, `dependency_impact`, `security_impact`, `customer_impact` — each `HIGH`/`MEDIUM`/`LOW` only where a real, citable evidence source exists, and `UNKNOWN` everywhere no such source exists in this project today — never invented), a deterministically-derived `priority` (`P0`–`P3`) and `execution_recommendation`, and a `risk_rationale` string that makes the derivation independently explainable from the persisted artifact alone, without needing to ask an LLM why. It is explicitly distinct from the Dependency/Reusability Matrix (§7): RBTP answers *"what order,"* the Dependency Matrix answers *"what depends on / can reuse what."*

This definition does not conflict with, replace, or duplicate any existing frozen schema (`Testcase`, `GovernedTestcase`, `TestDataSet`, `PlaywrightArtifact`). It is implemented in `rbtp/schema.py` (this batch).

## 5. Target Architecture (summary — full diagram in the companion Architecture Impact Assessment §B)

```text
APPROVED SRS
     ↓
TESTCASE GENERATION  →  PERSIST TESTCASE ARTIFACT
     ↓
REQUIREMENT ↔ TESTCASE TRACEABILITY ARTIFACT (persisted)
     ↓
RBTP ARTIFACT — RISK-BASED TEST PRIORITIZATION (persisted, per §4)
     ↓
REQUIREMENT ↔ TESTCASE ↔ RBTP TRACEABILITY ARTIFACT (persisted)
     ↓
DEPENDENCY / REUSABILITY MATRIX (persisted)
     ↓
TEST DATA GENERATION  →  PERSIST TEST DATA ARTIFACT
     ↓
TESTCASE ↔ TEST DATA TRACEABILITY ARTIFACT (persisted)
     ↓
PLAYWRIGHT AUTOMATION GENERATION  →  PERSIST AUTOMATION ARTIFACT
     ↓
TESTCASE ↔ AUTOMATION TRACEABILITY ARTIFACT (persisted)
     ↓
REUSABLE PLAYWRIGHT COMPONENTS (page objects / utilities / fixtures)
     ↓
EXECUTION  →  TIMESTAMPED EXECUTION LOGS (persisted)
     ↓
EXECUTION SUMMARY (persisted)
     ↓
EVIDENCE / RCA / GOVERNANCE  (CP-MVP2-07, not started)
```

Every arrow above annotated "persisted" is now implemented (Batch 1). CP-06's own execution evidence already persisted before Batch 1 (§3); Batch 1's resolution of the directory-convention question (§8, Open Question §12.2) was to leave the frozen `runs/cp_mvp2_06/<execution_id>/` default completely untouched and add a **separate, additive** `runs/YYYY/MM/DD/<execution_id>/` path (`execution/persist.py`) — the frozen CP-06 checkpoint's own already-cited evidence paths were never changed.

## 6. Requested Changes — Mapped to This CR's Own Instruction Sections

| Instruction section | Requested change | New artifact(s) |
|---|---|---|
| §4 Requirement Artifact | Persist the requirement baseline/version actually used for each downstream generation run (already partially present as `source_version`/`source_document` on generated testcases; formalize as a first-class, queryable reference). | Baseline/version reference (extends existing `source_attribution`, does not replace it) |
| §5 Testcase persistence | Persist every ACCEPTED testcase as a first-class, ID-addressed artifact. | Persisted Testcase Artifact |
| §6 Requirement↔Testcase traceability | Persist a deterministic matrix: covered/uncovered requirements, 1:many testcase mappings, orphan/invalid references, duplicates/possible-duplicates. | Traceability Artifact (REQ↔TC) |
| §7 RBTP | Persist the RBTP (Risk-Based Test Prioritization) artifact per §4. | RBTP Artifact |
| §8 Dependency Matrix | Persist a matrix of shared preconditions, data reuse/uniqueness, auth/session requirements, reusable components, dependency ordering. | Dependency/Reusability Matrix |
| §9 Test data persistence | Persist every ACCEPTED CP-04 dataset as a first-class artifact (CP-04's existing schema/governance rules preserved unchanged). | Persisted Test Data Artifact |
| §10 Testcase↔Test Data traceability | Persist a deterministic TC↔Data mapping; detect missing/orphan/incompatible/duplicate data. | Traceability Artifact (TC↔Data) |
| §11 Automation persistence | Persist every CP-05 automation artifact; map Automation→Testcase→Requirement→Test Data. | Persisted Automation Artifact |
| §12 Playwright reuse | Batch 1 implements real, evidence-backed **candidate identification** (`automation/components.py`) — literal locator repetition across 2+ distinct automation artifacts. It does not yet scaffold actual page-object/utility source files; that is left for a future task once a real `ACCEPTED` automation artifact exists to refactor (no speculative framework was built). | Reusable component candidates (identification only, not extraction) |
| §13 Automation traceability | Persist REQ→TC→Data→Automation→Component mapping; answer "which automation implements this testcase / which components does it use." | Traceability Artifact (Automation) |
| §14–16 Execution logging/summary | Persist timestamped, per-execution evidence (extending CP-06's existing `ExecutionResult`) plus a batch-level execution summary distinguishing requirement/testcase/execution coverage. | Timestamped Execution Log, Execution Summary |
| §17 Security/pentest | Define (not implement) the same governed shape for a future, explicitly-authorized security-testing checkpoint — **without lifting the current POST-MVP/PARKED scope decision.** | (Future) Security artifacts — design only |
| §18 Repository structure | Implemented in Batch 1: `persistence/`, `testcases/generated/`, `testdata/generated/`, `automation/generated/`, `rbtp/generated/`, `dependencies/generated/`, `traceability/*/`, `reports/execution_summaries/`. | — (Architecture Impact §D) |
| §19 End-to-end traceability | Ensure every artifact above carries enough ID cross-references that a human can navigate the full chain in either direction. | — (cross-cutting requirement on every artifact contract) |

## 7. Affected Checkpoints (summary — full matrix in companion document §D)

| Checkpoint | Current state | Affected by this CR? | Nature of change |
|---|---|---|---|
| CP-MVP2-01 | Frozen — application discovery/Approved SRS | **No** | None — remains the authoritative, unmodified source |
| CP-MVP2-02 | Frozen — Knowledge Base/RAG | **No** | None — already persists its own corpus; not touched |
| CP-MVP2-03 | Frozen — testcase generation | **Yes** | Additive: a new persistence step after governance, not a change to generation/validation logic or schema semantics |
| CP-MVP2-04 | Frozen — test data generation | **Yes** | Additive: persistence + traceability, same governance rules preserved |
| CP-MVP2-05 | Frozen — Playwright generation | **Yes** | Additive: persistence + traceability + reusable-component architecture |
| CP-MVP2-06 | Frozen — real browser execution | **Yes** | Implemented additively only: (a) `execution/persist.py`/`execution/summary.py` consume real `ExecutionResult`s produced by the unmodified, frozen `run_cp_mvp2_06()`; (b) the timestamped `runs/YYYY/MM/DD/<execution_id>/` layout was added as a **separate, additional** path — the frozen `runs/cp_mvp2_06/<id>/` default and every file `execution/evidence.py`/`engine.py`/`pipeline.py`/`schema.py`/`validate.py` produce are byte-for-byte unchanged (`git diff` empty) |
| CP-MVP2-07 | Not started — RCA + Replanning + Governance (per README) | **Yes** | This CR's "Evidence/RCA/Governance" stage is CP-07's own stated scope; this CR only lays the artifact groundwork CP-07 will consume — it does not implement CP-07 |
| CP-MVP2-08 | Not started — JMeter Performance Testing | Indirect | Same artifact/traceability *pattern* is reusable; no direct change requested here |
| CP-MVP2-09 | Not started — Unified Final QE Reporting | **Yes (dependency)** | CP-09 cannot produce a durable, evidence-backed final report without the persisted artifacts this CR introduces; this CR is a prerequisite, not an implementation of CP-09 |

## 8. Schema Impact

* **No existing frozen schema's semantics changed** (confirmed by `git diff`). `Testcase`, `GovernedTestcase` (testcases/schema.py), `TestDataSet`, `GovernedTestDataSet` (testdata/schema.py), `PlaywrightArtifact`, `GovernedPlaywrightArtifact` (automation/schema.py), and `ExecutionResult` (execution/schema.py) were **wrapped**, not edited — each gains an additive, versioned persistence envelope (`persistence/envelope.py`: `artifact_id`, `artifact_version`, `generated_at`, `provenance`, `content_hash`) around its existing `to_dict()` output, following the same "new parallel file, frozen file untouched" precedent this project already established for `llm/test_data_client.py` and `llm/automation_client.py`.
* **New schemas implemented:** Traceability schemas (REQ↔TC, TC↔Data, Automation chain — `traceability/`), RBTP schema (§4, `rbtp/schema.py`), Dependency Matrix schema (`dependencies/schema.py`), Execution Summary shape (`execution/summary.py`).
* **The originally-flagged breaking-adjacent change (CP-06's evidence directory convention) was NOT made** — resolved as additive-only (§5/§7/§10 above). No frozen schema or output path changed.

## 9. Security/Penetration Testing — Explicit Scope Note

`README.md` currently states: *"Security testing and penetration testing are **POST-MVP — PARKED**."* This CR's §17 requirement asks for the same governance *shape* to be defined for future security/penetration testing, and this document does so at the design level only (Architecture Impact §C, artifact contracts for Security Test Scenario/Data/Finding). **This CR does not lift the POST-MVP/PARKED status.** Actually starting security/penetration-testing work is a separate scope decision requiring its own explicit human authorization — raised here as Open Question §12.4, not decided by this CR.

## 10. Backward Compatibility

* Existing valid functionality (`run_cp_mvp2_03/04/05/06`, all governance rules, all existing tests) remains intact, confirmed. Batch 1 implemented every persistence function as a **separate, explicit call the caller makes after** the existing frozen pipeline returns (Open Question §12.3, RESOLVED this way) — no frozen pipeline function signature changed.
* The originally-flagged exception (CP-06 evidence-directory convention) was resolved as **fully backward compatible**: the frozen `runs/cp_mvp2_06/<id>/` convention was never touched; the timestamped layout was added as an additional, separate path (§5 above).
* Regression: all 204 pre-Batch-1 tests continue to pass unmodified; 45 new tests were added. See §11.

## 11. Regression Impact

**Actual result (Batch 1):** `.venv/Scripts/python.exe -m pytest -q` → **249 passed, 0 failed** (204 pre-existing + 45 new). Full regression was run before and after implementation, exactly as every prior checkpoint in this project has done.

## 12. Open Questions

1. **RBTP definition (§4):** RESOLVED — corrected to Risk-Based Test Prioritization by the Batch 1 implementation instruction.
2. **CP-06 evidence directory convention (§7/§8):** RESOLVED — the frozen `runs/cp_mvp2_06/<execution_id>/` convention is kept exactly as frozen; the timestamped `runs/YYYY/MM/DD/<execution_id>/` hierarchy was added as a separate, additive path (`execution/persist.py`). No frozen CP-06 behavior changed.
3. **Persistence trigger point:** RESOLVED — an explicit, separate step the caller invokes after receiving the governed in-memory result (each `*/persist.py` module). No frozen pipeline signature or behavior changed.
4. **Security/penetration testing scope (§9):** RESOLVED (deferred) — this CR's Batch 1 documents only the future *governance shape* (`docs/CP-MVP2-CR-001-SECURITY-DESIGN-BOUNDARY.md`, design-only); POST-MVP/PARKED status is unchanged; lifting it remains a separate, not-yet-made decision.
5. **Artifact versioning/concurrency:** RESOLVED — `persistence/envelope.py` implements an immutable-version + mutable-pointer model: a byte-identical regeneration (ignoring only the volatile `generated_at` field) is reused, not reversioned; a genuinely different regeneration gets its own new, permanently retained version. No prior version is ever overwritten.
6. **Historical evidence treatment:** RESOLVED for Batch 1 (no backfill performed) — the embedded-in-report testcase (`TC-REQ-REG-01-01`, §2) was **not** retroactively extracted or backfilled into the new persisted format; that execution report remains exactly as frozen. Whether a one-time, explicitly-labeled backfill should be separately authorized in the future remains genuinely open — not decided either way by Batch 1, and not blocking.

## 13. Risks

* **Scope creep risk:** this CR is intentionally broad (spans 4 frozen checkpoints + 3 not-yet-started ones). This document originally recommended phased, per-checkpoint implementation; the Human/Di-authorized Batch 1 instruction explicitly directed a single, controlled batch covering all phases (A–E) instead, with one comprehensive regression run and one implementation report rather than a freeze checkpoint per phase. That was a deliberate, explicit authorization decision — not a silent deviation from this CR's own recommendation.
* **Frozen-checkpoint reopening risk:** any implementation phase must re-verify, at the start of each phase, that the specific frozen artifact being extended is still byte-for-byte what was last frozen (the same `git diff --stat` discipline used throughout this project) — this CR does not relax that discipline.
* **Over-engineering risk (§12 of the CR's own instruction, "reusable components"):** the Playwright reusability architecture (§6/§11) must be justified by real, evidence-backed repetition, not built speculatively — consistent with this project's existing "no premature abstraction" principle.
* **Security-scope risk:** designing the future security-testing shape without a clear, separate authorization boundary could be misread as silently un-parking POST-MVP scope — mitigated by explicitly surfacing this as Open Question §12.4, not a decision this CR makes.

## 14. Acceptance Criteria — Status

1. RESOLVED — the RBTP definition (§4) was explicitly corrected to Risk-Based Test Prioritization.
2. RESOLVED — the CP-06 evidence-directory-convention question was resolved as additive-only (§5/§7/§10/§12.2); no frozen CP-06 behavior was changed.
3. RESOLVED (deferred) — security/penetration-testing scope remains POST-MVP/PARKED (§9, §12.4); not lifted by Batch 1.
4. RESOLVED — a single, controlled Batch 1 implementation (covering phases A–E together) was explicitly authorized and executed (§13).
5. RESOLVED — this document and its companion Architecture Impact Assessment have been reconciled with the actual Batch 1 implementation and evidence (see the governance reconciliation report under `docs/claude-execution-reports/CP-MVP2-CR-001/`).

**All five items above are resolved at the engineering-documentation level. This CR document does not itself constitute Di's independent final governance gate for CR-001 or for the Batch 1 implementation — that determination is Di's separate, independent responsibility.**
