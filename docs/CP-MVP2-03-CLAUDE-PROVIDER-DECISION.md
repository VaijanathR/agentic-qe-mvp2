# CP-MVP2-03 — Claude Provider Architecture Decision & Governance Record

> **Status:** Implementation Architecture Decision — APPROVED IN PRINCIPLE.
> **Implementation authorization:** NOT YET AUTHORIZED. This document records
> the decision only; a separate, explicit implementation instruction is
> required before any code, dependency, or test change is made.
> **Persisted from:** the Human Owner + Di decision record supplied for
> CP-MVP2-03, verbatim below (sec. 2 onward), following the same
> recovery/persistence convention already used for
> `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` — this file canonicalizes an
> already-made decision, it does not itself decide anything new.

---

## 1. Purpose

Formally record the decision to use the user's existing Claude Pro subscription through the authenticated Claude Code / `claude -p` mechanism as the live LLM provider for CP-MVP2-03 verification.

This document is a governance and architecture decision.

It is NOT authorization to implement the provider yet.

---

# 2. EXISTING FROZEN CONTRACT

The following remains unchanged and continues to be the authoritative CP-MVP2-03 contract:

```text
CP-MVP2-03-SPECIFICATION-v1.0.md
```

Status:

```text
APPROVED / FROZEN
```

The functional contract remains:

```text
APPROVED SRS
      ↓
MVP2 Knowledge Base
      ↓
GOVERNED RAG RETRIEVAL
      ↓
Retrieved requirement context
      ↓
LLM
      ↓
Structured testcase output
      ↓
DETERMINISTIC VALIDATORS
      ↓
Coverage / Traceability / Governance
      ↓
CP-MVP2-03 RESULT
```

No functional requirement in this contract is being changed.

---

# 3. PROVIDER INVESTIGATION RESULT

The completed provider investigation established:

* Claude Code is installed and authenticated.
* Authentication is through the user's Claude Pro subscription.
* `ANTHROPIC_API_KEY` is not required for the current subscription-authenticated environment.
* `claude -p` is available.
* Structured output capabilities are available.
* No MVP2 implementation was changed during investigation.
* No package was installed.
* No specification was changed.
* No RAG or requirement artifacts were changed.

Investigation evidence:

```text
docs/claude-execution-reports/CP-MVP2-03-CLAUDE-PROVIDER-INVESTIGATION/
```

Investigation commit:

```text
65b85ff0307b21276f44c99c401b6710198b1973
```

---

# 4. ARCHITECTURE DECISION

## Decision

APPROVED IN PRINCIPLE:

Use a Claude-backed provider through the existing LLM abstraction, invoking the locally authenticated Claude Code interface through:

```text
claude -p
```

with machine-readable output.

The intended provider boundary is:

```text
MVP2 LLMClient
      ↓
Claude provider adapter
      ↓
claude -p
      ↓
Authenticated Claude Pro subscription
```

The Claude provider adapter MUST remain behind the existing LLM abstraction.

---

# 5. IMPORTANT ARCHITECTURAL BOUNDARY

This is NOT an authorization to modify the frozen specification.

The decision changes only the implementation provider mechanism.

The following MUST remain unchanged:

* requirement semantics
* testcase schema
* testcase governance
* traceability rules
* coverage rules
* Draft protection
* duplicate handling
* unsupported-requirement handling
* source attribution
* RAG behavior
* deterministic validators
* acceptance criteria
* CP-MVP2-03 scope boundary

The provider is an implementation detail behind the LLM abstraction.

---

# 6. TARGET ARCHITECTURE

The intended implementation architecture is:

```text
                    APPROVED SRS
                         ↓
                  MVP2 Knowledge Base
                         ↓
                  GOVERNED RAG
                         ↓
             Retrieved Requirement Context
                         ↓
                    LLMClient
                         ↓
                Claude Provider Adapter
                         ↓
                   claude -p
                         ↓
                  Claude Pro Session
                         ↓
              Structured LLM Response
                         ↓
             Existing Deterministic
                    Validators
                         ↓
          Traceability / Coverage /
              Governance / Audit
```

The Claude adapter MUST NOT bypass:

* RAG
* testcase schema
* deterministic validators
* governance
* attribution
* coverage

---

# 7. SUBPROCESS BOUNDARY

If implemented as a subprocess provider, the adapter MUST:

1. invoke the existing installed `claude` executable
2. use non-interactive `claude -p`
3. request machine-readable output
4. capture stdout/stderr separately
5. apply an explicit timeout
6. detect non-zero exit status
7. reject malformed output
8. never expose credentials
9. never modify repository files as part of the LLM invocation
10. return a controlled error to the existing LLM abstraction when invocation fails

No shell command injection must be possible through requirement text or generated prompts.

Requirement text must be passed safely to the subprocess.

---

# 8. STRUCTURED OUTPUT

Prefer the existing supported structured-output capability:

```text
claude -p
```

with machine-readable JSON output.

Where appropriate, use the supported JSON schema capability.

The provider adapter MUST normalize the returned response into the existing CP-MVP2-03 LLM response contract.

The adapter MUST NOT redefine the testcase governance schema.

---

# 9. RESPONSIBILITY BOUNDARY

Claude is responsible for:

* reasoning about the retrieved requirement
* generating testcase content
* proposing scenario type
* generating test steps
* generating expected outcomes
* assisting reasoning

Deterministic code remains responsible for:

* schema validation
* requirement ID validation
* Approved/Draft enforcement
* traceability
* attribution
* coverage
* duplicate governance
* unsupported requirement governance
* final acceptance/rejection

Therefore:

```text
Claude reasons.
Deterministic code governs.
```

Claude MUST NOT become the final governance authority.

---

# 10. SECURITY

The implementation MUST NOT:

* require an API key when subscription authentication is being used
* create or persist an API key
* print authentication tokens
* write credentials to reports
* commit credentials
* create a credential-containing `.env`
* log authentication headers
* expose Claude authentication state beyond safe classification

The provider must rely on the already authenticated Claude Code environment.

---

# 11. BILLING SAFETY

The implementation MUST NOT silently switch authentication from the user's Claude Pro subscription to API pay-as-you-go billing.

Before live execution, authentication must be verified as subscription-based.

If an `ANTHROPIC_API_KEY` is detected and would override subscription authentication:

```text
STOP
REPORT
DO NOT EXECUTE
```

Anthropic documentation states that an `ANTHROPIC_API_KEY` takes precedence over subscription authentication. Therefore this must be explicitly guarded.

---

# 12. FORMAL CHANGE CLASSIFICATION

Classify this as:

```text
Implementation Architecture Decision
```

rather than a functional requirement change.

No CP-MVP2-03 requirement is changed.

No testcase acceptance criterion is changed.

No RAG contract is changed.

No governance rule is changed.

No scope expansion is authorized.

---

# 13. IMPLEMENTATION AUTHORIZATION

This document records the architectural decision.

It does NOT by itself authorize implementation.

Implementation will be authorized by a separate explicit instruction after HUMAN + DI review.

Until that instruction is issued:

```text
NO CODE CHANGES
NO DEPENDENCY CHANGES
NO TEST CHANGES
NO LIVE SMOKE
NO CP-MVP2-04
```

---

# 14. GOVERNANCE RULE

If implementation discovers that the frozen CP-MVP2-03 contract cannot be satisfied using this provider architecture:

```text
STOP
REPORT
DO NOT CHANGE THE SPECIFICATION
WAIT FOR HUMAN + DI DECISION
```

---

# 15. DECISION

Human decision:

```text
APPROVED
```

Di decision:

```text
APPROVED IN PRINCIPLE
```

Implementation status:

```text
NOT YET AUTHORIZED
```

Next governed step:

```text
Claude provider adapter implementation
```

only after a separate implementation instruction is issued.
