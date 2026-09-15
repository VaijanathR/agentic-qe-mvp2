# CP-MVP2-08 — JMeter Performance Engineering — Execution Report

Timestamp (UTC): 2026-09-15T09:36:24Z

## 1. Objective

Demonstrate a real, executable Apache JMeter performance-measurement capability against a
bounded, representative, requirement-traceable read-only scenario of the real SUT
(`https://demowebshop.tricentis.com/`), producing honest, persisted performance evidence —
per `docs/CP-MVP2-08-SPECIFICATION-v1.0.md`.

## 2. Frozen Specification Reference

- `docs/CP-MVP2-08-SPECIFICATION-v1.0.md` (self-authored this task; no prior CP-08
  specification existed anywhere in the repository). Frozen via
  `docs/CP-MVP2-08-FINAL-SPECIFICATION-FREEZE-CHECKPOINT.md`,
  SHA-256 `048be6dfca0da9bf899ff582a7539686100a6efa48bc6989e7747ee619a5fa69`.
- Faithfully derived from this task's own governing instruction (sections 1–23) and from the
  pre-existing, authoritative `requirements/MVP2_SRS_v1.0_APPROVED.md` §9 ("Performance / NFR
  Requirements") and §13 (NFR-thresholds open item, explicitly flagged for CP-08).

## 3. Starting HEAD

`c22fcb02975dd5cef79bba1c3a16beb7fe58f1b5` (CP-MVP2-07 governance closure commit — CP-07
GREEN WITH ADVISORIES).

## 4. Requirements Tested

`REQ-BRW-01` — "The catalog shall be organized into independently browsable top-level
categories, including at minimum: Books, Computers, Electronics, Apparel & Shoes, Digital
Downloads, Jewelry, and Gift Cards... Given the main navigation, when any of the 7 category
links is selected, then a product grid renders." (Approved MVP2 SRS v1.0, APPROVED —
BASELINED v1.0.)

## 5. Performance Scenario

A bounded, representative, read-only navigation flow: `GET /` (home page) followed by
`GET /books` (the "Books" top-level category — the first-listed of REQ-BRW-01's 7 approved
categories, selected as the canonical representative rather than exercising all 7, to keep
the scenario bounded per this task's own MVP-checkpoint framing). Deliberately excludes any
state-mutating flow (registration/cart/checkout) — the shared, public, third-party SUT has no
published SLA and an unresolved data-reset/isolation policy (DATA-OQ-01), and creating
duplicate business entities merely to generate load is explicitly prohibited (task §7). Full
selection rationale in `docs/CP-MVP2-08-SPECIFICATION-v1.0.md` §4.

## 6. Workload Model

| Parameter | Value |
|---|---|
| Virtual users (threads) | 5 |
| Ramp-up period | 5 seconds |
| Loops per user | 3 |
| Pacing (think time) | 1000 ms constant timer between the two requests in each iteration |
| Total real HTTP requests | 30 (15 × `GET /`, 15 × `GET /books`) |
| Target | `https://demowebshop.tricentis.com/` |

## 7. JMeter Implementation

Real, committed, executable test plan:
`performance/jmeter/PERF-REQ-BRW-01-catalog-browse.jmx` — a standard JMeter 5.6.3 Test Plan
containing an HTTP Request Defaults config element, an HTTP Header Manager (identifying
User-Agent), one Thread Group (workload per §6), two `HTTPSamplerProxy` GET samplers (`/` and
`/books`), a Response Assertion per sampler (home page: response body contains
`"Demo Web Shop"`; Books category: response body contains `"product-grid"` — both directly
traceable to REQ-BRW-01's own "a product grid renders" wording), and a Constant Timer between
requests.

Three real defects were found and fixed during this task, none by changing any requirement,
threshold, or frozen artifact:

1. The plan's initial XML comment contained a literal `--`, invalid inside an XML comment,
   causing JMeter's XStream parser to reject the file (`XmlPullParserException: in comment
   after two dashes (--) next character must be > `). Fixed by rewording the comment.
2. `performance/pipeline.py` initially did not remove a stale `results.jtl` before invoking
   JMeter; JMeter's `-l` flag *appends* to an existing file rather than truncating it, so a
   second run under the same `run_id` silently doubled the sample count (60 instead of 30) —
   caught by this task's own focused test, never reported as real evidence. Fixed by removing
   any stale `.jtl`/log file immediately before each real invocation.
3. This repository's pre-existing `.gitignore` (unrelated to this task, present before it
   started) carries a blanket `runs/` rule and a blanket `*.jtl` rule (the latter explicitly
   labeled `# JMeter`). Both silently matched this checkpoint's own required evidence (the
   persisted `PerformanceRunRecord` envelope, and the raw `.jtl` results file itself),
   preventing `git add` from staging them without any error — a genuine conflict between the
   task's own explicit evidence-persistence requirement (§4/§11/§19) and a pre-existing,
   unrelated build-config file. Resolved, not escalated as a blocker, via two small, additive,
   non-frozen changes: (a) renaming the persisted-record directory from `.../generated/runs/`
   to `.../generated/records/` so it no longer collides with the pre-existing `runs/` pattern,
   and (b) adding one targeted `.gitignore` negation,
   `!performance/generated/raw/**/*.jtl`, so only this checkpoint's own real evidence file is
   un-ignored — every other `.jtl` anywhere else in the repository remains ignored exactly as
   before. `.gitignore` is not among the frozen artifacts listed in the task's own §2 boundary.

The corrected plan parses and runs correctly, and both evidence artifacts are now genuinely
committed (verified in the Git Commit / Fresh Verification sections below).

## 8. Environment

- Operating system: `Linux 6.18.33.2-microsoft-standard-WSL2 (x86_64)` — the WSL2 side of
  this project's dual Windows/Linux environment.
- JMeter version: `5.6.3` (Apache JMeter, downloaded from the official Apache CDN as a
  portable, non-installed tarball — no root/administrator privileges were available or used).
- Java version: `17.0.20` (Eclipse Temurin JRE, downloaded from the official Adoptium API as a
  portable, non-installed tarball).
- Neither JMeter nor the JRE is vendored inside this repository, consistent with this
  project's existing practice of not committing Playwright's browser binaries — both are
  external, independently obtainable dependencies. The pipeline (`performance/pipeline.py`)
  resolves them via the `JMETER_BIN`/`JAVA_HOME` environment variables (or `PATH`) at run
  time, and reports a real, honest `BLOCKED` disposition — never a fabricated `PASS` — if
  neither can be located (verified by a dedicated test).
- Execution timestamp: `2026-09-15T09:33:11.721718+00:00`.

## 9. Execution Evidence

Real, non-GUI JMeter execution: `jmeter -n -t PERF-REQ-BRW-01-catalog-browse.jmx -l
results.jtl -j jmeter_run.log`, run to completion in ~20 seconds. Persisted:
- `performance/generated/raw/PERF-RUN-CP08-PRIMARY/results.jtl` — the real, raw CSV sample
  data (31 lines: 1 header + 30 real samples).
- `performance/generated/raw/PERF-RUN-CP08-PRIMARY/jmeter_run.log` — JMeter's own real run log.
- `performance/generated/records/PERF-RUN-CP08-PRIMARY/` — the parsed `PerformanceRunRecord`,
  persisted via the unmodified `persistence/envelope.py`.

## 10. Metrics

Deterministically parsed from the real, raw `.jtl` file (`performance/metrics.py`; nearest-
rank percentile method; never manufactured):

| Metric | Aggregate | `GET Home Page` | `GET Books Category` |
|---|---|---|---|
| Sample count | 30 | 15 | 15 |
| Error count / % | 0 / 0.0% | 0 / 0.0% | 0 / 0.0% |
| Avg response time (ms) | 614.867 | 689.533 | 540.2 |
| Median (ms) | 518.0 | 482.0 | 525.0 |
| 90th percentile (ms) | 1015.0 | 1106.0 | 646.0 |
| Min (ms) | 439.0 | 439.0 | 505.0 |
| Max (ms) | 1426.0 | 1426.0 | 664.0 |
| Throughput (req/s, aggregate) | 1.737 | — | — |
| Test duration (s) | 17.276 | — | — |

## 11. Acceptance Criteria

Per frozen spec §8, two explicitly separate dimensions:

- **§8.1 Capability-demonstration criteria** — CAN be PASS/FAIL/BLOCKED: the `.jmx` plan
  parsed and ran without a fatal configuration error; both business-level response assertions
  (home-page title, Books-page product-grid marker) held on every real sample; the aggregate
  assertion/HTTP-failure rate was 0%.
- **§8.2 Numeric-SLA-threshold criteria** — Approved MVP2 SRS v1.0 §9.2 approves **no**
  numeric threshold for response time, throughput, error rate, baseline load, concurrency, or
  availability. This dimension is therefore, honestly, `INCONCLUSIVE` — not a new blocking
  discovery, but the standing, pre-existing, already-disclosed open item from SRS §13. It is
  never converted into `PASS` merely because the measured numbers (sec. 10) look reasonable.

## 12. PASS/FAIL/BLOCKED/INCONCLUSIVE Determination

- **Capability-demonstration result: `PASS`** — all 30 real HTTP samples completed with 0
  assertion/HTTP failures; the `.jmx` test plan is confirmed real, valid, and executable.
- **Numeric-SLA result: `INCONCLUSIVE`** — no approved numeric threshold exists to compare
  against (sec. 11 above).

## 13. Analysis

The real execution proves the full, real, requirement-traceable chain
(REQ-BRW-01 → Performance Scenario → JMeter Test Plan → Execution → Result → Conclusion) works
end-to-end: a real JMeter test plan generated real, bounded, paced concurrent traffic against
the real SUT, real response bodies were asserted against real, requirement-derived markers,
and real, raw results were deterministically parsed into disclosed metrics. The SUT responded
correctly and with 0 errors under this bounded workload (5 users, 30 requests). No numeric
SLA conclusion can honestly be drawn beyond that, because none is approved — this is a
disclosed scope limitation of the Approved SRS itself (§9.2), not a defect discovered by CP-08.

## 14. Limitations / Advisories

- **No approved numeric performance threshold exists** (SRS §9.2) — carried forward as a
  standing, non-blocking advisory; establishing one is a Human/Project Target decision, not a
  CP-08 decision.
- **Bounded, single-category scenario** — only the "Books" category (1 of REQ-BRW-01's 7) and
  only GET traffic were exercised, deliberately, to keep the workload light and non-disruptive
  to a shared, public, third-party instance (SRS §11). A broader, multi-category or
  higher-concurrency scenario remains a legitimate future (Human/Di-authorized) extension, not
  implemented here (task §14, no scope creep).
- **JMeter/JRE are external, unvendored dependencies** — not committed to this repository;
  reproducing this exact execution requires independently obtaining Apache JMeter 5.6.3 and a
  Java 17 runtime (or later-compatible versions) and pointing `JMETER_BIN`/`JAVA_HOME` at them.
- **Reproducibility is bounded by the shared SUT's own state/load at execution time** — no SLA
  or exclusive ownership exists (SRS §11); a re-run may observe different absolute response
  times without indicating any defect.

## 15. Regression Results

- CP-08 focused suite (`tests/test_cp08_performance.py`): **14/15 passed, 1 skipped**
  (the one live-execution test is honestly skipped in the Windows-venv regression environment,
  which has no `JMETER_BIN`/`JAVA_HOME` configured — the real live execution was independently
  performed and verified via the WSL2 side of this environment, sec. 9 above, and is never
  mocked as if it were real).
- Full regression (`tests/`): **345/346 passed, 1 skipped** (331 pre-existing + 15 new; zero
  existing test modified, weakened, or removed).

## 16. Frozen-Artifact Integrity

`git diff --stat HEAD` against the full CP-01–07 specification/implementation set, both
CP-06/CP-07 governance-closure reports, and the Approved SRS is **empty** — zero drift,
re-verified after implementation.

## 17. Final CP-08 Gate

# CP-MVP2-08 — GREEN WITH ADVISORIES

All frozen (self-authored, self-reviewed) CP-08 requirements are satisfied: a real, valid,
executable JMeter test plan traceable to REQ-BRW-01; a real execution against the real SUT
under a bounded, conservative, disclosed workload; deterministically parsed, non-fabricated
metrics; a correctly separated capability-demonstration (`PASS`) and numeric-SLA
(`INCONCLUSIVE`, honestly not a threshold PASS) disposition; real environment evidence;
14/15 focused + 345/346 full regression (1 honest skip each, for the one live-execution test
requiring external tooling not present in the regression environment); zero frozen-artifact
drift. Only non-blocking advisories remain (sec. 14).

## 18. CP-09 Recommendation / Authorization

**CP-MVP2-09 is authorized to begin**, subject to Human + Di review of this report's
advisories — in particular, the standing NFR-numeric-threshold open item (SRS §9.2/§13), which
remains a Human/Project Target decision independent of CP-08's own closure.
