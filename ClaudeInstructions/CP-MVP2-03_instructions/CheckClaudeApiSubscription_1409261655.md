# CP-MVP2-03 — Claude Subscription / Agent SDK Capability Investigation

## Objective

Determine whether the current local Claude Code environment can support a **real Claude LLM invocation using the user's existing Claude Pro subscription**, through the officially supported Claude Code / `claude -p` / Claude Agent SDK mechanism.

This is an **investigation-only task**.

We are NOT implementing Claude integration yet.

---

# 1. GOVERNANCE — HARD BOUNDARY

DO NOT:

* modify CP-MVP2-03 specification
* modify CP-MVP2-03 implementation
* modify `llm/`
* modify `testcases/`
* modify `knowledge/`
* modify `requirements/`
* add `ClaudeLLMClient`
* add an Anthropic SDK dependency
* add `ANTHROPIC_API_KEY`
* create or modify `.env`
* change configuration files
* change tests
* change RAG
* change validators
* modify the frozen architecture
* start CP-MVP2-04
* perform the live CP-MVP2-03 smoke test yet

This task only determines whether the existing authenticated Claude environment provides a legitimate path for the later live smoke.

If implementation changes appear necessary:

**STOP → REPORT → HUMAN + DI DECIDE**

---

# 2. ENVIRONMENT

Known environment:

* Windows host
* WSL Ubuntu
* Claude Code running inside WSL
* MVP2 repository is local
* User has an active Claude Pro subscription
* User does NOT currently have an OpenAI API account/key
* User does NOT currently have an Anthropic API key

Do not ask the user to create an API key during this task.

Do not ask the user to provide any credential to the chat.

---

# 3. VERIFY CLAUDE CODE AUTHENTICATION

Inside the existing Claude Code session, use the supported `/status` command.

Determine:

* whether Claude Code is authenticated
* authentication method
* whether the current account is the user's Claude subscription
* currently selected model, if shown
* whether an API key is being used
* whether subscription authentication is active

Do NOT print or expose any credential/token.

If `/status` reveals sensitive information, record only the safe authentication classification, not secrets.

Expected desired state:

```text
Claude subscription authentication
```

not:

```text
API key authentication
```

Anthropic documentation states that an `ANTHROPIC_API_KEY` environment variable takes precedence over subscription authentication, so explicitly verify that no such environment variable is overriding the subscription.

---

# 4. CHECK ENVIRONMENT — SAFE ONLY

From the WSL environment, check whether:

```text
ANTHROPIC_API_KEY
```

exists.

Do NOT print its value.

If it exists:

**STOP and report that it is present.**

Do not unset it automatically.

If it does not exist, record:

```text
ANTHROPIC_API_KEY: NOT SET
```

This is the preferred state when using the Claude subscription.

---

# 5. CHECK `claude -p`

Determine whether the currently installed Claude Code supports:

```bash
claude -p
```

Use only a harmless capability/version/help inspection if required.

Do NOT perform the CP-MVP2-03 real testcase-generation smoke yet.

Do NOT consume a substantive model request merely to test the command.

Determine:

* whether `claude -p` exists
* installed Claude Code version
* whether it can use the current authenticated subscription
* whether additional authentication is required

---

# 6. CHECK AGENT SDK AVAILABILITY

Determine whether the installed Claude tooling supports the officially documented Claude Agent SDK path for subscription-authenticated usage.

Check only locally available documentation/package metadata/help information.

Do NOT install packages.

Do NOT modify `requirements.txt`.

Do NOT modify `pyproject.toml`.

Do NOT modify the repository.

Determine:

* whether Claude Agent SDK is available
* whether Python and/or TypeScript SDK support is available
* whether subscription authentication can be used
* whether API-key authentication is mandatory for the intended integration
* whether the existing Claude Code authentication can legitimately be used

---

# 7. IMPORTANT — DO NOT CONFUSE CLAUDE CODE WITH OUR APPLICATION

Do NOT claim that:

```text
Claude Code itself can generate a testcase
```

proves that:

```text
MVP2 application's LLMClient can call Claude
```

Those are different things.

We need to establish whether our application can legitimately invoke Claude through an officially supported mechanism.

The desired future architecture is:

```text
Approved SRS
      ↓
MVP2 RAG
      ↓
Retrieved requirement
      ↓
LLM abstraction
      ↓
Claude
      ↓
Structured testcase
      ↓
Existing deterministic validators
```

This task only determines whether the Claude step is technically and legitimately available.

---

# 8. PROVIDER DECISION

At the end classify the result as exactly one of:

### OPTION A — SUBSCRIPTION PATH AVAILABLE

The existing Claude Pro authentication can legitimately support the required programmatic invocation mechanism.

### OPTION B — API ACCESS REQUIRED

Claude Pro authenticates Claude Code, but the required application-level invocation requires separate Anthropic API/Console access.

### OPTION C — ADDITIONAL CONFIGURATION REQUIRED

The capability exists but requires a documented local configuration step that does not involve changing MVP2 implementation.

### OPTION D — NOT AVAILABLE

The current environment cannot support the intended integration.

---

# 9. REPOSITORY INTEGRITY

Before and after the investigation:

* check Git status
* verify HEAD
* verify origin/main
* confirm no implementation files changed

Expected:

```text
No MVP2 implementation/specification changes
```

If any repository modification occurs:

**STOP and report it.**

Do not commit unrelated changes.

---

# 10. REPORT

Create a concise investigation report under:

```text
docs/claude-execution-reports/CP-MVP2-03-CLAUDE-PROVIDER-INVESTIGATION/
```

Also create a summary under:

```text
docs/claude-execution-reports/CP-MVP2-03-CLAUDE-PROVIDER-INVESTIGATION/summaries/
```

The report must include:

* timestamp
* environment
* Claude Code version
* authentication classification
* `/status` result classification
* `ANTHROPIC_API_KEY` presence/absence
* `claude -p` availability
* Agent SDK availability
* whether subscription authentication can legitimately support the intended use
* whether API access is required
* repository integrity
* recommendation for the next governed step

NEVER include:

* API keys
* OAuth tokens
* credentials
* secrets
* authentication headers
* private account information

---

# 11. FINAL STOP

This task ends after the provider capability investigation.

DO NOT:

* implement Claude integration
* run the CP-MVP2-03 live testcase smoke
* modify the LLM abstraction
* modify tests
* modify specifications
* start CP-MVP2-04

Return the investigation result and wait for HUMAN + DI decision.

The next implementation step will only happen after we review the evidence and determine whether a formal governed change is required.
