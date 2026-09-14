# CP-MVP2-03 — Controlled Live Claude Smoke Verification Authorization

## 1. TASK CLASSIFICATION

**Checkpoint:** CP-MVP2-03 — LLM Testcase Generation
**Task:** Controlled Live Claude LLM Smoke Verification
**Status:** LIVE VERIFICATION AUTHORIZED
**Specification:** `docs/CP-MVP2-03-SPECIFICATION-v1.0.md`
**Specification Status:** APPROVED / FROZEN
**Provider Decision:** `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`
**Provider Implementation:** Claude provider adapter already implemented and tested.

This is a **verification-only task**.

It is NOT an implementation task and NOT a specification task.

---

# 2. PURPOSE

Perform one tightly controlled real-world verification of the newly implemented Claude provider adapter.

The purpose is to prove the complete path:

```text
APPROVED SRS
      ↓
CP-MVP2-02 Knowledge Base
      ↓
Governed RAG
      ↓
Real Approved Requirement
      ↓
Existing CP-MVP2-03 generation path
      ↓
ClaudeLLMClient
      ↓
real `claude -p`
      ↓
authenticated Claude Pro subscription
      ↓
real Claude response
      ↓
existing parser
      ↓
existing deterministic validators
      ↓
governed testcase result
```

The objective is specifically to close the one remaining advisory from the implementation review:

> The actual Claude CLI JSON response envelope has not yet been verified against the adapter's parser using a real Claude invocation.

---

# 3. GOVERNANCE — NON-NEGOTIABLE

### DO NOT MODIFY THE SPECIFICATION

`docs/CP-MVP2-03-SPECIFICATION-v1.0.md` is frozen.

Do not modify it.

### DO NOT MODIFY THE PROVIDER DECISION

`docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md` is approved.

Do not modify it.

### DO NOT MODIFY IMPLEMENTATION

Do not modify:

* `llm/client.py`
* `testcases/`
* `tests/`
* `requirements/`
* `knowledge/`
* any other implementation file

unless a previously unknown defect makes the smoke test impossible.

If that occurs:

**STOP → REPORT → HUMAN + DI DECIDE**

Do not patch the implementation during this verification.

---

# 4. EXACTLY ONE REAL CLAUDE INVOCATION

Perform **ONE and only ONE** real Claude LLM invocation.

The invocation must use the existing implemented provider path.

Do NOT:

* perform multiple exploratory prompts,
* retry automatically,
* run a second prompt,
* invoke Claude manually for troubleshooting,
* invoke Claude outside the adapter,
* run a testcase-generation batch,
* start an interactive Claude session.

If the first real invocation fails:

**STOP.**

Do not retry.

Record the failure evidence.

---

# 5. AUTHENTICATION

Use the already authenticated local Claude Code / Claude Pro subscription.

Expected authentication model:

```text
claude auth status
      ↓
logged-in Claude Pro session
      ↓
claude -p
```

Do NOT introduce:

* `ANTHROPIC_API_KEY`
* Anthropic API credentials
* OpenAI API credentials
* `.env` credentials
* API billing
* any new credential

Do not print, log, or persist credential values.

Before executing the real call, verify only that the intended subscription authentication is available.

Safe information that may be reported:

```text
loggedIn = true
authMethod = claude.ai
subscriptionType = pro
```

Never report token values.

---

# 6. API-KEY / BILLING SAFETY

Before the live call, inspect whether:

```text
ANTHROPIC_API_KEY
```

is explicitly present.

If it is present:

**STOP.**

Do not execute the live smoke.

Do not print its value.

Report only:

```text
ANTHROPIC_API_KEY detected — live smoke blocked to prevent unintended API-key/billing path.
```

The intended path is the authenticated Claude Pro subscription.

---

# 7. REPOSITORY PRE-CHECK

Record:

* branch
* starting HEAD
* origin/main
* working-tree status

Confirm that the repository is at the expected implementation state.

The implementation commit under verification is:

```text
12c7627bee283b85969a6d9a97fc5fb0564ca660
```

Do not reset, rebase, amend, or otherwise alter repository history.

---

# 8. BASELINE REGRESSION

Before the live call, run the existing automated regression suite.

Expected baseline:

```text
67 passed
0 failed
```

If the baseline is not green:

**STOP.**

Do not perform the live smoke.

The live result must not be contaminated by a pre-existing regression.

---

# 9. REQUIREMENT SELECTION

Use exactly **one real Approved requirement** from the existing CP-MVP2-02 governed Knowledge Base.

Prefer:

```text
REQ-REG-01
```

if it is still present and Approved.

Verify:

* requirement ID
* requirement text
* source document
* source version
* approval status
* governed retrieval metadata

The requirement must come through the existing CP-MVP2-02 RAG path.

Do NOT manually copy a requirement into the test prompt if the existing implementation can retrieve it.

---

# 10. REAL RAG RETRIEVAL

Execute the existing governed RAG retrieval.

The retrieval must use the existing implementation without modification.

Confirm that the selected requirement is:

```text
Approved
```

and originates from the Approved SRS.

Do not use:

* Draft SRS content,
* manually invented requirements,
* website discovery,
* external web content,
* undocumented functionality.

Record the retrieved requirement attribution.

---

# 11. LIVE CLAUDE PROMPT

Use the existing CP-MVP2-03 generation mechanism to construct the prompt.

Do not redesign the prompt during the smoke.

The prompt must provide Claude with the governed requirement context already retrieved by RAG.

Claude should be asked to generate testcase reasoning/content consistent with the existing CP-MVP2-03 contract.

The prompt must make clear that Claude is the reasoning component, not the governance authority.

Do not ask Claude to:

* browse the Demo Web Shop,
* discover new requirements,
* change requirements,
* override approval status,
* determine final coverage,
* bypass deterministic validation,
* execute tests,
* create Git commits.

---

# 12. REAL PROVIDER CALL

Invoke the existing:

```text
ClaudeLLMClient
```

and allow it to execute the actual:

```text
claude -p
```

subscription-authenticated process.

Use the implementation's existing:

* timeout,
* subprocess handling,
* stdout/stderr separation,
* JSON parsing,
* error handling.

Do not bypass the adapter.

The test is specifically intended to verify the adapter.

---

# 13. VERIFY THE REAL RESPONSE

Capture enough evidence to establish that:

1. the real Claude process executed,
2. the process returned,
3. the exit status was handled,
4. stdout was received,
5. the JSON envelope was parsed,
6. the expected response structure was recognized,
7. the actual Claude-generated content reached the existing CP-MVP2-03 pipeline.

Do NOT persist:

* authentication tokens,
* session credentials,
* secrets,
* unnecessary private environment information.

Do not dump an entire raw response if doing so creates unnecessary sensitive or excessive evidence.

Record only the minimum evidence necessary.

---

# 14. DETERMINISTIC VALIDATION

Pass the actual Claude-generated candidate through the **existing deterministic validation path**.

Do not substitute:

* StubLLMClient output,
* manually constructed output,
* previously generated output.

The purpose of this test is to prove:

```text
REAL CLAUDE OUTPUT
        ↓
EXISTING PARSER
        ↓
EXISTING DETERMINISTIC VALIDATORS
```

Verify as applicable:

* schema validity,
* requirement linkage,
* Approved requirement eligibility,
* traceability,
* attribution,
* coverage,
* governance status,
* duplicate handling.

Do not change validators to make the result pass.

---

# 15. IMPORTANT DISTINCTION

A successful Claude response does NOT automatically mean a testcase is governance-approved.

The correct architecture remains:

```text
Claude
  ↓
reasoning / candidate
  ↓
deterministic validation
  ↓
governed result
```

If Claude produces invalid, incomplete, invented, or untraceable content, report that result honestly.

Do not repair the Claude output manually.

Do not edit it to make the smoke pass.

---

# 16. IF THE REAL RESPONSE DOES NOT MATCH

If the real Claude response does not match the adapter's expected envelope:

**STOP.**

Do NOT modify `ClaudeLLMClient`.

Do NOT modify the parser.

Do NOT retry with another prompt.

Report:

* actual response classification,
* expected structure,
* mismatch,
* failure point,
* evidence.

This becomes a follow-up implementation decision after Di review.

---

# 17. IF CLAUDE RETURNS AN ERROR

If `claude -p` exits non-zero or returns a provider error:

**STOP.**

Do not retry.

Classify the result, for example:

```text
AUTHENTICATION_FAILURE
CLI_FAILURE
TIMEOUT
PROVIDER_ERROR
MALFORMED_OUTPUT
PARSING_FAILURE
GOVERNANCE_FAILURE
```

Use the actual observed condition rather than guessing.

---

# 18. NO IMPLEMENTATION CHANGES

This task must leave implementation unchanged.

After the smoke test:

```text
git diff
```

must show no implementation/specification changes caused by this task.

Only the authorized execution report and summary documentation may be added.

---

# 19. REGRESSION AFTER SMOKE

After the single live call and validation, run the full regression suite again.

Expected:

```text
67 passed
0 failed
```

If additional tests exist because of unrelated prior work, report the exact count rather than assuming 67.

Do not modify tests to obtain a green result.

---

# 20. EVIDENCE REPORT

Create a detailed report under:

```text
docs/claude-execution-reports/CP-MVP2-03-LIVE-LLM-SMOKE/
```

Use the established project naming convention.

The report must contain:

### Repository

* starting HEAD
* ending HEAD
* branch
* working-tree status

### Authentication

* Claude Code authentication status
* subscription type
* confirmation that no API key was used
* confirmation that no credential value was logged

### Baseline

* pre-smoke test result

### Requirement

* requirement ID
* source document
* version
* Approved status
* RAG retrieval confirmation

### Live call

* exactly one invocation
* confirmation that it was executed through `ClaudeLLMClient`
* confirmation that real `claude -p` executed
* exit status
* response parsing result

### Validation

* actual Claude output reached the existing deterministic validator
* schema result
* traceability result
* attribution result
* governance result
* coverage result, where applicable

### Post-smoke regression

* exact result

### Repository integrity

* frozen specification unchanged
* provider decision unchanged
* implementation unchanged
* requirements unchanged
* knowledge unchanged
* no downstream files changed

### Usage

State that exactly one live Claude invocation was performed.

Do not claim a token count unless the implementation reliably exposes it.

---

# 21. SUMMARY REPORT

Create a concise summary under:

```text
docs/claude-execution-reports/CP-MVP2-03-LIVE-LLM-SMOKE/summaries/
```

The summary must clearly state:

```text
LIVE CLAUDE INVOCATION: SUCCESS / FAILED / BLOCKED
REAL RESPONSE PARSING: PASS / FAIL / NOT REACHED
DETERMINISTIC VALIDATION: PASS / FAIL / NOT REACHED
REGRESSION: <exact count>
SPECIFICATION: UNCHANGED
IMPLEMENTATION: UNCHANGED
CP-MVP2-04: NOT STARTED
```

Do not use ambiguous language.

---

# 22. GIT COMMIT

Commit only the smoke-test evidence.

Suggested commit message:

```text
docs: record CP-MVP2-03 live Claude smoke verification
```

Push the evidence commit.

Do not amend the existing implementation commit.

Provide the final commit SHA.

---

# 23. HARD STOP CONDITIONS

STOP immediately if:

1. Claude Pro authentication is unavailable.
2. `ANTHROPIC_API_KEY` is detected.
3. baseline regression is not green.
4. the Approved requirement cannot be retrieved through CP-MVP2-02 RAG.
5. the frozen specification is found changed.
6. the provider implementation is found changed unexpectedly.
7. the real Claude invocation requires implementation changes.
8. the first live invocation fails.
9. the response cannot be parsed.
10. deterministic governance cannot process the real response without code modification.

No retry.

No patching.

No autonomous recovery.

---

# 24. ABSOLUTELY OUT OF SCOPE

Do NOT start or implement:

* CP-MVP2-04
* test-data generation
* browser execution
* Playwright
* Demo Web Shop execution
* JMeter
* performance testing
* security testing
* penetration testing
* RCA
* replanning
* self-healing
* CI/CD
* Git PR automation
* multi-agent orchestration
* production deployment
* dashboards
* additional LLM providers

---

# 25. FINAL EXPECTED COMPLETION RESPONSE

Return:

1. detailed execution report GitHub path,
2. summary report GitHub path,
3. evidence commit SHA,
4. starting and ending HEAD,
5. exact pre-smoke regression result,
6. exact post-smoke regression result,
7. confirmation of exactly one real Claude invocation,
8. real response parsing result,
9. deterministic validation result,
10. requirement ID and Approved-SRS attribution,
11. files changed,
12. confirmation frozen artifacts remain unchanged,
13. confirmation no API key was used,
14. confirmation no downstream checkpoint was started.

Do not proceed to CP-MVP2-04.

**This task ends after the single live smoke verification and evidence commit.**

The next action is **Di's independent review and gate decision**.
