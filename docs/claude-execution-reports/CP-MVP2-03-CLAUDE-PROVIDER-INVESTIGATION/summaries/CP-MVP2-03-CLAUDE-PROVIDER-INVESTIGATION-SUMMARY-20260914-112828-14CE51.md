Execution: CP-MVP2-03-CLAUDE-PROVIDER-INVESTIGATION-20260914-112828-14CE51

Investigation only — no CP-MVP2-03 implementation, specification, or configuration was changed. No testcase generation was performed with either provider.

Claude Code version: 2.1.270

Authentication classification: SUBSCRIPTION (OAuth via claude.ai, apiProvider "firstParty", subscriptionType "pro") — NOT API-key authentication.

ANTHROPIC_API_KEY: NOT SET (checked in current shell, a fresh login shell, and all standard shell-profile files) — confirms subscription auth is not being overridden.

claude -p availability: CONFIRMED via --help (documented, installed). Supports --output-format json and --json-schema for structured single-result output. Not actually invoked (no prompt was sent, no tokens consumed), per this task's "help/version inspection only" boundary.

Claude Agent SDK (package) availability: NOT INSTALLED anywhere accessible (system pip, project venv, global npm). Not installed during this task (installation was out of scope). Its own auth behavior in isolation is therefore UNCONFIRMED.

Repository integrity: HEAD d3157a7038ae8b0918385d64400f497e4ef116d8, equal to origin/main, both before and after. No file under llm/, testcases/, knowledge/, requirements/, or the frozen CP-MVP2-03 specification was modified. No package installed, no .env touched, no environment variable changed.

PROVIDER DECISION:
OPTION A — SUBSCRIPTION PATH AVAILABLE, specifically via "claude -p --output-format json" (CLI subprocess invocation), which is already installed, documented, and authenticated under the existing Claude Pro subscription with zero additional configuration. The separate Agent SDK package was not tested (not installed, out of scope) so its own subscription-auth support remains unconfirmed — but the CLI mechanism it wraps is already demonstrated available without it.

Important distinction preserved: this is a CLI-subprocess mechanism, not the Anthropic REST API and not (yet confirmed) the Agent SDK package — architecturally different from the existing OpenAILLMClient (in-process HTTP client) pattern, and would need its own governed design if pursued.

RECOMMENDATION:
Human + Di decide whether a future, separately authorized implementation task should add a ClaudeLLMClient built on "claude -p --output-format json" subprocess invocation. This investigation does not implement it and does not run the CP-MVP2-03 live smoke test with either provider.

Next step: HUMAN + DI DECISION (no implementation authorized by this task).
