# CP-MVP2-08 — Advisory Closure & Pre-CP09 Reconciliation

## Mission

Before starting CP-MVP2-09, perform a final **CP-MVP2-08 advisory-resolution and governance-reconciliation pass**.

The objective is to eliminate every actionable CP08 loose end that can legitimately be closed now, while explicitly and permanently distinguishing items that are genuine Human/Project decisions and therefore must remain outside CP08.

Do NOT start CP09 in this task.

Do NOT redesign CP08.

Do NOT reopen CP06 or CP07.

Do NOT introduce post-MVP enhancements.

---

# 1. Current CP08 Baseline

CP-MVP2-08 is currently:

**GREEN WITH ADVISORIES**

Implementation commit:

`77c7d64`

Current HEAD:

`77c7d64`

CP08 closure report:

`docs/claude-execution-reports/CP-MVP2-08/CP-MVP2-08-EXECUTION-REPORT-20260915-093624.md`

Current reported regression:

* focused: 14/15 passed, 1 skipped
* full: 345/346 passed, 1 skipped

Real JMeter execution was performed through WSL2 and produced real persisted evidence.

---

# 2. Inspect Before Acting

Inspect:

1. CP08 frozen specification.
2. CP08 closure report.
3. CP08 implementation.
4. JMeter `.jmx`.
5. persisted `.jtl`.
6. JMeter execution log.
7. performance record.
8. CP08 focused tests.
9. performance pipeline.
10. current `.gitignore`.
11. current repository HEAD.
12. Approved MVP2 SRS §9 and §13.
13. CP01–CP07 frozen artifacts and closure reports.

Do not rely only on this instruction.

Verify the actual repository state.

---

# 3. Advisory Classification

Classify every CP08 advisory into exactly one of:

### A. ACTIONABLE AND CLOSABLE NOW

Something that can be fixed or formally reconciled without changing any frozen requirement/specification.

### B. ACCEPTED MVP SCOPE BOUNDARY

A deliberate limitation that is not a defect and does not require implementation.

### C. HUMAN/PROJECT DECISION

Something that cannot legitimately be closed by Claude because it requires an external business/project decision.

### D. TRUE BLOCKER

Something that prevents CP08 from being considered closed.

Do not manufacture category D findings.

---

# 4. Numeric Performance Threshold Advisory

The Approved SRS currently has no approved numeric performance threshold.

The CP08 report correctly classified numeric SLA validation as:

**INCONCLUSIVE**

Do NOT:

* invent a response-time target;
* invent a throughput target;
* invent a concurrency target;
* invent an error-rate threshold;
* modify the Approved SRS;
* modify CP08 acceptance criteria;
* convert INCONCLUSIVE into PASS.

This is a **Human/Project Target decision**, not a CP08 implementation defect.

Instead, formally reconcile it as:

> **ACCEPTED AS STANDING HUMAN/PROJECT DECISION — NOT A CP08 BLOCKER**

Verify that:

* the SRS remains unchanged;
* the CP08 frozen specification remains unchanged;
* the CP08 result remains honest;
* the issue is clearly carried forward as a project-level decision rather than an unresolved CP08 implementation defect.

If an existing governance mechanism already records this appropriately, reuse it.

Do not create duplicate conflicting governance documents.

---

# 5. Bounded Books / GET-Only Scenario

The CP08 scenario intentionally used:

* GET /
* GET /books
* 5 virtual users
* 5-second ramp-up
* 3 loops/user
* 1000 ms pacing
* 30 total requests

The scenario was deliberately read-only and conservative because the target is a shared public third-party Demo Web Shop.

This was a conscious CP08 design choice.

Do NOT expand the workload merely to eliminate this advisory.

Do NOT introduce:

* registration load;
* cart mutation load;
* checkout load;
* duplicate business entities;
* destructive/state-mutating traffic;
* additional categories solely for cosmetic completeness.

Instead formally classify this as:

**ACCEPTED MVP SCOPE BOUNDARY**

Verify that the CP08 report already clearly explains the rationale.

If a concise reconciliation artifact is needed, create one without changing the frozen specification.

Do not alter the CP08 frozen specification merely to remove the word "advisory."

---

# 6. JMeter/JRE External Dependency

Review whether JMeter 5.6.3 and Java 17 being external dependencies is genuinely an actionable problem.

The project already intentionally avoids vendoring browser binaries and other heavyweight runtime dependencies.

Do NOT vendor JMeter or Java merely to make the repository appear self-contained.

If the current documentation already provides a reproducible acquisition/configuration mechanism, classify this as:

**ACCEPTED MVP RUNTIME DEPENDENCY**

If documentation is genuinely insufficient to reproduce the CP08 execution, improve only the documentation necessary to make the existing external dependency contract explicit.

Do not add unnecessary infrastructure.

---

# 7. Windows Regression Skip — Investigate Carefully

Current state:

One CP08 focused test is skipped because the Windows-venv regression environment does not have `JMETER_BIN` / `JAVA_HOME`.

The real execution was performed through WSL2 and independently verified.

Determine whether the skipped test can be legitimately converted to PASS using the existing environment/tooling without:

* vendoring JMeter;
* inventing execution results;
* mocking the JMeter execution;
* weakening the test;
* changing CP08 acceptance criteria;
* introducing a fragile machine-specific dependency.

### If a clean solution exists:

Implement it.

Then run:

* focused CP08 suite;
* full regression;
* actual live JMeter execution if required;
* fresh-process verification.

### If no clean solution exists:

Keep the skip.

Explicitly classify it as:

**ENVIRONMENT-BOUND REGRESSION SKIP — REAL EXECUTION ALREADY VERIFIED VIA WSL2**

Do NOT fake or mock the missing Windows dependency merely to obtain 15/15.

---

# 8. Evidence Integrity

Do not change the existing real performance measurements.

The following must remain traceable to the committed raw evidence:

* 30 samples;
* 0 errors;
* 614.867 ms average;
* 518 ms median;
* 1015 ms p90;
* 1426 ms maximum;
* 1.737 req/s.

Do not regenerate measurements merely to make them look better.

If another real run is performed, preserve the distinction between the original CP08 evidence and any new verification run.

---

# 9. Frozen Artifact Protection

Absolutely do not modify:

* Approved SRS v1.0;
* CP01–CP07 specifications;
* CP01–CP07 implementations;
* CP06 closure;
* CP07 closure;
* CP08 frozen specification;
* CP08 acceptance criteria.

If resolving an advisory appears to require such a modification:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 10. Regression

After any legitimate implementation/documentation change:

Run:

1. CP08 focused regression.
2. Full regression.
3. Frozen-artifact integrity check.
4. Fresh-process verification.

Report exact counts.

Do not weaken, remove, skip, or alter existing tests simply to improve the result.

---

# 11. Advisory Closure Report

Create a single authoritative report:

`docs/claude-execution-reports/CP-MVP2-08/CP-MVP2-08-ADVISORY-CLOSURE-RECONCILIATION-<timestamp>.md`

The report must contain:

1. CP08 baseline commit.
2. Current HEAD.
3. Each original advisory.
4. Classification.
5. Action taken, if any.
6. Evidence supporting closure/acceptance.
7. Items explicitly requiring Human/Project decision.
8. Regression results.
9. Frozen-artifact integrity.
10. Final CP08 advisory status.
11. Explicit statement whether CP09 can begin without carrying any actionable CP08 implementation debt.

Use this distinction:

### CLOSED

Actionable implementation issue resolved.

### ACCEPTED

Deliberate MVP boundary/dependency, no implementation action required.

### HUMAN DECISION REQUIRED

Cannot be closed by Claude without authorized project decision.

### BLOCKED

Only use if something genuinely prevents CP08 closure.

---

# 12. Desired End State

The desired result is NOT necessarily "zero words called advisory."

The desired result is:

> **Zero unresolved ACTIONABLE CP08 implementation issues.**

A legitimate Human/Project decision may remain open.

That is acceptable and should not be disguised as an implementation defect.

If the only remaining item is the missing numeric performance target, explicitly state:

**CP08 implementation debt = ZERO**

**Human/Project target decision = OPEN**

**CP08 = CLOSED**

---

# 13. CP08 Final Status

If all actionable items are resolved and no blocker exists, formally reconcile CP08 as:

**CP-MVP2-08 — CLOSED**

with an appropriate notation such as:

**GREEN — CLOSED; Human/Project NFR target decision carried forward separately**

or, if governance conventions require retaining the advisory label:

**GREEN WITH ADVISORIES — CLOSED; ZERO ACTIONABLE CP08 DEBT**

Do not change the historical CP08 execution report merely to rewrite history.

The new reconciliation report should be the authoritative closure of the advisory state.

---

# 14. CP09 Readiness

At the end explicitly state:

* whether CP08 has zero actionable implementation debt;
* whether any Human/Project decision remains;
* whether any blocker remains;
* whether CP09 is authorized to begin.

CP09 must NOT be started in this task.

---

# 15. Git Discipline

Commit only legitimate CP08 advisory-resolution/reconciliation changes.

Use a clear commit message such as:

`chore: reconcile CP-MVP2-08 advisories before CP09`

Do not include unrelated changes.

Report:

* commit SHA;
* final HEAD;
* changed files;
* focused regression;
* full regression.

---

# 16. Completion Notification

When the entire task is complete:

**Play the Windows system notification sound.**

Do NOT display a message box.

The sound is the only completion notification.

---

# 17. Final Response

Return:

* CP08 advisory-resolution result;
* actionable issues closed;
* accepted scope boundaries;
* Human/Project decisions still open;
* focused regression;
* full regression;
* commit SHA;
* final HEAD;
* CP09 readiness.

Do not start CP09 automatically.
