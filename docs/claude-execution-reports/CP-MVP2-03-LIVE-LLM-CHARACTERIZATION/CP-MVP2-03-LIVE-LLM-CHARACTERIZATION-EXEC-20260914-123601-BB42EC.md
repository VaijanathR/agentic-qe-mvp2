# CP-MVP2-03 — Controlled 5-Call Claude Response-Format Characterization Study

**Headline result: CASE 1 — all 5 calls returned directly parseable JSON (5/5 FORMAT-A). The parsing failure from the earlier live-smoke task was NOT reproduced in this controlled sample. A separate, distinct content-level observation (not a format/parsing issue) is also reported: 2 of the 5 calls returned an empty array `[]` for the same requirement/evidence that the other 3 calls used to produce a populated POSITIVE candidate.**

## A. Governance

* `docs/CP-MVP2-03-SPECIFICATION-v1.0.md`: verified **UNCHANGED** (empty `git diff`, before and after).
* `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`: verified **UNCHANGED.**
* `llm/client.py`, `testcases/`, `tests/`: verified **UNCHANGED** — no parser modification, no prompt change, no provider change.
* `CP-MVP2-04`: **NOT STARTED.** No downstream/out-of-scope capability touched.

## B. Environment

* Claude Code version: `2.1.270` (`claude --version`).
* Authentication method: `claude.ai` (OAuth), `apiProvider: "firstParty"`.
* Subscription type: `pro`.
* `ANTHROPIC_API_KEY`: checked in the current shell and a fresh `bash -lc` login shell — **NOT SET** in either. Study proceeded on the subscription path per sec. 4.
* Model selection: none configured (`CP_MVP2_03_CLAUDE_MODEL` unset) — the CLI's own default model applied for all 5 calls, identically. `client.model_name` reported `claude-cli:default` for every call.
* No credential value was printed, logged, or persisted anywhere in this task's evidence.

## C. RAG

* Requirement ID: `REQ-REG-01`
* Source document: `requirements/MVP2_SRS_v1.0_APPROVED.md`
* Version: `1.0`
* Approval status: `APPROVED_BASELINED_V1_0`
* Retrieved once via the existing, unmodified `testcases.generate.requirement_context()` / `KnowledgeBase.by_id()` (CP-MVP2-02 governed RAG). The identical retrieved context (and therefore the identical `user_prompt`, built by copying — not altering — the exact `json.dumps({...})` expression from `ClaudeLLMClient.propose_testcases()`) was reused for all 5 calls, so response variability across calls reflects the provider, not a differing input.

## D. Five-Call Results

| Call | Exit | Outer JSON | is_error | Result Type | Direct JSON Parse | Format | Duration (s) |
|---|---|---|---|---|---|---|---|
| 1 | 0 | PASS | false | str (len 2) | PASS | FORMAT-A | 8.47 |
| 2 | 0 | PASS | false | str (len 582) | PASS | FORMAT-A | 5.99 |
| 3 | 0 | PASS | false | str (len 635) | PASS | FORMAT-A | 17.10 |
| 4 | 0 | PASS | false | str (len 2) | PASS | FORMAT-A | 11.18 |
| 5 | 0 | PASS | false | str (len 652) | PASS | FORMAT-A | 17.08 |

Safe first/last-40-character excerpts (`repr()`):

| Call | First 40 | Last 40 |
|---|---|---|
| 1 | `'[]'` | `'[]'` |
| 2 | `'[{"scenario_type": "POSITIVE", "title": '` | `'ated successfully", "priority": "HIGH"}]'` |
| 3 | `'[{"scenario_type": "POSITIVE", "title": '` | `'ated successfully", "priority": "HIGH"}]'` |
| 4 | `'[]'` | `'[]'` |
| 5 | `'[{"scenario_type":"POSITIVE","title":"Re'` | `' account is created","priority":"HIGH"}]'` |

None of the 5 results began or ended with a Markdown code fence (`` ``` ``); `starts_with_fence`/`ends_with_fence` were `false` for all 5.

## E. Aggregate Characterization

* Successful invocations: **5 / 5** (exit code 0 for all).
* Outer-envelope parse success rate: **5 / 5 (100%).**
* Direct JSON parse success rate (inner `result`): **5 / 5 (100%).**
* FORMAT-A (clean JSON): **5**
* FORMAT-B (Markdown-wrapped JSON): **0**
* FORMAT-C (prose + JSON): **0**
* FORMAT-D (invalid JSON): **0**
* FORMAT-E (provider/invocation failure): **0**

## F. Observations vs. Hypotheses

**Confirmed observations:**
* All 5 independent real invocations, using byte-for-byte the same production prompt/argv construction, returned an outer envelope that parsed as JSON with `is_error: false`, and an inner `result` string that parsed directly as JSON with no Markdown fence and no explanatory prose.
* 3 of 5 calls (2, 3, 5) returned a non-empty JSON array containing one `POSITIVE`-scenario candidate object with the expected keys (`scenario_type`, `title`, ..., `priority: "HIGH"`).
* 2 of 5 calls (1, 4) returned a JSON array that was simply `[]` — a valid, directly parseable JSON value, but containing zero candidates for a governed requirement (`REQ-REG-01`) that the other 3 calls, using the identical retrieved evidence, judged sufficient to produce a `POSITIVE` candidate. This is a **content-level decision variability** observation, not a format/parsing failure — `[]` is FORMAT-A by the study's own classification (directly parseable JSON) — and it is reported here as a distinct, additional fact because it is directly relevant to whether the provider reliably produces usable output, separate from whether that output is syntactically parseable.

**Hypotheses (not proven by this study):**
* The earlier live-smoke failure ("Expecting value: line 1 column 1 (char 0)") remains unexplained by this sample: none of these 5 calls reproduced anything resembling that failure. It is possible the failure is a low-probability event (this sample of 5 did not happen to encounter it), or that some other factor (not characterized here) was present during the original smoke call. Neither can be confirmed or ruled out by this study.
* Whether the empty-array outcome (calls 1, 4) reflects genuine model non-determinism in interpreting "does the evidence justify a POSITIVE scenario," a stricter-than-expected reading of the system prompt's "only propose where justified" instruction, or some other cause, is not established here — reported as an observation, not diagnosed.

**Unknown / requires further evidence:**
* The true failure rate of the original parsing-failure mode (FORMAT-B/C/D/E) cannot be estimated from a 0-in-5 sample with statistical confidence — a 0/5 observed rate is consistent with a failure probability anywhere from 0% up to a non-trivial percentage; this sample size cannot distinguish "never happens" from "happens occasionally."

## G. Regression

* Baseline (pre-study): `.venv/Scripts/python.exe -m pytest -q` → **67 passed, 0 failed.**
* Final (post-study): same command → **67 passed, 0 failed.** No regression.

## H. Repository Integrity

* Starting HEAD: `477373b45d72fa5935f578362b27f2f76884d6d2` (== `origin/main`, confirmed via `git fetch` + `git rev-parse`).
* Final HEAD (before this evidence commit): `477373b45d72fa5935f578362b27f2f76884d6d2` — unchanged.
* Files changed by this task: none in implementation/specification. Only this report and its companion summary were added.
* Frozen artifacts (`docs/CP-MVP2-03-SPECIFICATION-v1.0.md`, `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`, `requirements/`, `knowledge/`, `llm/`, `testcases/`, `tests/`): all confirmed **UNCHANGED** via `git diff --stat`, before and after.
* Pre-existing, unrelated working-tree items (`.gitignore`, `README.md`, `ClaudeInstructions/*.md`) left untouched throughout.

## I. Scope

```text
CP-MVP2-04: NOT STARTED
Parser patch: NONE
Prompt change: NONE
Provider change: NONE
Specification change: NONE
```

## Final Characterization Decision

**CASE 1 — All five are clean JSON.**

Observed sample: **5/5 directly parseable JSON** (FORMAT-A). The previous parsing failure was not reproduced in this controlled sample. This does not prove the failure cannot recur (see "Unknown / requires further evidence" above) — it establishes only that, across this specific 5-call sample, the response was always at least syntactically valid JSON at the top level. Separately, this sample also surfaced a content-level variability finding (2/5 empty-array responses for a requirement the other 3/5 calls served correctly) that is offered to Human + Di as additional evidence relevant to any future governed-resilience decision, without this task drawing that conclusion itself.

No implementation, parser, prompt, or specification change was made. This task ends here, per its own governance, with the evidence delivered for Di's independent review.
