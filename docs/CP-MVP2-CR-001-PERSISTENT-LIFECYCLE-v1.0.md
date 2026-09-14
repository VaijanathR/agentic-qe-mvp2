# CP-MVP2-CR-001 — Persistent, Traceable, Evidence-Driven End-to-End Agentic QE Lifecycle

## Formal Change Request

* **CR ID:** CP-MVP2-CR-001
* **Status:** **APPROVED FOR BATCH 1 IMPLEMENTATION** (RBTP corrected to Risk-Based Test Prioritization; see §4). Implementation report: `docs/claude-execution-reports/CP-MVP2-CR-001/` (this batch).
* **Raised against:** CP-MVP2-03, CP-MVP2-04, CP-MVP2-05, CP-MVP2-06 (all currently **FROZEN/CLOSED**), and the not-yet-started CP-MVP2-07/08/09.
* **Trigger evidence:** `docs/claude-execution-reports/CP-MVP2-03/CP-MVP2-03-TESTCASE-PERSISTENCE-INVESTIGATION-20260914-173808-FAE651.md` (commit `21ce740`) — a read-only forensic investigation that established, by direct code inspection, that CP-03-generated testcase instances are **not** persisted as first-class artifacts (governance classification **RED**).
* **Companion document:** `docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md` (current-vs-proposed architecture, per-artifact contract, checkpoint impact matrix, migration strategy).
* **This document is specification/change-control only. No implementation, schema edit, or frozen-checkpoint edit accompanies this CR.**

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
10. A proposed repository structure for all of the above (see companion Architecture Impact Assessment §C/§D) — **proposed only, not created by this CR.**

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

Every arrow above that is annotated "persisted" is new relative to today's implementation, except CP-06's own execution evidence, which already persists (§3) but whose directory convention this CR also proposes changing (§8, and Architecture Impact §D — this is itself a change against the **frozen** CP-06 checkpoint and requires explicit approval, not a silent adjustment).

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
| §12 Playwright reuse | Introduce page objects / components / utilities / fixtures where real evidence justifies reuse; avoid duplicated selectors/workflow logic. | Reusable Component Artifacts |
| §13 Automation traceability | Persist REQ→TC→Data→Automation→Component mapping; answer "which automation implements this testcase / which components does it use." | Traceability Artifact (Automation) |
| §14–16 Execution logging/summary | Persist timestamped, per-execution evidence (extending CP-06's existing `ExecutionResult`) plus a batch-level execution summary distinguishing requirement/testcase/execution coverage. | Timestamped Execution Log, Execution Summary |
| §17 Security/pentest | Define (not implement) the same governed shape for a future, explicitly-authorized security-testing checkpoint — **without lifting the current POST-MVP/PARKED scope decision.** | (Future) Security artifacts — design only |
| §18 Repository structure | Propose (not create) a clean directory layout separating each artifact family. | — (proposal only, Architecture Impact §D) |
| §19 End-to-end traceability | Ensure every artifact above carries enough ID cross-references that a human can navigate the full chain in either direction. | — (cross-cutting requirement on every artifact contract) |

## 7. Affected Checkpoints (summary — full matrix in companion document §D)

| Checkpoint | Current state | Affected by this CR? | Nature of change |
|---|---|---|---|
| CP-MVP2-01 | Frozen — application discovery/Approved SRS | **No** | None — remains the authoritative, unmodified source |
| CP-MVP2-02 | Frozen — Knowledge Base/RAG | **No** | None — already persists its own corpus; not touched |
| CP-MVP2-03 | Frozen — testcase generation | **Yes** | Additive: a new persistence step after governance, not a change to generation/validation logic or schema semantics |
| CP-MVP2-04 | Frozen — test data generation | **Yes** | Additive: persistence + traceability, same governance rules preserved |
| CP-MVP2-05 | Frozen — Playwright generation | **Yes** | Additive: persistence + traceability + reusable-component architecture |
| CP-MVP2-06 | Frozen — real browser execution | **Yes** | Two parts: (a) additive — consuming persisted upstream artifacts instead of only in-memory ones; (b) a **behavioral change** to the existing frozen evidence directory convention (`runs/cp_mvp2_06/<id>/` → the timestamped `runs/YYYY/MM/DD/<id>/` layout requested in §15) — this specific part is a change to already-frozen CP-06 behavior and must be called out and separately approved, not silently adopted |
| CP-MVP2-07 | Not started — RCA + Replanning + Governance (per README) | **Yes** | This CR's "Evidence/RCA/Governance" stage is CP-07's own stated scope; this CR only lays the artifact groundwork CP-07 will consume — it does not implement CP-07 |
| CP-MVP2-08 | Not started — JMeter Performance Testing | Indirect | Same artifact/traceability *pattern* is reusable; no direct change requested here |
| CP-MVP2-09 | Not started — Unified Final QE Reporting | **Yes (dependency)** | CP-09 cannot produce a durable, evidence-backed final report without the persisted artifacts this CR introduces; this CR is a prerequisite, not an implementation of CP-09 |

## 8. Schema Impact

* **No existing frozen schema's semantics change.** `Testcase`, `GovernedTestcase` (testcases/schema.py), `TestDataSet`, `GovernedTestDataSet` (testdata/schema.py), `PlaywrightArtifact`, `GovernedPlaywrightArtifact` (automation/schema.py), and `ExecutionResult` (execution/schema.py) are proposed to be **wrapped**, not edited — each gains an additive, versioned persistence envelope (artifact ID, schema version, baseline reference) around its existing `to_dict()` output, following the same "new parallel file, frozen file untouched" precedent this project already established for `llm/test_data_client.py` and `llm/automation_client.py`.
* **New schemas required** (none yet implemented): Traceability Artifact schema (REQ↔TC, TC↔Data, Automation chain), RBTP schema (§4, `rbtp/schema.py`), Dependency Matrix schema, Execution Summary schema.
* **One proposed breaking-adjacent change:** CP-06's evidence *directory convention* (not its `ExecutionResult` schema) — see §7 above. Everything else is additive.

## 9. Security/Penetration Testing — Explicit Scope Note

`README.md` currently states: *"Security testing and penetration testing are **POST-MVP — PARKED**."* This CR's §17 requirement asks for the same governance *shape* to be defined for future security/penetration testing, and this document does so at the design level only (Architecture Impact §C, artifact contracts for Security Test Scenario/Data/Finding). **This CR does not lift the POST-MVP/PARKED status.** Actually starting security/penetration-testing work is a separate scope decision requiring its own explicit human authorization — raised here as Open Question §12.4, not decided by this CR.

## 10. Backward Compatibility

* Existing valid functionality (`run_cp_mvp2_03/04/05/06`, all governance rules, all existing tests) is intended to remain intact. The proposed approach is **additive**: new persistence functions/modules wrap existing pipeline outputs; existing function signatures are not required to change (a persistence call can be inserted by the *caller* of each pipeline, or the pipeline can be given an optional `persist: bool` /`persist_dir` parameter — a design choice for the implementation phase, not decided here).
* The one flagged exception is the CP-06 evidence-directory-convention change (§7, §8) — explicitly not backward compatible with the current frozen convention, and explicitly called out for separate approval rather than silently changed.
* All 204 currently-passing tests are expected to keep passing unmodified; new tests are additive.

## 11. Regression Impact

No regression is anticipated from adopting this CR's *design* (this document changes nothing executable). Once implementation is authorized, the Migration Strategy (Architecture Impact §E) requires: full regression run before and after each additive persistence module is introduced, exactly as every prior checkpoint in this project has done.

## 12. Open Questions

1. **RBTP definition (§4):** RESOLVED — corrected to Risk-Based Test Prioritization by the Batch 1 implementation instruction.
2. **CP-06 evidence directory convention (§7/§8):** approve or reject changing `runs/cp_mvp2_06/<execution_id>/` to the timestamped `runs/YYYY/MM/DD/<execution_id>/` hierarchy — this is a change to already-frozen CP-06 behavior.
3. **Persistence trigger point:** should each pipeline (`run_cp_mvp2_03/04/05`) persist automatically as part of its own call, or should persistence be an explicit, separate step the caller invokes after receiving the governed in-memory result? (Affects whether existing frozen pipeline function signatures/behavior change at all, or only new code is added around them.)
4. **Security/penetration testing scope (§9):** this CR proposes only the future *governance shape*; actually lifting POST-MVP/PARKED status and starting real security-testing work requires a separate, explicit decision — is that decision being made now, or deferred?
5. **Artifact versioning/concurrency:** if the same requirement/testcase is regenerated multiple times (e.g., repeated CP-03 runs against the same requirement), how are multiple persisted instances of the "same" logical testcase ID reconciled — overwrite, version-suffix, or reject-as-duplicate? This CR does not decide this; it is a design question for the implementation phase.
6. **Historical evidence treatment:** the existing embedded-in-report testcase (`TC-REQ-REG-01-01`, §2) is explicitly **not** proposed to be retroactively extracted into the new persisted format — is that correct, or should a one-time, clearly-labeled backfill be authorized separately?

## 13. Risks

* **Scope creep risk:** this CR is intentionally broad (spans 4 frozen checkpoints + 3 not-yet-started ones). Recommend phased implementation (per checkpoint, each with its own focused Change Request execution against this CR, mirroring how CP-04/05/06 were each implemented individually) rather than one monolithic implementation task.
* **Frozen-checkpoint reopening risk:** any implementation phase must re-verify, at the start of each phase, that the specific frozen artifact being extended is still byte-for-byte what was last frozen (the same `git diff --stat` discipline used throughout this project) — this CR does not relax that discipline.
* **Over-engineering risk (§12 of the CR's own instruction, "reusable components"):** the Playwright reusability architecture (§6/§11) must be justified by real, evidence-backed repetition, not built speculatively — consistent with this project's existing "no premature abstraction" principle.
* **Security-scope risk:** designing the future security-testing shape without a clear, separate authorization boundary could be misread as silently un-parking POST-MVP scope — mitigated by explicitly surfacing this as Open Question §12.4, not a decision this CR makes.

## 14. Proposed Acceptance Criteria (for the CR itself, not for implementation)

This CR is ready to be marked **APPROVED** when:

1. RESOLVED — the RBTP definition (§4) was explicitly corrected to Risk-Based Test Prioritization by the Batch 1 implementation instruction.
2. The CP-06 evidence-directory-convention change (§7/§8) is explicitly approved or rejected.
3. The security/penetration-testing scope question (§9, Open Question §12.4) is explicitly answered (deferred is an acceptable answer).
4. A phasing decision is made (single monolithic implementation vs. per-checkpoint phased implementation, §13).
5. The companion Architecture Impact Assessment's per-artifact contracts and Checkpoint Impact Matrix are reviewed and found consistent with this CR's requested changes.

**No implementation work is authorized until all five items above are explicitly resolved by Human + Di.**
