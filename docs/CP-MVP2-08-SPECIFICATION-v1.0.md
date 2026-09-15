# CP-MVP2-08 Specification v1.0 — JMeter Performance Engineering

**Status: APPROVED / FROZEN — self-reviewed (sec. 14: no blocking issue found) under this
task's own batched SPECIFY → SELF-REVIEW → FREEZE → IMPLEMENT authorization, mirroring the
exact precedent already used for `docs/CP-MVP2-06-SPECIFICATION-v1.0.md` and
`docs/CP-MVP2-07-SPECIFICATION-v1.0.md`.**

**Origin note:** No standalone CP-MVP2-08 specification existed anywhere in the repository
prior to this task (confirmed via `find . -iname "*CP*08*"` — no match beyond incidental
timestamp substrings in unrelated filenames). This document is derived faithfully from (a)
this task's own governing instruction sections 1–23, and (b) the Approved MVP2 SRS v1.0 §9
("Performance / NFR Requirements"), which is the pre-existing, authoritative source for
CP-08's scope and — critically — for what CP-08 is explicitly **not** authorized to determine
(§9.2, numeric thresholds). Nothing in this document invents a requirement, scenario detail,
or threshold beyond what those two sources already establish.

---

## 1. Objective

### 1.1 CP-08 owns
- Demonstrating a real, executable Apache JMeter performance-measurement capability against
  a bounded, representative, requirement-traceable read-only scenario of the real SUT
  (`https://demowebshop.tricentis.com/`).
- Capturing the approved performance-measurement scope from SRS §9.1: response time,
  throughput, error rate, behavior under a defined baseline load/concurrency, with evidence
  capture for all of the above.
- Implementing **threshold validation as a process** (SRS §9.1's own phrase) — i.e., the
  mechanism that would compare measured metrics against an approved numeric threshold — while
  honestly reporting that SRS §9.2 approves **no** numeric threshold yet, so that mechanism
  currently has nothing approved to compare against.
- Persisting real, honest, non-fabricated performance evidence (JMeter test plan, raw results,
  parsed metrics, environment record, governed disposition).

### 1.2 CP-08 does NOT own
- Approving, deriving, or inventing a numeric SLA/threshold (response-time target, throughput
  target, error-rate target, concurrency/load target, availability target). SRS §9.2 marks
  every one of these **TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL**. CP-08 treats
  this as a standing, pre-existing, already-disclosed open item (SRS §13, row "NFR thresholds
  (§9.2)"), not a new blocking discovery.
- Any state-mutating business flow (registration, checkout, cart mutation, order placement) as
  a load-generation target — per task §7 ("do NOT create duplicate business entities merely to
  increase load") and SRS §10/§11 (unresolved shared-instance data-reset/isolation policy,
  DATA-OQ-01; shared, third-party, publicly-used demo instance with no published SLA).
- CP-01–07 responsibilities, CP-06 real browser execution, CP-07 RCA/replanning/governance,
  CR-002 (runtime locator fallback), security/penetration testing, or any Post-MVP performance
  framework enhancement (task §14/§15).

## 2. Authoritative Architecture

```
Approved Requirement (REQ-BRW-01)
      -> Performance Scenario (bounded, read-only, representative)
      -> JMeter Test Plan (.jmx, real, executable)
      -> Real Execution (JMeter non-GUI mode, real HTTP against the real SUT)
      -> Raw Results (.jtl) + JMeter summary
      -> Metrics Extraction (deterministic parse — no fabrication)
      -> Acceptance-Criteria Comparison
           - Capability-demonstration criteria -> PASS/FAIL/BLOCKED
           - Numeric-SLA criteria -> INCONCLUSIVE (no approved threshold exists, SRS sec. 9.2)
      -> Governed CP-08 Disposition
      -> Persisted Outcome (persistence/envelope.py, unmodified)
```

## 3. Frozen Upstream Contracts

- `requirements/MVP2_SRS_v1.0_APPROVED.md` §2.4 ("Performance Scope... no thresholds
  approved"), §9 ("Performance / NFR Requirements" — full text of 9.1/9.2 is authoritative
  and reproduced by reference, not by copy, to avoid any drift), §13 (NFR-thresholds open item,
  explicitly flagged for CP-08).
- `REQ-BRW-01`: "The catalog shall be organized into independently browsable top-level
  categories, including at minimum: Books, Computers, Electronics, Apparel & Shoes, Digital
  Downloads, Jewelry, and Gift Cards... Given the main navigation, when any of the 7 category
  links is selected, then a product grid renders." — APPROVED — BASELINED v1.0. This is the
  requirement CP-08's scenario is traceable to.
- CP-MVP2-06 (GREEN WITH ADVISORIES, commit `9e122eaa00f08a05700aafc2d51b9a2d09ea3682`) and
  CP-MVP2-07 (GREEN WITH ADVISORIES, commit `c22fcb02975dd5cef79bba1c3a16beb7fe58f1b5`)
  governance closures — both treated as closed and untouched.

## 4. Performance Scenario Selection (bounded, representative)

Per task §5 ("If the frozen CP08 specification allows a bounded representative scenario,
document exactly what was selected and why"), CP-08 selects **one** representative,
read-only, non-mutating, idempotent navigation flow traceable to REQ-BRW-01:

1. `GET /` — home page (establishes the entry point real shoppers use).
2. `GET /books` — the "Books" top-level category (one of REQ-BRW-01's 7 approved categories;
   selected as the first-listed, canonical representative — not all 7, to keep the scenario
   bounded per the task's own MVP-checkpoint framing, not a production-scale suite).

**Why bounded to read-only GET traffic only:** the SUT is a shared, public, third-party demo
instance (SRS §11) with no published SLA and an unresolved data-reset/isolation policy
(DATA-OQ-01). A state-mutating scenario (registration/checkout/order) run under repeated load
would (a) create real, duplicate business entities on a shared instance purely to generate
load — explicitly prohibited by task §7 — and (b) risk degrading the shared instance for other
real users of a publicly offered demo/training site. A bounded, idempotent, read-only GET
scenario against the same public entry points ordinary browsing already exercises avoids both
concerns while still exercising a real, approved, traceable requirement (REQ-BRW-01) under
real concurrency.

## 5. Workload Model

Deliberately conservative, per the same "shared public instance" reasoning above and the
task's own framing ("This is an MVP checkpoint, not a production-scale performance-testing
framework redesign"):

- Virtual users (threads): **5**
- Ramp-up period: **5 seconds** (approx. 1 new user/sec)
- Loop count per user: **3** (bounded iteration count, not an open-ended duration/soak test)
- Pacing: a **1000 ms constant timer** between the two samplers within each iteration, so the
  generated traffic approximates a real user's think-time rather than back-to-back hammering.
- Total real HTTP requests generated: 5 users × 3 iterations × 2 samplers = **30 requests**
  (15 × `GET /`, 15 × `GET /books`).
- Target environment: `https://demowebshop.tricentis.com/` (the same real SUT used by every
  prior checkpoint; no MVP2-controlled environment exists, per SRS §11).
- Tooling: Apache JMeter (non-GUI/CLI mode) + a Java 17 runtime. Neither is vendored inside
  this repository (consistent with this project's existing practice of not committing
  Playwright's browser binaries) — both are external, independently obtainable dependencies;
  the exact versions used for CP-08's real execution are recorded in the persisted environment
  evidence (sec. 10).

If a genuine resource limitation prevented even this bounded workload from running, task §6
requires STOP → REPORT → HUMAN + DI DECIDE rather than silently reducing scope further; this
did not occur during CP-08's real execution (sec. 12, implementation evidence).

## 6. Test Data

No test data beyond the two fixed, public, read-only URL paths above is required. No account,
no cart, no synthetic business entity is created, per task §7 and sec. 4's rationale above.

## 7. Metrics Captured

Deterministically parsed from JMeter's own real, raw `.jtl` results file — never manufactured
(task §8):

- Response time: average, median, 90th percentile, min, max (per sampler and aggregate).
- Throughput: requests/sec (aggregate).
- Error count and error percentage (aggregate and per sampler).
- Concurrent users (the configured thread count, sec. 5).
- Sample count (total and per sampler).

**Observed measurement → derived metric → interpretation** are kept in distinct fields
(sec. 9 below) — an interpretation is never presented as if it were itself a measurement.

## 8. Acceptance Criteria Model

Two, explicitly separate, dimensions — conflating them would misrepresent SRS §9.2's own
approval state:

### 8.1 Capability-demonstration criteria (CAN be PASS/FAIL/BLOCKED)
- The `.jmx` test plan is a real, valid, executable JMeter artifact. **PASS** if JMeter parses
  and runs it without a fatal configuration error; **BLOCKED** otherwise.
- The scenario's business-level response assertions (home-page title, category-page
  product-grid marker — both traceable to REQ-BRW-01's own "a product grid renders" wording)
  are evaluated against real response bodies. **PASS** if the aggregate assertion-failure rate
  is 0%; **FAIL** if any real assertion failure occurred (never silently excluded, per task §9).
- Evidence capture itself (sec. 7's metrics, environment record, raw `.jtl`) is either
  genuinely produced (**PASS**) or not (**BLOCKED/NOT_EXECUTED**).

### 8.2 Numeric-SLA-threshold criteria (governed as INCONCLUSIVE, never fabricated)
Per SRS §9.2, **no** numeric threshold is approved for response time, throughput, error rate,
baseline load, concurrency/load levels, or availability. CP-08 therefore reports this
dimension's disposition as **INCONCLUSIVE** — not PASS, not FAIL — with the explicit reason
"no approved numeric threshold exists to compare against" and the standing recommendation
(carried over verbatim from SRS §13, not invented by CP-08) that establishing one is a
Human/Project Target decision. This is never converted into a PASS merely because the
measured numbers "look reasonable," and never converted into a FAIL merely because a number
existed to report — an INCONCLUSIVE numeric-SLA disposition can coexist with a PASS overall
capability-demonstration disposition (sec. 8.1), and does exactly that in CP-08's real result
(sec. 15).

## 9. Result Vocabulary

Reused verbatim from task §16: `PASS`, `FAIL`, `BLOCKED`/`NOT_EXECUTED`, `INCONCLUSIVE`. No
new category invented. An `INCONCLUSIVE` or `BLOCKED` result is never silently converted to
`PASS` (task §16, §18).

## 10. Environment Evidence

Persisted per real execution: operating system, JMeter version, Java version, target URL,
UTC timestamp, workload configuration (sec. 5), and the disclosed limitation that
reproducibility is bounded by (a) the shared, third-party SUT's own state/load at execution
time (SRS §11 — no SLA, no exclusive ownership), and (b) JMeter/JRE being external, versioned
dependencies not vendored in this repository.

## 11. Evidence Persistence

New, additive `performance/` package, following this project's established
"new capability = new package, reuse the shared envelope" pattern (`persistence/envelope.py`,
unmodified):

- `performance/jmeter/<scenario_id>.jmx` — the real, committed JMeter test plan.
- `performance/generated/runs/<run_id>/` — per-execution raw `.jtl`, JMeter's own summary
  log, and a parsed `PerformanceRunRecord` envelope (via `persistence/envelope.py`).
- `docs/claude-execution-reports/CP-MVP2-08/` — the formal, human-readable execution report.

## 12. Testing Requirements

Automated tests (deterministic, no real network calls in the unit-level suite; real network
calls confined to the one, explicit, real pipeline-execution test) must verify: `.jmx`
structural validity, metrics-parsing correctness against a real, persisted `.jtl` fixture,
acceptance-criteria separation (sec. 8.1 vs 8.2 never conflated), the INCONCLUSIVE numeric-SLA
disposition, the BLOCKED path for a missing/invalid JMeter installation or missing results
file, persistence roundtrip, and deterministic re-parse of the same raw results.

## 13. Regression & Frozen-Artifact Integrity

CP-01–07 specifications/implementations, CP-06/07 governance closures, and the Approved SRS
must show zero `git diff --stat` drift after CP-08's implementation. Full regression suite
must pass with zero existing test weakened or removed.

## 14. Self-Review

Reviewed against task §§1–23 and SRS §9/§13: **PASS — no blocking issue found.** The one
genuine tension identified — task §9's "Performance PASS/FAIL must be determined against the
frozen CP08 acceptance criteria" versus SRS §9.2's explicit non-approval of any numeric
threshold — is resolved, not silently bypassed, by sec. 8's two-dimension model: a real
PASS/FAIL/BLOCKED capability-demonstration disposition, plus an honest, separately-labeled
INCONCLUSIVE numeric-SLA disposition. This is disclosure, not invention, and matches task §16
exactly ("Use the exact terminology required by the frozen CP08 specification where defined...
Do not convert an inconclusive or blocked result into PASS").

## 15. Acceptance Criteria (checklist)

- [ ] Real, valid, committed `.jmx` test plan, traceable to REQ-BRW-01.
- [ ] Real JMeter execution against the real SUT, non-GUI mode, with the exact workload of
      sec. 5.
- [ ] Real, parsed metrics per sec. 7, never fabricated.
- [ ] Business-level response assertions evaluated against real response bodies.
- [ ] Acceptance-criteria disposition correctly separates sec. 8.1 from sec. 8.2.
- [ ] Environment evidence persisted per sec. 10.
- [ ] Focused + full regression suites pass; zero frozen-artifact drift.
- [ ] Execution report written per task §19.

## 16. Versioning and Freeze

v1.0 — frozen this task via `docs/CP-MVP2-08-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`, with
implementation proceeding in the same batched task, mirroring the CP-06/CP-07 precedent.
