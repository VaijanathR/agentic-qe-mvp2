# CP-MVP2-03 — Persisted Testcase Artifact Investigation

**Read-only forensic investigation. No source code, specification, test, or frozen artifact was modified. No Change Request was created. No testcase was regenerated. No checkpoint was reopened.**

## 1. Executive Finding

> **CP-03 generated testcase instances ARE NOT persisted as first-class artifacts.**

Every production code path from `testcases.pipeline.run_cp_mvp2_03()` down to
`testcases.generate` / `testcases.validate` performs zero file I/O. The only
place a real, live-generated testcase instance's full content exists on disk
anywhere in this repository is embedded as a JSON code block inside a
human-authored Markdown execution report (and its companion summary) — not
as an independently addressable, machine-consumable artifact, and not as
something any downstream code path (CP-04, CP-05, CP-06, or any test) ever
reads.

## 2. Actual Persistence Location

```text
NO INDEPENDENT PERSISTED TESTCASE ARTIFACT FOUND
```

No `testcases/generated/`, `artifacts/`, `outputs/`, `results/`, or
`reports/` directory exists anywhere in the repository. `runs/` exists but
contains only CP-MVP2-06 execution evidence (`runs/cp_mvp2_06/...`) — no
CP-MVP2-03 testcase output. A repository-wide search for `*.json` files
(excluding `.venv`/`.git`) found only: CP-02 knowledge-ingestion manifests
and chunk data, CP-06's own `runs/cp_mvp2_06/VERIFY-ALL-01/results.json`
(execution results, not CP-03 testcase artifacts), and historical
discovery-evidence probe results. None is a CP-03 testcase artifact.

The one place a real live-generated testcase's full field set is written to
disk is inside:

```text
docs/claude-execution-reports/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE-EXEC-20260914-132454-ACCA85.md
docs/claude-execution-reports/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE/summaries/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE-SUMMARY-20260914-132454-ACCA85.md
```

— a narrative Markdown report containing an embedded JSON snippet, authored
by hand as evidence documentation for a specific verification task. This is
not a persistence *mechanism*; it is incidental transcription. No code in
the repository writes it, and no code in the repository reads it back.

## 3. Actual Live Testcase

Exact content, reproduced verbatim from
`docs/claude-execution-reports/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE/CP-MVP2-03-LIVE-PIPELINE-GOVERNANCE-EXEC-20260914-132454-ACCA85.md`
§E ("Deterministic Governance"), itself stated there to be "as actually
returned by the pipeline — not edited":

```json
{
  "governance_status": "ACCEPTED",
  "reasons": [],
  "testcase_id": "TC-REQ-REG-01-01",
  "title": "Successful registration with all required fields correctly filled",
  "requirement_ids": ["REQ-REG-01"],
  "scenario_type": "POSITIVE",
  "preconditions": [
    "User is a Guest with no existing account",
    "Registration page is accessible"
  ],
  "test_steps": [
    "Navigate to the registration page",
    "Enter a valid First name",
    "Enter a valid Last name",
    "Enter a valid, unique Email",
    "Enter a valid Password",
    "Enter the same value in Confirm password",
    "Submit the registration form"
  ],
  "expected_result": "No field-specific required messages are shown, and the account is created successfully",
  "priority": "HIGH",
  "journey_id": "J-01",
  "test_data_reference": null,
  "source_attribution": [
    {
      "requirement_id": "REQ-REG-01",
      "source_document": "requirements/MVP2_SRS_v1.0_APPROVED.md",
      "source_version": "1.0",
      "chunk_id": "srs_v1.0__REQ-REG-01"
    }
  ],
  "generation_metadata": {
    "generator": "claude-cli:default",
    "generated_at": "2026-09-14T13:24:24.501548+00:00",
    "retrieval_mode": "exact_id",
    "scenario_types_requested": ["POSITIVE"]
  }
}
```

Note `test_data_reference: null` — this specific live instance carried no
forward link to any test-data artifact even at the moment it was generated.

A repository-wide search for the literal string `TC-REQ-REG-01-01` found it
in exactly three other places, none of which is an independent copy of
*this* generated instance:

* `docs/CP-MVP2-04-SPECIFICATION-v1.0.md:208` — a narrative example in prose
  ("Example (grounded, not invented): for `REQ-REG-01` via `TC-REQ-REG-01-01`
  ...") referencing the ID pattern, not this object's content.
* `tests/test_cp_mvp2_04_claude_provider.py:28` — a hand-authored
  `SAMPLE_CONTEXT` test fixture reusing the same ID string for an unrelated
  mock, not a copy of the live object.
* The summary companion to the execution report above (same evidence, not
  an independent source).

This confirms the ID's reappearance is coincidental/deterministic (see §4 —
`testcase_id` is computed as `f"TC-{requirement_id}-{seq:02d}"`, so any
first-generated `POSITIVE` testcase for `REQ-REG-01` gets this exact ID
regardless of which LLM call or run produced it), not evidence of
independent persistence.

## 4. Data-Flow Trace

```text
Claude (ClaudeLLMClient.propose_testcases(), llm/client.py)
  ↓  returns raw candidate dicts (title, preconditions, test_steps,
     expected_result, priority, scenario_type — narrative fields only)
CP-03 parser (llm/client.py::ClaudeLLMClient._parse_response / propose_testcases)
  ↓  parses the CLI JSON envelope; no file write
schema (testcases/schema.py::Testcase, testcases/generate.py::generate_for_requirement)
  ↓  deterministically assembles testcase_id, requirement_ids, journey_id,
     source_attribution, generation_metadata around the LLM's narrative
     fields — held as an in-memory dataclass instance; no file write
validator (testcases/validate.py::govern_testcase / govern_batch / detect_duplicates)
  ↓  computes GovernanceStatus in memory, mutating a List[GovernedTestcase]
     held in the caller's process memory; no file write
pipeline (testcases/pipeline.py::run_cp_mvp2_03)
  ↓  returns a Python dict (report) to its caller; no file write anywhere
     in this function or any function it calls
PERSISTENCE / NO PERSISTENCE
  ↓  NO PERSISTENCE. The returned dict exists only as long as the calling
     process holds a reference to it. In the one live-verification task
     that produced the instance in §3, the calling script printed/embedded
     the dict's content into a manually-authored Markdown report; in every
     other invocation (all `tests/test_cp_mvp2_03_*.py` runs, the CI/pytest
     regression suite, this repository's other CP-03 exercises), the
     returned dict is simply discarded when the test function returns.
CP-04 (testdata/pipeline.py::run_cp_mvp2_04)
  ↓  receives `cp03_governed_testcases: List[GovernedTestcase]` as a
     Python parameter passed directly by its caller — see §5. Never reads
     a file.
CP-05 (automation/pipeline.py::run_cp_mvp2_05)
  ↓  receives `cp03_governed_testcases: List[GovernedTestcase]` identically
     — see §6. Never reads a file.
```

Exact evidence for "no file write" — a repository-wide search (excluding
`.venv`) for `json.dump(`, `write_text(`, `open(..., "w"`, `model_dump(`,
`model_dump_json(`, `write_bytes(` found matches only in:

| File | What it persists | Relation to CP-03 testcases |
|---|---|---|
| `execution/evidence.py` | CP-MVP2-06 execution logs/JSON | Unrelated — CP-06 execution evidence, not CP-03 testcases |
| `knowledge/lib/ingest_historical.py` | CP-02 historical-evidence manifest | Unrelated — knowledge ingestion |
| `knowledge/lib/ingest_srs.py` | CP-02 SRS chunk/manifest JSONL | Unrelated — knowledge ingestion (requirements, not testcases) |
| `knowledge/lib/validate.py` | `print(json.dumps(...))` to stdout only | Not a file write at all |
| `tests/test_cp_mvp2_0{3,4,5}_claude_provider.py` | Mocked Claude CLI JSON *envelopes*, in-memory strings used only to feed a mocked `subprocess.run` | Test fixtures, not CP-03 output persistence |

No occurrence of any of these calls exists in `testcases/generate.py`,
`testcases/validate.py`, `testcases/pipeline.py`, `testcases/schema.py`, or
`llm/client.py`.

## 5. CP-04 Handoff

```python
# testdata/pipeline.py
def run_cp_mvp2_04(
    kb: KnowledgeBase,
    llm: TestDataLLMClient,
    cp03_governed_testcases: List[GovernedTestcase],
    requested_categories: Optional[List[str]] = None,
) -> Dict:
    accepted = [tc for tc in cp03_governed_testcases if tc.governance_status == GovernanceStatus.ACCEPTED]
    ...
```

`cp03_governed_testcases` is a plain Python parameter — a list of
`GovernedTestcase` dataclass instances the **caller** already holds in
memory. `run_cp_mvp2_04` performs no file read, no deserialization, no
lookup by testcase ID against any persisted store. In every actual
invocation found in this repository — production usage (none exists outside
tests/manual verification scripts) and every test in
`tests/test_cp_mvp2_04_testdata_generation.py` — the caller either (a) calls
`testcases.generate`/`testcases.validate` itself, moments earlier in the
same process, to produce fresh `GovernedTestcase` objects (regeneration,
confirmed at `tests/test_cp_mvp2_04_testdata_generation.py:74`,
`govern_testcases(result.testcases, kb)`), or (b) hand-constructs a
`GovernedTestcase(tc, TestcaseGovernanceStatus.ACCEPTED, [])` fixture
directly (confirmed at lines 154, 310, 387, 495 of the same file). Neither
path reads a persisted CP-03 artifact, because none exists to read.

**Answer to the posed question:** CP-04 receives a testcase object
directly in memory, and that object is, in every actual invocation found,
either freshly regenerated via a new LLM call or a hand-built test fixture
— never a persisted CP-03 artifact loaded from disk.

## 6. CP-05 Handoff

```python
# automation/pipeline.py
def run_cp_mvp2_05(
    kb: KnowledgeBase,
    llm: AutomationLLMClient,
    cp03_governed_testcases: List[GovernedTestcase],
    cp04_governed_datasets: List[GovernedTestDataSet],
) -> Dict:
    accepted_testcases = [tc for tc in cp03_governed_testcases if tc.governance_status == TestcaseGovernanceStatus.ACCEPTED]
    ...
```

Identical pattern to §5: `cp03_governed_testcases` is an in-memory
parameter; `automation/generate.py` and `automation/validate.py` both
import `testcases.schema.GovernedTestcase` as a type only (`from
testcases.schema import GovernedTestcase`) — used for type-checking a
parameter, never for loading one from a file. No file read exists anywhere
in `automation/`.

**Answer to the posed question:** CP-05 consumes the same in-memory
`GovernedTestcase` object CP-04 was given — not a persisted artifact, not
an independent regeneration of its own (it relies on whatever the caller
already assembled for CP-04), not a report.

## 7. Live CP-03 Verification — Direct Answers

1. **What actual testcase did Claude generate?** `TC-REQ-REG-01-01` (full content in §3).
2. **Testcase ID?** `TC-REQ-REG-01-01`.
3. **Requirement covered?** `REQ-REG-01`.
4. **Steps?** 7 steps (navigate → fill 5 fields → submit); see §3.
5. **Expected result?** "No field-specific required messages are shown, and the account is created successfully."
6. **Test-data reference?** `null` — none.
7. **Was it persisted separately?** No. Only embedded inside the Markdown execution report and its companion summary (§2).
8. **Can CP-04 consume that exact testcase?** **No.** CP-04's real entry point takes an in-memory `List[GovernedTestcase]`; the process that generated this specific object exited when the live-verification task completed. A later CP-04 run against `REQ-REG-01` would need to call `run_cp_mvp2_03` (or the equivalent LLM call) again, which — because content depends on a fresh, non-deterministic LLM invocation — is **not guaranteed to reproduce this exact title/steps/expected_result**, even though the deterministic `testcase_id` would likely collide (`TC-REQ-REG-01-01` again, since it is computed from `requirement_id` + sequence, not from content).
9. **Can CP-05 consume that exact testcase?** **No**, for the same reason as (8) — CP-05 receives whatever CP-04 was given, and that was never this specific object.
10. **Can a human independently retrieve and review that exact testcase without reconstructing it from an execution report?** **No.** The only way to see this specific instance's exact fields is to open the execution report (or its summary) — i.e., to read an execution report. There is no separate, non-report artifact to retrieve instead.

## 8. Six-State Classification

Two different states apply, depending on the execution path:

* **General/automated pipeline execution** (every `pytest` run of
  `tests/test_cp_mvp2_03_testcase_generation.py`/`test_cp_mvp2_03_claude_provider.py`,
  and any future ad-hoc call to `run_cp_mvp2_03` whose caller does not itself
  write the result somewhere): **STATE-4 — Generated only in memory and
  discarded after pipeline execution.** Confirmed by the complete absence of
  any write call in `testcases/`/`llm/client.py` (§4).
* **The one specific live-verification execution** analyzed in §3/§7:
  **STATE-5 — Generated and persisted only inside execution/report
  evidence.** The full testcase content survives only because a human
  (this project's own prior Claude Code task) manually transcribed it into
  a Markdown execution report as documentation — not because any system
  component persists it as a matter of course.

**STATE-1 and STATE-2 do not apply anywhere in this repository** — no
first-class testcase artifact file, and no artifact that embeds a
complete, independently-identifiable testcase record in a
machine-consumable way, was found.

## 9. Traceability Chain — the Actual Live Testcase

```text
Testcase ID           PRESENT    (TC-REQ-REG-01-01, in the execution report)
    ↓
Requirement ID         PRESENT    (REQ-REG-01, in the same record)
    ↓
Approved SRS            PRESENT    (source_document: requirements/MVP2_SRS_v1.0_APPROVED.md, source_version: 1.0)
    ↓
Source attribution     PRESENT    (chunk_id: srs_v1.0__REQ-REG-01, in the same record)
    ↓
Test Data               ABSENT     (test_data_reference: null on the record itself; no CP-04 run ever consumed this specific object — §5/§7.8)
    ↓
Playwright Automation  ABSENT     (depends on Test Data being present; never reached — §6/§7.9)
    ↓
Browser Execution       ABSENT     (depends on the two links above; never reached)
```

Every link up to and including source attribution is directly present in
the recorded evidence. Every link from Test Data onward is absent for this
specific instance — not because CP-04/05/06 are broken, but because no
mechanism exists anywhere in the repository for a downstream checkpoint to
reach backward and retrieve *this particular* upstream instance; downstream
checkpoints only ever operate on whatever `GovernedTestcase` object their
caller currently holds in memory.

## 10. Governance Assessment

```text
RED — testcase is not independently persisted
```

**Why RED, not YELLOW:** YELLOW ("persisted indirectly / partial
traceability") would fit if some system mechanism reliably captured
generated testcases in a location a human or downstream process could
depend on, even indirectly. That is not the case here: the one existing
copy of a real generated testcase exists only because a specific,
one-off verification task happened to transcribe it into prose evidence.
There is no repeatable mechanism, no consumer of that transcription, and no
guarantee any future live/regenerated run would produce a matching or even
retrievable record. Absent any system-level persistence mechanism at all,
this is a RED finding, not a partial (YELLOW) one.

## 11. Frozen Checkpoint Impact

* **CP-MVP2-03 frozen status:** **Not affected.** The frozen
  `docs/CP-MVP2-03-SPECIFICATION-v1.0.md` (§1 Objective, §2.1/2.2 Scope,
  checked directly in this investigation) never states a requirement to
  persist individual generated testcase instances as files; its objective
  item 10 is "Produce a governed CP-MVP2-03 result with evidence and
  attribution" — satisfied by the in-memory report `run_cp_mvp2_03`
  actually returns. This investigation finds an **architecture gap
  relative to the downstream-consumption expectation now being examined**,
  not a violation of the frozen specification's literal text. The CP-03
  freeze itself is not reopened or invalidated by this finding.
* **CP-MVP2-04:** **Affected in a disclosure sense, not a functional one.**
  CP-04's real entry point never actually depended on a persisted CP-03
  artifact — it was always designed around an in-memory
  `List[GovernedTestcase]` parameter (confirmed §5) — so no CP-04 behavior
  is incorrect. However, this means CP-04's own implicit assumption ("its
  input is CP-03's governed output") is only true within a single
  in-process pipeline run; there is currently no way to run CP-04 later,
  independently, against a specific previously-governed CP-03 testcase.
* **CP-MVP2-05:** Same disclosure-level effect as CP-04, one layer further
  downstream (§6).
* **CP-MVP2-06:** Same effect, propagated furthest: CP-06's own eligibility
  gate (`execution/validate.py::check_eligibility`) operates on whatever
  `PlaywrightArtifact` its caller passes in; it inherits the same
  in-memory-only lineage all the way back to CP-03, with no independent
  persisted checkpoint at any layer in between.

**No checkpoint's FROZEN/CLOSED status is changed by this investigation.**

## 12. Recommendation

**A minimum governed corrective action, if pursued, would be:** introduce a
deterministic, explicitly-scoped persistence step at the CP-MVP2-03
pipeline boundary (e.g., `run_cp_mvp2_03` — or a thin wrapper around it —
writing each `GovernedTestcase.to_dict()` to a stable, ID-addressed path
such as `testcases/generated/<testcase_id>.json`, plus an index/manifest),
so that:

* a human can open a persisted, first-class artifact per testcase without
  reading an execution report;
* CP-04/CP-05 can be pointed at a specific, previously-governed CP-03
  output rather than only ever consuming whatever the current process
  happens to hold in memory;
* reproducibility no longer depends on re-invoking the LLM.

**This recommendation is not implemented by this investigation.** Because
it would add new behavior to the already-frozen CP-MVP2-03 implementation
(and touch the downstream call signatures of `run_cp_mvp2_04`/`run_cp_mvp2_05`
if they are to load rather than receive testcases), it requires a formal,
versioned **Change Request against the frozen CP-MVP2-03 checkpoint**
before any implementation work begins — per this project's standing
governance rule that no frozen specification or implementation may be
silently modified.
