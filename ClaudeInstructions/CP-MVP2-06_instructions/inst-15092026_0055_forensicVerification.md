# CP-MVP2 — Persistent Artifact Forensic Verification

## READ-ONLY — NO REPOSITORY MODIFICATIONS

You are performing a **forensic verification only**.

The purpose is to independently establish whether the CP-MVP2 Batch-1 generated **testcases and test data actually exist as first-class persisted repository artifacts**, rather than merely existing in memory, in runtime output, or being described in an execution report.

## 1. ABSOLUTE GOVERNANCE RULE

This is a READ-ONLY investigation.

### You MUST NOT:

* modify any source code;
* modify any testcase/test-data implementation;
* modify any CP-MVP2 specification;
* modify CR-001;
* modify any governance document;
* modify any execution report;
* regenerate artifacts;
* create replacement artifacts;
* "fix" anything discovered;
* commit any implementation change;
* change frozen status;
* change Batch-1/Batch-2 status;
* alter `.gitignore`;
* alter repository configuration.

Do NOT solve or repair any problem discovered.

If something is missing or incorrect, REPORT it exactly as found.

The only permitted output is a forensic report generated from read-only inspection. If you create that report as a repository file, do so ONLY if explicitly required by the existing repository reporting convention; otherwise print the complete report to the terminal and do not modify the repository.

---

# 2. VERIFY THE ACTUAL REPOSITORY STATE

Start from the current repository state.

Capture:

* current branch
* current HEAD
* `origin/main`
* working-tree status
* latest commits
* whether HEAD equals origin/main

Explicitly inspect these known commits where available:

* Batch-1 implementation:
  `415038ca9892d2574cfdff8fabf13d4c4d1006da`
* Batch-1 evidence:
  `546c568b616e408ce2f2ee41055f3e087e7821a0`
* CR reconciliation:
  `26625b49f5b2641af5c0c111af366fb9042b5f91`

Do not assume these commits contain the artifacts. Verify.

---

# 3. TESTCASE FORENSIC INVENTORY

Determine whether the actual generated testcase instances are persisted as first-class artifacts.

Inspect the entire relevant repository structure.

Specifically investigate:

* `testcases/`
* `testcases/generated/`
* `artifacts/`
* `data/`
* `runs/`
* any other directory used by `testcases/persist.py`
* any paths referenced by Batch-1 implementation/report

Use actual filesystem inspection and Git inspection.

### Required commands/evidence

Use appropriate read-only commands such as:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git ls-files
```

and targeted inspection such as:

```bash
find . -type f
```

or equivalent.

Inspect:

```text
testcases/persist.py
testcases/schema.py
testcases/generate.py
testcases/validate.py
testcases/pipeline.py
```

Determine the exact persistence path and filename convention.

---

# 4. PROVE WHETHER TESTCASE ARTIFACTS EXIST

The Batch-1 report claims:

> 9 real testcases generated and persisted for four profiled requirements.

Do NOT accept this statement as evidence.

Find the actual persisted testcase files.

For every persisted testcase found, capture:

* filename/path
* testcase ID
* title
* requirement IDs
* journey ID
* scenario type
* test steps
* expected result
* test-data reference
* priority
* source attribution
* generation metadata
* validation status
* Git-tracked status
* commit in which the artifact first appears

Create a table:

| TC ID | File | Requirement(s) | Scenario | Git tracked? | Commit |
| ----- | ---- | -------------- | -------- | ------------ | ------ |

If fewer than 9 exist, report the exact number.

If zero exist, explicitly state:

**NO FIRST-CLASS PERSISTED TESTCASE ARTIFACTS FOUND.**

Do not infer persistence from Python persistence code.

---

# 5. TESTCASE ID FORENSICS

Search the repository for known generated IDs, including:

```text
TC-REQ-REG-01-01
```

and all testcase IDs found during the inventory.

For each ID determine whether it appears in:

1. actual testcase artifact;
2. execution report only;
3. source code fixture;
4. test output;
5. generated runtime directory;
6. Git history.

Distinguish:

**artifact existence** from **reference to artifact existence**.

A Markdown report mentioning a testcase is NOT itself proof that the testcase is persisted as a first-class artifact.

---

# 6. GIT TRACKING VERIFICATION

For each actual testcase artifact:

Verify:

```bash
git ls-files -- <path>
```

Determine whether the file is:

* committed and tracked;
* present locally but untracked;
* gitignored;
* generated only at runtime;
* absent.

Also determine the commit where it was introduced:

```bash
git log --follow -- <path>
```

If the artifact exists only locally and is not committed, report that clearly.

---

# 7. FRESH-PROCESS RELOAD TEST

This is critical.

Select at least one actual persisted testcase.

Demonstrate:

### Process A

Load the testcase from the persisted artifact.

Record:

* path
* testcase ID
* content/hash

Terminate the process.

### Process B

Start a completely new Python process.

Load the SAME testcase from disk.

Record:

* path
* testcase ID
* content/hash

Compare the results.

The purpose is to prove:

```text
GENERATE
   ↓
PERSIST
   ↓
PROCESS ENDS
   ↓
NEW PROCESS
   ↓
LOAD FROM DISK
```

Do NOT regenerate the testcase during Process B.

If this cannot be demonstrated from an actual persisted artifact, say so.

---

# 8. TEST-DATA FORENSIC INVENTORY

Now perform the same investigation for test data.

Inspect:

```text
testdata/
testdata/persist.py
testdata/schema.py
testdata/generate.py
testdata/validate.py
testdata/pipeline.py
```

Determine the actual persisted test-data location and filename convention.

The Batch-1 report claims:

> 24 real datasets:
> 16 ACCEPTED
> 2 REJECTED
> 6 POSSIBLE_DUPLICATE

Do NOT accept this claim without finding the actual artifacts.

For every actual persisted dataset, capture:

* data_set_id
* testcase_id
* requirement IDs
* data category
* purpose
* validity
* validation status
* field names
* field values
* value types
* boundary classification
* uniqueness requirement
* dependency reference
* source attribution
* generation metadata
* Git-tracked status
* introducing commit

Create:

| Dataset ID | TC ID | Requirement(s) | Category | Status | File | Git tracked? | Commit |
| ---------- | ----- | -------------- | -------- | ------ | ---- | ------------ | ------ |

Report exact counts.

If zero actual persisted datasets are found:

**NO FIRST-CLASS PERSISTED TEST-DATA ARTIFACTS FOUND.**

---

# 9. TESTCASE ↔ TEST-DATA TRACEABILITY

Verify the actual persisted mapping.

For each selected testcase:

```text
Requirement
   ↓
Testcase
   ↓
Test-data dataset
```

Demonstrate that the IDs are actually resolvable from persisted artifacts.

Do not rely solely on Python code that could theoretically create the mapping.

At least demonstrate:

* 2 real testcase artifacts;
* their linked test-data IDs;
* the corresponding actual test-data files;
* matching testcase IDs;
* matching requirement IDs.

If any mapping exists only in memory, report that.

---

# 10. REQUIREMENT ↔ TESTCASE TRACEABILITY

Verify the actual persisted requirement mapping.

For at least 2 real testcases:

```text
TC ID
 ↓
REQ ID
 ↓
Approved SRS requirement
```

Confirm that the requirement ID exists in:

`requirements/MVP2_SRS_v1.0_APPROVED.md`

Report:

| TC ID | Requirement ID | Requirement exists in Approved SRS? | Evidence |
| ----- | -------------- | ----------------------------------- | -------- |

Do not modify the SRS.

---

# 11. RBTP AND DEPENDENCY ARTIFACT CHECK

Although the primary objective is testcase/test-data persistence, verify whether Batch-1 also persisted:

* RBTP artifacts;
* dependency/reusability matrix;
* traceability artifacts.

For each, identify:

* actual artifact path;
* whether it is first-class;
* whether it is Git tracked;
* whether it contains stable IDs;
* whether it references actual testcase IDs.

Do not repair anything.

---

# 12. DISTINGUISH THREE DIFFERENT STATES

Your report MUST clearly distinguish:

### A. First-class persisted artifact

A real artifact exists on disk and is tracked/committed.

### B. Runtime-generated artifact

An artifact exists only during a run or in a generated/ignored runtime directory.

### C. Report-only representation

The artifact is represented only inside an execution report, log, summary, JSON output, fixture, or documentation.

Do not classify B or C as A.

---

# 13. HASH / CONTENT INTEGRITY

For at least:

* 2 testcase artifacts;
* 2 test-data artifacts;

calculate a content hash, preferably SHA-256.

Record:

```text
path
SHA-256
size
Git commit
```

Then perform the fresh-process reload using those artifacts.

---

# 14. DO NOT REGENERATE ANYTHING

This is extremely important.

The purpose is to determine whether the artifacts ALREADY EXIST.

Therefore:

**DO NOT run testcase generation.**

**DO NOT run test-data generation.**

**DO NOT invoke Claude.**

**DO NOT invoke an LLM.**

**DO NOT create replacement artifacts.**

**DO NOT populate missing artifacts.**

If something is missing, report it.

---

# 15. FINAL FORENSIC VERDICT

At the end, issue exactly one of:

### GREEN — VERIFIED

Only if actual first-class persisted testcase AND test-data artifacts are found and independently reloadable from a fresh process.

### YELLOW — PARTIALLY VERIFIED

If persistence is demonstrated for some artifacts but one or more major artifact classes are only runtime/report evidence.

### RED — NOT VERIFIED

If actual first-class persisted testcase/test-data artifacts cannot be found.

The verdict must be evidence-driven.

Do NOT use the Batch-1 report's claims as evidence of artifact existence.

---

# 16. REQUIRED FINAL REPORT STRUCTURE

Return:

```text
============================================================
CP-MVP2 PERSISTENT ARTIFACT FORENSIC VERIFICATION
============================================================

Repository:
HEAD:
origin/main:
Working tree:

TESTCASE ARTIFACTS
------------------
Expected:
Found:
First-class persisted:
Runtime-only:
Report-only:
Git-tracked:
Example artifacts:

TEST-DATA ARTIFACTS
-------------------
Expected:
Found:
First-class persisted:
Runtime-only:
Report-only:
Git-tracked:
Example artifacts:

TRACEABILITY
------------
REQ → TC:
TC → DATA:
TC → RBTP:
Dependency:

FRESH PROCESS RELOAD
--------------------
Testcase:
Result:

Test-data:
Result:

CONTENT INTEGRITY
------------------
Artifact:
SHA-256:

GIT HISTORY
-----------
Artifact:
Introducing commit:

FINAL VERDICT
-------------
GREEN / YELLOW / RED

BLOCKERS:
ADVISORIES:
EVIDENCE PATHS:
============================================================
```

---

# 17. WINDOWS COMPLETION NOTIFICATION

When the forensic investigation is genuinely complete, attempt to notify me on the Windows 10 host.

The preferred notification is:

### Visual

A native Windows PowerShell message box:

**Task complete**

Title:

**Claude**

### Sound

Also attempt to play a Windows system notification sound.

Because this is WSL, invoke native Windows PowerShell rather than relying on Linux desktop notification services.

Use a best-effort command such as:

```bash
powershell.exe -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Task complete','Claude','OK','Information')"
```

For the sound, use an appropriate native Windows mechanism if available, for example a Windows system sound.

If the sound cannot be produced, the visual message box is sufficient.

**Notification failure MUST NOT affect the forensic verdict.**

Do not claim the notification succeeded unless it actually did.

============================================================
END OF INSTRUCTION
==================
