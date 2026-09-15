"""
CP-MVP2-08 — real JMeter execution pipeline.

Orchestrates: locate a real JMeter + Java installation (via the
`JMETER_EXECUTABLE` and `JAVA_HOME` environment variables; neither tool is
bundled in this repository -- an external, independently-obtainable
dependency, per frozen spec sec. 5/10, exactly like this project's existing,
unbundled Playwright browser dependency) -> execute the real, committed
`.jmx` test plan in non-GUI mode against the real SUT -> parse the real, raw
`.jtl` results -> evaluate the two, separate acceptance-criteria dimensions
(frozen spec sec. 8.1 capability-demonstration, sec. 8.2 numeric-SLA) ->
persist.

Note: this pipeline deliberately does NOT use the environment variable name
`JMETER_BIN`, even though that is a natural-sounding choice. Apache JMeter's
own Windows launcher (`jmeter.bat`) defines and internally relies on an
environment variable of that exact name to mean "the JMeter bin/ directory"
(must end in a path separator) -- a real, discovered collision that silently
corrupted the constructed jar path on Windows when this pipeline used the
same name for a different purpose (the path to the jmeter executable
itself). `JMETER_EXECUTABLE` avoids the collision entirely.

Never fabricates a result: if JMeter/Java cannot be located, or the real
subprocess fails to produce a results file, the disposition is BLOCKED, not
a manufactured PASS (frozen spec sec. 9).
"""
from __future__ import annotations

import datetime
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from performance.metrics import compute_aggregate_metrics, compute_sampler_metrics, read_jtl_rows
from performance.persist import persist_run
from performance.schema import (
    CapabilityResult,
    NumericSLAResult,
    PerformanceEnvironment,
    PerformanceRunRecord,
    WorkloadModel,
)
from persistence.envelope import REPO_ROOT

JMX_PATH = REPO_ROOT / "performance" / "jmeter" / "PERF-REQ-BRW-01-catalog-browse.jmx"
SCENARIO_ID = "PERF-REQ-BRW-01-CATALOG-BROWSE"
REQUIREMENT_IDS = ["REQ-BRW-01"]
TARGET_URL = "https://demowebshop.tricentis.com/"

RAW_EVIDENCE_ROOT = REPO_ROOT / "performance" / "generated" / "raw"

WORKLOAD = WorkloadModel(virtual_users=5, ramp_up_seconds=5, loops_per_user=3, think_time_ms=1000)

NUMERIC_SLA_REASON = (
    "No approved numeric threshold exists to compare against (Approved MVP2 SRS v1.0 sec. "
    "9.2: response-time/throughput/error-rate/baseline-load/concurrency/availability targets "
    "are all TBD -- HUMAN/PROJECT TARGET REQUIRING EXPLICIT APPROVAL). This is a standing, "
    "pre-existing, already-disclosed open item (SRS sec. 13), not a new blocking discovery "
    "made by this checkpoint. INCONCLUSIVE is the honest disposition; it is never converted "
    "into PASS merely because the measured numbers look reasonable."
)

_VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")


def _resolve_java_bin() -> Optional[str]:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        for name in ("java", "java.exe"):
            candidate = Path(java_home) / "bin" / name
            if candidate.exists():
                return str(candidate)
    return shutil.which("java")


def _resolve_jmeter_bin() -> Optional[str]:
    explicit = os.environ.get("JMETER_EXECUTABLE")
    if explicit and Path(explicit).exists():
        return explicit
    return shutil.which("jmeter")


def _java_version(java_bin: str) -> str:
    try:
        proc = subprocess.run([java_bin, "-version"], capture_output=True, text=True, timeout=30)
        text = proc.stderr or proc.stdout
        match = _VERSION_RE.search(text)
        return match.group(0) if match else text.splitlines()[0].strip() if text else "unknown"
    except Exception as exc:
        return f"unknown (java -version failed: {exc})"


def _jmeter_version(jmeter_bin: str) -> str:
    try:
        proc = subprocess.run([jmeter_bin, "--version"], capture_output=True, text=True, timeout=60)
        text = proc.stdout or proc.stderr
        match = _VERSION_RE.search(text)
        return match.group(0) if match else "unknown"
    except Exception as exc:
        return f"unknown (jmeter --version failed: {exc})"


def run_cp08_performance_scenario(run_id: Optional[str] = None) -> Dict:
    """Runs the real, committed CP-08 JMeter test plan against the real SUT
    and returns a persisted PerformanceRunRecord. Returns a real BLOCKED
    disposition -- never a fabricated PASS -- if JMeter/Java cannot be
    located or the plan does not produce a results file."""
    now = datetime.datetime.now(datetime.timezone.utc)
    run_id = run_id or f"PERF-RUN-{now.strftime('%Y%m%dT%H%M%SZ')}"

    java_bin = _resolve_java_bin()
    jmeter_bin = _resolve_jmeter_bin()

    if not java_bin or not jmeter_bin:
        record = PerformanceRunRecord(
            run_id=run_id,
            scenario_id=SCENARIO_ID,
            requirement_ids=REQUIREMENT_IDS,
            jmx_path=_relative(JMX_PATH),
            raw_results_path=None,
            environment={"error": "JAVA_HOME/java or JMETER_EXECUTABLE/jmeter could not be resolved"},
            aggregate_metrics=None,
            capability_result=CapabilityResult.BLOCKED,
            capability_result_detail="No usable Java and/or JMeter installation could be located via JAVA_HOME/JMETER_EXECUTABLE or PATH. Per frozen spec sec. 9, this is reported as BLOCKED, never fabricated as PASS.",
            numeric_sla_result=NumericSLAResult.INCONCLUSIVE,
            numeric_sla_result_detail=NUMERIC_SLA_REASON,
            generation_metadata={"generator": "performance.pipeline.run_cp08_performance_scenario"},
        )
        persist_result = persist_run(record)
        return {"status": "BLOCKED", "record": record.to_dict(), "persisted": persist_result}

    run_dir = RAW_EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jtl_path = run_dir / "results.jtl"
    log_path = run_dir / "jmeter_run.log"
    # JMeter's -l flag APPENDS to an existing results file rather than
    # truncating it; without removing any stale file first, a re-run under
    # the same run_id would silently double-count samples.
    jtl_path.unlink(missing_ok=True)
    log_path.unlink(missing_ok=True)

    try:
        subprocess.run(
            [jmeter_bin, "-n", "-t", str(JMX_PATH), "-l", str(jtl_path), "-j", str(log_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except Exception as exc:
        record = PerformanceRunRecord(
            run_id=run_id,
            scenario_id=SCENARIO_ID,
            requirement_ids=REQUIREMENT_IDS,
            jmx_path=_relative(JMX_PATH),
            raw_results_path=None,
            environment={"error": f"JMeter subprocess failed to run: {exc}"},
            aggregate_metrics=None,
            capability_result=CapabilityResult.BLOCKED,
            capability_result_detail=f"The real JMeter subprocess invocation failed: {exc}",
            numeric_sla_result=NumericSLAResult.INCONCLUSIVE,
            numeric_sla_result_detail=NUMERIC_SLA_REASON,
            generation_metadata={"generator": "performance.pipeline.run_cp08_performance_scenario"},
        )
        persist_result = persist_run(record)
        return {"status": "BLOCKED", "record": record.to_dict(), "persisted": persist_result}

    if not jtl_path.exists():
        record = PerformanceRunRecord(
            run_id=run_id,
            scenario_id=SCENARIO_ID,
            requirement_ids=REQUIREMENT_IDS,
            jmx_path=_relative(JMX_PATH),
            raw_results_path=None,
            environment={"error": "JMeter ran but produced no results.jtl file"},
            aggregate_metrics=None,
            capability_result=CapabilityResult.BLOCKED,
            capability_result_detail="JMeter's subprocess exited without producing a results.jtl file -- see the persisted jmeter_run.log for detail.",
            numeric_sla_result=NumericSLAResult.INCONCLUSIVE,
            numeric_sla_result_detail=NUMERIC_SLA_REASON,
            generation_metadata={"generator": "performance.pipeline.run_cp08_performance_scenario"},
        )
        persist_result = persist_run(record)
        return {"status": "BLOCKED", "record": record.to_dict(), "persisted": persist_result}

    rows = read_jtl_rows(jtl_path)
    aggregate = compute_aggregate_metrics(rows)
    samplers = compute_sampler_metrics(rows)

    environment = PerformanceEnvironment(
        operating_system=_os_description(),
        jmeter_version=_jmeter_version(jmeter_bin),
        java_version=_java_version(java_bin),
        target_url=TARGET_URL,
        execution_timestamp=now.isoformat(),
        workload=WORKLOAD,
        reproducibility_note=(
            "Reproducibility is bounded by the real, shared, third-party SUT's own state/load "
            "at execution time (Approved SRS sec. 11 -- no SLA, no exclusive ownership) and by "
            "JMeter/Java being external, versioned dependencies not vendored in this repository."
        ),
    )

    if rows and aggregate.error_percentage == 0.0:
        capability_result = CapabilityResult.PASS
        capability_result_detail = (
            f"All {aggregate.sample_count} real HTTP samples completed with 0 assertion/HTTP "
            "failures; the .jmx test plan is confirmed real, valid, and executable."
        )
    elif rows:
        capability_result = CapabilityResult.FAIL
        capability_result_detail = (
            f"{aggregate.error_count}/{aggregate.sample_count} real samples failed "
            f"({aggregate.error_percentage}% error rate) -- reported honestly, not excluded."
        )
    else:
        capability_result = CapabilityResult.BLOCKED
        capability_result_detail = "results.jtl was produced but contained zero rows."

    record = PerformanceRunRecord(
        run_id=run_id,
        scenario_id=SCENARIO_ID,
        requirement_ids=REQUIREMENT_IDS,
        jmx_path=_relative(JMX_PATH),
        raw_results_path=_relative(jtl_path),
        environment=environment.to_dict(),
        aggregate_metrics=aggregate.to_dict(),
        sampler_metrics=[s.to_dict() for s in samplers],
        capability_result=capability_result,
        capability_result_detail=capability_result_detail,
        numeric_sla_result=NumericSLAResult.INCONCLUSIVE,
        numeric_sla_result_detail=NUMERIC_SLA_REASON,
        generation_metadata={"generator": "performance.pipeline.run_cp08_performance_scenario"},
    )
    persist_result = persist_run(record)
    return {"status": "COMPLETE", "record": record.to_dict(), "persisted": persist_result}


def _os_description() -> str:
    import platform

    return f"{platform.system()} {platform.release()} ({platform.machine()})"


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
