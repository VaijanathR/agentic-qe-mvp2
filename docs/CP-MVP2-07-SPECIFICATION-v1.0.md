# CP-MVP2-07 — RCA, Replanning & Governance

### Specification — v1.0

> **Status:** APPROVED / FROZEN — self-reviewed (sec. 15: no blocking issue found) under this task's own batched SPECIFY → SELF-REVIEW → FREEZE → IMPLEMENT authorization, mirroring the exact precedent already used for `docs/CP-MVP2-06-SPECIFICATION-v1.0.md`.
> **Origin:** No standalone frozen CP-MVP2-07 specification document existed in the repository prior to this task — confirmed by direct inspection (`find . -iname "*CP*07*"` under `docs/`, zero results) before this document was authored. This specification is derived faithfully from: the governing "CP-MVP2-07 — RCA, Replanning & Governance" task instruction's own sections 1–21 (which supplies specification-grade content: objective, failure taxonomy, RCA record model, replanning vocabulary, governance rules, testing requirements, deliverables, and gate criteria), README.md's one-line CP-07 description ("RCA + Replanning + Governance"), and the frozen `docs/CP-MVP2-06-SPECIFICATION-v1.0.md` (secs. 13/15/28), which already names CP-MVP2-07 as the sole authorized future consumer of CP-06's recorded `LOCATOR_FAILURE`/`ASSERTION_FAILURE` evidence. Nothing in this document was invented beyond what those sources establish.
> **Important:** This document does not implement CP-MVP2-07 by itself (implementation is a later section of the same governing task) and does not modify any frozen artifact.

---

## 1. Objective

CP-MVP2-07 owns **evidence-based Root Cause Analysis (RCA), governed replanning decisions, and the deterministic governance enforcement** that sits between a real CP-MVP2-06 `ExecutionResult` and any future corrective action. It demonstrates that the Agentic QE system can consume real execution evidence, determine what happened, classify the failure, perform evidence-based RCA, determine whether replanning is permitted, and produce a governed, persisted outcome — **without** silently changing any upstream artifact and **without** implementing any capability CP-06 or CR-002 explicitly reserved for separate authorization.

### 1.1 CP-MVP2-07 owns

* Ingesting a real, persisted CP-MVP2-06 `ExecutionResult` (never manufacturing one).
* Deterministic failure classification (reusing, not reinventing, the frozen CP-MVP2-06 `FailureCategory`/`FailureSubtype` vocabulary — sec. 5).
* Structured, evidence-based RCA record production, with FACT/EVIDENCE/INFERENCE/CONCLUSION kept explicitly distinct (sec. 6).
* Treating historical evidence as supporting, never overriding, current evidence (sec. 7).
* A governed replanning decision (`REPLAN_ALLOWED` / `REPLAN_NOT_ALLOWED` / `HUMAN_REVIEW_REQUIRED` / `GOVERNANCE_BLOCKED`), including the valid outcome of recommending no replan (sec. 8/11).
* Deterministic enforcement that no prohibited silent change occurs (sec. 9).
* Persistence of every RCA/replanning/governance artifact as a first-class, reloadable repository artifact.

### 1.2 CP-MVP2-07 does NOT own

* Requirement interpretation, testcase generation, test-data generation, or Playwright/locator generation (CP-03/04/05 — unchanged).
* Real browser execution itself (CP-06 — unchanged; CP-07 only *consumes* CP-06's already-produced `ExecutionResult`).
* Runtime locator fallback or self-healing (remains CR-002's exclusive scope — sec. 10; CP-07 may only *recommend*, never implement).
* Performance testing (CP-08) or unified final reporting (CP-09).
* Any Post-MVP enhancement (Excel I/O, production-grade Playwright redesign, page-object modernization, self-healing frameworks — sec. 15 of the governing instruction).

## 2. Authoritative Architecture

```text
CP-MVP2-06 EXECUTION RESULT (real, persisted, unmodified)
      ↓
FAILURE DETECTION            (did overall_status indicate a real problem?)
      ↓
FAILURE CLASSIFICATION       (deterministic; reuses CP-06's own taxonomy)
      ↓
EVIDENCE COLLECTION          (logs, screenshots, upstream testcase/data/requirement context, historical prior executions of the same lineage)
      ↓
RCA                          (FACT → EVIDENCE → INFERENCE → CONCLUSION, confidence-rated)
      ↓
REPLANNING DECISION          (governed vocabulary; "do not replan" is a valid outcome)
      ↓
GOVERNANCE DECISION          (prohibited-change enforcement; CR-002 status re-affirmed, never self-authorized)
      ↓
PERSISTED OUTCOME            (first-class artifact, reloadable from a fresh process)
```

## 3. Frozen Upstream Contracts (verified by direct repository inspection)

* `execution/schema.py` — `OverallStatus`, `FailureCategory`, `FailureSubtype`, `FAILURE_SUBTYPE_TO_CATEGORY`, `ExecutionResult`, `StepResult`, `AssertionResult` — **reused verbatim, never redefined.**
* `execution/persist.py`, `execution/summary.py`, `execution/persisted_lifecycle.py` (Batch 1/2, additive, not frozen but stable) — the source of real `ExecutionResult` JSON this checkpoint ingests.
* `docs/CP-MVP2-06-SPECIFICATION-v1.0.md` secs. 13/14/15 — the failure taxonomy, retry prohibition, and self-healing boundary CP-07 must respect and never silently expand.
* `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md` — status `PROPOSED — NOT IMPLEMENTED. NOT AUTHORIZED`, re-confirmed, not changed by this checkpoint.
* `docs/CP-MVP2-06-GOVERNANCE-CLOSURE-*.md` — CP-06's formal closure (`GREEN WITH ADVISORIES`), treated as complete and not reopened.

## 4. CP-07 Input Contract

CP-07 consumes exactly one real, persisted `ExecutionResult` per RCA run (identified by `execution_id`, loaded from the real, timestamped `runs/YYYY/MM/DD/<execution_id>/final_result.json` path Batch 2's `execution/persist.py` already produces), plus, optionally, zero or more **other real, persisted `ExecutionResult`s** sharing the same `automation_id`/testcase lineage, used strictly as **historical evidence** (sec. 7). CP-07 never invents an `ExecutionResult`; if the identified execution_id cannot be loaded from disk, CP-07 produces a governed `BLOCKED`/`ERROR` disposition, never a fabricated RCA.

## 5. Failure Classification

CP-07 does not define a new failure taxonomy. It **reuses `execution.schema.FailureCategory`/`FailureSubtype` verbatim** (the same seven base categories and execution-specific subtypes CP-06 already froze) as the authoritative classification for `final_rca_classification`. No new category is invented "merely for convenience," per the governing instruction's own explicit instruction (sec. 5) — reuse, not reinvention, mirrors this project's standing precedent (CP-04/05/06 all reused, never reinvented, the governance-status vocabulary).

## 6. RCA Record Model

Every RCA conclusion is a persisted record with, at minimum, the following fields, each populated only from real data (never fabricated):

| Field | Source | Kind |
|---|---|---|
| `failure_symptom` | `ExecutionResult.overall_status` + `.failure_summary` | FACT |
| `observed_evidence` | `ExecutionResult.step_results`, `.assertion_results`, `.evidence_references` | EVIDENCE |
| `requirement_testcase_data_context` | `ExecutionResult.requirement_ids`/`.testcase_id`/`.test_data_set_id`, cross-checked against the real persisted testcase/dataset artifacts | EVIDENCE |
| `historical_evidence` | Zero or more other real, persisted `ExecutionResult`s for the same automation lineage (sec. 7) | EVIDENCE (supporting only) |
| `agent_inference` | A disclosed, deterministic, rule-based interpretation of the evidence above — never an invented cause, never an LLM guess presented as fact | INFERENCE, explicitly labeled |
| `root_cause_hypothesis` | Derived from `agent_inference` | CONCLUSION, explicitly labeled |
| `confidence` | `HIGH` / `MEDIUM` / `LOW`, assigned deterministically from how directly the evidence supports the hypothesis (e.g. an identical failure across every available historical execution of the same lineage is `HIGH`; a single occurrence with no corroborating history is `MEDIUM`) | — |
| `final_rca_classification` | One of the reused `FailureCategory`/`FailureSubtype` values (sec. 5) | CONCLUSION |
| `recommended_next_action` | A plain, disclosed recommendation string — never an authorization, never self-executed | RECOMMENDATION |

`agent_inference` and `root_cause_hypothesis` are **always** rendered with an explicit label distinguishing them from `failure_symptom`/`observed_evidence` (FACT/EVIDENCE) — the governing instruction's own explicit rule ("Do not present inference as fact") is enforced structurally (separate, always-labeled fields), not merely by convention.

## 7. Historical Evidence Policy

Historical `ExecutionResult`s for the same automation lineage may be loaded and cited, but **only ever as supporting context** for `confidence` and `historical_evidence` — they never override, replace, or outrank the current execution's own `failure_classification`/`failure_summary` when deriving `final_rca_classification`. If historical evidence and current evidence would suggest different classifications, **current evidence always wins**; the disagreement itself is recorded, not silently resolved in favor of history.

## 8. Replanning Decision Model

```text
REPLAN_ALLOWED           -- a governed, non-prohibited corrective action exists and may proceed automatically
REPLAN_NOT_ALLOWED        -- no automated corrective action is authorized for this failure class
HUMAN_REVIEW_REQUIRED     -- a corrective path may exist, but selecting/authorizing it is a Human + Di decision, not CP-07's to make
GOVERNANCE_BLOCKED        -- a specific, named governance rule (e.g. CR-002 non-authorization, the CP-06 self-healing boundary) directly prohibits the only available corrective action
```

A `ReplanningRecord` states: `reason`, `evidence` (references into the RCA record), `proposed_change` (if any — described, never applied), `affected_artifacts` (testcase/automation/data IDs), `expected_benefit`, `governance_impact`, and `human_approval_required: bool`. **`REPLAN_NOT_ALLOWED` / `HUMAN_REVIEW_REQUIRED` are valid, complete Agentic outcomes** — CP-07 must never synthesize an artificial replan merely to exercise the feature (governing instruction sec. 11).

## 9. Prohibited Actions (absolute)

CP-07 must **never**, under any circumstance:

* change a requirement, testcase, expected result, or test data to obtain a different outcome;
* remove or weaken a failing assertion;
* invent a missing business step;
* implement runtime locator fallback or any other self-healing behavior (remains CR-002's exclusive, unauthorized scope);
* retry a prohibited action;
* report a failed execution as `PASS`;
* bypass DATA-OQ-01, the authorization-precondition gate, or any other CP-06 governance gate.

A deterministic **prohibited-change guard** (sec. 14/§9 governance enforcement) re-verifies, at the end of every CP-07 run, that no frozen file and no upstream persisted artifact was modified by that run — mirroring the `git diff --stat`-style integrity check already used at every prior checkpoint closure in this project, implemented here as an in-process content-hash comparison (no `git` invocation required at runtime).

## 10. CR-002 Boundary

CR-002 (`docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`) remains **OPEN — FUTURE CHANGE**, not authorized, not implemented. CP-07 may **record** a recommendation that CR-002 be authorized (as a `recommended_next_action` / `ReplanningRecord.proposed_change`, always clearly labeled `NOT AUTHORIZED — RECOMMENDATION ONLY`), but must never self-authorize or implement it, even when the RCA's own root-cause hypothesis is locator-related.

## 11. Governance Decision Model

```text
ACTION_AUTHORIZED         -- a governed, in-scope corrective action was identified and is authorized under an EXISTING frozen contract (rare; most CP-07 findings will not reach this)
ACTION_DEFERRED_TO_HUMAN  -- a corrective path exists but requires a Human + Di decision (mirrors HUMAN_REVIEW_REQUIRED)
NO_ACTION_REQUIRED        -- the execution's outcome requires no corrective action (e.g. a genuine PASS, or a FAIL correctly attributable to an already-fully-disclosed, accepted limitation)
GOVERNANCE_BLOCKED        -- a named governance rule directly prohibits the only available action
```

## 12. Evidence Persistence

Every CP-07 run persists, as first-class, `persistence/envelope.py`-backed artifacts (reused, unmodified, exactly as every prior checkpoint's persistence layer already does): the RCA record, the replanning record, and the governance record — plus a human-readable Markdown report and summary under `docs/claude-execution-reports/CP-MVP2-07/`, per this project's own established reporting convention.

## 13. Testing Requirements

Deterministic, automated tests must verify: evidence ingestion (including the missing-execution-id case), failure classification (reuse, never redefinition), RCA field separation (FACT/EVIDENCE/INFERENCE/CONCLUSION never conflated), historical-evidence precedence (current evidence always wins on disagreement), the replanning decision vocabulary (including a real `HUMAN_REVIEW_REQUIRED`/`REPLAN_NOT_ALLOWED` case — never an artificial `REPLAN_ALLOWED` manufactured to exercise the feature), governance enforcement (the prohibited-change guard actually detects a tampering attempt in a dedicated test), CR-002 remaining unauthorized (a direct assertion against the real proposal document's status line), persistence (real save + real reload), and deterministic behavior (running the same pipeline twice over the same input produces byte-identical RCA content, modulo the one disclosed volatile timestamp field `persistence/envelope.py` already knows how to ignore).

## 14. Regression & Frozen-Artifact Integrity

Every CP-07 implementation task must re-verify, by direct `git diff`, that CP-01–06 (specifications, freeze checkpoints, and implementation files), the Approved SRS, and the CP-06 governance closure report remain byte-for-byte unchanged, and that the full regression suite remains green with the new CP-07 tests added (never removed or weakened to obtain green).

## 15. Self-Review

Performed against: the governing task instruction's own sections 1–21 (source content, §Origin above); the frozen CP-06 specification (no boundary crossed — sec. 3); CP-06's governance closure (not reopened); the Approved SRS (not touched); this project's standing governance principles (no fabrication, no silent change, reuse over reinvention, deterministic-code-decides). **Result: PASS — no blocking issue found.** One internal-consistency completion was made before computing the final SHA-256: the header above was written directly as `APPROVED / FROZEN` (this document's self-review concludes PASS within the same authoring pass, mirroring the exact precedent already used for CP-MVP2-06's own specification) rather than staged through an intermediate `DRAFT` state.

## 16. Acceptance Criteria

* Scope is unambiguous (sec. 1) and does not silently absorb CP-08/09 or Post-MVP work.
* CP-06's frozen contract is treated as authoritative input, never reopened (sec. 3/4).
* Failure classification reuses, never reinvents, CP-06's taxonomy (sec. 5).
* RCA structurally separates FACT/EVIDENCE/INFERENCE/CONCLUSION (sec. 6).
* Historical evidence is explicitly subordinate to current evidence (sec. 7).
* The replanning vocabulary supports, and does not penalize, a "do not replan" outcome (sec. 8/11 — via §11's outcome, not a numbered section here).
* Every prohibited action (sec. 9) is enforced, not merely documented.
* CR-002 is re-affirmed as unauthorized, never self-authorized (sec. 10).
* Every artifact is persisted as a first-class, reloadable repository artifact (sec. 12).
* Testing requirements (sec. 13) and regression/integrity requirements (sec. 14) are both satisfied by the implementation.

## 17. Versioning and Freeze

Version 1.0. SHA-256 computed and recorded in `docs/CP-MVP2-07-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md` immediately after this document's authoring, before any implementation code is written.
