# CP-MVP2-08 — Advisory Closure & Pre-CP09 Reconciliation

Timestamp (UTC): 2026-09-15T10:11:13Z

This report is the authoritative closure of CP-MVP2-08's advisory state. It does not modify,
and should be read alongside, the original historical execution report:
`docs/claude-execution-reports/CP-MVP2-08/CP-MVP2-08-EXECUTION-REPORT-20260915-093624.md`
(left unchanged, per this task's own instruction not to rewrite history).

## 1. CP-08 Baseline Commit

`77c7d642e3b58bd5f6f95abeb93b5f25143ce92f`

## 2. Current HEAD (at start of this task)

`77c7d642e3b58bd5f6f95abeb93b5f25143ce92f` (unchanged — no commits made between CP-08's
original closure and the start of this reconciliation pass).

## 3–5. Advisories, Classification, and Action Taken

### Advisory 1 — No approved numeric performance threshold (SRS §9.2)

**Classification: HUMAN DECISION REQUIRED.**

**Action taken:** None to the SRS or the CP08 acceptance-criteria model — none is permitted.
Formally reconciled, per this task's own §4, as:

> **ACCEPTED AS STANDING HUMAN/PROJECT DECISION — NOT A CP08 BLOCKER.**

The existing governance mechanism already records this correctly and is reused, not
duplicated: `requirements/MVP2_SRS_v1.0_APPROVED.md` §9.2 (numeric thresholds table, all rows
`TBD — HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL`) and §13 (open-item row "NFR
thresholds (§9.2)... flagged for CP-MVP2-08"), and `docs/CP-MVP2-08-SPECIFICATION-v1.0.md`
§8.2 (the frozen, two-dimension acceptance-criteria model that keeps this INCONCLUSIVE,
never a fabricated PASS/FAIL). No new or duplicate governance document was created.

**Verification:** `requirements/MVP2_SRS_v1.0_APPROVED.md` and
`docs/CP-MVP2-08-SPECIFICATION-v1.0.md` (SHA-256
`048be6dfca0da9bf899ff582a7539686100a6efa48bc6989e7747ee619a5fa69`) are both byte-identical to
their state at CP-08's original closure (`git diff --stat HEAD` empty for both, sec. 9 below).
The CP-08 result remains honestly `INCONCLUSIVE` for this dimension — never converted to
`PASS`.

### Advisory 2 — Bounded, single-category, GET-only scenario

**Classification: ACCEPTED MVP SCOPE BOUNDARY.**

**Action taken:** None — the workload (5 users, 5s ramp-up, 3 loops/user, 1000ms pacing, `GET
/` + `GET /books`, 30 requests total) is unchanged, per this task's own explicit instruction
not to expand it merely to remove the advisory label. `docs/CP-MVP2-08-SPECIFICATION-v1.0.md`
§4 already documents the rationale in full (shared, public, third-party instance; no
published SLA; unresolved data-reset/isolation policy DATA-OQ-01; task's own prohibition on
creating duplicate business entities merely to increase load). No new reconciliation artifact
was needed beyond this entry, since the existing spec/report rationale is already complete
and was re-verified as still accurate.

### Advisory 3 — JMeter/JRE are external, unvendored dependencies

**Classification: ACCEPTED MVP RUNTIME DEPENDENCY** (documentation gap closed by this report).

**Action taken:** No vendoring. The existing execution report already discloses the general
approach and versions (JMeter 5.6.3, Temurin JRE 17) but did not give a precise,
copy-pasteable acquisition/configuration recipe. That gap is closed here, as the minimum
documentation necessary to make the existing external-dependency contract explicit and
reproducible on either platform this project uses:

- **JMeter:** `https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz` (official
  Apache CDN; the same archive contains both the Unix `bin/jmeter` and Windows `bin/jmeter.bat`
  launchers — no separate Windows download is needed for JMeter itself). Extract anywhere.
- **Java:** a Java 17 (or later-compatible) JRE/JDK. This session used Eclipse Temurin 17 from
  the official Adoptium API, per-platform:
  `https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jre/hotspot/normal/eclipse` (WSL/
  Linux) and `https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse`
  (Windows). Extract anywhere.
- **Wiring:** set `JAVA_HOME` to the extracted JRE/JDK root, and `JMETER_EXECUTABLE` to the
  full path of the platform-appropriate launcher (`bin/jmeter` on Unix, `bin\jmeter.bat` on
  Windows) before invoking `performance.pipeline.run_cp08_performance_scenario()` or the
  pytest suite. Neither variable is read from, nor written to, any file committed to this
  repository — this is a genuine, standard, per-environment external-tool contract, exactly
  like this project's existing, already-accepted Playwright-browser dependency (`playwright
  install`), not a new pattern.

This is the same, intentional, avoid-vendoring stance the project already applies elsewhere;
nothing further is required.

### Advisory 4 — Reproducibility bounded by the shared SUT's own state/load

**Classification: ACCEPTED MVP SCOPE BOUNDARY.**

**Action taken:** None — this is a property of the real, third-party SUT (Approved SRS §11:
no SLA, no exclusive ownership), not an implementation gap. Already correctly disclosed in
the frozen spec and the historical report's own `reproducibility_note` field, reproduced
verbatim in every persisted `PerformanceRunRecord` (sec. 6/7 below).

### Advisory 5 — Windows regression skip (`test_pipeline_real_live_execution_end_to_end`)

**Classification: was investigated per this task's §7; found ACTIONABLE AND CLOSABLE NOW —
CLOSED**, via a genuine, root-caused code fix (not a mock, not a machine-specific hack).

**Investigation:** Attempted a real, non-mocked Windows-native JMeter execution by downloading
a Windows x64 Temurin 17 JRE (`https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse`)
alongside the already-downloaded JMeter 5.6.3 distribution (which ships both Unix and Windows
launchers in one archive), placed at a local, non-repo path, and invoking the real CP-08
pipeline via `.venv\Scripts\python.exe` with `JAVA_HOME`/`JMETER_BIN` set.

**Real defect found:** Apache JMeter's own Windows launcher, `jmeter.bat`, defines and
internally relies on an environment variable literally named `JMETER_BIN` to mean "the JMeter
bin/ directory" (must end in a path separator) — see
`apache-jmeter-5.6.3/bin/jmeter.bat` lines 28, 137-138, 200. This project's
`performance/pipeline.py` had independently chosen the same variable name, `JMETER_BIN`, to
mean something different (the full path to the jmeter executable itself). On Windows the two
collide: JMeter's own script reads the pipeline's value, misinterprets it as a directory, and
constructs a corrupted jar path
(`...\bin\jmeter.batApacheJMeter.jar`), failing with `Error: Unable to access jarfile ...`.
This collision does not occur on Unix (`bin/jmeter`, the shell launcher, defines no internal
variable of that name) — which is exactly why the original WSL/Linux-side live execution
(CP-08's original closure) worked cleanly while a genuine Windows attempt, had one been made
at that time, would have failed outright (not merely skipped).

**Fix:** renamed the pipeline's environment variable from `JMETER_BIN` to
`JMETER_EXECUTABLE` throughout `performance/pipeline.py` and `tests/test_cp08_performance.py`
(the frozen CP-08 specification itself never referenced the name `JMETER_BIN` — grep-verified
— so no frozen artifact required any change). Also hardened `_resolve_java_bin()` to check for
both `java` and `java.exe` under `JAVA_HOME/bin`, for correctness on both platforms.

**Result — this is a real, live, non-mocked pass, not a fabrication:**

With `JAVA_HOME`/`JMETER_EXECUTABLE` configured to point at a real, independently-downloaded,
Windows-native JMeter 5.6.3 + Temurin 17 JRE (outside this repository), run via
`.venv\Scripts\python.exe`:

```
===== CP08 FOCUSED =====
15 passed in 25.50s
===== FULL REGRESSION =====
346 passed in 27.25s
```

`test_pipeline_real_live_execution_end_to_end` genuinely executed a real, live, 30-request
JMeter run against the real SUT, natively on Windows, and asserted a real `PASS`/`INCONCLUSIVE`
disposition — captured as new, additional, clearly-labeled evidence:
`performance/generated/records/PERF-RUN-CP08-WINDOWS-VERIFICATION/` and
`performance/generated/raw/PERF-RUN-CP08-WINDOWS-VERIFICATION/results.jtl` (30 samples, 0
errors, avg 571.633ms, median 482ms, p90 948ms, max 1423ms, throughput 1.754 req/s —
genuinely different numbers from the original `PERF-RUN-CP08-PRIMARY` evidence, exactly as
expected for two independent real runs against a live, shared, third-party instance; see
sec. 8 for the explicit distinction).

**Without** those two environment variables configured (this repository's normal, out-of-the-
box regression state — nothing was made to rely on them by default), the identical suite
correctly and honestly reverts to:

```
14 passed, 1 skipped in 0.09s   (focused)
345 passed, 1 skipped in 2.43s  (full regression)
```

Both states were verified in this session (sec. 10). The skip is not eliminated from the
*default* environment — that remains correct, since JMeter/Java remain genuinely external,
unvendored, per-environment dependencies (Advisory 3) — but the underlying implementation
defect that would have blocked a real pass even on a *properly configured* Windows machine is
now fixed. No result was invented, mocked, or forced; the skip condition itself
(`JMETER_EXECUTABLE`/`JAVA_HOME` unset) is unchanged and still governs honestly.

## 6. Evidence Integrity

The original CP-08 evidence, exactly as committed at `77c7d64`, was re-verified unchanged in
this task (`git diff --stat HEAD` empty for `performance/generated/raw/PERF-RUN-CP08-PRIMARY`,
`performance/generated/records/PERF-RUN-CP08-PRIMARY`, and `performance/jmeter/`):

| Metric | Committed value (`PERF-RUN-CP08-PRIMARY`) |
|---|---|
| Samples | 30 |
| Errors | 0 |
| Avg (ms) | 595.4 |
| Median (ms) | 503.0 |
| p90 (ms) | 985.0 |
| Max (ms) | 1465.0 |
| Throughput (req/s) | 1.742 |

**Note on a discrepancy discovered during this task's inspection (§2):** the *historical*
execution report's own §10 prose table cites different figures (614.867 / 518 / 1015 / 1426 /
1.737 ms/req-s). Investigation (re-parsing the actual committed `results.jtl` with
`performance.metrics.compute_aggregate_metrics`, which reproduces the 595.4/503/985/1465/1.742
figures exactly, confirming internal self-consistency between the committed raw `.jtl` and the
committed `PerformanceRunRecord`) established the cause: between drafting that report's prose
and the final commit, the primary evidence had to be regenerated once more (a second, still
fully real, live execution) to fix the `.gitignore` packaging defect discovered and resolved
within the same original CP-08 task (see that task's own commit message, "defect 3"). The
report's prose table was written against the *first* real run's numbers and was not updated to
reflect the *second* real run's numbers that were actually committed. Both runs are genuinely
real, live, 30/30-sample, 0-error executions — this is a documentation/evidence cross-
reference inconsistency, not fabricated or altered evidence, and not a case of "regenerating
measurements to make them look better" (the historical report's numbers and the actually-
committed numbers are of comparable magnitude, neither more favorable than the other). Per
this task's own §13 ("do not change the historical CP08 execution report merely to rewrite
history"), that report is left as-is; **this report's table above is the authoritative,
git-verified figure set going forward.**

The new Windows-verification run (`PERF-RUN-CP08-WINDOWS-VERIFICATION`) is explicitly a
separate, additional, cross-platform verification artifact — never a replacement for, and
clearly distinct in its `run_id` from, the original `PERF-RUN-CP08-PRIMARY` evidence, per this
task's own §8.

## 7. Items Explicitly Requiring Human/Project Decision

- **Numeric performance thresholds** (Approved SRS §9.2 / §13) — response-time, throughput,
  error-rate, baseline-load, concurrency, and availability targets. This is the sole remaining
  open item after this reconciliation pass, and it is explicitly a Human/Project Target
  decision, not a CP-08 implementation defect (sec. 3, Advisory 1).

## 8. Regression Results

- **Default environment (no `JMETER_EXECUTABLE`/`JAVA_HOME` configured — this repository's
  normal state):** CP-08 focused 14/15 passed, 1 honestly skipped; full regression 345/346
  passed, 1 skipped.
- **With a real, independently-configured JMeter 5.6.3 + Java 17 (verifying the fix in sec. 5
  — not this repository's default state, and nothing was changed to make it the default):**
  CP-08 focused **15/15 passed**; full regression **346/346 passed**. Zero tests weakened,
  removed, or altered to obtain this result — the same test file, unmodified in assertion
  content, simply stopped skipping once its own documented prerequisite was genuinely met.

## 9. Frozen-Artifact Integrity

`git diff --stat HEAD` against the full CP-01–08 specification/implementation set, all
CP-06/07/08 governance-closure and execution reports, and the Approved SRS is **empty** — zero
drift. Re-verified at the start and end of this task.

## 10. Final CP-08 Advisory Status

| # | Advisory | Classification | Status |
|---|---|---|---|
| 1 | No approved numeric performance threshold | HUMAN DECISION REQUIRED | Open (correctly, permanently, by design) |
| 2 | Bounded, single-category, GET-only scenario | ACCEPTED MVP SCOPE BOUNDARY | Accepted, no action |
| 3 | JMeter/JRE external, unvendored dependencies | ACCEPTED MVP RUNTIME DEPENDENCY | Accepted; documentation gap CLOSED (sec. 3) |
| 4 | Reproducibility bounded by shared SUT state | ACCEPTED MVP SCOPE BOUNDARY | Accepted, no action |
| 5 | Windows regression skip | Investigated — was ACTIONABLE | **CLOSED** (sec. 5) |

**CP08 implementation debt = ZERO.**

**Human/Project target decision = OPEN** (numeric NFR thresholds, Advisory 1).

**CP08 = CLOSED.**

**GREEN WITH ADVISORIES — CLOSED; ZERO ACTIONABLE CP08 DEBT.**

## 11. CP-09 Readiness

- CP-08 has **zero** actionable implementation debt remaining.
- **One** Human/Project decision remains genuinely open (numeric NFR thresholds) — by design,
  not a defect, and it does not block CP-08's own closure.
- **No** blocker remains.
- **CP-09 is authorized to begin** (in a future, separate task — not started by this one, per
  this task's own explicit instruction).
