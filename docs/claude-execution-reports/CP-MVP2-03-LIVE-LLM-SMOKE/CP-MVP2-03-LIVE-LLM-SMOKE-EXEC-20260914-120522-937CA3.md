# CP-MVP2-03 — Controlled Live Claude Smoke Verification: Detailed Execution Report

**Result: FAILED at the real-response-parsing step. No retry, no patch, and no implementation change were performed, per this task's explicit governance. This is a genuine finding to be decided on by Di, not a masked or fabricated success.**

## Repository

* Branch: `main`
* Starting HEAD: `7d8542222b0c9a9553a418ba0c85924aee896785` (== `origin/main`; confirmed via `git fetch` + `git rev-parse`)
* Ending HEAD (before this evidence commit): `7d8542222b0c9a9553a418ba0c85924aee896785` — unchanged, because no implementation/specification file was modified by this task.
* Working-tree status: dirty only with the same pre-existing, unrelated `.gitignore`/`README.md` modifications and untracked `ClaudeInstructions/*.md` files present at the start of this task; none referenced by this task, none touched.
* Implementation commit under verification: `12c7627bee283b85969a6d9a97fc5fb0564ca660` — confirmed an ancestor of HEAD via `git merge-base --is-ancestor`.

## Authentication

* `claude auth status` (safe fields only): `loggedIn: true`, `authMethod: "claude.ai"`, `apiProvider: "firstParty"`, `subscriptionType: "pro"`.
* `ANTHROPIC_API_KEY`: checked in the current shell and a fresh `bash -lc` login shell — **NOT SET** in either. Live smoke was therefore not blocked by sec. 6 and proceeded on the Claude Pro subscription path.
* No credential, token, or authentication-header value was printed, logged, or persisted anywhere in this task's evidence.

## Baseline

* Command: `.venv/Scripts/python.exe -m pytest -q`
* Result (pre-smoke): **67 passed, 0 failed.**

## Requirement

* Requirement ID: `REQ-REG-01`
* Source document: `requirements/MVP2_SRS_v1.0_APPROVED.md`
* Version: `1.0`
* Approval status: `APPROVED_BASELINED_V1_0`
* RAG retrieval: **PASS** — retrieved via the existing, unmodified `testcases.generate.requirement_context()` (which itself uses only `KnowledgeBase.by_id()`, CP-MVP2-02's own governed exact-ID lookup). Evidence chunks returned: `srs_v1.0__REQ-REG-01`, `srs_v1.0__NEG-01` through `srs_v1.0__NEG-07` (all `approved_srs`, all `APPROVED_BASELINED_V1_0`).

## Live Call

* **Exactly one** real invocation was performed, through the existing `ClaudeLLMClient` (`llm/client.py`), unmodified — no bypass, no manual `claude` invocation outside the adapter, no second attempt.
* Client construction: **PASS** (`ClaudeLLMClient()` succeeded — executable found on PATH, `ANTHROPIC_API_KEY` absent). `model_name`: `claude-cli:default`.
* Invocation: `client.propose_testcases(requirement_context, ["POSITIVE"])`. This internally ran `claude -p <json-prompt> --append-system-prompt <system> --output-format json --restricted` as a real subprocess.
* **The real `claude` process executed and returned** — elapsed time **15.03 seconds**, confirming a genuine round trip (not an instantly-failing stub or a cached/mocked path).
* Exit status: handled — the process did not raise a non-zero-exit `ClaudeProviderError`, so it returned exit code 0. The failure occurred at a later step (envelope/result parsing), not at process-exit handling.
* Response parsing result: **FAILED.**
  * The outer `--output-format json` envelope was received and appears to have parsed as a JSON object (no "stdout was not valid JSON" / "not a JSON object" / "is_error=true" / "missing 'result' field" error was raised — all of which are distinct, earlier failure points in the same code path and did not fire).
  * The failure occurred specifically at the **inner** parse — treating the envelope's `result` field (the model's final text) as a JSON array of candidates:
    ```
    ClaudeProviderError: Claude CLI 'result' text was not valid JSON: Expecting value: line 1 column 1 (char 0)
    ```
  * This is the exact Python `json.JSONDecodeError` signature produced when the very first character of the string being parsed is not a valid start of any JSON value — consistent with (though not confirmed as, since the raw `result` text is not retained by the adapter on this failure path and a second call to inspect it was not performed, per this task's no-retry rule) the model having wrapped its JSON array in a markdown code fence (e.g. `` ```json `` at the very start) despite the system prompt's explicit "no markdown fences" instruction.
* Actual Claude-generated content reaching the existing CP-MVP2-03 pipeline: **NO** — because `propose_testcases()` raised before returning anything, no candidate ever reached `testcases.generate`'s deterministic assembly step or `testcases.validate`.

## Validation

```text
Deterministic validation: NOT REACHED
```

No real Claude-generated candidate exists to validate, because the live invocation failed at the response-parsing step before any candidate was returned. `validate_schema`, `govern_testcase`, traceability, attribution, and coverage were consequently **not exercised against real Claude output** in this execution — there is nothing to run them against without either (a) a second live call (forbidden by sec. 4/16) or (b) substituting non-real content (forbidden by sec. 14/15). Neither was done.

## Post-Smoke Regression

* Command: `.venv/Scripts/python.exe -m pytest -q`
* Result: **67 passed, 0 failed** — identical to baseline. Confirms the live-smoke failure did not corrupt or affect any other part of the repository or test state.

## Repository Integrity

* `docs/CP-MVP2-03-SPECIFICATION-v1.0.md`: **UNCHANGED** (`git diff --stat` empty, before and after).
* `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`: **UNCHANGED.**
* `llm/`, `testcases/`, `tests/`: **UNCHANGED** — no patch was applied to `ClaudeLLMClient` or any parser/validator despite the failure, per sec. 3/16/18.
* `requirements/`, `knowledge/`: **UNCHANGED.**
* No downstream file (CP-MVP2-04 or later) was created or touched.

## Usage

Exactly one live Claude invocation was performed in this task. The implementation does not currently expose a token count from the `claude -p --output-format json` envelope in a way this script captured (the failure occurred before any such metadata could be read from the envelope's outer fields); no token count is claimed.

## Failure Classification

```text
Observed: ClaudeLLMClient.propose_testcases() raised ClaudeProviderError
          after a real ~15s claude CLI round trip: "Claude CLI 'result'
          text was not valid JSON: Expecting value: line 1 column 1
          (char 0)".
Expected: The envelope's 'result' field, parsed as JSON, should be a
          list of candidate objects (per the system prompt's "respond
          with ONLY a JSON array" instruction).
Evidence: Exact exception message above; 15.03s elapsed (a genuine
          subprocess round trip, not an immediate/cached failure);
          earlier failure points in the same code path (invalid outer
          JSON, non-dict envelope, is_error=true, missing/empty
          'result') did NOT fire, narrowing the failure to the inner
          JSON parse of a non-empty 'result' string.
Likely cause (hypothesis, not confirmed — the raw 'result' text is not
          retained on this failure path, and a second call to inspect
          it directly was not performed per the no-retry rule): the
          model's response was not raw JSON at character 0 — most
          consistent with a markdown code-fence wrapper (e.g. a
          leading ```` ```json ````) despite the system prompt's "no
          markdown fences" instruction.
Specification impact: NONE. This is a provider-adapter parsing-
          robustness gap, not a CP-MVP2-03 functional-contract issue —
          the frozen specification does not mandate a specific LLM
          provider's exact wire format.
Implementation impact: ClaudeLLMClient.propose_testcases()'s JSON-
          parsing of the 'result' field is currently strict (a bare
          json.loads with no fence-stripping/tolerance), unlike a
          model that may (despite instruction) wrap output in markdown.
          This was NOT changed in this task.
Recommended next action: a separate, explicitly authorized follow-up
          implementation task to (a) capture and inspect one raw
          'result' string (e.g. via a debug/log path, or a single
          additional controlled call authorized specifically for that
          purpose) to confirm the fence-wrapping hypothesis, and (b) if
          confirmed, add a narrow, disclosed tolerance (e.g. stripping
          a leading/trailing ``` fence) to the parsing step — decided
          by Human + Di, not performed autonomously here.
Reproducible: UNKNOWN — a second attempt was deliberately not made in
          this task (sec. 4/16 forbid retrying). Reproducibility can
          only be established by a separate, explicitly authorized
          follow-up call.
```

## Final Smoke Result

```text
FAILED
```

Classification: **PARSING_FAILURE** (real-response-parsing step, specifically the inner `result`-as-JSON-array parse). Not `AUTHENTICATION_FAILURE` (auth and construction both succeeded), not `CLI_FAILURE`/`TIMEOUT` (the process completed and returned within the timeout, in ~15s), not `GOVERNANCE_FAILURE` (governance was never reached). This is an honest, evidence-based FAILED result — the task's purpose (closing the "envelope unverified" advisory) has been served by discovering, for real, exactly where the current implementation and a real Claude response diverge; it has not been served by producing a governed testcase, which did not occur.
