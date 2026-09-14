# CP-MVP2-05 — Playwright E2E Generation: Implementation Notes

Implements the frozen `docs/CP-MVP2-05-SPECIFICATION-v1.0.md` on top of the
unmodified CP-MVP2-02 RAG layer, CP-MVP2-03 testcase pipeline, and
CP-MVP2-04 test-data pipeline. This document explains the implementation;
it does not redefine or extend the specification.

## Architecture

```text
ACCEPTED CP-MVP2-03 TESTCASE + ACCEPTED/POSSIBLE_DUPLICATE CP-MVP2-04 DATASET
      |
GOVERNED RAG ATTRIBUTION  (testcases/generate.py::requirement_context, reused unmodified)
      |
DETERMINISTIC LOCATOR EVIDENCE LOOKUP  (automation/evidence.py — reads real
      |                                 discovery captures from disk, never via KnowledgeBase)
LLM STEP-STRUCTURE REASONING  (llm/automation_client.py::AutomationLLMClient.propose_steps())
      |
STRUCTURED PLAYWRIGHT ARTIFACT  (automation/schema.py)
      |
DETERMINISTIC VALIDATORS  (automation/validate.py)
      |
DUPLICATE / COVERAGE / GOVERNANCE
      |
CP-MVP2-05 RESULT  (automation/pipeline.py::run_cp_mvp2_05())
```

| Path | Role |
|---|---|
| `automation/schema.py` | `PlaywrightArtifact` / `PlaywrightStep` / `LocatorSpec` / `Assertion` / `GovernedPlaywrightArtifact`, and fixed vocabularies. |
| `automation/evidence.py` | Deterministic locator-evidence lookup, reading `knowledge/historical/discovery_evidence/captures/*.html` **directly from disk** — never via `KnowledgeBase`. |
| `llm/automation_client.py` | The reasoning boundary. `AutomationLLMClient` (abstract), `ClaudeAutomationClient` (real backend), `StubAutomationClient` (deterministic offline stand-in). **New file — `llm/client.py` is not modified** (see below). |
| `automation/generate.py` | Context-building + generation orchestration. Locators come exclusively from `automation.evidence`; field values are never seen by this module (only field *names*, from the linked CP-MVP2-04 dataset — actual values are read later by whatever executes the artifact, i.e. CP-MVP2-06, not by CP-MVP2-05 itself). |
| `automation/validate.py` | Deterministic governance: schema, traceability, data-mapping integrity, assertion integrity, locator/load-bearing rule, duplicate detection, coverage. |
| `automation/pipeline.py` | `run_cp_mvp2_05()`, scoped strictly to CP-MVP2-03's `ACCEPTED` testcases paired with their CP-MVP2-04 `ACCEPTED`/`POSSIBLE_DUPLICATE` datasets. |

## Design decision — `llm/client.py` not modified (same precedent as CP-MVP2-04)

`llm/client.py` is formally frozen (CP-MVP2-03 checkpoint). Its only
abstract method, `propose_testcases()`, is inapplicable to step-structure
reasoning. `llm/automation_client.py` is a **new, parallel** file,
reusing `ClaudeProviderError` (imported, not redefined) and the identical
Claude Pro subscription/subprocess-safety mechanism (`claude -p
--restricted`, argument-list `subprocess.run` with `shell=False`,
explicit timeout, `ANTHROPIC_API_KEY` billing-safety guard) already
proven by `ClaudeLLMClient` and `ClaudeTestDataClient`. `git diff`
against `llm/client.py` is empty throughout this implementation.

## The LLM's role is narrower here than in CP-MVP2-03/04

`AutomationLLMClient.propose_steps()` returns **only**: `action_type`,
`field_name` (a name, never a value or locator), `synchronization_strategy`,
and an optional narrative `assertion_condition`. It never returns a
locator, a field value, or a governance status. This is a stricter
narrowing than CP-MVP2-04's "field values only" contract, because the
frozen CP-MVP2-05 specification repeatedly and explicitly prohibits
locator fabrication — the model is given no surface to fabricate one on
in the first place. The one mandatory `BUSINESS_REQUIRED` assertion is
**always** assembled deterministically from the anchor testcase's own
`expected_result` (`automation/generate.py`), never contingent on the
LLM proposing it — any LLM-proposed assertion narrative is classified
`TECHNICAL_USEFUL` and never counts toward coverage.

## Locator evidence: real findings, not invented examples

Direct inspection of `knowledge/historical/discovery_evidence/captures/checkout_00.html`
(performed while writing the frozen specification, and re-verified while
implementing `automation/evidence.py`) found:

* **Evidenced (real, stable):** the Billing/Shipping address form uses
  ASP.NET MVC model-binding IDs — `BillingNewAddress_FirstName`,
  `_LastName`, `_Email`, `_CountryId` (a `<select>`, not `_Country` —
  corrected during implementation after the naive guess failed a
  sanity check against the real file), `_City`, `_Address1`, `_Address2`,
  `_ZipPostalCode`, `_PhoneNumber`, `_Company`, `_FaxNumber` — one per
  `REQ-ACO-03` mandatory/optional field, all 11 confirmed present by a
  fresh regex search of the real file at call time (`lookup_locator`
  never returns a value without confirming it in the actual file).
* **Genuinely ambiguous (real, disclosed, not resolved by guessing):**
  the "Continue" submit control for the Billing step shares its CSS
  class (`new-address-next-step-button`) with the Shipping step's
  "Continue" control — two elements, one class, on the same real page.
  `lookup_submit_locator("REQ-ACO-03")` explicitly counts the real
  matches and returns `None` (`UNSUPPORTED`) whenever there is not
  exactly one — this is why a `REQ-ACO-03` artifact built from real
  evidence currently reaches `UNSUPPORTED_NEEDS_CLARIFICATION` overall
  (see "Known limitations" and the live-verification evidence report),
  not `ACCEPTED` — a correct, evidence-driven outcome, not a defect.
* **No evidence at all:** `REQ-REG-01` (no `/register` capture exists),
  `REQ-CART-03`'s quantity locator (only a fragile, item-specific
  literal is evidenced), and `REQ-PAY-01`'s per-option locators
  (unconfirmed) — all `lookup_locator`/`lookup_submit_locator` calls for
  these return `None`, never a guess.

## Load-bearing rule (spec sec. 12.1)

`automation/validate.py::validate_locators` conservatively treats
**every** `FILL`/`CLICK`/`SELECT` step as load-bearing (the
implementation has no deterministic way to prove a given UI action is
safely skippable without inventing that judgment itself). Any one such
step with an `UNSUPPORTED` locator makes the **whole artifact**
`UNSUPPORTED_NEEDS_CLARIFICATION` — never partially `ACCEPTED`.

## Configuration / dependencies

* `ClaudeAutomationClient`: same requirements as `ClaudeLLMClient`/
  `ClaudeTestDataClient` — `claude` on `PATH` (or
  `CP_MVP2_05_CLAUDE_EXECUTABLE`), `ANTHROPIC_API_KEY` absent (billing-
  safety guard), `CP_MVP2_05_CLAUDE_MODEL`/`CP_MVP2_05_CLAUDE_TIMEOUT_SECONDS`
  (default `120`) optional.
* `StubAutomationClient` requires no configuration, makes no network calls.

## Test execution

```text
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_05_automation_generation.py -v
.venv/Scripts/python.exe -m pytest tests/test_cp_mvp2_05_claude_provider.py -v
.venv/Scripts/python.exe -m pytest -q   # full regression (CP-MVP2-01 through 05)
```

## Known limitations (disclosed, not hidden)

* **No genuinely `ACCEPTED` `REQ-ACO-03` artifact exists against real
  evidence today**, because the real submit-button locator is
  ambiguous. One test (`test_valid_artifact_reaches_accepted_with_synthetic_unambiguous_evidence`)
  proves the acceptance *mechanism* works correctly given unambiguous
  evidence, using a disclosed synthetic/mocked evidence lookup — it does
  not claim the real capture is unambiguous. This mirrors the exact
  "disclosed synthetic mechanism test" convention already used
  elsewhere in this project (CP-MVP2-02's supersession test, CP-MVP2-04's
  draft-leakage test).
* **The stub/LLM does not distinguish `SELECT`-worthy dropdown fields
  (e.g. `country`, which renders as a `<select>`) from `FILL`-worthy
  text fields** — both `StubAutomationClient` and the real backend's
  system prompt currently let the model choose freely, and neither is
  forced to pick `SELECT` for `country` specifically. This does not
  affect locator evidence or governance correctness (the locator lookup
  and data-mapping checks are keyed by `field_name`, not `action_type`),
  but a future refinement could make the `action_type` choice itself
  more evidence-driven.
* **No live Claude call was exercised during automated-test authoring**
  — `ClaudeAutomationClient` is verified only against a mocked
  subprocess boundary. A separate, live verification is performed after
  this implementation, with its own independently reported evidence.
* **`DATA-OQ-01` remains unresolved**, inherited unchanged — no part of
  this implementation encodes an assumption about shared-instance
  isolation.
* **`REQ-CART-03`'s cart-quantity locator pattern remains unresolved** —
  `lookup_locator` never generalizes the evidenced item-specific literal.
* **`REQ-PAY-01`'s per-option locators remain unconfirmed** — omitted
  from `evidence.py` entirely; requesting one always yields `UNSUPPORTED`.

## Downstream Contract (CP-MVP2-06)

`run_cp_mvp2_05()`'s `governed_artifacts` (status `ACCEPTED`/
`POSSIBLE_DUPLICATE`) are the only artifacts CP-MVP2-06 should execute.
Each carries a fully resolved `steps` sequence (locators, ordering,
sync strategy), an `input_mapping` per data-consuming step (CP-MVP2-06
resolves the actual value by looking up that field on the linked
CP-MVP2-04 dataset — CP-MVP2-05 itself does not embed literal values into
the artifact, only the field-name reference), and `evidence_requirements`/
`failure_handling_metadata` declaring what CP-MVP2-06 should capture on
failure. CP-MVP2-06 is not implemented, specified, or started by this task.
