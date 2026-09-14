# TASK-CP-MVP2-03-PREP

## Objective

Prepare the repository for implementation of **CP-MVP2-03 — LLM Testcase Generation**.

This task is a **PREPARATION / GOVERNANCE task only**.

**DO NOT IMPLEMENT CP-MVP2-03 functionality.**

The frozen CP-MVP2-03 Specification v1.0 has already been approved by the Human Owner + Di and is immutable.

---

# 1. Governing Documents

The following are authoritative:

### Functional specification

**CP-MVP2-03 Specification v1.0 — APPROVED AND FROZEN**

The specification defines what CP-MVP2-03 must eventually implement.

### Execution governance

**CLAUDE-EXECUTION-EVIDENCE-GOVERNANCE-v1.0.md**

This defines how Claude must execute, document, validate, and report implementation work.

---

# 2. Critical Rules

## MUST

* Work in the existing local MVP2 repository.
* Preserve the existing MVP2 architecture.
* Preserve CP-MVP2-01 frozen artifacts.
* Preserve CP-MVP2-02 frozen artifacts.
* Create the canonical frozen CP-MVP2-03 specification locally.
* Create the Claude execution/evidence governance document locally.
* Create the execution-report directory structure.
* Verify repository integrity.
* Commit the preparation artifacts.
* Push the commit to GitHub.
* Produce a detailed execution report.
* Produce a short execution summary.
* Return the commit and GitHub links/references.

## MUST NOT

* Implement CP-MVP2-03.
* Implement LLM testcase generation.
* Implement new RAG functionality.
* Modify CP-MVP2-01.
* Modify CP-MVP2-02.
* Modify the Approved SRS.
* Modify the Draft SRS.
* Modify frozen requirements.
* Modify frozen governance artifacts.
* Modify tests merely to make validation pass.
* Create CP-MVP2-04 or later-checkpoint functionality.
* Change the frozen CP-MVP2-03 specification.
* Invent requirements.
* Invent journeys.
* Crawl or inspect Demo Web Shop for requirements.
* Create a parallel framework.

---

# 3. First Action — Inspect Local Repository

Before making changes:

1. Confirm the repository and current branch.
2. Record current Git HEAD.
3. Record current working-tree status.
4. Inspect the existing documentation/specification structure.
5. Identify CP-MVP2-01 frozen artifacts.
6. Identify CP-MVP2-02 frozen artifacts.
7. Identify existing execution/report conventions if present.

Do not alter anything during this inspection phase.

---

# 4. Create Canonical CP-MVP2-03 Specification

Create the approved specification locally in the MVP2 repository.

Preferred location:

```text
docs/
  specifications/
    CP-MVP2-03-SPEC-v1.0-FROZEN.md
```

The content must correspond to the **approved and frozen CP-MVP2-03 Specification v1.0** supplied in the task context.

Important:

* Preserve its meaning.
* Do not add functional requirements.
* Do not remove functional requirements.
* Do not reinterpret requirements.
* Do not improve or optimize the specification.
* Do not change version 1.0.

The filename and document status must clearly identify it as:

**FROZEN**

---

# 5. Create Claude Execution Governance

Create:

```text
CLAUDE-EXECUTION-EVIDENCE-GOVERNANCE-v1.0.md
```

Place it in the repository's appropriate documentation/governance location.

Preferred location if consistent with the existing repository structure:

```text
docs/
  governance/
    CLAUDE-EXECUTION-EVIDENCE-GOVERNANCE-v1.0.md
```

Use the approved **Claude Execution & Evidence Governance v1.0** document supplied in the task context.

Do not alter its governing principles.

---

# 6. Create Execution Report Structure

Create the appropriate structure for future Claude execution reports.

Preferred:

```text
docs/
  claude-execution-reports/
    CP-MVP2-03/
      summaries/
```

Do not create fake execution reports for implementation work that has not occurred.

The directory structure is being prepared for future execution evidence.

If Git does not preserve empty directories, use an appropriate minimal repository convention such as a README or `.gitkeep`, provided this does not conflict with existing repository conventions.

---

# 7. Frozen Artifact Integrity Check

Before committing:

Verify that:

* CP-MVP2-01 frozen artifacts are unchanged.
* CP-MVP2-02 frozen artifacts are unchanged.
* Approved SRS is unchanged.
* Draft SRS is unchanged.
* No existing implementation was unintentionally modified.

Use actual Git evidence.

Record:

```text
Frozen artifacts modified: YES / NO
```

The expected result is:

```text
Frozen artifacts modified: NO
```

If any frozen artifact has changed as a result of this task:

**STOP before committing and report the conflict.**

Do not overwrite, revert, or conceal the change without human/Di direction.

---

# 8. Scope Check

Before commit, verify that this task contains ONLY:

1. Canonical frozen CP-MVP2-03 Specification v1.0.
2. Claude Execution & Evidence Governance v1.0.
3. Execution-report directory structure.
4. Necessary documentation supporting those artifacts.

There must be:

* no CP-MVP2-03 implementation
* no LLM integration
* no testcase generator
* no new RAG implementation
* no CP-MVP2-04 implementation
* no unrelated refactoring

---

# 9. Commit

After all checks pass:

Create a meaningful Git commit.

Recommended commit message:

```text
docs: establish CP-MVP2-03 specification and execution governance
```

Before committing, record:

* starting HEAD
* changed files
* diff/stat
* frozen-artifact integrity result

After committing, record:

* commit SHA
* branch
* final status

---

# 10. Push to GitHub

Push the commit to the appropriate remote branch.

Verify that the push succeeded.

Record:

* repository
* branch
* commit SHA
* push result

Do not claim that the work was pushed unless the push actually succeeded.

---

# 11. Detailed Execution Report

After the preparation task has been completed and pushed, create the detailed execution report.

Preferred location:

```text
docs/
  claude-execution-reports/
    CP-MVP2-03/
      CP-MVP2-03-EXEC-YYYYMMDD-HHMMSS-<UNIQUE-ID>.md
```

The report must include:

## Execution Identity

* execution ID
* checkpoint
* date/time
* repository
* branch
* starting commit
* ending commit

## Instruction Received

Summarize the complete task given to Claude, including the scope restrictions.

## Actions Performed

List exactly what was done.

## Files Created

List every newly created file.

## Files Modified

List every modified file.

Expected:

Only authorized preparation artifacts.

## Files Deleted

State explicitly:

```text
None
```

if none were deleted.

## CP-MVP2-01 Integrity

State the result with evidence.

## CP-MVP2-02 Integrity

State the result with evidence.

## SRS Integrity

State the result.

## Scope Audit

Confirm that no CP-MVP2-03 implementation was performed.

## Validation

Record actual commands/checks performed and their results.

## Git Evidence

Include:

* status
* diff/stat
* changed files
* commit SHA
* push result

## Deviations

This section is mandatory.

If none:

```text
Deviations from instruction/specification: NONE
```

Otherwise list every deviation.

## Problems Encountered

State actual problems encountered.

If none:

```text
Problems encountered: NONE
```

## Human Decision Required

State:

```text
Human decision required: NONE
```

if no decision is required.

## Final Result

Use one of:

```text
PASS
FAIL
BLOCKED
PARTIAL
```

The result must be supported by actual evidence.

---

# 12. Short Execution Summary

Create a concise summary under:

```text
docs/
  claude-execution-reports/
    CP-MVP2-03/
      summaries/
        CP-MVP2-03-SUMMARY-YYYYMMDD-HHMMSS-<UNIQUE-ID>.md
```

The summary must contain:

```text
Execution ID:
Checkpoint:
Task:
Result:

Specification:
CP-MVP2-03 Specification v1.0 — FROZEN

Actions completed:
<short summary>

CP-MVP2-01 frozen artifacts:
UNCHANGED / CHANGED

CP-MVP2-02 frozen artifacts:
UNCHANGED / CHANGED

CP-MVP2-03 implementation:
NOT IMPLEMENTED

Deviations:
NONE / <details>

Tests/checks:
<actual results>

Commit:
<commit SHA>

Push:
SUCCESS / FAILURE

Detailed report:
<GitHub path/link>

Human + Di decision required:
YES / NO
```

---

# 13. Reporting Requirement

The detailed report and short summary are themselves part of the task.

Therefore:

```text
Preparation
    ↓
Verification
    ↓
Detailed Report
    ↓
Short Summary
    ↓
Commit
    ↓
Push
```

Do not report the task as fully complete while required reporting artifacts remain uncommitted/unpushed.

If GitHub push fails, explicitly report the failure.

---

# 14. Final Response to Human + Di

Your final response must be concise but evidence-based.

Provide:

1. Execution ID.
2. Result.
3. What was created.
4. Confirmation that CP-MVP2-01 is unchanged.
5. Confirmation that CP-MVP2-02 is unchanged.
6. Confirmation that CP-MVP2-03 implementation was NOT performed.
7. Deviations.
8. Commit SHA.
9. Push status.
10. Detailed report GitHub link.
11. Short summary GitHub link.
12. Any human/Di decision required.

Do not merely say "Done."

---

# 15. STOP Conditions

Immediately stop and report if:

* a frozen artifact must be changed to complete the task
* the approved CP-MVP2-03 specification is unclear or unavailable
* existing repository state conflicts with the requested preparation
* a requested action would require modifying CP-MVP2-01/02
* Git state reveals unexpected changes that cannot safely be distinguished
* push cannot be completed
* implementation of CP-MVP2-03 appears necessary to satisfy this task

Do not solve a STOP condition by silently changing the specification.

Use:

```text
STOP → REPORT → HUMAN + DI DECIDE
```

---

# 16. Final Boundary

This task establishes the governance foundation.

It does NOT authorize implementation of CP-MVP2-03.

After this task is verified by Human + Di, a separate task will authorize:

**CP-MVP2-03 — LLM Testcase Generation Implementation**

That future task will use the frozen specification and this execution governance standard.

---

## Golden Rule

**DO NOT CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

For this preparation task, there should be no implementation to make pass.

The objective is to establish the authoritative specification and evidence-governance foundation cleanly and verifiably.
