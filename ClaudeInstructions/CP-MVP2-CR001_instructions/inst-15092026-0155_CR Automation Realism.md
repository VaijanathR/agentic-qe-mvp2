# MVP2 CONTINUATION — PLAYWRIGHT AUTOMATION REALISM + EXACT TESTCASE STEP TRACEABILITY

## Objective

Continue the MVP2 Agentic QE implementation from the current repository state.

The next priority is to make Playwright automation a **faithful executable representation of the testcase**, rather than merely a collection of UI actions.

The immediate target is:

**Approved Requirement → Persisted Testcase → Persisted Test Data → Playwright Automation → Real Browser Execution → Evidence**

The MVP remains Windows-first.

Linux/macOS persistence portability remains parked and must NOT consume implementation effort in this task.

---

# 1. GOVERNANCE

Starting repository state:

* previous verified HEAD: `220c16fccf040468c40f1120f6dc937685afc9b6`
* latest implementation/evidence commits must be inspected before proceeding
* current multi-locator implementation and CR-002 proposal must be inspected

Before modifying anything:

1. Inspect current CP-MVP2-05 and CP-MVP2-06 frozen specifications.
2. Inspect current Playwright automation implementation.
3. Inspect the new multi-locator implementation.
4. Inspect the generated `ML-PW-*` artifact.
5. Inspect the real execution failure from the previous vertical slice.
6. Inspect the persisted testcase and test-data artifacts used by that slice.
7. Inspect the current CR-002 proposal.
8. Inspect actual Demo Web Shop DOM/discovery evidence.
9. Determine which improvements can be made without changing frozen contracts.

If a change requires modification of a frozen specification:

**STOP → REPORT → PROPOSE FORMAL CR**

Do not silently modify CP-05 or CP-06.

Golden rule:

**NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

---

# 2. NEW HUMAN REQUIREMENT — EXACT TESTCASE STEP FIDELITY

This is now a mandatory Agentic QE architectural rule.

## Rule

A Playwright automation mapped to a testcase MUST contain the **same business/test steps as the testcase it is mapped to**.

The automation may add implementation-level technical actions required to execute those steps, but it MUST NOT:

* omit a testcase business step;
* invent a new business step;
* reorder business steps;
* replace a business step with a different business action;
* silently add a different journey;
* silently remove a precondition required by the testcase.

The testcase remains the source of truth for the intended test flow.

---

# 3. BUSINESS STEP VS TECHNICAL STEP

Distinguish explicitly between:

### Testcase business step

Example:

```text
1. Navigate to the Demo Web Shop.
2. Add the eligible product to the cart.
3. Proceed to checkout.
4. Enter the required billing information.
5. Submit the checkout.
6. Verify the expected result.
```

### Playwright implementation steps

The automation may need technical actions such as:

```text
wait for page
locate element
scroll into view
wait for network idle
select option
```

These are implementation mechanics.

They MUST NOT be mistaken for additional business/testcase steps.

The automation should preserve an explicit mapping such as:

```text
Testcase Step 1
    ↓
Automation Step 1.x

Testcase Step 2
    ↓
Automation Step 2.x

Testcase Step 3
    ↓
Automation Step 3.x
```

Every testcase business step must have at least one automation implementation step.

No automation business step may exist without a corresponding testcase step.

---

# 4. EXACT STEP TRACEABILITY

Add deterministic validation for:

### Coverage

Every testcase step must map to one or more automation steps.

### No orphan business actions

Every automation business action must map to a testcase step.

### Ordering

Mapped testcase steps must occur in the same business order.

### Identity

Each automation step should retain the testcase step identifier/reference wherever the current schema permits.

Conceptually:

```text
testcase_step_id: TC-STEP-03
automation_steps:
  - AUTO-STEP-03-01
  - AUTO-STEP-03-02
  - AUTO-STEP-03-03
```

Do not invent a parallel business-step model if the existing schema already provides an equivalent mechanism. Reuse the existing architecture.

---

# 5. MULTIPLE TEST DATA SETS

A single testcase MAY have multiple test-data sets.

This is explicitly supported.

For example:

```text
TC-REQ-REG-01-01
    ├── TD-001
    ├── TD-002
    ├── TD-003
    └── TD-004
```

The testcase business steps remain exactly the same.

The data changes.

Therefore:

```text
Testcase
   ↓
same business steps
   ↓
Dataset A

Testcase
   ↓
same business steps
   ↓
Dataset B

Testcase
   ↓
same business steps
   ↓
Dataset C
```

Do NOT create separate business flows merely because datasets differ.

The automation identity/versioning model must distinguish the testcase from its dataset execution instance.

---

# 6. AUTOMATION ↔ TESTCASE CONTRACT

Every persisted automation artifact must explicitly identify:

* testcase_id
* requirement_ids
* test_data_set_id or supported dataset association
* testcase step mappings
* automation step mappings
* journey_id where applicable
* scenario_type
* locator evidence
* assertions
* source attribution
* generation metadata
* validation status

If the existing frozen CP-05 schema cannot support the exact mapping cleanly:

**STOP → REPORT → PROPOSE CR**

Do not weaken the requirement.

---

# 7. CP-05 REALISM GAP

The previous real browser execution exposed an important defect:

The generated automation attempted to interact with Billing/Shipping fields without first establishing the required checkout state.

This must be investigated.

The automation generator must reason about:

```text
preconditions
    ↓
required journey/setup
    ↓
testcase steps
    ↓
target actions
    ↓
expected assertions
```

It must NOT generate isolated UI actions merely because a matching DOM element exists.

Before generating automation, determine:

1. What state must the application be in?
2. What actions establish that state?
3. Which testcase steps establish that state?
4. Which steps are preconditions?
5. Which steps are actual test actions?
6. Which expected results must be asserted?

Use actual approved testcase content and direct application evidence.

Do not invent missing business steps.

If the testcase itself is insufficient to establish the required state:

**STOP → classify as TESTCASE / REQUIREMENT insufficiency rather than silently adding steps.**

---

# 8. IMPORTANT — DO NOT CONFUSE TESTCASE COMPLETENESS WITH AUTOMATION COMPLETENESS

If the testcase says:

```text
Step 1: Login
Step 2: Search for product
Step 3: Add product to cart
Step 4: Checkout
```

the automation must execute those steps.

It cannot say:

```text
Open checkout URL directly
Fill billing form
```

unless the testcase explicitly contains that journey or an approved precondition establishes that state.

Direct URL shortcuts must not bypass testcase business steps unless explicitly justified and traceable as a technical implementation of an existing testcase step/precondition.

---

# 9. MULTI-LOCATOR REQUIREMENT

Retain the newly implemented evidence-backed multi-locator candidate architecture.

For each load-bearing element:

* primary locator
* fallback candidate(s)
* evidence source
* evidence reference
* strategy
* confidence
* deterministic priority

Do not invent candidates.

Do not implement runtime fallback unless CR-002 is formally authorized.

For this task, multi-locator generation/persistence may continue.

Runtime fallback remains governed by CR-002.

---

# 10. CR-002

Inspect:

`docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`

Do not self-authorize it.

If the current task requires runtime fallback implementation, STOP and report that CR-002 authorization is required.

Otherwise continue with:

**candidate generation + validation + persistence**

without changing CP-06 runtime behavior.

---

# 11. FIRST TARGET — REBUILD THE VERTICAL SLICE CORRECTLY

Use the previously selected real testcase:

`TC-REQ-ACO-03-01`

and its associated accepted test data:

`TD-TC-REQ-ACO-03-01-01`

unless inspection shows that the frozen artifact is no longer the correct target.

Before generating a new automation artifact:

1. Load the persisted testcase from disk.
2. Load the persisted test data from disk.
3. Load the requirement from the Approved SRS.
4. Inspect actual Demo Web Shop evidence.
5. Construct the testcase-step → automation-step mapping.
6. Validate that all testcase business steps can actually be implemented.
7. Only then generate Playwright automation.

Do NOT modify the testcase merely to make automation easier.

---

# 12. SUCCESS CRITERIA FOR THE VERTICAL SLICE

The new vertical slice should demonstrate:

### A. Testcase fidelity

100% testcase business-step coverage.

### B. Step order

100% preserved business order.

### C. No invented business steps

Zero orphan automation business steps.

### D. Test-data independence

The same testcase can support multiple datasets without changing the testcase business flow.

### E. Locator resilience

Multiple evidence-backed candidates exist for load-bearing elements where the DOM provides them.

### F. Persistence

Automation artifact exists as a first-class repository artifact.

### G. Traceability

```text
Automation
 → Testcase
 → Requirement
 → Test Data
```

resolves deterministically.

### H. Real browser execution

Execute against real Demo Web Shop using Chromium on Windows.

### I. Honest result

If execution fails:

* report the real failure;
* classify it;
* preserve evidence;
* do NOT change the testcase to make it pass.

---

# 13. AUTOMATION QUALITY

Generated Playwright code should:

* use reusable functions/components where genuine reuse exists;
* avoid unnecessary duplication;
* use deterministic synchronization;
* avoid arbitrary sleeps where better synchronization exists;
* use evidence-backed locators;
* preserve business intent;
* produce meaningful assertions;
* maintain step traceability;
* maintain testcase/data traceability;
* avoid secrets/real PII;
* avoid silently modifying expected behavior.

Do not build unnecessary framework complexity.

---

# 14. TESTCASE-TO-AUTOMATION VALIDATOR

Add deterministic validation tests for:

1. all testcase steps represented;
2. correct step order;
3. no missing testcase step;
4. no orphan automation business step;
5. testcase ID matches;
6. requirement IDs match;
7. dataset association is valid;
8. multiple datasets do not alter testcase steps;
9. locator candidates are evidence-backed;
10. automation persistence;
11. traceability;
12. automation identity collision handling.

If schema changes are required, stop and propose the appropriate CR rather than modifying the frozen contract.

---

# 15. REAL EXECUTION EVIDENCE

For each real execution persist:

* execution ID
* actual timestamp
* automation ID
* testcase ID
* test-data-set ID
* requirement ID(s)
* browser/version
* environment
* testcase step ID
* automation step ID
* locator candidate attempted
* locator candidate selected
* fallback information where applicable
* step status
* assertion status
* final status
* screenshots/evidence
* logs
* failure classification

No fabricated evidence.

---

# 16. REGRESSION

Run:

1. focused tests for the new functionality;
2. full regression suite.

Existing frozen tests must remain untouched.

Do not weaken existing validators simply to obtain GREEN.

---

# 17. PERSISTENCE VERIFICATION

After implementation:

1. Commit the actual generated automation artifact.
2. Push to `origin/main`.
3. Verify the actual artifact exists in `origin/main`.
4. Verify the actual testcase/test-data/automation traceability.
5. Start a genuinely new Python process.
6. Load testcase.
7. Load test data.
8. Load automation.
9. Resolve mappings.
10. Confirm hashes/content.
11. Do not regenerate anything during verification.

Repository-grade persistence requires actual files in GitHub.

---

# 18. COMPLETION REPORT

Report:

1. starting HEAD
2. implementation commit
3. evidence commit
4. files added
5. files modified
6. frozen files verified untouched
7. testcase selected
8. test-data selected
9. testcase business steps
10. automation business steps
11. exact testcase-step ↔ automation-step mapping
12. proof that the business steps are identical in content/order
13. number of datasets supported by the testcase
14. locator candidates and evidence
15. automation identity
16. browser execution result
17. execution evidence
18. traceability
19. focused tests
20. full regression
21. fresh-process verification
22. CR-002 status
23. advisories
24. blockers

Do NOT declare the Human/Di gate.

---

# 19. COMPLETION NOTIFICATION — ORDER IS IMPORTANT

When ALL work is genuinely complete:

1. First play the Windows system notification sound.
2. ONLY AFTER the sound has played, show the native Windows message box:

**Task complete**

The required order is:

**SYSTEM SOUND → MESSAGE BOX**

Do not show the message box first.

Do not trigger the notification before implementation, tests, commits, push and verification are complete.

---

# FINAL ENGINEERING PRINCIPLE

The objective is not merely:

**"Generate Playwright code that can interact with the page."**

The objective is:

**"Generate Playwright automation that is a faithful, traceable, executable implementation of the approved testcase."**

Therefore:

**Testcase is the business source of truth.**

**Test data changes data, not business steps.**

**Automation implements testcase steps; it does not invent them.**

**Multiple locators improve resilience; they do not change business behavior.**

**Real browser execution provides the truth.**

**Evidence supports every conclusion.**

**Frozen specifications are never silently changed.**

Proceed continuously unless a genuine governance conflict requires Human + Di intervention.
