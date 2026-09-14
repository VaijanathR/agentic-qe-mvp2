# CP-MVP2-06 — Governance Closure Task

## Objective

Close the **CP-MVP2-06 Governance Action** cleanly and formally so that CP06 can be considered complete before proceeding to CP07.

This is a **governance closure and verification task**, NOT a redesign or enhancement task.

The objective is to determine whether the already-implemented and frozen CP06 checkpoint satisfies its approved governance requirements and to formally disposition all remaining CP06 advisories/actions.

---

# 1. Mandatory Starting Point

Before doing anything:

1. Inspect the frozen CP-MVP2-06 specification.
2. Inspect the CP06 implementation freeze.
3. Inspect the final CP06 evidence/report.
4. Inspect the CP06 regression results.
5. Inspect the subsequent multi-locator work that was performed after CP06.
6. Inspect the current CR-002 proposal concerning runtime locator fallback.
7. Inspect the repository history/commits relevant to CP06 and the subsequent multi-locator work.
8. Establish the exact current repository HEAD.

Do NOT rely only on previous Claude summaries.

Use the actual repository contents and Git history as the source of truth.

---

# 2. Frozen Governance Boundary

The following are frozen and MUST NOT be modified:

* CP-MVP2-01
* CP-MVP2-02
* CP-MVP2-03
* CP-MVP2-04
* CP-MVP2-05
* CP-MVP2-06
* Approved MVP2 SRS v1.0

Do not modify their specifications, requirements, acceptance criteria, or historical evidence merely to achieve closure.

Golden rule:

> NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.

If any apparent conflict is discovered:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 3. CP06 Closure Questions

Answer these questions explicitly.

### Q1 — CP06 implementation

Does the existing CP06 implementation satisfy the frozen CP06 specification?

### Q2 — Browser execution

Was the required real-browser execution mechanism demonstrated?

### Q3 — Execution result

Was the browser execution result honestly recorded, including failures?

### Q4 — Evidence

Is sufficient evidence persisted to prove what actually happened?

### Q5 — Deterministic blocking

Was the DATA-OQ-01 condition correctly handled as a deterministic NOT_EXECUTED/blocking condition where applicable?

### Q6 — Governance

Did CP06 correctly prevent unauthorized automatic retry/self-healing/runtime fallback?

### Q7 — Multi-locator work

Does the subsequent multi-locator implementation create any unresolved CP06 governance obligation?

Distinguish carefully between:

* CP06 requirement
* later enhancement
* advisory
* proposed change
* actual governance obligation

Do not assume that every later enhancement must be incorporated into CP06.

### Q8 — CR-002

Determine the exact status of CR-002.

Specifically establish whether:

1. CR-002 is required to close CP06;
2. CR-002 is merely a future change proposal;
3. CR-002 can remain OPEN/PENDING without blocking CP06 closure;
4. CR-002 requires a separate future human decision.

Do NOT implement CR-002 as part of this task unless the frozen CP06 specification explicitly requires it.

---

# 4. Important Distinction

The following must NOT be conflated:

### CP06 requirement

What CP06 v1.0 actually requires.

### CP06 evidence

What was actually executed and observed.

### CP06 advisory

A known limitation or non-blocking observation.

### CR-002

A proposed future governance change.

### Post-MVP enhancement

Something deliberately outside the current MVP.

The purpose of this task is to close CP06 according to its **approved frozen contract**, not to upgrade CP06 to a future architecture.

---

# 5. Honest Browser Failure

Do NOT attempt to make the previous browser execution green.

The existing real-browser execution failure must remain truthful.

Determine whether the failure:

* violates a CP06 acceptance criterion;
* is an expected/allowed execution outcome;
* is caused by insufficient testcase content;
* is an environment issue;
* is a governance-blocked condition;
* or is another correctly classified condition.

Use actual evidence.

Do not invent a root cause.

Do not modify requirements, testcase data, locators, response expectations, or execution behavior merely to obtain PASS.

---

# 6. Runtime Fallback / Self-Healing

The current CP06 governance prohibited unauthorized automatic retry/self-healing/runtime locator fallback.

Confirm whether that rule was respected.

If yes:

* record it as CP06-compliant;
* do not implement fallback;
* do not retroactively require fallback.

If runtime fallback requires CR-002:

* leave it governed by CR-002;
* record its status clearly;
* do not implement it during CP06 closure.

---

# 7. Multi-Locator Work

Inspect the subsequent multi-locator implementation.

Verify:

* evidence-backed locator candidates;
* persistence;
* deterministic locator representation;
* testcase/dataset identity;
* absence of unauthorized runtime fallback;
* regression safety;
* whether it introduced any actual CP06 specification conflict.

Do not expand this into a post-MVP locator architecture exercise.

The question is simply:

> Does this work leave CP06 with an unresolved governance obligation?

---

# 8. Required Closure Matrix

Produce a formal CP06 closure matrix.

Use at least:

| CP06 Item          | Frozen Requirement | Evidence | Actual Status | Governance Disposition | Blocking? |
| ------------------ | ------------------ | -------- | ------------- | ---------------------- | --------- |
| Browser launch     | ...                | ...      | ...           | ...                    | YES/NO    |
| Real execution     | ...                | ...      | ...           | ...                    | YES/NO    |
| Evidence           | ...                | ...      | ...           | ...                    | YES/NO    |
| Failure handling   | ...                | ...      | ...           | ...                    | YES/NO    |
| DATA-OQ-01         | ...                | ...      | ...           | ...                    | YES/NO    |
| Retry/self-healing | ...                | ...      | ...           | ...                    | YES/NO    |
| Multi-locator      | ...                | ...      | ...           | ...                    | YES/NO    |
| CR-002             | ...                | ...      | ...           | ...                    | YES/NO    |
| Regression         | ...                | ...      | ...           | ...                    | YES/NO    |

Do not mark an item PASS merely because implementation exists.

---

# 9. Closure Decision

At the end, provide exactly one of:

### CP06 — GREEN

All frozen CP06 requirements satisfied and no blocking governance action remains.

### CP06 — GREEN WITH ADVISORIES

All frozen CP06 requirements satisfied, but non-blocking advisories/future proposals remain.

### CP06 — BLOCKED

A genuine frozen CP06 requirement or governance obligation remains unresolved.

If BLOCKED, clearly identify:

* exact requirement;
* evidence;
* blocker;
* why it cannot be closed;
* required human decision.

Do NOT fix the blocker by modifying the frozen specification.

---

# 10. CR-002 Disposition

The report must explicitly state:

### CR-002 Status

One of:

* NOT REQUIRED FOR CP06
* OPEN — FUTURE CHANGE
* REQUIRES HUMAN + DI DECISION
* IMPLEMENTED UNDER AUTHORIZATION

If CR-002 is not required for CP06 closure, state explicitly:

> CR-002 remains outside CP06 closure and does not block CP07.

Do not implement CR-002 merely because it exists.

---

# 11. Regression and Integrity

Run the appropriate CP06 regression/governance validation.

Verify:

* CP01–CP05 remain unchanged/frozen.
* CP06 frozen specification remains unchanged.
* Approved SRS remains unchanged.
* No unauthorized modifications were introduced.
* Existing evidence remains reproducible/consistent.
* Repository state is clean and intentional.

Report:

* focused test count/result;
* full regression count/result where applicable;
* relevant commit SHA;
* repository HEAD;
* changed files.

---

# 12. Evidence Persistence

Persist a formal CP06 Governance Closure Report.

Suggested location:

`docs/claude-execution-reports/CP-MVP2-06/`

Use a clear filename such as:

`CP-MVP2-06-GOVERNANCE-CLOSURE-<timestamp>.md`

The report must contain:

1. Scope
2. Starting repository HEAD
3. Frozen CP06 specification reference
4. Evidence reviewed
5. CP06 closure matrix
6. Browser execution disposition
7. DATA-OQ-01 disposition
8. Multi-locator disposition
9. CR-002 disposition
10. Regression results
11. Frozen-artifact integrity verification
12. Remaining advisories
13. Final CP06 governance decision

---

# 13. Git Commit

Commit ONLY the artifacts legitimately required for CP06 governance closure.

Do not commit unrelated changes.

Use a clear commit message, for example:

`docs: close CP-MVP2-06 governance action`

Report:

* commit SHA;
* commit message;
* files changed;
* final repository HEAD.

---

# 14. Fresh Verification

After committing:

1. Verify the committed report from the repository itself.
2. Verify the commit ancestry.
3. Verify no frozen specification was modified.
4. Verify the closure report is actually persisted.
5. Verify the final HEAD.
6. If practical, perform a fresh-process/fresh-clone verification of the closure evidence.

Do not report success based solely on the working tree before commit.

---

# 15. Do NOT Do the Following

Do NOT:

* redesign CP06;
* modify CP06 specification;
* modify CP01–CP05;
* modify the approved SRS;
* implement Excel testcase/test-data enhancements;
* redesign Playwright automation;
* implement production-grade page objects;
* implement runtime locator fallback;
* implement CR-002 unless explicitly authorized by the frozen CP06 contract;
* regenerate the testcase corpus;
* change testcase requirements to make execution pass;
* change test data to make execution pass;
* fabricate browser evidence;
* turn a failed execution into PASS;
* begin CP07 implementation.

This task ends at **CP06 governance closure**.

---

# 16. Completion Notification

When the entire CP06 governance-closure task has completed:

1. Play the Windows system notification sound.
2. AFTER the sound, display the native Windows message box:

**Task complete.**

The sound must occur before the message box.

---

# 17. Final Claude Response

The final response must be concise and include:

* CP06 decision: GREEN / GREEN WITH ADVISORIES / BLOCKED
* closure report path
* commit SHA
* final HEAD
* focused regression result
* full regression result if run
* CR-002 disposition
* remaining advisories
* whether CP07 is now authorized to begin

Do not claim CP07 authorization if CP06 is BLOCKED.
