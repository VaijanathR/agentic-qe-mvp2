# CP-MVP2-09 Specification v1.0 — Unified Final QE Reporting

**Status: APPROVED / FROZEN — self-reviewed (sec. 14: no blocking issue found) under this
task's own batched SPECIFY → SELF-REVIEW → FREEZE → IMPLEMENT authorization, mirroring the
exact precedent already used for `docs/CP-MVP2-06-SPECIFICATION-v1.0.md`,
`docs/CP-MVP2-07-SPECIFICATION-v1.0.md`, and `docs/CP-MVP2-08-SPECIFICATION-v1.0.md`.**

**Origin note:** No standalone CP-MVP2-09 specification existed anywhere in the repository
prior to this task (confirmed via `find . -iname "*CP*09*"` — no genuine match). This document
is derived faithfully from this task's own governing instruction sections 1–29 and from the
Approved MVP2 SRS v1.0's own forward references to a final, unified QE report as the closing
MVP2 checkpoint. Nothing invented beyond what those sources already establish.

## 1. Objective

### 1.1 CP-09 owns
- Producing **one** authoritative, evidence-backed Unified QE Report synthesizing the
  complete, real MVP2 Agentic QE lifecycle (CP01–CP08), answering the 18 reviewer questions
  in the governing instruction §3.
- A deterministic, read-only aggregation layer (`reporting/gather.py`) that counts and groups
  facts already recorded by each upstream, frozen pipeline — never re-deriving or
  reinterpreting a stored status, never invoking an LLM.
- Preserving the evidence hierarchy (Approved baseline → direct system evidence → current
  testing artifact → historical evidence → agent inference) and the FACT/OBSERVED/DERIVED/
  INFERRED/OPEN-DECISION distinction throughout the report.
- Explicitly separating "covered by test design" from "actually executed" from "verified PASS
  evidence" for every reported requirement (governing instruction §6).
- Preparing the evidence base for a future, separate Human + Di final MVP governance gate —
  never declaring that gate itself.

### 1.2 CP-09 does NOT own
- CP-01–08 responsibilities, re-execution, or re-governance of any kind.
- Any new real browser execution, RCA, replanning, or performance run beyond what already
  exists as persisted evidence (the report may cite existing evidence; it does not manufacture
  new evidence to fill a gap).
- CR-002 (runtime locator fallback) — remains OPEN, NOT AUTHORIZED, listed only as backlog.
- Any post-MVP enhancement (governing instruction §16).
- The final MVP approval gate itself (governing instruction §23) — that is a separate,
  future Human + Di action.

## 2. Authoritative Architecture

```
Persisted CP01-CP08 evidence (testcases/, testdata/, rbtp/, dependencies/,
traceability/, automation/, runs/, rca/, performance/)
      -> reporting/gather.py  (deterministic, read-only counts/groupings; no LLM)
      -> Unified Final QE Report (hand-authored prose, every number traceable
         to a gather_*() call; no number appears in the report that gather.py
         did not also produce)
      -> docs/claude-execution-reports/CP-MVP2-09/
```

## 3. Frozen Upstream Contracts

`requirements/MVP2_SRS_v1.0_APPROVED.md` (35 total requirement IDs; §9.1/§9.2 performance
scope/non-approval; §13 open items), all CP-01–08 specifications/freeze-checkpoints, the
CP-06 and CP-07 governance-closure reports, and the CP-08 execution + advisory-reconciliation
reports — all treated as closed and untouched (governing instruction §2).

## 4. Real-vs-Fixture Evidence Discipline

`runs/` (CP-06's real execution corpus, intentionally not git-tracked per this repository's
own `.gitignore`) also contains synthetic executions produced by this project's own pytest
suites (fixture testcase_ids such as `TC-X`, `TC-X-01`, `TC-TEST-01`; fixture execution_ids
such as `T1`–`T9`, `EXEC-ISOLATION-01`, `T-UNRESOLVED`). `reporting/gather.py` deterministically
excludes these — by requiring `testcase_id` membership in the actually-persisted, real
`testcases.persist.list_persisted_testcase_ids()` set, never a hardcoded id list — so the
Unified Report never counts a unit-test fixture as real QE evidence.

## 5. Committed-vs-Local-Only Evidence Discipline

Per the CR-001-era Repository Persistence Closure decision (already made and disclosed
earlier in this project, not re-litigated here), `automation/generated/PW-*` and the entire
`runs/` tree are real, on-disk, but deliberately **not git-committed**. The Unified Report
must state this distinction explicitly wherever it cites such evidence, rather than implying
every cited artifact is reproducible from a fresh clone.

## 6. Result Vocabulary Reuse

Reuses, verbatim, every governed vocabulary already frozen by CP-06 (`OverallStatus`,
`FailureCategory`, `FailureSubtype`), CP-07 (`Confidence`, `ReplanningDecision`,
`GovernanceDecision`), and CP-08 (`CapabilityResult`, `NumericSLAResult`). No new
PASS/FAIL/BLOCKED-style vocabulary is invented for CP-09.

## 7. Consistency / Contradiction Check

Before the Unified Report is finalized, every number and status it cites is cross-checked
against the live output of `reporting/gather.py` run against the real, current repository
state (governing instruction §21). Any contradiction found between authoritative sources that
cannot be deterministically resolved from those sources themselves triggers STOP → REPORT →
HUMAN + DI DECIDE, per the golden rule.

## 8. Evidence Persistence

The Unified Final QE Report is persisted as a single Markdown document under
`docs/claude-execution-reports/CP-MVP2-09/`, per governing instruction §22's 19-section
structure.

## 9. Testing Requirements

`tests/test_cp09_reporting.py` verifies every `gather_*()` function against the real,
persisted corpus: correct counts, correct real-vs-fixture separation, correct
committed-vs-local-only distinction where applicable, non-fabrication of governance/CR-002
status, and deterministic repeated-call behavior.

## 10. Regression & Frozen-Artifact Integrity

CP-01–08 specifications/implementations/governance-closures and the Approved SRS must show
zero `git diff --stat` drift after CP-09's implementation. Full regression suite must pass
with zero existing test weakened or removed.

## 11. Self-Review

Reviewed against governing instruction §§1–29: **PASS — no blocking issue found.** The
report's own honesty about partial requirement/execution coverage (governing instruction §6,
§19) is treated as the correct, intended CP-09 outcome — not a defect to be minimized.

## 12. Acceptance Criteria (checklist)

- [ ] `reporting/gather.py` deterministically reproduces every count cited in the Unified
      Report, verified by `tests/test_cp09_reporting.py` against the real corpus.
- [ ] The Unified Report answers all 18 reviewer questions (governing instruction §3).
- [ ] Requirement/testcase/test-data/automation coverage sections each distinguish
      design-time coverage from executed coverage from verified-PASS coverage.
- [ ] CP-08's reconciled (not the stale historical-report) figures are used.
- [ ] CR-002 is listed as OPEN — NOT AUTHORIZED, never as implemented.
- [ ] No frozen artifact is modified; zero `git diff --stat` drift.
- [ ] No final MVP gate is declared by this checkpoint.

## 13. Versioning and Freeze

v1.0 — frozen this task via `docs/CP-MVP2-09-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`, with
implementation proceeding in the same batched task, mirroring the CP-06/07/08 precedent.
