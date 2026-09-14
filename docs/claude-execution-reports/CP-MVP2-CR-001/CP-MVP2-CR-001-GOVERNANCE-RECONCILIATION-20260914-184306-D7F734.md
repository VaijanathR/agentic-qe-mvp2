# CP-MVP2-CR-001 — Governance Reconciliation Report

**This report does not declare Di's independent final gate. It reconciles
the canonical CR-001 governance documents with the completed Batch 1
implementation and evidence, per Di's independent engineering
assessment: Batch 1 implementation PASS with advisories; governance
BLOCKED only on document reconciliation.**

## A. Scope

Governance reconciliation and repository-consistency audit only. No new
functional implementation, no redesign, no modification to the
persistence architecture, RBTP, testcase/test-data/Playwright
generation, CP-06 execution, any frozen CP-MVP2-01–06 specification, the
Approved SRS, or `llm/client.py`. The Batch 1 implementation (commit
`415038c`) and its evidence (commit `546c568`) remain the implementation
under review, unmodified by this task.

## B. Previous Inconsistency

The two canonical CR-001 documents —
`docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md` and
`docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md` — still
contained language written *before* Batch 1 was authorized and executed:

* Status lines read `PROPOSED — PENDING HUMAN + DI REVIEW. NOT APPROVED.
  NOT IMPLEMENTED.` (CR doc) and `PROPOSED — PENDING REVIEW. Design/
  analysis only; nothing in this document has been implemented.`
  (Architecture doc) — both stale once Batch 1 completed.
* The Architecture doc's Artifact Contract section (§C) stated "None of
  these artifacts exist yet; none is created by this CR" and listed
  "(proposed)" persistence locations that did not match the actual
  implemented paths (a flat `<id>.json` was proposed; the real
  implementation writes `<id>/v<N>.json` + `latest.json` via
  `persistence/envelope.py`).
* The Checkpoint Impact Matrix (§D) described CP-03/04/05/06 changes as
  "requires a scoped Change Request/implementation task" — future tense,
  even though that task had already occurred.
* Several Open Questions (§12) and Acceptance Criteria (§14) in the CR
  document had been partially updated in the prior task (RBTP
  definition only) but left the CP-06 directory-convention question,
  the persistence-trigger-point question, the versioning question, and
  the phasing question still phrased as open/undecided.
* The Migration Strategy (§E) still recommended a five-phase, separately
  frozen rollout and stated "No part of this migration strategy is
  executed by this CR" — contradicted by the fact Batch 1 executed all
  five phases together in one authorized batch.
* §C.8 ("Reusable Component Artifact") described actual page-object/
  utility source-file scaffolding (`automation/components/`, `pages/`,
  `utils/`) that Batch 1 never built — Batch 1 implemented only
  candidate *identification* (`automation/components.py`), folded into
  the Automation Traceability artifact, not a separate persisted
  artifact family.

## C. Reconciled State

Both documents were edited in place (never frozen documents — both were
still `PROPOSED` prior to this task, so this is legitimate correction of
a live, unfrozen document, not modification of a frozen artifact):

* Status lines changed to **`BATCH 1 IMPLEMENTATION AUTHORIZED AND
  COMPLETE`**, explicitly stating Di's independent engineering review
  result (`PASS with advisories`) and explicitly stating that this
  status describes implementation completion, **not** a final CR-001
  governance gate.
* Every Artifact Contract row (§C.1–C.11) updated from "(proposed)" flat
  paths to the actual implemented `persistence.envelope` directory
  structure (`<artifact_id>/v<N>.json` + `latest.json`).
* §C.8 rewritten to accurately describe candidate *identification* only
  — no source-file scaffolding, no independent persistence, folded into
  §C.9's `automation_to_components` field.
* §C.7 (Automation Artifact) now explicitly documents the discovered
  `AUTOMATION_ID_COLLISION_ADVISORY` directly on the `ID` field it
  concerns.
* The Checkpoint Impact Matrix (§D) rows for CP-03/04/05/06 changed from
  future-tense "requires a scoped task" to past-tense "IMPLEMENTED
  (Batch 1)," each explicitly re-stating that the frozen files
  themselves were not reopened (`git diff` empty).
* The Migration Strategy (§E) rewritten to record that the originally-
  recommended five-phase, separately-frozen rollout was explicitly
  superseded by the Human/Di-authorized decision to execute phases A–E
  together in one controlled batch — a recorded, deliberate deviation,
  not a silent one.
* CR-doc §§10–14 (Backward Compatibility, Regression Impact, Open
  Questions, Risks, Acceptance Criteria) updated to record actual
  resolutions: the CP-06 directory-convention question resolved as
  **additive-only, fully backward compatible** (frozen convention
  untouched); the persistence-trigger-point question resolved as an
  **explicit, separate call** (no frozen pipeline signature changed);
  the artifact-versioning question resolved via
  `persistence/envelope.py`'s immutable-version/mutable-pointer model;
  the phasing question resolved as **one controlled batch**; the
  historical-evidence-treatment question resolved for Batch 1 (no
  backfill performed; whether one should be authorized later remains
  genuinely open and non-blocking).

## D. RBTP Definition

**RBTP = Risk-Based Test Prioritization.**

> *"What should we test first, and why?"*

Confirmed correct and consistent in both canonical documents and in the
implemented `rbtp/schema.py`. It is explicitly distinct from the
Dependency/Reusability Matrix:

> *"What depends on what, what can be reused, and what should not be
> retested unnecessarily?"*

`tests/test_cr001_rbtp.py::test_rbtp_and_dependency_matrix_schemas_are_disjoint`
verifies this distinction at the schema-field level (no risk-factor
field, `priority`, or `risk_rationale` exists on `DependencyMatrix`).

## E. Batch 1 Architectural Decisions (as recorded in the reconciled CR)

1. **Persistent lifecycle artifacts** — persistence is now recorded for:
   Testcases, Requirement↔Testcase traceability, RBTP,
   Dependency/Reusability Matrix, Test Data, Testcase↔Test Data
   traceability, Playwright Automation, Automation↔Testcase
   traceability, reusable-component candidates (identification only),
   Execution persistence, and Execution Summary. The chain
   `REQ ↔ TC ↔ RBTP ↔ DATA ↔ AUTO ↔ COMPONENT ↔ EXECUTION ↔ EVIDENCE ↔ RESULT ↔ REPORT`
   is the recorded target architecture.
2. **Persistence model** — additive to the frozen checkpoint
   implementations. Existing frozen behavior remains intact (`git diff`
   empty against every CP-01–06 implementation file). No retroactive
   rewriting of frozen checkpoint artifacts occurred or is permitted.
3. **Timestamped execution persistence** — supported additively and
   backward-compatibly. `runs/YYYY/MM/DD/<execution_id>/` was added as a
   new, separate path (`execution/persist.py`); the existing frozen
   `runs/cp_mvp2_06/<execution_id>/` convention (`execution/evidence.py`)
   was not modified, renamed, or broken. Both paths coexist.

## F. Frozen Boundaries — Verified Unchanged

`git diff --stat 546c568 -- <files>` (the commit immediately preceding
this reconciliation task) against every one of the following returned
**empty**:

* `llm/client.py`
* `testcases/{schema,generate,validate,pipeline}.py`
* `testdata/{schema,generate,validate,pipeline,constraints}.py`
* `automation/{schema,generate,validate,pipeline,evidence}.py`
* `execution/{schema,validate,evidence,engine,pipeline}.py`
* `requirements/` (Approved SRS)
* `knowledge/`
* Every CP-MVP2-03/04/05/06 specification and freeze-checkpoint document
* Every file under `rbtp/`, `dependencies/`, `traceability/`,
  `persistence/`, and the Batch 1 `persist.py`/`components.py`/
  `summary.py`/`llm/rbtp_client.py` modules (confirmed unchanged since
  the Batch 1 evidence commit — this reconciliation task touched no
  code)
* `tests/` (no test file modified; no test added; none needed to be)

**No frozen artifact required modification. No STOP condition was
triggered.**

## G. Advisories

### G.1 `AUTOMATION_ID_COLLISION_ADVISORY`

Confirmed, recorded, not modified: the frozen `automation/generate.py`
constructs `automation_id` as `f"PW-{testcase_id}-01"`, which does not
incorporate the paired `test_data_set_id`. A testcase with multiple
eligible CP-04 datasets therefore causes CP-05 to generate multiple,
genuinely distinct `PlaywrightArtifact`s that all share one
`automation_id` (observed live: 6 distinct artifacts under
`PW-TC-REQ-REG-01-01-01`). Recorded facts:

* No data was lost — `persistence/envelope.py` retained all 6 as
  separate, immutable versions (`v1.json`…`v6.json`).
* Persistence remains version-safe by construction (this is exactly
  what the immutable-version model exists to guarantee).
* This was not silently corrected — frozen `automation/generate.py` was
  not touched, in Batch 1 or in this reconciliation task.
* This is a future CP-05 Change Request candidate (e.g., incorporating
  `test_data_set_id` into `automation_id`), not decided or implemented
  here.
* **This is NOT a Batch 1 failure** — it is a pre-existing CP-05
  characteristic that persistence made newly visible; the persistence
  layer's own behavior in the presence of this characteristic is
  correct and safe.

### G.2 Live-Claude RBTP Verification — PATH Limitation

Confirmed, recorded, not worked around: `ClaudeRBTPClient()` was
invoked in Batch 1 against a real accepted `REQ-REG-01` testcase; the
Windows-side Python subprocess environment used for that verification
could not resolve the `claude` CLI executable (`shutil.which("claude")
→ None`) — a cross-environment `PATH` resolution limitation of that
specific attempt. Recorded facts:

* This was honestly reported in the Batch 1 implementation report, not
  hidden or retried into a different outcome.
* No workaround was used to fabricate a live-Claude result — the client
  correctly raised `ClaudeProviderError` and the attempt was recorded as
  `BLOCKED`.
* Deterministic tests (10, in `tests/test_cr001_rbtp.py`) passed.
* Stub-LLM narrative validation passed, and a real `StubRBTPClient`
  narrative was produced in the live end-to-end run.
* This remains an advisory/verification limitation only.
* It does **not** justify, and was not used to justify, any change to
  the RBTP implementation or to any governance rule.

## H. Security Boundary

**Security/penetration testing remains POST-MVP/PARKED**, unchanged from
`README.md`'s existing scope statement. `docs/CP-MVP2-CR-001-SECURITY-DESIGN-BOUNDARY.md`
is confirmed design-only: no `security/` package, schema, pipeline, or
executable code exists anywhere in the repository. This reconciliation
task did not convert the design boundary into implementation scope and
did not touch `README.md`.

## I. Regression

`.venv/Scripts/python.exe -m pytest -q` (run once, after all
reconciliation edits) → **249 passed, 0 failed.**

Matches the expected Batch 1 baseline exactly. No test was added,
removed, or modified by this reconciliation task (a documentation-only
task; the audit determined no purely documentation-validation test was
genuinely necessary beyond the 45 already added in Batch 1).

## J. Repository Consistency Result

**Consistent, with one pre-existing, minor, non-blocking documentation
cross-reference discovered during this audit (not fixed, per this
task's own "do not modify the RBTP implementation" instruction — a
docstring is part of that implementation's source file):**

* `rbtp/schema.py`'s module docstring (line 7–8, written during Batch 1)
  references `docs/CP-MVP2-CR-001-RBTP-CORRECTION.md` — a file that was
  never created. The actual RBTP correction was applied directly to the
  two canonical CR-001 documents reconciled by this task, rather than
  as a separate correction file. This is a stale, dangling comment
  reference only; it does not affect behavior, does not affect any test
  result, and does not misstate the RBTP definition itself (the
  docstring's own stated definition, "Risk-Based Test Prioritization,"
  is correct). Left unmodified in this task, per the explicit
  instruction not to modify the RBTP implementation; flagged here for a
  future, separate documentation-only fix.

Beyond that one item:

* **Terminology is consistent** — "RBTP = Risk-Based Test Prioritization"
  appears identically across `docs/CP-MVP2-CR-001-PERSISTENT-LIFECYCLE-v1.0.md`,
  `docs/CP-MVP2-CR-001-ARCHITECTURE-IMPACT-ASSESSMENT-v1.0.md`, the
  Batch 1 implementation report, its summary, and `rbtp/schema.py`'s own
  stated definition. No document defines it as "Requirement-Based Test
  Plan" as a current, active definition — every remaining occurrence of
  that phrase is explicitly framed as the superseded historical reading
  being corrected, never as the governing definition.
* **Batch 1 scope is consistent** across the CR, the Architecture Impact
  Assessment, the implementation report, and its summary — same file
  list, same test count (45 new / 249 total), same advisories, same
  security-boundary statement.
* **Frozen boundaries are respected** — §F above.
* **Advisory findings are consistent** — both advisories appear
  identically worded in substance across the implementation report, its
  summary, and the now-reconciled CR documents.
* **No implementation claim contradicts evidence** — every claim in the
  reconciled documents (artifact counts, test counts, regression
  results, persistence paths, the CP-06 additive decision) was checked
  against the actual repository state (`git diff`, `pytest`, directory
  listings) before being written.
* **No governance document claims Di approval of the final CR-001 gate**
  — status lines were specifically worded ("BATCH 1 IMPLEMENTATION
  AUTHORIZED AND COMPLETE... not a final CR-001 governance gate") to
  avoid this; verified by direct `grep` for `APPROVED`/`Di gate`/`final
  gate` across both documents (§C above; only the unrelated "Approved
  SRS" proper-noun phrase remains).
* **No fabricated live-Claude verification exists** — the one live
  attempt (RBTP) is recorded as `BLOCKED`, honestly, in every document
  that mentions it; no document claims it passed.

## K. Governance Status

Per Di's independent engineering assessment (as given): **Batch 1
implementation — PASS with advisories.** The governance-documentation
inconsistency that previously blocked closure has been reconciled by
this task (§B/§C above).

**This report does not declare, and is not authorized to declare, Di's
independent final gate for CR-001 or for the Batch 1 implementation.**
That determination remains Di's separate, independent responsibility.
