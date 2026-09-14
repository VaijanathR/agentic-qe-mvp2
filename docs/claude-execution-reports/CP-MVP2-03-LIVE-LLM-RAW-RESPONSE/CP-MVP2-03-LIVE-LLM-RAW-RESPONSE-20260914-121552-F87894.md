# CP-MVP2-03 — Controlled Raw Claude Response Investigation: Detailed Report

**Headline finding: this investigation's single real invocation did NOT reproduce the parsing failure observed in the previous live-smoke task. The response received this time was clean, directly-parseable JSON with no markdown fence. The prior "markdown-fence wrapping" hypothesis is therefore NOT confirmed by this evidence — root cause of the original failure remains UNKNOWN. This is reported honestly rather than overstated.**

## Repository

* Branch: `main`
* Starting HEAD: `f3b60187719b73ec042ee08f3ec5efac811bd4b9` (== `origin/main`; confirmed via `git fetch` + `git rev-parse`)
* Ending HEAD (before this evidence commit): `f3b60187719b73ec042ee08f3ec5efac811bd4b9` — unchanged; no implementation/specification file was modified.
* Working-tree status: dirty only with the same pre-existing, unrelated `.gitignore`/`README.md` modifications and untracked `ClaudeInstructions/*.md`/`Inst001-12_...` files present at task start; none referenced by this task, none touched.
* Implementation commit under investigation: `12c7627bee283b85969a6d9a97fc5fb0564ca660` — confirmed an ancestor of HEAD via `git merge-base --is-ancestor`.

## Authentication

* `claude auth status` (safe fields only): `loggedIn: true`, `authMethod: "claude.ai"`, `apiProvider: "firstParty"`, `subscriptionType: "pro"`.
* `ANTHROPIC_API_KEY`: checked in the current shell and a fresh `bash -lc` login shell — **NOT SET** in either. Investigation was not blocked by the sec. 6 guard.
* No credential, token, or authentication-header value was printed, logged, or persisted anywhere in this task's evidence. (Note: the response envelope's `session_id` field name was observed to exist — see "Response Analysis" below — but its value was deliberately never printed or recorded, out of caution, even though a Claude Code CLI session id is not an authentication secret.)

## Baseline

* Command: `.venv/Scripts/python.exe -m pytest -q`
* Result (pre-investigation): **67 passed, 0 failed.**

## Requirement

* Requirement ID: `REQ-REG-01`
* Source document: `requirements/MVP2_SRS_v1.0_APPROVED.md`
* Version: `1.0`
* Approval status: `APPROVED_BASELINED_V1_0`
* RAG retrieval: **PASS** — via the existing, unmodified `testcases.generate.requirement_context()` / `KnowledgeBase.by_id()`. Same requirement used in the previous smoke task, re-verified fresh (not assumed carried over).

## Live Invocation

* **Exactly one** investigative invocation was performed in this task (a new, separately authorized call — not a retry of the prior smoke's invocation, which remains a single, already-concluded event).
* Constructed via the existing, unmodified `ClaudeLLMClient()` (executable-availability and `ANTHROPIC_API_KEY`-absence checks both passed for real, as they did in the prior task). `model_name`: `claude-cli:default`.
* The exact argv sent was built by calling the adapter's own unmodified private helper, `client._build_argv(user_prompt)`, with `user_prompt` constructed by copying — not re-deriving or altering — the identical `json.dumps({...})` expression from `ClaudeLLMClient.propose_testcases()` in `llm/client.py`. This guarantees the investigative call is byte-for-byte what `propose_testcases()` itself would send; no prompt modification occurred (sec. 2/4/11 compliance). 8 argv elements total; flags present: `--append-system-prompt`, `--output-format`, `--restricted` (plus the `-p <prompt>` positional pair and the executable itself — `--model` was absent because no model override is configured, matching the "default" `model_name`).
* `subprocess.run` was called directly by this investigation script (once), with the same parameters `ClaudeLLMClient.propose_testcases()` uses internally (`capture_output=True, text=True, timeout=client.timeout_seconds, shell=False`) — the only reason this script calls `subprocess.run` itself, rather than calling `client.propose_testcases()`, is that the latter discards the raw envelope/result on a parse failure and this investigation's entire purpose is to inspect that raw content before any parsing/discarding happens.
* Result: **EXECUTED.** Elapsed time: **10.34 seconds** (a second, independent genuine round trip — different timing from the prior smoke's 15.03s, consistent with normal LLM-call variability, not a cached/mocked response). Exit code: **0.** stderr: empty (0 bytes).

## Response Analysis

### Outer envelope

* Valid JSON: **YES.**
* Type: JSON object (`dict`).
* Keys observed (names only — see note above on `session_id`): `api_error_status, duration_api_ms, duration_ms, fast_mode_disabled_reason, fast_mode_state, first_content_frame_ms, is_error, modelUsage, num_turns, permission_denials, queued_turn_count, result, result_index, session_id, stop_reason, subagent_stats, subtype, terminal_reason, time_to_request_ms, total_cost_usd, ttft_ms, ttft_stream_ms, type, usage, uuid`.
  * This is a considerably richer envelope than the two fields (`is_error`, `result`) `ClaudeLLMClient` currently reads — it also includes cost/usage/timing telemetry (`total_cost_usd`, `usage`, `modelUsage`, `duration_ms`, etc.), none of which this investigation's script printed the *values* of (only the field *names* were captured; see "Limitations" below).
* `is_error`: **`false`.**

### Inner `result` field

* Present: **YES.**
* Type: **`str`.**
* Length: **540 characters.**
* First 120 characters (safe `repr()`): `'[{"scenario_type": "POSITIVE", "title": "Registration succeeds when all required fields are provided", "preconditions": '`
* Last 120 characters (safe `repr()`): `'lt": "No required-field messages are shown, the submission is accepted, and an account is created", "priority": "HIGH"}]'`
* Starts with a backtick/markdown fence (`` ``` ``): **NO.**
* Ends with a backtick/markdown fence: **NO.**
* Contains explanatory prose before/after the JSON: **NO** (the string begins with `[` at character 0 and ends with `]`, matching the first/last-120-char excerpts above).
* Direct `json.loads(result)`: **PASS.** The result parsed successfully as a JSON list containing exactly one object with the expected keys (`scenario_type: "POSITIVE"`, `title`, `preconditions`, and, per the first/last excerpts, an `expected_result` describing exactly the REQ-REG-01 behavior and a `priority: "HIGH"`), matching the schema the system prompt requested and the governed evidence supplied.

## Root-Cause Assessment

**Confirmed evidence:**
* A real Claude CLI invocation, using the exact unmodified adapter construction, can and did return a `result` field that is pure, directly-parseable JSON with no markdown fence and no extraneous text — i.e., the "happy path" the adapter's parser expects does occur in practice.
* The outer envelope carries substantially more metadata (cost, usage, timing, session tracking) than the two fields (`is_error`, `result`) `ClaudeLLMClient` currently reads — none of this extra metadata caused or was involved in either invocation's outcome, but it is available for future evidence/telemetry purposes if a later task wants it.

**Likely hypothesis (not confirmed):**
* The original live-smoke failure ("Expecting value: line 1 column 1 (char 0)") was most consistent with a markdown-fence-wrapped or otherwise non-JSON-first-character response, as stated in the prior report. This investigation neither confirms nor refutes that specific historical response's content (it was never captured), but the fact that a fresh call under byte-for-byte identical construction returned clean JSON weakens confidence that fence-wrapping is a *consistent* behavior of this model/CLI combination for this prompt — it may instead be intermittent/non-deterministic model output variance.

**Unknown / requires further evidence:**
* The exact content of the original failing `result` string — never captured, and (per this and the prior task's no-retry governance) cannot be retroactively determined without a further, separately authorized invocation.
* Whether the failure is reproducible at any meaningful rate (e.g., 1-in-N calls) — determining this would require multiple additional controlled invocations, which neither this nor the prior task authorized.
* Whether `ClaudeLLMClient`'s current lack of a temperature/determinism setting for the Claude CLI path (unlike `OpenAILLMClient`, which sets `temperature=0`) contributes to response-format variability — this is a plausible contributing factor worth a future task's attention, but is not established as fact here.

## Diagnostic-Only Probe (not applied to any implementation file)

Because this call's `result` parsed directly, the script's fence-stripping diagnostic probe (which only runs on a parse *failure*) did not execute. No such probe was needed or performed this time; it remains available, unused, in the throwaway investigation script only (not committed to the repository, not part of `llm/client.py`).

## Implementation Integrity

* `llm/client.py`: **UNCHANGED.** No fence-stripping, normalization, regex repair, or fallback parsing was added.
* `testcases/`, `tests/`: **UNCHANGED.**
* `docs/CP-MVP2-03-SPECIFICATION-v1.0.md`, `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`: **UNCHANGED.**
* `requirements/`, `knowledge/`: **UNCHANGED.**
* Prompt: **UNCHANGED** — the investigative call used the exact same system/user prompt construction as production code; nothing was altered to "compensate" for anything.
* Post-investigation regression: **67 passed, 0 failed** (identical to pre-investigation baseline).

## Downstream

```text
CP-MVP2-04: NOT STARTED
```

No test-data generation, browser automation, Playwright, performance/security testing, self-healing, RCA, CI/CD, or any other out-of-scope capability was touched.

## Limitations

1. The numeric values of the richer telemetry fields observed in the outer envelope (`total_cost_usd`, `usage`, `modelUsage`, `duration_ms`, `num_turns`, etc.) were not captured by this investigation's script — only their field *names* were recorded. A future task wanting those values would need a further invocation.
2. This investigation cannot and does not claim to explain the specific historical failure from the prior smoke task; it only establishes that the failure did not recur on this occasion under identical construction, and that clean JSON output is achievable in practice.
