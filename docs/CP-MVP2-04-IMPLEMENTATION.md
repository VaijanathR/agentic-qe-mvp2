# CP-MVP2-04 — LLM Test Data Generation: Implementation Notes

Implements the frozen `docs/CP-MVP2-04-SPECIFICATION-v1.0.md` on top of the
existing, unmodified CP-MVP2-02 Knowledge Base/RAG layer and CP-MVP2-03
testcase-generation pipeline. This document explains the implementation;
it does not redefine or extend the specification.

## Architecture

```text
ACCEPTED CP-MVP2-03 TESTCASE  (testcases/schema.py::GovernedTestcase, unmodified)
      |
TEST-DATA REQUIREMENT IDENTIFICATION  (testdata/generate.py + testdata/constraints.py)
      |
GOVERNED RAG ATTRIBUTION  (testcases/generate.py::requirement_context, reused unmodified)
      |
LLM FIELD-VALUE REASONING  (llm/test_data_client.py::TestDataLLMClient.propose_field_values())
      |
STRUCTURED TEST DATA  (testdata/schema.py::TestDataSet / TestDataField)
      |
DETERMINISTIC VALIDATORS  (testdata/validate.py)
      |
UNIQUENESS / DUPLICATE / COVERAGE / GOVERNANCE
      |
CP-MVP2-04 RESULT  (testdata/pipeline.py::run_cp_mvp2_04())
```

| Path | Role |
|---|---|
| `testdata/schema.py` | `TestDataSet`, `TestDataField`, `GovernedTestDataSet`, and the fixed vocabularies (`DataCategory`, `BoundaryClassification`, `UniquenessRequirement`, `ValueType`, `DataValidity`, `DataGovernanceStatus`). |
| `testdata/constraints.py` | The deterministic, evidence-cited constraint table (spec sec. 8) — `ConstraintProfile`/`FieldSpec` keyed by requirement ID. |
| `llm/test_data_client.py` | The reasoning boundary for test data. `TestDataLLMClient` (abstract), `ClaudeTestDataClient` (real backend), `StubTestDataClient` (deterministic offline stand-in). See "Design decision: a new LLM file, not a modified one" below. |
| `testdata/generate.py` | Governed context-building (`build_dataset_context`) + generation orchestration (`generate_for_testcase(s)`). Assembles `data_set_id`, `requirement_ids`, `source_attribution`, `value_type`/`boundary_classification`/`uniqueness_requirement` deterministically — the LLM only ever supplies `field_value`. |
| `testdata/validate.py` | Deterministic governance: schema, traceability, symmetric VALID/INVALID constraint checking, duplicate detection, uniqueness enforcement, coverage. |
| `testdata/pipeline.py` | `run_cp_mvp2_04()` — sequences generation then governance into one CP-MVP2-04 result, scoped strictly to CP-MVP2-03's `ACCEPTED` testcases. |

## Design decision: a new LLM file, not a modified one

`llm/client.py` is formally frozen as part of the CP-MVP2-03 checkpoint
(`docs/CP-MVP2-03-FINAL-FREEZE-CHECKPOINT.md` explicitly lists "Claude
provider adapter (`llm/client.py`: `ClaudeLLMClient`, `ClaudeProviderError`,
...)" as frozen scope). `LLMClient.propose_testcases()` is that frozen
interface's only abstract method, and its real/stub implementations
hard-code a testcase-shaped system prompt and response contract
(`scenario_type`/`title`/`preconditions`/`test_steps`/`expected_result`/
`priority`) that cannot represent a field-value proposal without either
modifying the frozen file or repurposing a wrong-shaped call.

This implementation therefore adds a **new, parallel** file,
`llm/test_data_client.py`, rather than touching `llm/client.py`. It:

* imports and reuses `ClaudeProviderError` from `llm/client.py` (read-only
  reuse, not modification) so both checkpoints' real backends raise the
  same exception taxonomy;
* reuses the *exact same* provider mechanism as `ClaudeLLMClient` — the
  local `claude` CLI, `--restricted` mode (no Bash/Edit/WebFetch tool
  access), an argument-list `subprocess.run` call (`shell=False` always),
  an explicit configurable timeout, and the identical `ANTHROPIC_API_KEY`
  billing-safety guard;
* does **not** subclass `llm.client.LLMClient`, because that ABC's only
  method is genuinely inapplicable to field-value reasoning — subclassing
  it and stubbing out `propose_testcases()` with `NotImplementedError`
  would be more confusing than a small, clearly-named parallel interface.

`git diff` against `llm/client.py` before and after this implementation
is empty — the frozen file was never touched.

## Core architectural principle (spec sec. 4)

> RAG supplies the evidence. The accepted CP-MVP2-03 testcase supplies
> the data need. LLM performs the data-value reasoning. Deterministic
> code decides whether the generated data complies.

`TestDataLLMClient.propose_field_values()` receives only a fixed field
list (name/type/mandatory-ness/allowed-values, drawn from
`testdata/constraints.py`) plus any documented exceptional/boundary/
alternate case for the current data category, and returns **field
values only**. Every other attribute on the assembled `TestDataSet`/
`TestDataField` — IDs, requirement linkage, source attribution, value
type, boundary classification, uniqueness requirement — is assigned by
`testdata/generate.py`, never trusted from the model.

## Constraint extraction (spec sec. 8)

Implemented as a small, explicit, hand-authored table
(`testdata/constraints.py`), each entry citing the exact Approved SRS
section/business-rule/negative-case it represents — mirroring
`knowledge/lib/schema.py`'s deterministic authority-tier table
(CP-MVP2-02 governance rule #10: never let inference decide authority).
Profiles currently exist for:

* `REQ-REG-01` (registration: mandatory fields, password/confirm-password
  dependency, email uniqueness, and documented negative cases NEG-01
  through NEG-04 — including the exact literal `"not-an-email"` string
  from the Approved SRS's own Evidence Basis cell for NEG-03).
* `REQ-ACO-03` (billing/shipping address: mandatory vs. optional fields).
* `REQ-PAY-01` (payment method: the four enumerated methods actually
  observed).
* `REQ-CART-03` (cart quantity boundary: `quantity = 0`, per REQ-CART-03/
  NEG-07).

A requirement ID with no profile is **not** treated as unconstrained —
`testdata.generate.generate_for_testcase` reports `INSUFFICIENT_EVIDENCE`
(spec sec. 9) rather than inventing constraints. `REQ-SHIP-01` (Shipping
Method) has deliberately no profile, since the Approved SRS approves only
"existence of the choice," not an exact enumerated set — inventing one
would violate spec sec. 8's explicit prohibition.

## Uniqueness (spec sec. 10)

* `UniquenessRequirement.MUST_BE_UNIQUE` on the `email` field for
  `REQ-REG-01`'s POSITIVE/ALTERNATE/INVALID (blank) cases, grounded in
  Approved SRS Business Rule #1.
* The one documented case that **intentionally** violates that rule
  (NEG-04, "duplicate email") carries an explicit
  `uniqueness_override: {"email": MAY_REUSE}` in its constraint-table
  entry — `testdata.validate.validate_constraints` recognizes "a field
  the profile normally marks `MUST_BE_UNIQUE`, but this dataset
  explicitly carries as `MAY_REUSE`" as itself a governed signal of
  intentional documented invalidity (satisfying the "an INVALID dataset
  must violate something recognized" check without requiring a
  format/mandatory violation too).
* `testdata.validate.enforce_uniqueness` runs at the *batch* level (a
  single dataset cannot know in isolation whether its `MUST_BE_UNIQUE`
  field collides with another) and **rejects** a colliding dataset
  rather than silently regenerating or renaming its value.

## Duplicate detection (spec sec. 13)

Two independent checks, mirroring `testcases/validate.py` exactly:
`check_duplicate_dataset_ids` (exact `data_set_id` collision) and
`detect_duplicates` (content-level: `(testcase_id, data_category, sorted
normalized field values)` — exact repeat becomes `DUPLICATE`; same
`(testcase_id, data_category)` with different content becomes
`POSSIBLE_DUPLICATE`, kept, never dropped).

## Coverage (spec sec. 14)

`testdata.validate.calculate_coverage` counts only `ACCEPTED`/
`POSSIBLE_DUPLICATE` datasets, and only for `testcase_id`s in the
applicable set (`testdata.pipeline.run_cp_mvp2_04` scopes that set to
CP-MVP2-03's own `ACCEPTED` testcases — a testcase CP-MVP2-03 itself did
not accept is excluded from the denominator entirely, not merely
uncovered).

## Configuration / dependencies

* `ClaudeTestDataClient` (real backend): same requirements as
  `ClaudeLLMClient` — a `claude` executable on `PATH` (or
  `CP_MVP2_04_CLAUDE_EXECUTABLE`), already authenticated interactively.
  `ANTHROPIC_API_KEY` present at all raises `ClaudeProviderError`
  (billing-safety guard). `CP_MVP2_04_CLAUDE_MODEL` and
  `CP_MVP2_04_CLAUDE_TIMEOUT_SECONDS` (default `120`) are optional.
* `StubTestDataClient` requires no configuration and makes no network
  calls.

## Test execution

```text
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_04_testdata_generation.py -v
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_04_claude_provider.py -v
.venv/Scripts/python.exe -m pytest -q   # full regression (CP-MVP2-01/02/03/04)
```

Both new test files mock `subprocess.run`/`shutil.which` throughout
(`test_cp_mvp2_04_claude_provider.py`) or use `StubTestDataClient`/
`StubLLMClient` (`test_cp_mvp2_04_testdata_generation.py`) — no real
`claude` process, no subscription usage, no network call in the
automated suite. Anchor CP-MVP2-03 testcases used by the generation
tests are themselves produced by CP-MVP2-03's own real, unmodified
pipeline with `StubLLMClient` — never hand-built shortcuts.

## Known limitations (disclosed, not hidden)

* **Constraint-table coverage is intentionally narrow.** Only four
  requirements have profiles (see above). Extending it to more Approved
  SRS requirements is future work, each addition requiring its own
  evidence citation — not a blocking gap for this checkpoint, since an
  unprofiled requirement correctly reports `INSUFFICIENT_EVIDENCE`
  rather than silently doing nothing or inventing constraints.
* **No live Claude call was exercised during automated-test authoring**
  (mirrors CP-MVP2-03's own disclosed limitation) — `ClaudeTestDataClient`
  is verified against a mocked subprocess boundary. A separate, live
  verification is performed after this implementation and its own
  evidence is reported independently (see the execution report for this
  task).
* **Reproducibility is audit-level only** (spec sec. 15) — `StubTestDataClient`
  is deterministic; `ClaudeTestDataClient` is not assumed to reproduce
  identical values across calls.
* **`DATA-OQ-01` remains unresolved**, by design — no constraint profile
  encodes an assumption about the shared-instance data-reset/isolation
  policy; any generation path that would need one (e.g. `ALTERNATE`
  address-reuse for `REQ-REG-01`, which has no `documented_alternate`
  entry) correctly reports `UNSUPPORTED` instead.
