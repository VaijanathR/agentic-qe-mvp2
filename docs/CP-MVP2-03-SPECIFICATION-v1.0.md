# CP-MVP2-03 — LLM Testcase Generation

### Recovered Approved Specification — v1.0

> **Status:** APPROVED / FROZEN
> **Origin:** Recovered from the previously approved CP-MVP2-03 design discussion
> **Purpose:** Canonicalize the already-approved specification into a repository artifact
> **Important:** This is a recovery/persistence activity, **not a specification change**.

---

## 1. Objective

Generate governed, traceable testcases from requirements retrieved through the frozen MVP2 Knowledge Base / RAG layer.

The objective is to demonstrate that the Agentic QE system can:

1. Retrieve governed requirements from the approved knowledge base.
2. Provide those requirements as controlled context to an LLM.
3. Generate structured testcases.
4. Validate the generated testcases deterministically.
5. Establish requirement-to-testcase traceability.
6. Calculate genuine requirement coverage.
7. Detect duplicate or potentially duplicate testcases.
8. Prevent Draft/unapproved requirements from becoming accepted testcases.
9. Identify unsupported requirements rather than inventing functionality.
10. Produce a governed CP-MVP2-03 result with evidence and attribution.

---

# 2. Scope

## 2.1 In Scope

CP-MVP2-03 covers:

* Requirement retrieval through the frozen MVP2 Knowledge Base/RAG layer.
* LLM-based testcase generation.
* Structured testcase output.
* Positive scenarios.
* Alternate scenarios where justified.
* Exceptional scenarios where justified.
* Requirement-to-testcase traceability.
* Requirement coverage calculation.
* Source attribution.
* Testcase schema validation.
* Requirement ID validation.
* Duplicate detection.
* Unsupported requirement handling.
* Draft/Approved governance.
* Deterministic validation.
* Governance reporting.
* Regression validation against CP-MVP2-01 and CP-MVP2-02.

---

## 2.2 Explicitly Out of Scope

CP-MVP2-03 is **NOT responsible for**:

* Browser automation.
* API execution.
* Test-data execution.
* Performance testing.
* Security testing execution.
* Penetration testing.
* Self-healing.
* Git PR creation.
* Modifying requirements.
* Discovering new Demo Web Shop functionality.
* Implementing later checkpoints.
* CP-MVP2-04 or any downstream checkpoint capabilities.

---

# 3. Authoritative Architecture

The authoritative flow is:

```text
APPROVED SRS
     ↓
MVP2 KNOWLEDGE BASE
     ↓
GOVERNED RAG RETRIEVAL
     ↓
RETRIEVED REQUIREMENT CONTEXT
     ↓
LLM
     ↓
STRUCTURED TESTCASE OUTPUT
     ↓
DETERMINISTIC VALIDATORS
     ↓
COVERAGE / TRACEABILITY / GOVERNANCE
     ↓
CP-MVP2-03 RESULT
```

---

# 4. Core Architectural Principle

The fundamental responsibility boundary is:

> **RAG supplies the evidence.
> LLM performs the reasoning.
> Deterministic code decides whether the output complies.**

The LLM must not become the final authority for governance.

The generated testcase must pass deterministic validation before it can be considered an accepted CP-MVP2-03 testcase.

---

# 5. Input Contract

The source of testcase generation shall be the governed requirement context obtained from the frozen MVP2 Knowledge Base/RAG layer.

Each retrieved requirement context shall carry, as applicable:

* `requirement_id`
* `requirement_text`
* `source_document`
* `source_version`
* `approval_status`
* retrieval metadata

The generation request may specify controlled scenario types.

However:

> Generation parameters must not alter, reinterpret, weaken, or replace the underlying requirements.

---

# 6. Testcase Output Contract

The generated testcase shall contain the following logical information:

| Field                 | Purpose                               |
| --------------------- | ------------------------------------- |
| `testcase_id`         | Unique testcase identifier            |
| `title`               | Human-readable testcase title         |
| `requirement_ids`     | Requirement(s) covered                |
| `journey_id`          | Business/user journey association     |
| `scenario_type`       | Positive / Alternate / Exceptional    |
| `preconditions`       | Conditions required before execution  |
| `test_steps`          | Ordered testcase actions              |
| `expected_result`     | Expected outcome                      |
| `test_data_reference` | Reference to required test data       |
| `priority`            | Testcase priority                     |
| `source_attribution`  | Evidence/source supporting testcase   |
| `generation_metadata` | Generation and provenance information |

The exact implementation representation shall reuse the conventions established in CP-MVP2-01 and CP-MVP2-02 rather than unnecessarily introducing competing structures.

---

# 7. Scenario Types

The system may generate:

### 7.1 Positive

The primary valid business flow satisfying the requirement.

### 7.2 Alternate

A valid alternative flow supported by the requirement context.

### 7.3 Exceptional

An invalid, error, boundary, rejection, or exceptional flow where such a scenario is justified by governed requirement evidence.

### Governance rule

A scenario shall **not** be created merely because it is a common testing practice.

It must be justified by the governed requirement context.

The system must not invent business requirements or unsupported Demo Web Shop functionality.

---

# 8. Requirement Traceability

Every accepted testcase must map to one or more valid requirement IDs.

The traceability chain is:

```text
TESTCASE
   ↓
REQUIREMENT ID
   ↓
APPROVED SRS
   ↓
SOURCE DOCUMENT / VERSION
   ↓
RETRIEVED CHUNK / ATTRIBUTION
```

## Mandatory rules

### Missing requirement ID

Reject the testcase.

### Empty requirement ID

Reject the testcase.

### Unknown requirement ID

Reject or quarantine the testcase.

### Orphan testcase

A testcase without valid requirement traceability cannot be accepted.

---

# 9. Requirement Coverage

Requirement coverage shall be calculated as:

```text
Requirement Coverage =
Requirements having ≥1 valid testcase
-------------------------------------
Total applicable requirements
× 100
```

The report shall contain:

* Total applicable requirements.
* Covered requirements.
* Uncovered requirements.
* Coverage percentage.

Invalid, fabricated, unknown, or untraceable requirement IDs **do not count toward coverage**.

A testcase contributes to coverage only when:

1. It is valid.
2. Its requirement mapping is valid.
3. The mapped requirement exists in the authoritative requirement set.

---

# 10. Unsupported Requirements

If there is insufficient governed evidence to generate a valid testcase, the system must **not invent one**.

Instead, the requirement shall be reported as:

> **UNSUPPORTED / NEEDS CLARIFICATION**

The result shall include the reason why a valid testcase could not be generated.

Examples include:

* insufficient requirement information;
* ambiguous business rule;
* missing required acceptance condition;
* unavailable governed evidence.

The objective is to expose the gap rather than hide it.

---

# 11. Approved vs Draft Governance

The Approved SRS is authoritative.

### Approved

Approved requirements are eligible for testcase generation.

### Draft

Draft requirements are **not eligible** to become accepted testcases.

If Draft information is accidentally present in retrieved context:

```text
Draft information
       ↓
retrieved context
       ↓
LLM
       ↓
possible generated testcase
       ↓
DETERMINISTIC GOVERNANCE
       ↓
REJECT / QUARANTINE
```

The deterministic governance layer must prevent Draft information from becoming an accepted testcase.

An explicit test shall verify this behavior.

---

# 12. Requirement Invention Prevention

The system must not:

* create new business requirements;
* change requirement meaning;
* introduce unsupported business rules;
* assume undocumented application functionality;
* use general LLM knowledge as a substitute for missing approved requirements.

Where evidence is insufficient:

> **UNSUPPORTED / NEEDS CLARIFICATION**

rather than invention.

---

# 13. Duplicate Detection

Duplicate detection shall be deterministic where possible, with semantic similarity used where practical.

The objective is to prevent equivalent testcases from being generated merely because the wording differs.

A testcase may be classified as:

* `UNIQUE`
* `DUPLICATE`
* `POSSIBLE_DUPLICATE`

A particularly important duplicate condition is:

> Same requirement + same scenario + same expected outcome

Such testcases should not be accepted as separate equivalent testcases merely because their wording differs.

### Important safeguard

Duplicate detection must not be so aggressive that legitimate distinct scenarios are incorrectly removed.

Therefore, `POSSIBLE_DUPLICATE` may require further review rather than automatic deletion.

---

# 14. Attribution

Every testcase must preserve the reason it exists.

The conceptual attribution chain is:

```text
TC-004
  ↓
REQ-003
  ↓
Approved SRS
  ↓
Retrieved chunk / document reference
```

The purpose is to allow a reviewer to answer:

> **Why does this testcase exist?**

and:

> **Which approved requirement and evidence justify it?**

---

# 15. LLM Responsibilities

The LLM is responsible for reasoning and generation.

It may:

* understand the retrieved requirement;
* reason about applicable scenarios;
* generate testcase structure;
* generate testcase steps;
* generate expected outcomes;
* assist with requirement mapping;
* identify possible unsupported areas;
* assist duplicate reasoning where appropriate.

The LLM is **not** the final governance authority.

---

# 16. Deterministic Responsibilities

Deterministic code is responsible for enforcing the contract.

It shall validate, as applicable:

* testcase schema;
* requirement existence;
* requirement IDs;
* traceability;
* coverage;
* duplicate IDs;
* duplicate testcases;
* Approved/Draft status;
* governance rules;
* attribution presence;
* accepted/rejected/quarantined status.

LLM assistance may be used where semantic reasoning is genuinely required, but the final compliance decision must remain governed and auditable.

---

# 17. Governance Outcomes

The CP-MVP2-03 implementation shall distinguish between valid and invalid outputs.

Possible governance outcomes include:

```text
ACCEPTED
REJECTED
QUARANTINED
UNSUPPORTED / NEEDS CLARIFICATION
POSSIBLE_DUPLICATE
```

The exact implementation status vocabulary should remain consistent with the established MVP2 conventions.

---

# 18. Acceptance Criteria

## 18.1 Functional Acceptance

The implementation must demonstrate:

* LLM testcase generation works.
* Structured testcase output is produced.
* Positive scenarios are generated.
* Alternate scenarios are generated where applicable.
* Exceptional scenarios are generated where justified.

---

## 18.2 Governance Acceptance

The implementation must demonstrate:

* Only approved governed requirements are consumed for accepted output.
* Draft requirements cannot become accepted testcases.
* Unknown requirement IDs are rejected/quarantined.
* Unsupported requirements are explicitly reported.
* Requirements are not invented.

---

## 18.3 Traceability Acceptance

The implementation must demonstrate:

* Every accepted testcase maps to a valid requirement.
* Source attribution exists.
* Requirement coverage is calculated.
* Coverage excludes invalid/untraceable mappings.

---

## 18.4 Quality Acceptance

The implementation must demonstrate:

* Schema validation.
* Duplicate detection.
* Coverage calculation.
* Deterministic validation.
* Governance enforcement.
* Source attribution.

---

## 18.5 Regression Acceptance

All existing:

* CP-MVP2-01 tests
* CP-MVP2-02 tests

must continue to pass.

No CP-MVP2-03 implementation may break the previously frozen checkpoints.

---

# 19. CP-MVP2-03 Boundary

The checkpoint ends at:

```text
REQUIREMENT
    ↓
RAG
    ↓
LLM
    ↓
TESTCASE
    ↓
VALIDATION
    ↓
GOVERNED OUTPUT
```

The checkpoint does **not** proceed beyond governed testcase generation.

---

# 20. Explicitly Prohibited During Implementation

Claude must not use CP-MVP2-03 implementation as an opportunity to introduce:

* browser automation;
* Playwright execution;
* API execution;
* test-data execution;
* performance execution;
* security execution;
* penetration testing;
* self-healing;
* CI/CD;
* Git PR automation;
* downstream checkpoint functionality;
* changes to CP-MVP2-01;
* changes to frozen CP-MVP2-02;
* requirement modifications.

---

# 21. Frozen Specification Governance

This specification is **v1.0**.

Once persisted and frozen:

> **Claude must implement against this specification exactly as approved.**

Neither Claude nor Di may silently reinterpret the specification during implementation.

If an implementation issue is discovered:

```text
STOP
 ↓
REPORT
 ↓
EVIDENCE
 ↓
HUMAN + DI REVIEW
 ↓
DECISION
```

The implementation must not be made to pass by weakening the specification.

---

# 22. Change Control

Any change to this specification must be handled as a formal versioned Change Request.

The Change Request must identify:

1. Change requested.
2. Reason.
3. Evidence.
4. Impact.
5. Affected requirements.
6. Affected architecture.
7. Affected tests.
8. Backward compatibility.
9. Effect on previously generated artifacts.

Suggested versioning:

* **v1.0** — Initial approved/frozen specification.
* **v1.1** — Minor, non-breaking change.
* **v2.0** — Material change.

Claude cannot self-authorize such a change.

Human + Di must decide.

---

# 23. Governing Engineering Principle

The governing principle for CP-MVP2-03 is:

> **NEVER CHANGE THE SPECIFICATION TO MAKE THE IMPLEMENTATION PASS.**

If implementation and specification conflict, the specification remains authoritative until an explicitly approved Change Request changes it.

---

# 24. CP-MVP2-03 Gate

CP-MVP2-03 can be declared complete only when:

```text
Specification v1.0
        ↓
Implementation
        ↓
Deterministic Validation
        ↓
Traceability
        ↓
Coverage
        ↓
Governance
        ↓
Regression
        ↓
Evidence
        ↓
Git Checkpoint
        ↓
CP-MVP2-03 GATE
```

The final gate must establish that the implementation satisfies the frozen contract without silently modifying it.

---

## Status

**CP-MVP2-03 Specification v1.0 — RECOVERED FROM PREVIOUSLY APPROVED DESIGN**

**Recommended repository filename:**

`CP-MVP2-03-SPECIFICATION-v1.0.md`

**Not yet to be treated as a new specification.** Its purpose is to persist the specification that you and I had already approved.
