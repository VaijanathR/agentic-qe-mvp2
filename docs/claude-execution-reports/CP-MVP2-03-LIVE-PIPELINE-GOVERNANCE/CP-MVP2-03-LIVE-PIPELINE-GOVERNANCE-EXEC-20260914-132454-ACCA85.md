# CP-MVP2-03 — Live Pipeline Governance Verification: Detailed Report

**Headline result: OUTCOME A occurred (Claude returned a populated candidate). The candidate was passed through the actual, unmodified production pipeline (`testcases.pipeline.run_cp_mvp2_03`) and was genuinely evaluated — not assumed — ACCEPTED by the existing deterministic governance layer, with correct traceability, attribution, and coverage (1/1, 100%). No fabrication, substitution, retry, or code change occurred.**

## A. Governance

* `docs/CP-MVP2-03-SPECIFICATION-v1.0.md`: verified **UNCHANGED** (empty `git diff`, before and after).
* `docs/CP-MVP2-03-CLAUDE-PROVIDER-DECISION.md`: verified **UNCHANGED.**
* Implementation (`llm/client.py`, `testcases/`): verified **UNCHANGED.**
* Prompt: **UNCHANGED** — the verification called the real production entry point `testcases.pipeline.run_cp_mvp2_03(kb, client, requirement_ids=["REQ-REG-01"], scenario_types=["POSITIVE"])`, which internally builds the prompt exactly as `ClaudeLLMClient.propose_testcases()` already does; nothing about the prompt was altered for this verification.
* Parser: **UNCHANGED.**
* `CP-MVP2-04`: **NOT STARTED.** No downstream/out-of-scope work performed.

## B. Environment

* Claude Code version: `2.1.270`.
* Authentication method: `claude.ai` (OAuth), `apiProvider: "firstParty"`.
* Subscription type: `pro`.
* `ANTHROPIC_API_KEY`: checked in the current shell and a fresh `bash -lc` login shell — **NOT SET** in either. Verification proceeded on the subscription path.
* Model used: none configured (`CP_MVP2_03_CLAUDE_MODEL` unset) — CLI default; `model_name` reported as `claude-cli:default`.
* Timeout: default, `120` seconds (`CP_MVP2_03_CLAUDE_TIMEOUT_SECONDS` unset).
* No credential value was printed, logged, or persisted anywhere in this task's evidence.

## C. RAG

* Requirement ID: `REQ-REG-01`.
* Source: `requirements/MVP2_SRS_v1.0_APPROVED.md`, version `1.0`.
* Approval status resolved by the pipeline: `APPROVED_BASELINED_V1_0` (confirmed indirectly — see "Deterministic Governance" below: `govern_testcase` would have rejected/quarantined the candidate had the canonical `REQ-REG-01` chunk not resolved as `approved_srs`/`APPROVED`, and it did not).
* Retrieved through the existing, unmodified `testcases.generate.requirement_context()` / `KnowledgeBase.by_id()` (CP-MVP2-02 governed RAG) — the same call path `run_cp_mvp2_03` → `generate_for_requirements` → `generate_for_requirement` → `requirement_context` always uses; nothing was retrieved or reconstructed manually.

## D. Live Execution

* Invocation entry point: `testcases.pipeline.run_cp_mvp2_03()` — the actual, unmodified production function, not a hand-built substitute.
* Exactly **one** real Claude invocation occurred, entirely inside this unmodified call chain (`generate_for_requirement` calls `client.propose_testcases()` exactly once per requirement, and exactly one requirement was requested).
* Elapsed time: **4.74 seconds** — a genuine subprocess round trip.
* CLI status: success (no `ClaudeProviderError` was raised — the run completed and returned a report).
* Outer envelope / inner result status: both parsed successfully inside the unmodified `ClaudeLLMClient.propose_testcases()` (no parse error occurred this time — see "Observation vs. Interpretation" below for what this single data point does and does not establish).
* Result type: a JSON array containing exactly **1** candidate object.
* Number of generated candidates: **1** (scenario_type `POSITIVE`).

## E. Deterministic Governance

Recorded exactly as produced by the unmodified `testcases.validate.build_report()` (invoked internally by `run_cp_mvp2_03`):

* Schema validation: implicitly passed — the candidate reached `ACCEPTED` status, which `govern_testcase` only assigns after `validate_schema` passes (a schema failure would have produced `REJECTED` with `SCHEMA_INVALID:...` reasons; none were present).
* Requirement ID validity / requirement existence / Approved status: implicitly passed for the same reason — `validate_traceability` would have produced `QUARANTINED` (unknown ID) or `REJECTED` (not-approved/draft leakage) with explicit reasons had either condition held; the actual result was `ACCEPTED` with an empty `reasons` list.
* Traceability: `requirement_ids: ["REQ-REG-01"]` on the accepted testcase, consistent with the retrieved context.
* Source attribution: present and correct — `{"requirement_id": "REQ-REG-01", "source_document": "requirements/MVP2_SRS_v1.0_APPROVED.md", "source_version": "1.0", "chunk_id": "srs_v1.0__REQ-REG-01"}`.
* Duplicate handling: `duplicate_testcase_id_check` → `{"passed": true, "detail": {}}` (only one testcase existed, so no collision was possible; the check ran for real and reported the true, unremarkable result).
* Unsupported handling: `unsupported_requirements: []` — correctly empty, since a candidate was produced and accepted.
* Accepted testcase count: **1** (`TC-REQ-REG-01-01`).
* Rejected/quarantined count: **0**.

Full accepted record (as actually returned by the pipeline — not edited):

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

## F. Coverage

Recorded exactly as produced by the unmodified `testcases.validate.calculate_coverage()`:

* Total applicable requirements: **1** (`REQ-REG-01`, the only ID passed to this run).
* Covered requirements: **1** (`["REQ-REG-01"]`).
* Uncovered requirements: **0** (`[]`).
* Coverage percentage: **100.0%.**

This is the OUTCOME A coverage arithmetic specified in sec. 10 ("If testcase is accepted: Total = 1, Covered = 1, Coverage = 100%") — matched exactly by the real, unmodified calculation, not asserted independently of it.

## G. Final Result Chain

```text
LLM result:                 1 candidate returned (POSITIVE), valid direct JSON, no fence/prose
        ↓
Deterministic validation:   schema PASS, traceability PASS, requirement APPROVED, attribution PASS
        ↓
Traceability result:        TC-REQ-REG-01-01 -> REQ-REG-01 -> Approved SRS v1.0 -> srs_v1.0__REQ-REG-01
        ↓
Coverage result:            1/1 applicable requirements covered = 100%
        ↓
Governance result:          ACCEPTED (0 rejected, 0 quarantined, 0 duplicates)
```

## H. Regression

* Baseline (pre-execution): `.venv/Scripts/python.exe -m pytest -q` → **67 passed, 0 failed.**
* Final (post-execution): same command → **67 passed, 0 failed.** No regression.

## I. Git

* Starting HEAD: `378aab8cc28a5389879f97cc99c5b1c51ad6f038` (== `origin/main`, confirmed via `git fetch` + `git rev-parse`).
* Ending HEAD (before this evidence commit): `378aab8cc28a5389879f97cc99c5b1c51ad6f038` — unchanged.
* Files changed: none in implementation/specification — only this report and its companion summary were added.
* Commit / push status: recorded in the final chat response, from the actual `git commit`/`git push` output executed after this file was written.

## J. Scope

```text
CP-MVP2-04: NOT STARTED
Parser change: NONE
Prompt change: NONE
Provider change: NONE
Specification change: NONE
Requirement modified: NO
Retry performed: NO
Stub substituted: NO
```

## Pass/Fail Decision Table (this single execution)

| Observation | Expected governance behavior | Result |
|---|---|---|
| Valid testcase + valid REQ | Accept and trace | **PASS — verified** (real ACCEPTED status, real traceability/attribution/coverage, as documented above) |
| Valid testcase + unknown REQ | Reject/quarantine | NOT EXERCISED this execution (Claude did not return an unknown-REQ candidate; this rule is already covered by real evidence in `tests/test_cp_mvp2_03_testcase_generation.py::test_unknown_requirement_id_is_quarantined`, not re-asserted here as a live-Claude observation) |
| Draft-only testcase | Reject | NOT EXERCISED this execution (no draft-only candidate occurred; covered separately by `test_draft_leakage_cannot_produce_an_accepted_testcase` against a synthetic KB) |
| `[]` from Claude | Zero accepted TCs; requirement remains uncovered | NOT EXERCISED this execution — OUTCOME A occurred, not OUTCOME B. (A prior task's 5-call characterization study did observe `[]` twice, but did not run those calls through the full deterministic-governance/coverage pipeline the way this task's protocol requires — that is a genuine gap this specific execution does not close, since Claude did not return `[]` this time and no retry was performed to force it to.) |
| `[]` converted into testcase | PROHIBITED | N/A — did not occur; nothing to convert |
| `[]` counted as coverage | PROHIBITED | N/A — did not occur |
| Requirement changed to obtain testcase | PROHIBITED | **PASS — confirmed not to have occurred** (requirement text/ID untouched; `git diff` on `requirements/` empty) |
| Prompt changed after empty result | PROHIBITED | N/A — no empty result occurred to react to; prompt construction verified unchanged regardless |
| Parser changed | PROHIBITED | **PASS — confirmed not to have occurred** (`git diff` on `llm/`, `testcases/` empty) |
| Stub substituted for real Claude | PROHIBITED | **PASS — confirmed not to have occurred** (real `ClaudeLLMClient`, real subprocess, 4.74s elapsed) |
| Regression failure | PROHIBITED | **PASS — confirmed not to have occurred** (67/67 before and after) |

## Observation vs. Interpretation

**Confirmed observations:**
* This single execution produced OUTCOME A (populated candidate), which the real, unmodified deterministic governance layer accepted, traced, attributed, and counted toward coverage correctly.
* No prohibited behavior (fabrication, requirement modification, prompt change, parser change, stub substitution, retry) occurred, confirmed by `git diff` and by the fact only one invocation was made.

**Interpretation (reasonable conclusion from this observation, not overstated):**
* The existing CP-MVP2-03 pipeline, when a real Claude response is well-formed and populated, correctly assembles and governs it end-to-end without manual intervention — the "LLM reasons, deterministic code governs" principle held in this instance.

**Unknown / not established by this execution:**
* Whether the pipeline behaves correctly for OUTCOME B (`[]`) was **not verified by this specific execution**, because Claude did not return `[]` this time and this task's own governance (sec. 6/8) forbids retrying to force that case. A prior, separate task (the 5-call characterization study) did observe `[]` twice, but as a raw-subprocess characterization exercise, not run through this task's exact protocol (full `run_cp_mvp2_03` pipeline + explicit coverage/traceability verification against the `[]` case). Whether OUTCOME B is correctly governed by the *full* production pipeline therefore remains **not directly confirmed by any single execution to date** — this is disclosed honestly rather than assumed favorable by analogy to the deterministic unit tests (which do exercise the empty/unsupported path syntactically, via `test_scenario_not_manufactured_without_justifying_evidence` and `generate_for_requirement`'s own `unsupported` handling — but not via a live Claude `[]` response specifically).
* This single execution is a governance verification, not a statistical reliability study — no claim is made about how often Claude returns a populated vs. empty result.
