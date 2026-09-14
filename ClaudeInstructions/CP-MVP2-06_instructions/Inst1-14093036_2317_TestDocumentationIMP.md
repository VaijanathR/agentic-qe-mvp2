# MVP2 — Persistent End-to-End Agentic QE Lifecycle

## Formal Change Request and Implementation Instruction

## 1. Objective

We have identified an architectural gap in the current MVP2 implementation:

CP-MVP2-03 generates testcase objects in memory but does not persist the actual generated testcase instances as first-class artifacts.

This is not acceptable for the intended Agentic QE lifecycle.

We now need to evolve MVP2 into a **persistent, traceable, reusable, evidence-driven end-to-end Agentic QE system**.

The target lifecycle is:

```text
APPROVED REQUIREMENTS
        ↓
TESTCASE GENERATION
        ↓
PERSIST TESTCASES
        ↓
REQUIREMENT ↔ TESTCASE TRACEABILITY
        ↓
RBTP
        ↓
REQUIREMENT ↔ TESTCASE ↔ RBTP TRACEABILITY
        ↓
DEPENDENCY / REUSABILITY ANALYSIS
        ↓
TEST DATA GENERATION
        ↓
PERSIST TEST DATA
        ↓
TESTCASE ↔ TEST DATA TRACEABILITY
        ↓
PLAYWRIGHT AUTOMATION GENERATION
        ↓
PERSIST PLAYWRIGHT AUTOMATION
        ↓
TESTCASE ↔ AUTOMATION TRACEABILITY
        ↓
REUSABLE PLAYWRIGHT COMPONENTS / FUNCTIONS
        ↓
EXECUTION
        ↓
TIMESTAMPED EXECUTION LOGS
        ↓
EXECUTION SUMMARY
        ↓
EVIDENCE / RCA / GOVERNANCE
```

The same fundamental governance principles must apply to future **security and penetration testing**, while respecting the separately governed security scope and avoiding unsafe or destructive testing.

---

# 2. IMPORTANT GOVERNANCE RULE

CP-MVP2-01 through CP-MVP2-06 are currently frozen.

**Do NOT silently modify any frozen checkpoint.**

Do NOT:

* directly edit frozen specifications
* silently change frozen schemas
* silently change frozen architecture
* silently change frozen testcases
* silently change frozen automation
* silently change CP-06 execution rules
* reopen checkpoints without governance approval
* change requirements to make implementation pass
* remove existing governance controls

This task must begin with a **formal Change Request and impact analysis**.

The implementation may proceed only after the Change Request and affected specification changes are explicitly reviewed and approved.

---

# 3. First Deliverable — Formal Change Request

Create a formal Change Request for this architectural evolution.

The CR must clearly document:

### Change requested

Introduce persistent first-class artifacts and deterministic traceability across:

```text
Requirements
Testcases
RBTP
Dependency Matrix
Test Data
Playwright Automation
Execution Logs
Execution Summary
Security/Penetration Testing
```

### Reason

The current implementation:

* generates testcase objects in memory
* does not independently persist testcase instances
* hands testcase objects to CP-04/CP-05 in memory
* does not provide durable testcase artifacts for human audit
* does not provide reliable testcase reproducibility
* does not provide a durable artifact chain across the complete QE lifecycle

### Business / engineering impact

The CR must explicitly analyze:

* CP-03
* CP-04
* CP-05
* CP-06
* CP-07
* CP-08
* CP-09
* repository structure
* schemas
* traceability
* reporting
* execution
* regression
* future CI/CD integration

### Backward compatibility

Existing valid functionality must remain intact unless explicitly changed through this CR.

---

# 4. Requirement Artifact

Requirements remain the authoritative source.

The system must:

1. Read the Approved SRS.
2. Respect the existing evidence hierarchy.
3. Never modify requirements to make tests pass.
4. Preserve requirement IDs.
5. Preserve source attribution.
6. Detect unsupported/ambiguous requirements.
7. Persist the requirement baseline/version used for downstream generation.

Every downstream artifact must be traceable back to an approved requirement.

---

# 5. Testcase Generation and Persistence

The system must generate governed testcases from the Approved requirements.

Every accepted testcase MUST be persisted as a first-class artifact.

The testcase must not exist only in memory.

Define and implement a canonical persistent testcase format.

At minimum preserve:

```text
testcase_id
title
requirement_ids
journey_id
scenario_type
preconditions
test_steps
expected_result
test_data_reference
priority
source_attribution
generation_metadata
validation_status
```

Use the existing frozen CP-03 testcase schema as the starting point.

Do not silently alter its semantics.

Every persisted testcase must have:

* stable ID
* requirement traceability
* source attribution
* generation metadata
* validation status
* version/baseline reference

The artifact must be independently readable by:

* humans
* CP-04
* CP-05
* future CP-06 execution
* reporting
* audit/review processes

---

# 6. Requirement ↔ Testcase Traceability

Create and persist a deterministic traceability artifact.

At minimum:

```text
Requirement ID
    ↓
Testcase ID(s)
    ↓
Scenario type
    ↓
Testcase status
```

The traceability matrix must identify:

* covered requirements
* uncovered requirements
* multiple testcases covering one requirement
* invalid/orphan references
* unsupported requirements
* duplicate testcases
* possible duplicates

No testcase with an invalid requirement ID may be accepted as traceable.

---

# 7. RBTP

Create a persisted **RBTP artifact**.

First inspect the existing MVP2 terminology and documentation to determine the intended meaning and structure of RBTP.

Do NOT invent a conflicting definition.

If RBTP is not currently defined, explicitly document the definition proposed for approval before implementation.

The RBTP must map appropriately to:

```text
Requirement
    ↕
RBTP item
    ↕
Testcase
```

The RBTP must be persisted and independently auditable.

It must support identification of:

* requirement coverage
* test intent
* test priority/risk where applicable
* positive/alternate/exceptional coverage
* dependencies
* gaps
* execution relevance

Do not duplicate requirement meaning unnecessarily.

---

# 8. Dependency Matrix

Create and persist a deterministic dependency/reusability matrix.

Purpose:

> Understand testcase repetition, shared prerequisites, dependencies and reusable testing assets before automation is generated.

The dependency matrix should identify, where applicable:

```text
Testcase
Requirement
Precondition
Test Data
Shared setup
Authentication/session requirement
Application dependency
External dependency
Reusable component
Potential duplicate/repetition
Execution dependency
```

It must help determine:

* what can be reused
* what should not be repeated unnecessarily
* which testcases share setup
* which data can be reused
* which data must remain unique
* which automation components can be reused
* dependency ordering where required

Persist the matrix as a first-class artifact.

---

# 9. Test Data Generation and Persistence

Generate governed test data from:

```text
Approved SRS
+
accepted testcase
+
RBTP/dependency context where relevant
```

Every accepted test-data dataset MUST be persisted.

Preserve the existing CP-04 schema and governance rules unless explicitly changed through the CR.

Every dataset must map to:

```text
Test Data Set ID
        ↓
Testcase ID
        ↓
Requirement ID(s)
```

Persist:

* dataset ID
* testcase ID
* requirement IDs
* category
* purpose
* validity
* fields
* uniqueness requirements
* dependency references
* source attribution
* generation metadata
* validation status

No fabricated constraints.

No real PII.

No real credentials.

No secrets.

---

# 10. Testcase ↔ Test Data Traceability

Create and persist a deterministic mapping:

```text
Testcase
    ↓
Test Data Set(s)
```

The system must be able to answer:

> Which test data is required to execute this testcase?

and:

> Which testcases consume this test data?

Detect:

* missing test data
* orphan test data
* incompatible test data
* duplicate/possible duplicate data
* uniqueness conflicts

---

# 11. Playwright Automation Generation

Generate Playwright automation from:

```text
Approved testcase
+
approved test data
+
dependency/reusability information
+
authoritative application evidence
```

Automation must be persisted as first-class artifacts.

Every automation artifact must map back to:

```text
Automation ID
    ↓
Testcase ID
    ↓
Requirement ID(s)
    ↓
Test Data Set ID
```

No automation may exist only in memory.

---

# 12. Playwright Reusability Architecture

Do NOT generate one completely independent script per testcase if functionality can be reused.

The automation architecture must support reusable:

* page objects
* components
* functions
* fixtures
* utilities
* authentication/session helpers
* navigation helpers
* data helpers
* assertion helpers
* common business workflows

Where appropriate, separate:

```text
Business workflow
Testcase-specific logic
Reusable UI components
Reusable utilities
Test data
Configuration
Execution
Reporting
```

Avoid duplicated selectors and duplicated workflow logic.

A change to a common application component should require modification in one reusable location wherever technically appropriate.

Do not over-engineer abstractions where the application evidence does not justify them.

---

# 13. Automation Traceability

Persist a deterministic mapping:

```text
Requirement
    ↓
Testcase
    ↓
Test Data
    ↓
Playwright Automation
    ↓
Reusable Component(s)
```

The system must be able to answer:

> Which automation implements this testcase?

and:

> Which requirements are covered by this automation?

and:

> Which reusable components are used by this automation?

---

# 14. Execution Logging

Every real testcase execution must generate persisted execution evidence.

Every execution must have a unique execution ID.

Logs must contain an actual runtime timestamp.

Minimum information:

```text
execution_id
testcase_id
automation_id
requirement_ids
test_data_set_id
browser
environment
start_timestamp
end_timestamp
duration
overall_status
step results
assertion results
errors
diagnostics
evidence locations
```

Do not fabricate runtime values.

Do not report an execution as real unless it actually executed.

---

# 15. Timestamped Log Files

Execution logs must be saved with deterministic timestamped names.

Example:

```text
runs/
  YYYY/
    MM/
      DD/
        <execution_id>/
          execution.log
          step_results.json
          assertions.json
          screenshots/
          traces/
          final_result.json
```

Use actual runtime timestamps.

Do not overwrite previous execution evidence.

A later run must not destroy evidence from an earlier run.

---

# 16. Execution Summary

Every execution batch must produce a persisted execution summary.

The summary must contain:

```text
Execution ID
Date/time
Testcases planned
Testcases executed
Passed
Failed
Blocked
Not Executed
Errors
Requirement coverage
Testcase coverage
Automation coverage
Environment
Browser
Evidence locations
Failure summary
Next actions
```

The summary must distinguish:

* requirement coverage
* testcase coverage
* execution coverage
* pass/fail result

Do not claim requirement coverage merely because a testcase exists.

---

# 17. Security and Penetration Testing

The same fundamental Agentic QE governance principles must apply to security and penetration testing:

```text
Requirement
    ↓
Security Test Scenario
    ↓
Security Test Data / Configuration
    ↓
Security Test Automation / Tool
    ↓
Execution
    ↓
Evidence
    ↓
Finding
    ↓
Severity / Classification
    ↓
Traceability
    ↓
Report
```

Security testing must also have:

* persistent test scenarios
* requirement traceability
* test data/configuration traceability
* reusable security testing components where applicable
* execution logs
* timestamps
* evidence
* findings
* reproducibility
* final reporting

Apply the same principles of:

* no fabricated evidence
* no fabricated results
* deterministic traceability
* human governance
* evidence-backed conclusions
* explicit runtime dependencies
* reproducibility
* versioned artifacts

However:

**Do not introduce destructive, unsafe, unauthorized or production-impacting penetration testing.**

Use authorized, controlled, non-destructive testing within the defined SUT/environment.

Also note that the existing MVP2 scope previously treated security/penetration testing as POST-MVP. Therefore this portion MUST be handled explicitly through the CR rather than silently changing the existing scope.

---

# 18. Artifact Repository Structure

Propose a clean repository structure for persistent artifacts.

The structure should clearly separate:

```text
requirements/
testcases/
rbtp/
traceability/
dependencies/
testdata/
automation/
automation/components/
automation/pages/
automation/utils/
runs/
reports/
security/
```

Do not implement the structure until the CR/specification impact is approved.

Use stable naming conventions and IDs.

---

# 19. End-to-End Traceability Requirement

The final architecture must support this complete chain:

```text
REQ-XXX
   ↓
TC-XXX
   ↓
RBTP-XXX
   ↓
DATA-XXX
   ↓
AUTO-XXX
   ↓
COMPONENT-XXX
   ↓
EXEC-XXX
   ↓
EVIDENCE
   ↓
RESULT
   ↓
REPORT
```

A human must be able to start from **any major artifact** and navigate backward and forward through the chain.

For example:

```text
Requirement → Testcases
Testcase → Requirement
Testcase → Test Data
Testcase → Automation
Automation → Testcase
Automation → Reusable Components
Execution → Automation
Execution → Testcase
Execution → Requirement
Execution → Evidence
```

---

# 20. Deterministic Governance

The LLM may propose:

* testcases
* test data
* RBTP content
* automation
* reusable components
* security scenarios

But deterministic code must validate:

* schema
* IDs
* traceability
* artifact existence
* requirement validity
* duplicate status
* data compatibility
* automation linkage
* execution linkage
* evidence linkage

The LLM must never silently override deterministic governance.

---

# 21. No Requirement Mutation

Absolute rule:

> NEVER CHANGE THE REQUIREMENT TO MAKE THE TEST PASS.

Also:

> NEVER CHANGE TEST DATA TO MAKE THE TEST PASS.

Also:

> NEVER CHANGE EXPECTED RESPONSE/BEHAVIOR TO MAKE AUTOMATION PASS.

If implementation conflicts with an approved requirement:

```text
STOP
↓
REPORT
↓
CLASSIFY
↓
HUMAN + DI DECISION
```

---

# 22. Required Development Approach

Use the existing frozen MVP1/MVP2 architecture wherever reusable.

Do not reinvent existing working components unnecessarily.

Before writing new code:

1. inspect existing implementation
2. identify reusable modules
3. identify interfaces that can remain unchanged
4. identify interfaces requiring formal change
5. document impact
6. implement only after approval

---

# 23. Phase 1 — Required Now

DO NOT implement the change yet.

First produce:

### A. Formal Change Request

Include:

* current architecture
* current gap
* target architecture
* requested changes
* affected checkpoints
* schema impact
* repository impact
* backward compatibility
* regression impact
* security impact
* reporting impact
* migration impact
* risks
* open questions
* proposed acceptance criteria

### B. Architecture Impact Assessment

Show current:

```text
SRS → RAG → TC → DATA → PLAYWRIGHT → EXECUTION
```

versus proposed:

```text
SRS
 ↓
TC ───────────────→ TRACEABILITY
 ↓
RBTP
 ↓
DEPENDENCY MATRIX
 ↓
DATA
 ↓
PLAYWRIGHT
 ↓
REUSABLE COMPONENTS
 ↓
EXECUTION
 ↓
LOGS
 ↓
SUMMARY
 ↓
EVIDENCE
```

### C. Artifact Contract

Define each persistent artifact:

```text
Artifact
Purpose
Schema
ID
Version
Owner
Inputs
Outputs
Traceability
Consumer
Persistence location
```

### D. Checkpoint Impact Matrix

Explicitly identify which checkpoints require change.

At minimum evaluate:

```text
CP-03
CP-04
CP-05
CP-06
CP-07
CP-08
CP-09
```

### E. Migration Strategy

Explain how the existing in-memory implementation will transition to persisted artifacts without corrupting or silently changing frozen historical evidence.

---

# 24. STOP CONDITION

After producing the CR and architecture impact assessment:

**STOP.**

Do not implement.

Do not modify frozen checkpoints.

Do not generate new testcase artifacts yet.

Do not modify CP-03/04/05/06.

Return the CR/report links and commit hash.

We will review the proposed change before authorizing implementation.

---

# 25. Final Response Required

Return:

1. CR status
2. Current architecture finding
3. Proposed target architecture
4. Affected checkpoints
5. Artifact list
6. Traceability model
7. Persistence strategy
8. Playwright reuse strategy
9. Execution evidence strategy
10. Security/penetration-testing impact
11. Migration strategy
12. Open questions
13. Acceptance criteria
14. CR report link
15. Architecture impact report link
16. Commit hash

**This task is specification/change-control only.**

**No implementation changes are authorized in this phase.**
