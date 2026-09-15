# POST-MVP2 ENHANCEMENT 01 — Governed Playwright Automation + Test Management + JMeter Performance Foundation

Timestamp (UTC): 2026-09-15T15:08:00Z

This is a **post-MVP2 enhancement**. The frozen MVP2 baseline `33b9946` was not modified
anywhere in this task (verified sec. "Governance" below). All new work lives in clearly
identified, additive, new locations: `testmgmt/`, `automation/playwright/`,
`performance/jmeter/{fragments,scenarios,data,results}/`, `.vscode/`, `requirements.txt`, and
`tests/test_enh01_*.py`.

## Baseline

- Starting SHA: `33b9946`
- Final SHA (this enhancement, pre-commit): to be recorded at commit time (sec. "Git Commit"
  in the closing summary of this task)
- Baseline integrity: **zero drift** — `git diff --stat 33b9946 -- <every frozen MVP1/MVP2
  path>` is empty (re-verified immediately before this report was drafted; full path list in
  the Governance section).

## Environment

See `docs/claude-execution-reports/ENHANCEMENT-01/environment_record.json` for the full,
persisted record. Summary:

| Component | Evidence |
|---|---|
| Windows | Microsoft Windows 10 Home, 10.0.19045 |
| VS Code | 1.137.0 |
| Python | 3.13.2, `.venv\Scripts\python.exe` (genuine Windows venv, reached via WSL interop in this session, never a WSL/Linux interpreter) |
| Playwright | 1.62.0 (package + CLI) |
| Chromium | 151.0.7922.34 — real headless launch verified |
| Java/JRE | Eclipse Temurin 17.0.20.1+1, external, Windows-native, not vendored in this repository |
| `JAVA_HOME` | Not set by default; must be configured per-machine (same external-dependency contract as CP-MVP2-08) |
| JMeter | 5.6.3, external, Windows-native `bin/jmeter.bat`, not vendored |
| `JMETER_EXECUTABLE` | Not set by default; must be configured per-machine |
| Windows Playwright execution | **DEMONSTRATED** |
| Windows JMeter execution | **DEMONSTRATED** |
| Windows parallel execution | **DEMONSTRATED** (pytest-xdist, 2 workers) |
| Distributed execution | **CONFIGURED** (architecture documented) — **NOT IMPLEMENTED** (no second machine/grid available) |
| WSL status | **INFORMATIONAL ONLY** — used solely for repository inspection/orchestration (git, curl, file edits); every claimed real execution ran through the Windows-native interpreter/JMeter, never WSL |

## Test Management (`testmgmt/`)

- `testmgmt/generate_workbooks.py` — deterministic, read-only Excel generator over the
  frozen, persisted MVP2 corpus (`testcases/generated/`, `testdata/generated/`,
  `traceability/`, `automation/generated/`, plus real CP-06 execution status via
  `reporting.gather`). **Never a second, hand-editable source of truth**: JSON remains
  authoritative for automation consumption; `.xlsx` is authoritative for human review only,
  and is regenerated deterministically (verified byte-identical on repeated regeneration by
  `tests/test_enh01_testmgmt.py::test_workbook_regeneration_is_deterministic_in_content`).
- **`testmgmt/generated/MVP2_Testcases.xlsx`** — one row per real, persisted testcase (10
  rows), columns: Testcase ID, Requirement ID(s), Title, Objective/Expected Result,
  Preconditions, Business Steps, Test Type, Priority, Dataset Reference(s), Automation
  Reference(s), Execution Status (real, rolled up from CP-06 evidence via
  `reporting.gather`), Governance Status. A `Notes` sheet discloses provenance and the
  historical testcase-content limitation explicitly — **the generic placeholder steps are
  shown exactly as persisted, never rewritten** (verified by
  `test_testcase_workbook_never_rewrites_the_disclosed_generic_steps`).
- **`testmgmt/generated/MVP2_TestData.xlsx`** — one row per real field-value across all 25
  real, persisted datasets, plus a **Testcase-Dataset Mapping** sheet demonstrating "one
  testcase → multiple datasets" with real data (`TC-REQ-REG-01-01` → 6 real datasets).
- **`testmgmt/generated/MVP2_Requirement_Testcase_Traceability.xlsx`** — real, persisted
  requirement→testcase coverage (4 requirements: `REQ-ACO-03`, `REQ-CART-03`, `REQ-PAY-01`,
  `REQ-REG-01`).
- **IMPLEMENTED, VERIFIED.**

## Playwright (`automation/playwright/`)

### Architecture

```
automation/playwright/
├── config.py            # centralized, environment-overridable config
├── locators.py           # multi-locator candidate model + governed fallback
├── data_access.py        # dataset loader (reads the frozen testdata/ JSON, never .xlsx)
├── evidence.py            # screenshot/evidence-directory helpers
├── logging_.py            # ExecutionLogRecord model + persistence
├── enh01_testcase.py      # the NEW, explicit testcase (sec. "Testcase Fidelity" below)
├── pages/
│   ├── base_page.py
│   ├── home_page.py
│   └── registration_page.py
├── components/
│   └── navigation.py      # reusable "start at home" entry sequence
├── tests/
│   ├── conftest.py         # real, non-mocked sync_playwright() fixtures
│   └── test_enh01_registration.py
└── generated/
    ├── executions/         # persisted ExecutionLogRecord artifacts
    └── evidence/            # real screenshots
```

**IMPLEMENTED, VERIFIED.** No frozen `automation/schema.py`, `generate.py`, `validate.py`,
`pipeline.py`, `evidence.py`, `persist.py`, or `automation/multi_locator/` file was modified,
imported for write, or otherwise touched.

### Page Object Model

`HomePage` (navigate, select "Register" link) and `RegistrationPage` (fill five real form
fields, submit, read real result text) — **IMPLEMENTED, VERIFIED** against the real SUT.
Broader page coverage (Login, Search, Product, Cart, Checkout, Wishlist, Account pages) is
**DEFERRED** — only the scope actually built and verified is claimed here.

### Reusable components

`components/navigation.py::start_at_home()` — **IMPLEMENTED, VERIFIED** (used by the real
test). Given the bounded scope of this first enhancement (one POM flow), no further
components were extracted yet; this is disclosed as **DEFERRED**, not hidden.

### Multiple evidence-backed locators

Every field on the real registration form has **2–3 real, live-captured candidates** (ID →
LABEL → NAME priority; ID → ROLE for the submit button), documented with their exact real DOM
source in `automation/playwright/locators.py`. **No locator was invented** —
`tests/test_enh01_playwright_foundation.py::test_registration_form_candidates_are_real_evidence_backed_not_invented`
asserts every candidate's `source` field is tagged `"live capture: ..."`.

**IMPLEMENTED, VERIFIED.**

### Runtime locator fallback

A real, working, NEW post-MVP2 fallback mechanism (`locators.py::resolve_with_fallback()`):
tries each real candidate in priority order, records every attempt (success or failure) —
never silent — and flags `used_fallback=True` only when a non-primary candidate resolved. In
this enhancement's real executions, every field's **primary (priority-1)** candidate resolved
on the first try (the real SUT's `id`-based selectors are stable), so `used_fallback=False`
in every persisted execution log — the fallback *mechanism* is real, tested (4 deterministic
unit tests), and wired into the real POM, but a genuine fallback-triggering condition was not
independently observed in this enhancement's own real runs.

**This does not modify CR-002.** CR-002 (`docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`)
remains, unchanged, `PROPOSED — NOT IMPLEMENTED. NOT AUTHORIZED.` — that document is scoped
exclusively to the frozen CP-06 execution engine; this enhancement's fallback is a wholly
separate, new capability in a wholly separate, new code path.

**IMPLEMENTED, VERIFIED (mechanism); fallback-triggering condition NOT independently
observed in real execution.**

### Testcase ↔ automation step fidelity

The historical `TC-REQ-REG-01-01` (frozen MVP2 baseline) carries only the disclosed generic
placeholder steps and was **not modified**. A **new**, explicit, clearly-labeled testcase,
`ENH01-TC-REQ-REG-01-BLANK-VALIDATION` (`automation/playwright/enh01_testcase.py`), was
created instead — grounded directly in REQ-REG-01's own Approved SRS acceptance criterion
("Given all fields blank, when submitted, then all required-field messages show and no
account is created," `requirements/MVP2_SRS_v1.0_APPROVED.md` line 94). This scenario is
deliberately **non-state-mutating** (submitting all-blank fields never creates a real account
on the shared, public, third-party SUT) — consistent with this project's established practice
around DATA-OQ-01 and shared-instance safety, and avoiding repeated real account creation
under parallel execution.

**IMPLEMENTED, VERIFIED.**

### Test data separation

`automation/playwright/data_access.py::load_dataset()` loads strictly by Dataset ID from the
real, frozen `testdata/generated/` JSON corpus, validates required fields are present
(raising, never silently proceeding, if not), and is the **only** way the automation obtains
field values — no dataset is hard-coded in the POM or the test. **IMPLEMENTED, VERIFIED**
(3 deterministic unit tests, plus real use in the live test).

### Execution logging and evidence

Every real execution persists a full `ExecutionLogRecord` (Execution/Requirement/Testcase/
Dataset/Automation IDs, browser + version, environment, worker ID, start/end/duration, full
step results including per-field locator-resolution detail, final status, failure category,
error detail, evidence references) via the shared `persistence/envelope.py`, plus a real
screenshot per execution. **IMPLEMENTED, VERIFIED** — two real, persisted execution logs
(committed) and two real screenshots exist under `automation/playwright/generated/` as of
this report.

**Disclosed, precedent-consistent gitignore finding:** this repository's pre-existing
`.gitignore` "Runtime artifacts" rule (`evidence/`) matches any directory literally named
`evidence` anywhere in the tree, including this enhancement's own
`automation/playwright/generated/evidence/`. Rather than weaken that rule (which already,
deliberately, keeps the frozen CP-06 `execution/evidence.py` output out of git), the same,
established, whole-project convention is followed here: the real screenshots remain real,
on-disk, but **not git-committed**; the committed `ExecutionLogRecord` JSON already carries
their relative paths in `evidence_references`, so the link
"Execution → Automation → Dataset → Testcase → Requirement" (sec. 24 of the governing
instruction) remains fully traceable even though the binary PNG itself is not committed.

### VS Code Windows integration

`.vscode/settings.json` (interpreter path, pytest discovery), `.vscode/tasks.json` (5 tasks:
run Playwright tests, run in parallel, generate workbooks, run full regression, run the
JMeter scenario), `.vscode/launch.json` (2 debug configs). These are committed (a targeted,
justified `.gitignore` negation was required and is disclosed in the Governance section
below) so a QE engineer opening this repository in Windows VS Code has a working setup.

**Disclosure on verification method:** the underlying commands these tasks invoke were
executed for real, directly, via the same `.venv\Scripts\python.exe` / Windows-native JMeter
a VS Code task or terminal would invoke — this is a genuine, real, Windows-native execution.
This session has no capability to drive the VS Code GUI itself (click "Run Task", view the
integrated terminal, etc.), so the literal GUI interaction was not separately captured on
video/screenshot. The underlying execution is identical either way; this is disclosed
honestly rather than claiming a GUI-click verification that did not occur.

**IMPLEMENTED; VERIFIED via the equivalent terminal invocation, not via literal VS Code GUI
interaction (disclosed above).**

### Local parallel execution

`pytest -n 2` against the real registration test: **DEMONSTRATED** — real output:

```
[gw0] [ 50%] PASSED ...test_registration_rejects_all_fields_blank[TD-TC-REQ-REG-01-01-02]
[gw1] [100%] PASSED ...test_registration_rejects_all_fields_blank[TD-TC-REQ-REG-01-01-06]
2 passed in 13.02s
```

Both workers used distinct, real, isolated execution IDs, distinct real datasets, and
produced distinct, correctly-tagged (`worker_id: gw0`/`gw1`) persisted execution logs and
screenshots — real, isolated artifacts, no collision, no shared mutable state.

**DEMONSTRATED.**

### Distributed execution

Local parallel execution (multiple workers, one Windows machine) is explicitly **not** the
same as distributed execution (multiple machines/nodes), per this task's own Rule 5.
`pytest-xdist` does support a `--dist` / remote-worker (`rsync`+SSH) mode for genuine
multi-machine distribution, and `worker_id` is already carried through every execution log —
this is the real, available contract a future distributed configuration would use. No second
machine or browser grid was available in this environment to actually exercise it.

**CONFIGURED (architecture/contract ready — worker-safe IDs, worker-tagged evidence, and
pytest-xdist's own remote-worker support are the real building blocks) — NOT IMPLEMENTED.**

## JMeter (`performance/jmeter/`)

### Architecture

```
performance/jmeter/
├── PERF-REQ-BRW-01-catalog-browse.jmx   # frozen CP-MVP2-08 evidence -- UNTOUCHED
├── fragments/
│   └── common_http_config.jmx            # real Test Fragment (see disclosed finding below)
├── scenarios/
│   └── PERF-REQ-SRCH-01-search.jmx        # NEW scenario, this enhancement
├── data/
│   └── search_terms.csv                    # real, non-secret, externalized test data
└── results/
    ├── enh01_search_results.jtl             # real execution results
    └── enh01_search_jmeter.log
```

**IMPLEMENTED.** The frozen `performance/jmeter/PERF-REQ-BRW-01-catalog-browse.jmx` and every
`performance/*.py` module (`gather.py`, `metrics.py`, `persist.py`, `pipeline.py`,
`schema.py`) are **unmodified** — this enhancement adds new files only.

### New scenario: REQ-SRCH-01 (search)

Traceable to `REQ-SRCH-01` ("Search shall return matching product results for a valid
keyword"). Real, live GET requests (`/search?q=<term>`) using real, non-secret search terms
(`book`, `computer`, `jacket`, matching real REQ-BRW-01 category names) externalized in
`data/search_terms.csv` via `CSVDataSet`, parameterized rather than hard-coded. Bounded
workload: 3 virtual users, 3s ramp-up, 2 loops/user, 1000ms pacing — 6 real requests.

### Disclosed finding: JMeter Config-Element modularity via IncludeController

A real, standard-JMeter **Test Fragment** (`fragments/common_http_config.jmx`, containing
HTTP Request Defaults + Header Manager) was built and wired into the scenario via a core
JMeter `IncludeController`, per the governing instruction's own suggested architecture
(sec. 30). **Real, live execution showed this does not work as expected in this JMeter
version**: the fragment loaded successfully (confirmed in the JMeter log:
`IncludeController: loadIncludedElements — try to load included module:
...common_http_config.jmx`), but its Config Elements did not propagate scope to the sibling
Thread Group's sampler — every real sample failed with a malformed, empty-domain URL
(`http:/search?q=book`, 100% error rate, confirmed via a real run before the fix). This is
disclosed here rather than hidden. **Fix applied**: the scenario now defines its HTTP config
directly (the same, already-proven-reliable pattern verified real in CP-MVP2-08's own
`catalog-browse.jmx`). The Test Fragment file itself remains a real, valid, documented,
reusable artifact for future adoption once this scoping behavior is further investigated (a
GUI-authored fragment, or a different JMeter/plugin version, may behave differently) — it is
**not** currently wired into the executed scenario.

**Config-element cross-file modularity: CONFIGURED (real artifact exists) — NOT SUCCESSFULLY
DEMONSTRATED at runtime (real, disclosed limitation). Test-data modularity (CSV): FULLY
DEMONSTRATED.**

### Real Windows execution

```
Created the tree successfully using scenarios\PERF-REQ-SRCH-01-search.jmx
summary = 6 in 00:00:06 = 1.0/s Avg: 995 Min: 628 Max: 1752 Err: 0 (0.00%)
```

All 6 real samples: `200 OK`, real response assertion (`"Demo Web Shop. Search"`) passed,
real, distinct search terms per request (`q=book`, `q=computer`, `q=jacket`, cycling via the
CSV data set), 0 errors. Evidence: `performance/jmeter/results/enh01_search_results.jtl`,
`enh01_search_jmeter.log`.

**DEMONSTRATED.**

### JMeter distributed execution

JMeter's own controller/engine architecture (`-R` remote-engines flag,
`remote_hosts`/`remote_hosts_RMI` properties) is the real, standard mechanism for this and was
not modified or worked around; no second Windows JMeter engine was available in this
environment to actually exercise it.

**CONFIGURED (standard JMeter distributed-execution mechanism, unmodified, available for
future use) — NOT IMPLEMENTED.**

## Validation

### Focused enhancement tests

- `tests/test_enh01_playwright_foundation.py`: **8/8 passed** (locator-fallback logic,
  data-access layer — deterministic, real-corpus-backed).
- `tests/test_enh01_testmgmt.py`: **7/7 passed** (Excel generation — real-corpus-backed,
  deterministic regeneration verified).
- `automation/playwright/tests/test_enh01_registration.py`: **2/2 passed**, real, live,
  non-mocked, against the real SUT (single-threaded and, separately, under 2-worker parallel
  execution — both runs 2/2 PASS).

### Existing full regression

`tests/` (unchanged, pre-existing suite): **375 passed, 1 skipped** — the 1 skip is the same,
pre-existing, honestly-disclosed CP-08 live-JMeter-execution skip (unset
`JMETER_EXECUTABLE`/`JAVA_HOME` in the *default* environment) carried forward unchanged; 15
new tests (8 + 7 above) added to the 360 pre-existing passed tests. **Zero existing test was
weakened, removed, or altered.**

### Real Playwright

**Executed** (see "Local parallel execution" above): 2/2 real, live browser executions
against `https://demowebshop.tricentis.com/`, from the Windows-native `.venv\Scripts\python.exe`.

### Real JMeter

**Executed** (see "Real Windows execution" above): 6/6 real HTTP samples, 0 errors, against
the real SUT, from the Windows-native `jmeter.bat`.

**No mock was used for any claimed execution result, in either framework.**

## Governance

### Baseline integrity

`git diff --stat 33b9946 -- <every frozen MVP1/MVP2 path: Approved SRS; CP01-09
specifications; CP06/07/08/09 governance-closure and reconciliation reports; MVP2-FINAL
closure; CR-002 proposal; testcases/, testdata/, rbtp/, dependencies/, traceability/; frozen
automation/*.py + automation/multi_locator/; execution/; rca/; performance/*.py and the
frozen catalog-browse.jmx; reporting/>` is **empty** — re-verified immediately before this
report. **Zero unauthorized frozen-artifact drift.**

### CR-002 status

**OPEN — NOT AUTHORIZED**, unchanged, re-verified this task. Not modified. Not implemented as
though authorized anywhere in this enhancement — the new, separate fallback mechanism built
here (`automation/playwright/locators.py`) is its own, independently-governed, clearly-labeled
capability, never presented as CR-002 implementation.

### `.gitignore` changes (disclosed, justified)

Two targeted, justified negations were added (never a blanket weakening):

1. `!performance/jmeter/results/**/*.jtl` — mirrors the existing, precedented CP-MVP2-08
   negation, for this enhancement's own new, real JMeter result evidence.
2. `.vscode/*` (replacing the bare `.vscode/` directory-level ignore, which git cannot
   selectively un-ignore files within) plus `!.vscode/settings.json`,
   `!.vscode/tasks.json`, `!.vscode/launch.json` — required because VS Code Windows
   integration is an explicit, named deliverable of this enhancement (governing instruction
   sec. 22/38). Only these three shared, project-level files are un-ignored; any other
   machine-specific VS Code state remains ignored exactly as before.

### Deferred items (not implemented, honestly disclosed, not disguised as defects)

- Broader Page Object coverage (Login/Search/Product/Cart/Checkout/Wishlist/Account pages).
- Further reusable component extraction beyond `navigation.py`.
- JMeter Config-Element modularity via cross-file inclusion (real limitation found and
  disclosed above; CSV data modularity fully works).
- True multi-machine distributed execution, for both Playwright and JMeter (architecture/
  contract documented and CONFIGURED; not demonstrated, no second machine available).
- A positive (successful-registration) Playwright flow was deliberately not automated as a
  repeatable/parallel real execution, to avoid creating duplicate real accounts on the
  shared, public, third-party SUT; the safe, non-mutating, SRS-grounded blank-validation
  scenario was used instead.
