# CP-MVP2-03 — Claude Subscription / Agent SDK Capability Investigation

**This is an investigation-only report. No CP-MVP2-03 implementation, specification, or configuration change was made. No testcase generation was performed — Claude Code's own capability is not evidence that MVP2's `llm/` abstraction can call Claude; this report is strictly about whether/how the latter would be possible.**

## Timestamp / Environment

* Timestamp (UTC): 2026-09-14 11:28:28
* Environment: Windows host, WSL Ubuntu, Claude Code running inside WSL
* MVP2 repository: `D:\AI PROJECTS\agentic-qe-mvp2` (local)
* Claude Code version: **2.1.270** (`claude --version`)
* Claude CLI binary: `/home/vaij/.local/bin/claude` -> `/home/vaij/.local/share/claude/versions/2.1.270`

## Authentication Classification

Command run: `claude auth status` (a documented, safe, non-mutating CLI subcommand — no `/status` REPL meta-command is invocable from outside an interactive session, so this CLI equivalent was used instead; it reports the same authentication classification).

Result (redacted — see note below):

```json
{
  "loggedIn": true,
  "authMethod": "claude.ai",
  "apiProvider": "firstParty",
  "analyticsDisabled": false,
  "subscriptionType": "pro"
}
```

**Note on redaction:** the raw command output additionally included the account's email address, `orgId`, and `orgName`. These are private account information (not credentials/tokens, but explicitly out of scope per this task's "NEVER include ... private account information" instruction) and have been omitted from this report and from every other artifact this task touches.

* **Authentication method:** `claude.ai` (OAuth-based, browser sign-in) — **not** a raw Anthropic API key.
* **Account type:** Claude **Pro** subscription (`subscriptionType: "pro"`).
* **Provider classification:** `apiProvider: "firstParty"` — first-party Anthropic subscription auth, not a console/API-key-issued credential.
* Corroborating evidence: `~/.claude/.credentials.json` (mode `600`, not read for values) has a top-level `claudeAiOauth` object whose sub-keys are `accessToken, refreshToken, expiresAt, refreshTokenExpiresAt, scopes, subscriptionType, rateLimitTier` — an OAuth token structure, not a static API key. **No token/secret value was read, printed, or recorded anywhere.**

**Classification: Claude subscription authentication is active.** This is the desired state named in the task (as opposed to API-key authentication).

## `ANTHROPIC_API_KEY` Presence

Checked in the current shell and in a fresh `bash -lc` login shell (to rule out a shell-specific artifact), and searched `~/.bashrc`, `~/.bash_profile`, `~/.profile`, `~/.zshrc`, `/etc/environment`, and `~/.claude/settings.json` (which contains only `theme` and `autoMode` — no `apiKeyHelper` or API-key override).

```text
ANTHROPIC_API_KEY: NOT SET
```

This is the preferred state: subscription authentication is not being overridden by an API key anywhere this investigation could check.

## `claude -p` Availability

`claude -h` confirms `-p, --print` exists: "Print response and exit (useful for pipes)." No prompt was actually sent — only `--version` and `--help` were inspected, per the task's "harmless capability/version/help inspection only" instruction; no substantive model request was made and no tokens were consumed.

Relevant flags discovered (from `--help` text only, not exercised):

* `--output-format <format>` — `"text"` (default), `"json"` (single result), or `"stream-json"`. Works only with `--print`.
* `--json-schema <schema>` — "JSON Schema for structured output validation," works with `--print`.
* `--input-format <format>` — `"text"` or `"stream-json"`.

**Finding:** `claude -p --output-format json` (optionally with `--json-schema`) is a documented, non-interactive, single-JSON-result invocation mode. Because it runs inside the same authenticated Claude Code process, it uses the same subscription authentication verified above — it does not require a separate `ANTHROPIC_API_KEY`. This was inferred from the CLI's own `--help` text and the confirmed authentication state, not from an actual invocation (none was performed).

## Claude Agent SDK Availability

Checked (existence/metadata only, nothing installed):

* `pip3 show claude-agent-sdk` → not found.
* `pip3 show anthropic` → not found.
* `python3 -c "import claude_agent_sdk"` → `ModuleNotFoundError`.
* Project venv (`.venv/Scripts/python.exe -m pip list`, from the prior CP-MVP2-03 implementation task): no `anthropic`/`claude-agent-sdk` package either — only `openai`.
* `npm ls -g --depth=0` → empty (no global npm packages installed at all).
* No install was performed (per the hard governance boundary — "Do NOT install packages").

**Finding: the Claude Agent SDK (Python or TypeScript package) is NOT currently installed anywhere accessible to this repository or this system.** Whether that separate SDK package would itself support subscription-only authentication (vs. requiring `ANTHROPIC_API_KEY`) could not be determined without installing it, which this task does not authorize. This is recorded as **unconfirmed**, not as a negative finding about the SDK's own capabilities.

## Repository Integrity

* Before: `git status` — dirty only with the same pre-existing, unrelated `.gitignore`/`README.md` modifications and untracked `ClaudeInstructions/*.md` files (none referenced by this task); HEAD `d3157a7038ae8b0918385d64400f497e4ef116d8`, equal to `origin/main`.
* During this investigation: no file under `llm/`, `testcases/`, `knowledge/`, `requirements/`, or `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` was read for modification purposes, opened for editing, or written to. Only external system paths (`~/.claude*`, shell profile files) and CLI `--help`/`--version`/`auth status` output were inspected.
* After: `git diff --stat HEAD -- "docs/CP-MVP2-03-SPECIFICATION-v1.0.md" requirements/ knowledge/ llm/ testcases/ tests/` → empty. **No MVP2 implementation or specification changes occurred.**
* No package was installed; no `.env` was created or modified; no `ANTHROPIC_API_KEY` was set, unset, or written anywhere by this investigation.

## Provider Decision

**Classification: OPTION A — SUBSCRIPTION PATH AVAILABLE**, specifically via the `claude -p --output-format json` (optionally `--json-schema`) non-interactive CLI invocation mechanism:

* It is officially documented (`claude --help`), already installed, and already authenticated under the user's active Claude Pro subscription — confirmed via `claude auth status` (OAuth/`firstParty`/`pro`) and the confirmed absence of any `ANTHROPIC_API_KEY` override.
* It supports single-JSON-result structured output, which is the shape MVP2's `llm.LLMClient.propose_testcases()` boundary needs.
* No additional account creation, console access, or API key is required to reach this mechanism.

This is qualified in one respect: the specific, separately-branded **Claude Agent SDK package** was not found installed and was not tested (installing it is out of this task's scope), so its own auth behavior in isolation remains **unconfirmed** — but the CLI (`claude -p`) mechanism the SDK is built on top of is already demonstrated available and subscription-authenticated today, without it.

If a future implementation task chooses this path, the architecturally honest description is: MVP2's `LLMClient` implementation would invoke the `claude` binary as a subprocess (`claude -p --output-format json ...`), not the Anthropic REST API and not (yet confirmed) the Agent SDK package. This is a materially different implementation shape from `OpenAILLMClient` (an in-process HTTP client) and would need its own governed design (timeout handling, subprocess error handling, output-schema enforcement) — noted here as a recommendation, not something this investigation implements.

## Recommendation for Next Governed Step

1. Human + Di to decide whether the CLI-subprocess mechanism (`claude -p --output-format json`) is an acceptable architecture for a future `ClaudeLLMClient` implementation, given it differs structurally from the existing `OpenAILLMClient`/`StubLLMClient` (in-process) pattern.
2. If approved, a separate, explicitly authorized implementation task should design and add `ClaudeLLMClient` (or equivalent) under `llm/`, following the same reasoning-only boundary (`propose_testcases`) already established — this investigation does not do that.
3. Optionally, a follow-up micro-investigation could install the Claude Agent SDK in an isolated/throwaway environment (not this repository's venv, unless separately authorized) to confirm whether it, specifically, supports subscription-only auth or requires `ANTHROPIC_API_KEY` — this was left unconfirmed here per the "do not install packages" boundary.
