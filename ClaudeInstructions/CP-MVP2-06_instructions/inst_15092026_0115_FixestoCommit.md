# CR-001 — Repository Persistence Closure

## Local Notes + Generated Artifact Commit

### GOVERNED IMPLEMENTATION TASK

Buddy/Di has identified an important repository-persistence gap during forensic verification.

The CP-MVP2 generated artifacts currently exist in the local Claude Code repository and are reloadable from disk, but they are NOT committed to `origin/main`.

At the same time, the Human is adding additional notes to the local repository and explicitly wants those notes committed to Git.

This task must therefore establish a clean, auditable transition from:

LOCAL REPOSITORY STATE
→ INVENTORY
→ CLASSIFY
→ VERIFY
→ COMMIT
→ PUSH
→ INDEPENDENTLY VERIFY ON origin/main

---

# 1. GOVERNANCE RULE

Do NOT blindly `git add .` and commit everything.

First inspect the complete working-tree state.

The objective is to preserve and commit all legitimate Human-authored notes and intended CP-MVP2 artifacts while avoiding accidental inclusion of:

* secrets;
* credentials;
* API keys;
* temporary files;
* caches;
* virtual environments;
* OS files;
* generated runtime noise;
* unintended external repositories;
* unrelated files;
* test-run pollution;
* temporary logs that are not intended evidence.

Do NOT delete or modify anything merely to make the working tree clean.

If a file is ambiguous, REPORT it before deciding whether it should be committed.

---

# 2. FROZEN BOUNDARIES

The following remain frozen unless a separate approved change explicitly authorizes modification:

* CP-MVP2-01
* CP-MVP2-02
* CP-MVP2-03
* CP-MVP2-04
* CP-MVP2-05
* CP-MVP2-06
* Approved SRS v1.0

Do NOT redesign or reinterpret them.

Do NOT change their content merely to make this task pass.

If any local note or artifact conflicts with a frozen specification:

STOP → REPORT → HUMAN + DI DECIDE.

---

# 3. FIRST STEP — FULL LOCAL INVENTORY

Before changing anything, capture:

```bash
git status --short
git status --short --untracked-files=all
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
```

Then inventory all untracked and modified files.

Pay particular attention to:

```text
testcases/generated/
testdata/generated/
rbtp/generated/
dependencies/generated/
traceability/
automation/generated/
reports/
docs/
ClaudeInstructions/
```

Also inspect any other newly created local directories/files.

Do NOT assume a file is temporary merely because it is untracked.

---

# 4. HUMAN NOTES — PRIORITY

The Human has explicitly stated:

> "I am adding some notes to the local repository and I want all that committed to git."

Therefore:

### ALL clearly Human-authored project notes intended for this repository MUST be included in the commit.

Identify them explicitly in the report.

For each such note record:

* path
* filename
* whether modified/new
* brief purpose
* whether included in commit

Do NOT overwrite, reformat, relocate, or rewrite the Human's notes.

Do NOT remove notes simply because they are not part of the existing architecture.

If a note appears to belong to an external repository/subdirectory, report it separately rather than silently moving it.

---

# 5. GENERATED ARTIFACTS — DO NOT REGENERATE

The forensic investigation already established that these artifacts exist locally:

### Real testcase corpus

9 real testcases:

```text
TC-REQ-ACO-03-01
TC-REQ-ACO-03-02
TC-REQ-CART-03-01
TC-REQ-CART-03-02
TC-REQ-CART-03-03
TC-REQ-PAY-01-01
TC-REQ-PAY-01-02
TC-REQ-REG-01-01
TC-REQ-REG-01-02
```

plus the disclosed synthetic:

```text
TC-MECHANISM-CHECK-01
```

### Real test-data corpus

24 real datasets:

* 16 ACCEPTED
* 2 REJECTED
* 6 POSSIBLE_DUPLICATE

plus the disclosed synthetic:

```text
TD-MECHANISM-CHECK-01
```

### Additional artifacts

* 9 RBTP artifacts
* dependency/reusability matrix
* requirement↔testcase traceability
* testcase↔test-data traceability
* other Batch-1 generated lifecycle artifacts where actually present

DO NOT regenerate these artifacts.

Preserve their existing contents.

Do not convert the stub-generated artifacts into live-LLM artifacts.

The provenance must remain exactly as represented in the artifacts:

```text
generator = stub-deterministic-v1
```

unless a separate approved change explicitly authorizes regeneration.

---

# 6. CLASSIFY GENERATED ARTIFACTS

Before committing them, classify each artifact as:

### A. Canonical project artifact

Intended to be versioned and retained in Git.

### B. Evidence artifact

Useful for audit/reproducibility and intended to be retained.

### C. Runtime/temporary artifact

Should remain local/ignored.

### D. Synthetic mechanism-check artifact

Keep clearly labeled as synthetic; do not represent it as real production corpus.

### E. Ambiguous

STOP and report.

Do not silently choose for category E.

---

# 7. PERSISTENCE DECISION

For this task, treat the following as intended repository-grade lifecycle artifacts unless there is concrete evidence they are temporary:

```text
testcases/generated/
testdata/generated/
rbtp/generated/
dependencies/generated/
traceability/
```

These are the actual persistent Agentic QE lifecycle artifacts demonstrated by Batch 1.

They should therefore be committed so that:

```text
local repository
      ↓
git commit
      ↓
origin/main
      ↓
fresh clone
      ↓
same artifacts available
```

Do NOT include runtime execution directories merely because they exist.

In particular, inspect:

```text
runs/
```

and retain its existing governed behavior.

Do not change `.gitignore` merely to force runtime outputs into Git.

---

# 8. REPORTS AND NOTES

Include legitimate project documentation/evidence that was intentionally created for the lifecycle.

Especially inspect:

```text
docs/claude-execution-reports/
docs/
ClaudeInstructions/
```

Human-authored notes must be retained.

Existing governance/evidence reports must not be deleted.

---

# 9. TESTCASE / DATA QUALITY CHECK BEFORE COMMIT

Before committing the generated corpus, verify:

### Testcases

* 9 real testcase files exist.
* IDs match expected IDs.
* requirement IDs resolve to Approved SRS.
* governance status remains ACCEPTED where previously established.
* no accidental modifications occurred.

### Test data

* 24 real datasets exist.
* 16 ACCEPTED.
* 2 REJECTED.
* 6 POSSIBLE_DUPLICATE.
* testcase IDs resolve.
* requirement IDs resolve.
* no accidental modifications occurred.

### Traceability

Verify representative:

```text
REQ → TC
TC → DATA
TC → RBTP
```

Do not regenerate anything.

---

# 10. CHECK FOR ACCIDENTAL TEST POLLUTION

The forensic investigation discovered that running Batch-2 tests can create additional execution-summary versions under:

```text
reports/execution_summaries/BATCH2-TEST/
reports/execution_summaries/BATCH2-TEST2/
```

Do NOT automatically commit such test pollution.

Determine whether those files are:

* legitimate evidence;
* temporary test output;
* unintended persistence pollution.

If ambiguous, report them.

Do NOT fix the underlying idempotency issue during this task.

That remains a separate engineering advisory.

---

# 11. NO SPECIFICATION CHANGES

Do not modify:

```text
requirements/MVP2_SRS_v1.0_APPROVED.md
docs/CP-MVP2-03-SPECIFICATION-v1.0.md
docs/CP-MVP2-04-SPECIFICATION-v1.0.md
docs/CP-MVP2-05-SPECIFICATION-v1.0.md
docs/CP-MVP2-06-SPECIFICATION-v1.0.md
```

unless a separate explicit approved change authorizes it.

The stale journey-traceability wording discovered during forensic analysis must remain untouched.

---

# 12. NO CR REDESIGN

Do not reopen or redesign CR-001.

Do not change:

* RBTP definition;
* architecture;
* Batch-1 scope;
* Batch-2 scope;
* security scope;
* CP-01–06 frozen boundaries.

This task is specifically closing the **repository persistence gap** and preserving Human notes.

---

# 13. CREATE ONE CONTROLLED COMMIT

After classification and verification:

Stage ONLY the intended files.

Do NOT use an indiscriminate:

```bash
git add .
```

unless the final file inventory has been explicitly inspected and every item is known to be intended.

Show the exact staged file list:

```bash
git diff --cached --name-status
```

Then commit everything approved for persistence in ONE controlled commit.

Suggested commit message:

```text
chore: persist CP-MVP2 lifecycle artifacts and project notes
```

Use the actual commit hash in the final report.

---

# 14. PUSH TO origin/main

After the commit:

```bash
git push origin main
```

Verify:

```bash
git rev-parse HEAD
git rev-parse origin/main
```

They MUST match.

---

# 15. CRITICAL — VERIFY THE ACTUAL REMOTE REPOSITORY

Do NOT stop after `git push`.

Verify from the repository itself that the following now exist in `origin/main`:

```text
testcases/generated/
testdata/generated/
rbtp/generated/
dependencies/generated/
traceability/
```

Use:

```bash
git ls-tree -r --name-only origin/main
```

and targeted checks such as:

```bash
git ls-tree -r --name-only origin/main -- testcases/generated
git ls-tree -r --name-only origin/main -- testdata/generated
git ls-tree -r --name-only origin/main -- rbtp/generated
git ls-tree -r --name-only origin/main -- dependencies/generated
git ls-tree -r --name-only origin/main -- traceability
```

The expected result is that actual artifact files are now present.

---

# 16. FRESH-CLONE VERIFICATION

This is mandatory.

Do NOT merely inspect the existing working tree.

Create a temporary fresh clone of `origin/main` outside the project working tree.

From that fresh clone verify:

```text
testcases/generated/TC-REQ-REG-01-01/v1.json
testdata/generated/TD-TC-REQ-REG-01-01-01/v1.json
```

and at least one RBTP and traceability artifact.

Load the testcase and test data from the fresh clone using a new Python process.

Do NOT regenerate them.

This proves:

```text
COMMIT → PUSH → REMOTE → FRESH CLONE → LOAD
```

---

# 17. FINAL REPOSITORY VERIFICATION

The final state must demonstrate:

```text
Human notes
      ↓
Git tracked
      ↓
Commit
      ↓
origin/main
      ↓
Fresh clone
      ↓
Available
```

and:

```text
Requirement
      ↓
Testcase
      ↓
Test Data
      ↓
RBTP
      ↓
Traceability
```

---

# 18. DO NOT DECLARE DI'S GATE

You may report:

**READY FOR HUMAN + DI VERIFICATION**

but MUST NOT declare:

* Di PASS
* Di APPROVED
* Final Gate PASS

The final gate belongs to Human + Di.

---

# 19. FINAL REPORT

Return a concise but complete report containing:

```text
============================================================
CR-001 REPOSITORY PERSISTENCE CLOSURE
============================================================

Starting HEAD:
Starting origin/main:

Human notes found:
Human notes committed:

Testcase artifacts:
Real:
Synthetic:
Committed:
Remote verified:

Test-data artifacts:
Real:
Synthetic:
Committed:
Remote verified:

RBTP:
Committed:
Remote verified:

Dependency matrix:
Committed:
Remote verified:

Traceability:
Committed:
Remote verified:

Fresh clone:
Testcase load:
Test-data load:
Traceability resolution:

Files intentionally NOT committed:
Reason:

Files intentionally NOT modified:
Reason:

Commit:
Push:
Final HEAD:
Final origin/main:
Working tree:

Advisories:
Blockers:

READY FOR HUMAN + DI VERIFICATION
============================================================
```

Do not hide uncommitted files.

Do not claim GitHub persistence until the remote and fresh clone have actually been verified.

---

# 20. WINDOWS COMPLETION NOTIFICATION

When ALL repository work is genuinely complete, including:

* inventory;
* classification;
* commit;
* push;
* remote verification;
* fresh-clone verification;

show a native Windows message box:

**Task complete**

Title:

**Claude**

Also play a Windows system notification sound.

Preferred visual mechanism from WSL:

```bash
powershell.exe -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Task complete','Claude','OK','Information')"
```

Use an appropriate native Windows PowerShell mechanism for the notification sound.

The notification MUST occur only after the complete task is finished.

Notification failure must NOT alter the engineering result.

============================================================
END OF INSTRUCTION
==================
