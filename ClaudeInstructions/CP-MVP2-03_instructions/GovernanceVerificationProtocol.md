# CP-MVP2-03 — Live Pipeline Governance Verification Protocol

## 1. GOVERNANCE STATUS

This is a **controlled verification task only**.

The following are APPROVED/FROZEN and MUST NOT be modified:

* CP-MVP2-03 Specification v1.0
* CP-MVP2-03 implementation
* Claude Provider Architecture Decision
* CP-MVP2-02 Knowledge Base/RAG
* Approved SRS
* testcase schema
* deterministic validators
* parser
* prompts
* provider configuration

Do NOT start CP-MVP2-04 or any downstream checkpoint.

### Governing principle

> **LLM reasons. Deterministic code governs.**

This verification exists to prove that principle using a real Claude response.

---

# 2. OBJECTIVE

Verify the complete existing CP-MVP2-03 pipeline using:

* the real Approved SRS
* the existing CP-MVP2-02 RAG
* REQ-REG-01
* the existing Claude provider adapter
* the real authenticated Claude Pro subscription
* the existing testcase generation pipeline
* the existing deterministic validators

The verification must establish that:

1. Claude-generated testcase content is passed through the existing deterministic governance layer.
2. Valid testcase output can contribute to traceability and coverage.
3. A valid empty response (`[]`) cannot create a fabricated testcase.
4. Empty output cannot falsely produce coverage.
5. Deterministic governance remains the final authority.
6. No component silently changes requirements or generates unsupported content merely to achieve coverage.

---

# 3. EXACT SCOPE

Use exactly:

**Requirement:** `REQ-REG-01`

**Source:** `requirements/MVP2_SRS_v1.0_APPROVED.md`

**Version:** `v1.0`

**Approval:** Approved

Retrieve the requirement through the existing CP-MVP2-02 Knowledge Base/RAG implementation.

Do not manually reconstruct the requirement.

Do not substitute another requirement.

Do not modify the RAG.

---

# 4. PROVIDER

Use the existing:

`ClaudeLLMClient`

through the existing:

`LLMClient`

boundary.

Use the authenticated Claude Code / Claude Pro subscription path.

Do NOT:

* use the Anthropic REST API
* configure `ANTHROPIC_API_KEY`
* use an API key
* switch billing
* install an SDK
* modify provider code
* modify provider configuration
* introduce another LLM provider

If `ANTHROPIC_API_KEY` is detected:

**STOP immediately.**

Report only its presence. Never reveal its value.

---

# 5. EXECUTION PATH

The verification MUST exercise the actual production CP-MVP2-03 pipeline.

Expected path:

```text
APPROVED SRS
     ↓
MVP2 CP-02 Knowledge Base
     ↓
Governed RAG retrieval
     ↓
REQ-REG-01 context
     ↓
Existing testcase generation pipeline
     ↓
ClaudeLLMClient
     ↓
Real Claude
     ↓
Structured testcase candidate(s)
     ↓
Existing deterministic validators
     ↓
Traceability
     ↓
Coverage
     ↓
Governance result
```

Do NOT replace the pipeline with a hand-built testcase.

Do NOT use a stub.

Do NOT manually inject a Claude response into the validator.

The objective is to verify the actual integrated path.

---

# 6. EXECUTION COUNT

Perform **one controlled live pipeline execution**.

This is a verification execution, not a characterization study.

Do NOT retry automatically.

Do NOT repeat the execution if Claude returns `[]`.

A legitimate empty result must be treated as evidence.

---

# 7. EXPECTED POSSIBLE OUTCOMES

Claude may return either:

### OUTCOME A — POPULATED TESTCASE RESULT

Example:

```text
[
  {
    ...
  }
]
```

If this occurs:

* parse the actual Claude response
* pass it through the existing deterministic validators
* verify schema
* verify requirement ID
* verify requirement existence
* verify Approved status
* verify attribution
* verify traceability
* calculate coverage
* record governance result

Do not assume that because Claude produced a testcase it is automatically accepted.

---

### OUTCOME B — EMPTY RESULT

Example:

```text
[]
```

If this occurs:

* do NOT create a testcase
* do NOT substitute a testcase
* do NOT ask Claude again
* do NOT retry
* do NOT alter the prompt
* do NOT alter the requirement
* do NOT change the validators

The system must report the actual consequence of zero generated testcases.

Specifically verify:

```text
Generated TCs = 0
Accepted TCs = 0
REQ-REG-01 covered = NO
REQ-REG-01 uncovered = YES
```

The coverage calculation MUST NOT count REQ-REG-01 as covered.

If the existing governance layer reports an explicit unsupported/needs-clarification or equivalent status, record it exactly.

If it reports an uncovered requirement without a separate status, record that.

Do not invent a governance status.

---

# 8. CRITICAL GOVERNANCE RULE

The following behavior is PROHIBITED:

```text
Claude → []
       ↓
Agent generates its own testcase
       ↓
Requirement marked covered
```

Also prohibited:

```text
Claude → []
       ↓
System assumes coverage
       ↓
GREEN
```

Also prohibited:

```text
Claude → []
       ↓
Requirement modified
       ↓
Testcase generated
```

Also prohibited:

```text
Claude → []
       ↓
Prompt changed
       ↓
Claude retried
```

The implementation must faithfully preserve the real result.

---

# 9. TRACEABILITY VERIFICATION

For every accepted testcase, verify:

```text
Testcase
   ↓
Valid Requirement ID
   ↓
REQ-REG-01
   ↓
Approved SRS v1.0
   ↓
RAG/source attribution
```

If no testcase is generated:

```text
REQ-REG-01
   ↓
No accepted testcase
   ↓
Uncovered
```

No artificial traceability may be created.

---

# 10. COVERAGE VERIFICATION

Use the existing deterministic coverage calculation.

For this single applicable requirement:

### If testcase is accepted:

```text
Total applicable requirements = 1
Covered requirements = 1
Coverage = 100%
```

### If Claude returns `[]`:

```text
Total applicable requirements = 1
Covered requirements = 0
Coverage = 0%
```

Do not alter the denominator.

Do not exclude REQ-REG-01 merely because Claude generated no testcase.

Do not fabricate another requirement.

---

# 11. DETERMINISTIC VALIDATION

Use the existing validators unchanged.

Verify, as applicable:

* schema validity
* requirement ID validity
* Approved requirement status
* Draft protection
* traceability
* source attribution
* duplicate handling
* unsupported handling
* coverage calculation
* governance status

Do not modify any validator.

---

# 12. IMPORTANT DISTINCTION

Record separately:

### LLM result

What Claude actually returned.

### Deterministic result

What the existing validation/governance layer concluded.

### Coverage result

What the existing coverage calculation produced.

### Final governance result

What the pipeline ultimately reports.

Never combine these into one subjective judgment.

---

# 13. REGRESSION

Before execution:

```bash
pytest -q
```

Expected baseline:

**67 passed, 0 failed**

If the baseline is not 67/67:

**STOP before the live execution.**

After execution:

```bash
pytest -q
```

Expected:

**67 passed, 0 failed**

No regression is acceptable.

---

# 14. REPOSITORY INTEGRITY

Before execution record:

* current HEAD
* branch
* working tree
* origin/main relationship

After execution verify:

* CP-MVP2-03 specification unchanged
* provider decision unchanged
* implementation unchanged
* RAG unchanged
* Approved SRS unchanged
* parser unchanged
* prompts unchanged
* tests unchanged except evidence/report additions if applicable

No unrelated files may be changed.

---

# 15. EVIDENCE

Create:

```text
docs/claude-execution-reports/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE/
```

Detailed report:

```text
CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE-EXEC-<timestamp>-<id>.md
```

Summary:

```text
docs/claude-execution-reports/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE/summaries/
```

Summary filename:

```text
CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE-SUMMARY-<timestamp>-<id>.md
```

---

# 16. REQUIRED DETAILED REPORT

Include:

## A. Governance

* CP-MVP2-03 v1.0 verified frozen
* provider decision verified
* no implementation changes
* no prompt changes
* no parser changes
* no downstream work

## B. Environment

* Claude Code version
* authentication method
* subscription type
* `ANTHROPIC_API_KEY` presence/absence
* model used
* timeout
* no credential values

## C. RAG

* REQ-REG-01
* Approved SRS v1.0
* source attribution
* confirmation existing CP-02 RAG was used

## D. Live execution

Record:

* invocation start/end
* elapsed time
* CLI status
* outer envelope status
* inner result status
* result type
* number of generated candidates

Do not store secrets.

## E. Deterministic governance

Record:

* schema validation
* requirement validation
* approval validation
* traceability
* attribution
* duplicate handling
* unsupported handling
* accepted testcase count
* rejected/quarantined count

## F. Coverage

Record:

* total applicable requirements
* covered requirements
* uncovered requirements
* coverage percentage

## G. Final result

Explicitly show:

```text
LLM result
    ↓
Deterministic validation result
    ↓
Traceability result
    ↓
Coverage result
    ↓
Governance result
```

## H. Regression

* baseline
* final

## I. Git

* starting HEAD
* ending HEAD
* files changed
* commit
* push status

## J. Scope

Explicitly state:

**CP-MVP2-04 NOT STARTED**

---

# 17. PASS/FAIL DECISION TABLE

| Observation                            | Expected governance behavior                     | Result           |
| -------------------------------------- | ------------------------------------------------ | ---------------- |
| Valid testcase + valid REQ             | Accept and trace                                 | PASS if verified |
| Valid testcase + unknown REQ           | Reject/quarantine                                | PASS if verified |
| Draft-only testcase                    | Reject                                           | PASS if verified |
| `[]` from Claude                       | Zero accepted TCs; requirement remains uncovered | PASS if verified |
| `[]` converted into testcase           | PROHIBITED                                       | FAIL             |
| `[]` counted as coverage               | PROHIBITED                                       | FAIL             |
| Requirement changed to obtain testcase | PROHIBITED                                       | FAIL             |
| Prompt changed after empty result      | PROHIBITED                                       | FAIL             |
| Parser changed                         | PROHIBITED                                       | FAIL             |
| Stub substituted for real Claude       | PROHIBITED                                       | FAIL             |
| Regression failure                     | PROHIBITED                                       | FAIL             |

Only report PASS/FAIL based on observed evidence.

Do not manufacture a successful outcome.

---

# 18. OBSERVATION VS INTERPRETATION

Separate:

### CONFIRMED OBSERVATIONS

Facts directly observed during execution.

### INTERPRETATION

Reasonable conclusions based on those observations.

### UNKNOWN

Anything not established by the evidence.

Do not claim that an empty response means Claude is defective.

Do not claim that a populated response means Claude is reliable.

This single execution is a governance verification, not a statistical reliability study.

---

# 19. HARD STOPS

STOP immediately if:

* frozen specification differs
* implementation differs unexpectedly
* Approved SRS differs
* RAG differs unexpectedly
* API key is detected
* authentication changes unexpectedly
* baseline regression is not 67/67
* provider cannot execute
* an unauthorized code/specification change is required
* CP-MVP2-04 work is encountered

Do not work around the problem.

Report it.

---

# 20. FINAL RULE

This task ends after:

**ONE REAL CLAUDE PIPELINE EXECUTION + DETERMINISTIC GOVERNANCE OBSERVATION + COVERAGE VERIFICATION + REGRESSION + EVIDENCE + GIT PUSH**

Do not fix anything.

Do not improve anything.

Do not retry anything.

Do not proceed to CP-MVP2-04.

The evidence will be reviewed separately by Di before any implementation decision is made.

# EXPECTED GOVERNED END STATE

The experiment must leave the implementation exactly as it was before execution.

Only evidence/report artifacts may be added.

The purpose is to establish whether the existing CP-MVP2-03 implementation correctly governs a real Claude result—including the important case where Claude returns a valid empty testcase set.

**STOP and await Di's review after pushing the evidence.**
