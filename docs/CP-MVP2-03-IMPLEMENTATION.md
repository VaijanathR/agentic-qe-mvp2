# CP-MVP2-03 — LLM Testcase Generation: Implementation Notes

Implements the frozen `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` against the
existing CP-MVP2-02 Knowledge Base/RAG layer (`knowledge/lib/`). This
document explains the implementation; it does not redefine or extend the
specification.

## Architecture

```text
APPROVED SRS  (requirements/MVP2_SRS_v1.0_APPROVED.md)
      |
MVP2 KNOWLEDGE BASE  (knowledge/lib/retrieval.py — CP-MVP2-02, unchanged)
      |
GOVERNED RAG RETRIEVAL  (testcases/generate.py: requirement_context())
      |
RETRIEVED REQUIREMENT CONTEXT
      |
LLM  (llm/client.py: LLMClient.propose_testcases())
      |
STRUCTURED TESTCASE OUTPUT  (testcases/schema.py: Testcase)
      |
DETERMINISTIC VALIDATORS  (testcases/validate.py)
      |
COVERAGE / TRACEABILITY / GOVERNANCE
      |
CP-MVP2-03 RESULT  (testcases/pipeline.py: run_cp_mvp2_03())
```

Modules added by this checkpoint:

| Path | Role |
|---|---|
| `llm/client.py` | The reasoning boundary. `LLMClient` (abstract), `OpenAILLMClient` (real backend, Anthropic-unrelated), `ClaudeLLMClient` (real backend via the local `claude` CLI / Claude Pro subscription), `StubLLMClient` (deterministic offline stand-in). |
| `testcases/schema.py` | `Testcase`, `GovernedTestcase`, and the fixed vocabularies (`ScenarioType`, `GovernanceStatus`, `Priority`). |
| `testcases/generate.py` | Governed retrieval (`requirement_context`) + generation orchestration (`generate_for_requirement(s)`). Assembles `testcase_id`, `requirement_ids`, `source_attribution`, `generation_metadata` deterministically — never trusted from the model. |
| `testcases/validate.py` | Deterministic governance: schema validation, traceability, draft-leakage rejection, duplicate detection, coverage calculation. |
| `testcases/pipeline.py` | `run_cp_mvp2_03()` — sequences generation then governance into one CP-MVP2-03 result. |

## Core architectural principle (unchanged from spec sec. 4)

> RAG supplies the evidence. LLM performs the reasoning. Deterministic
> code decides whether the output complies.

Concretely: `LLMClient.propose_testcases()` receives only the governed
`requirement_context` dict built by `testcases.generate.requirement_context()`
and returns **narrative fields only** — `scenario_type`, `title`,
`preconditions`, `test_steps`, `expected_result`, `priority`. It never
returns (and nothing downstream trusts it for) `testcase_id`,
`requirement_ids`, or `source_attribution` — those are always assembled
by deterministic code from the actual KB/RAG retrieval result.

## Input contract

`requirement_context(kb, requirement_id)` returns `None` unless the ID
resolves to an `APPROVED` `requirement` chunk in `approved_srs` (via
`KnowledgeBase.by_id`, CP-MVP2-02's own governed exact-ID lookup — no
independent scraping). When it does resolve, the context additionally
carries, purely by deterministic lookup, never invention:

- `business_rule` chunks directly linked to the requirement (via
  `kb.by_id`), used only to justify an ALTERNATE scenario.
- `negative_case` chunks belonging to the requirement's own journey (via
  the journey_index chunk's membership list — the same membership
  CP-MVP2-02's `check_journey_traceability` validates), used only to
  justify an EXCEPTIONAL scenario.

## Testcase output contract

`testcases/schema.py::Testcase` implements spec sec. 6's field list
exactly: `testcase_id, title, requirement_ids, journey_id, scenario_type,
preconditions, test_steps, expected_result, test_data_reference,
priority, source_attribution, generation_metadata`. `test_data_reference`
is always `None` for now — CP-MVP2-04 (test-data generation) does not
exist yet, so there is nothing real to reference.

## Governance rules implemented

- **Schema** (`validate_schema`): required fields present, `scenario_type`
  in the fixed vocabulary.
- **Traceability** (`validate_traceability`, spec sec. 9): missing/empty
  requirement IDs and unresolvable-canonical-record lookups fail;
  `govern_testcase` then splits the failure into `REJECTED` (any ID
  resolves only to non-approved/draft content — a hard governance
  violation) vs. `QUARANTINED` (an ID does not resolve to *any* known
  requirement at all — held for human/Di clarification rather than
  outright discarded).
- **Draft/Approved governance** (spec sec. 11): enforced entirely inside
  `validate_traceability`/`govern_testcase` — a testcase can never reach
  `ACCEPTED` through a draft-only or otherwise non-approved canonical
  record, regardless of what the LLM proposed.
- **Duplicate detection** (`detect_duplicates`, spec sec. 13): exact
  repeats of `(requirement_ids, scenario_type, normalized expected_result)`
  among already-`ACCEPTED` testcases become `DUPLICATE`; same
  `(requirement_ids, scenario_type)` with different wording becomes
  `POSSIBLE_DUPLICATE` — flagged, never silently dropped. `testcase_id`
  collisions are checked separately by `check_duplicate_testcase_ids`.
- **Coverage** (`calculate_coverage`, spec sec. 10): counts only
  `ACCEPTED`/`POSSIBLE_DUPLICATE` testcases, and only for requirement IDs
  that are members of the caller-supplied (or manifest-derived) applicable
  set — an ID cannot inflate coverage no matter what governance status it
  was assigned.
- **Unsupported requirements** (spec sec. 15): `generate_for_requirement`
  returns an explicit `unsupported` dict (with a reason and detail,
  never a fabricated testcase) whenever a requirement ID doesn't resolve
  to approved evidence, or resolves but no requested scenario type is
  justified by the evidence found.

## Configuration / dependencies

- `OpenAILLMClient` (real backend) reuses the `openai` package already
  present in this project's Python environment.
  - `OPENAI_API_KEY` — **required** for this backend. No default; never
    hard-coded or committed. Construction raises `LLMUnavailableError`
    immediately if unset.
  - `CP_MVP2_03_LLM_MODEL` — optional, defaults to `gpt-4o-mini`.
- `ClaudeLLMClient` (real backend) uses the locally installed `claude`
  CLI and the user's already-authenticated Claude Code / Claude Pro
  **subscription** — see `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`
  for the approved architecture this implements. It does **not** use
  the Anthropic REST API and does **not** read/require
  `ANTHROPIC_API_KEY`.
  - Requires the `claude` executable on `PATH` (or
    `CP_MVP2_03_CLAUDE_EXECUTABLE` pointing to it), already authenticated
    interactively beforehand. Construction raises `ClaudeProviderError`
    immediately if the executable cannot be found.
  - **Billing safety guard:** if `ANTHROPIC_API_KEY` is present in the
    environment at all, construction raises `ClaudeProviderError`
    instead of proceeding — this class cannot deterministically
    guarantee the `claude` CLI would still bill the subscription rather
    than the API key (Anthropic's documented precedence favors the API
    key), so per the approved decision doc it fails clearly rather than
    risking a silent billing-provider switch.
  - `CP_MVP2_03_CLAUDE_MODEL` — optional; when unset, the CLI's own
    default model applies.
  - `CP_MVP2_03_CLAUDE_TIMEOUT_SECONDS` — optional, defaults to `120`.
  - Invocation: `claude -p <json-prompt> --append-system-prompt <system>
    --output-format json --restricted [--model <model>]`, run via
    `subprocess.run` with an **argument list** (`shell=False` always) —
    requirement text and prompt content can never be interpreted as
    shell syntax, regardless of quotes, `$()`, backticks, newlines, or
    Unicode content. `--restricted` (Claude Code's own documented flag)
    removes the built-in Bash/PowerShell/REPL/WebFetch tools, so this
    call cannot read or write repository files — it is a pure reasoning
    call, never an agentic coding session.
  - Response handling: parses the `--output-format json` envelope
    (`is_error`, `result`), then parses `result` itself as the expected
    JSON array of candidates. A non-zero exit code, a timeout, empty
    stdout, `is_error: true`, a missing/non-string `result`, or a
    `result` that isn't valid JSON / isn't a list all raise
    `ClaudeProviderError` — never a fabricated fallback candidate list.
  - **Disclosed assumption:** the exact JSON envelope shape (`is_error`,
    `result`) is implemented from Claude Code's documented non-
    interactive print-mode contract. It has not been exercised against
    a real `claude -p` invocation — no live Claude call was made while
    building this adapter (out of scope for that task; see the decision
    doc secs. 21/29). A live smoke test is a separate, later,
    explicitly-authorized task.
- `StubLLMClient` requires no configuration and makes no network calls.

## Test execution

```text
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_03_testcase_generation.py -v
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_03_claude_provider.py -v
.venv/Scripts/python.exe -m pytest -q   # full regression (CP-MVP2-01/02/03)
```

`tests/test_cp_mvp2_03_claude_provider.py` mocks `subprocess.run` and
`shutil.which` throughout — no real `claude` process is ever started by
the automated suite, no subscription usage is consumed, and no network
call occurs. It covers: executable availability, the
`ANTHROPIC_API_KEY` billing-safety guard (including that its value never
appears in an error message), successful parsing, argv-is-a-list /
`shell=False` / `--restricted` usage, explicit timeout propagation, every
failure mode in section "Response handling" above, shell-metacharacter
safety in requirement text, and that stderr content is never merged into
a successful result.

## Known limitations (disclosed, not hidden)

- **No live LLM call has been exercised.** This sandboxed execution
  environment has no `OPENAI_API_KEY` configured, so `OpenAILLMClient`
  has only been verified for its fail-fast behavior (raises
  `LLMUnavailableError` without one), not for a real generation call.
  All functional/governance/traceability/coverage/duplicate tests run
  against `StubLLMClient`, a disclosed deterministic stand-in — this
  proves the RAG -> reasoning-boundary -> governance pipeline is wired
  correctly and that governance holds regardless of which `LLMClient` is
  plugged in, but it does not prove live OpenAI output would parse
  cleanly under `OpenAILLMClient.propose_testcases`'s JSON-parsing path.
  Anyone enabling the real backend should re-run the suite with
  `OPENAI_API_KEY` set and review at least one real response.
- **No live Claude call has been exercised either.** `ClaudeLLMClient`
  is verified only against a mocked subprocess boundary (20 tests in
  `tests/test_cp_mvp2_03_claude_provider.py`) — its executable-discovery
  and billing-safety-guard logic run for real, but the actual `claude`
  process has never been started by this implementation, and the
  assumed `--output-format json` envelope shape (`is_error`/`result`)
  has not been checked against a genuine response. This is intentional:
  the task that added this class explicitly excluded a live Claude
  call. See `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md` for the
  planned, separate live-smoke-test task that will close this gap.
- `test_data_reference` is always `None` (CP-MVP2-04 does not exist yet).
- Duplicate detection is exact-normalization plus a coarse
  same-requirement/scenario heuristic — there is no semantic-similarity
  model. This matches the specification's "where practical" qualifier on
  semantic duplicate detection; it was judged not practical to add an
  embedding dependency for this checkpoint.
- `requirement_context` currently gathers ALTERNATE/EXCEPTIONAL evidence
  only from directly-linked business rules and same-journey negative
  cases. A requirement with relevant evidence expressed some other way in
  the Approved SRS (not business_rule/negative_case/journey-linked) will
  correctly get only a POSITIVE scenario rather than a fabricated one —
  this is the specification's own "do not manufacture scenarios" rule
  taking effect, not a bug, but it does mean ALTERNATE/EXCEPTIONAL
  coverage is only as complete as that evidence linkage.
