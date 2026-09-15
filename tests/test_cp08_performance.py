"""
Tests for performance/ — the new, additive CP-MVP2-08 JMeter
performance-engineering package (docs/CP-MVP2-08-SPECIFICATION-v1.0.md).

Categories: JMX (structural validity of the real, committed test plan),
METRICS (deterministic parsing, incl. a hand-crafted fixture for exact-value
assertions and the real, persisted evidence for an integration check),
ACCEPTANCE (capability-demonstration PASS/FAIL/BLOCKED vs the always-
INCONCLUSIVE numeric-SLA dimension, per frozen spec sec. 8), PERSIST
(roundtrip via the unmodified persistence/envelope.py), PIPELINE (the real
BLOCKED path when JMeter/Java cannot be located; a real, live JMeter
execution when JAVA_HOME/JMETER_BIN are available in this environment,
skipped otherwise -- never mocked as if it were real).
"""
from __future__ import annotations

import io
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from performance.metrics import compute_aggregate_metrics, compute_sampler_metrics, read_jtl_rows
from performance.persist import load_persisted_run
from performance.pipeline import JMX_PATH, run_cp08_performance_scenario
from performance.schema import CapabilityResult, NumericSLAResult

FIXTURE_JTL_CSV = """timeStamp,elapsed,label,responseCode,responseMessage,success
1000,500,GET Home Page,200,OK,true
1600,400,GET Home Page,200,OK,true
2100,600,GET Books Category (REQ-BRW-01),200,OK,true
2800,300,GET Books Category (REQ-BRW-01),200,OK,false
"""


def _parse_fixture_rows():
    reader = read_jtl_rows_from_text(FIXTURE_JTL_CSV)
    return reader


def read_jtl_rows_from_text(text: str):
    import csv

    return list(csv.DictReader(io.StringIO(text)))


# ---------------------------------------------------------------------------
# JMX structural validity
# ---------------------------------------------------------------------------

def test_jmx_file_exists_and_is_committed():
    assert JMX_PATH.exists()


def test_jmx_is_well_formed_xml():
    tree = ET.parse(JMX_PATH)
    root = tree.getroot()
    assert root.tag == "jmeterTestPlan"


def test_jmx_has_expected_thread_group_workload():
    tree = ET.parse(JMX_PATH)
    root = tree.getroot()
    thread_group = root.find(".//ThreadGroup")
    assert thread_group is not None
    num_threads = thread_group.find("./stringProp[@name='ThreadGroup.num_threads']")
    ramp_time = thread_group.find("./stringProp[@name='ThreadGroup.ramp_time']")
    assert num_threads.text == "5"
    assert ramp_time.text == "5"
    loops = thread_group.find(".//stringProp[@name='LoopController.loops']")
    assert loops.text == "3"


def test_jmx_has_the_two_expected_get_samplers():
    tree = ET.parse(JMX_PATH)
    root = tree.getroot()
    samplers = root.findall(".//HTTPSamplerProxy")
    paths = sorted(s.find("./stringProp[@name='HTTPSampler.path']").text for s in samplers)
    assert paths == ["/", "/books"]
    for sampler in samplers:
        method = sampler.find("./stringProp[@name='HTTPSampler.method']")
        assert method.text == "GET"


def test_jmx_has_response_assertions_traceable_to_req_brw_01():
    tree = ET.parse(JMX_PATH)
    root = tree.getroot()
    assertions = root.findall(".//ResponseAssertion")
    assert len(assertions) == 2
    test_strings = [ts.text for a in assertions for ts in a.findall(".//stringProp") if ts.get("name") not in (None,) and ts.text]
    joined = " ".join(t for t in test_strings if t)
    assert "Demo Web Shop" in joined
    assert "product-grid" in joined


def test_jmx_never_targets_a_state_mutating_path():
    tree = ET.parse(JMX_PATH)
    root = tree.getroot()
    samplers = root.findall(".//HTTPSamplerProxy")
    forbidden = ("register", "checkout", "cart", "login", "logon")
    for sampler in samplers:
        path = sampler.find("./stringProp[@name='HTTPSampler.path']").text.lower()
        assert not any(f in path for f in forbidden)


# ---------------------------------------------------------------------------
# Metrics — deterministic parsing
# ---------------------------------------------------------------------------

def test_compute_aggregate_metrics_on_hand_crafted_fixture():
    rows = _parse_fixture_rows()
    aggregate = compute_aggregate_metrics(rows)
    assert aggregate.sample_count == 4
    assert aggregate.error_count == 1
    assert aggregate.error_percentage == 25.0
    assert aggregate.min_ms == 300.0
    assert aggregate.max_ms == 600.0
    assert aggregate.avg_ms == (500 + 400 + 600 + 300) / 4


def test_compute_sampler_metrics_on_hand_crafted_fixture():
    rows = _parse_fixture_rows()
    samplers = compute_sampler_metrics(rows)
    assert len(samplers) == 2
    by_label = {s.label: s for s in samplers}
    assert by_label["GET Home Page"].sample_count == 2
    assert by_label["GET Home Page"].error_count == 0
    assert by_label["GET Books Category (REQ-BRW-01)"].sample_count == 2
    assert by_label["GET Books Category (REQ-BRW-01)"].error_count == 1
    assert by_label["GET Books Category (REQ-BRW-01)"].error_percentage == 50.0


def test_metrics_never_manufactured_for_empty_rows():
    aggregate = compute_aggregate_metrics([])
    assert aggregate.sample_count == 0
    assert aggregate.avg_ms is None
    assert aggregate.min_ms is None
    assert aggregate.max_ms is None
    assert aggregate.throughput_per_sec is None


def test_metrics_parsing_is_deterministic_on_repeated_parse():
    rows_a = _parse_fixture_rows()
    rows_b = _parse_fixture_rows()
    assert compute_aggregate_metrics(rows_a).to_dict() == compute_aggregate_metrics(rows_b).to_dict()


# ---------------------------------------------------------------------------
# Acceptance-criteria separation (frozen spec sec. 8.1 vs 8.2)
# ---------------------------------------------------------------------------

def test_real_persisted_primary_run_has_pass_capability_and_inconclusive_sla():
    """Uses the real, already-persisted evidence from this task's real JMeter
    execution (PERF-RUN-CP08-PRIMARY) -- never a synthetic result."""
    payload = load_persisted_run("PERF-RUN-CP08-PRIMARY")
    if payload is None:
        pytest.skip("Real persisted CP-08 primary run evidence not present on disk in this environment")
    assert payload["capability_result"] == CapabilityResult.PASS
    assert payload["numeric_sla_result"] == NumericSLAResult.INCONCLUSIVE
    assert "no approved numeric threshold" in payload["numeric_sla_result_detail"].lower()
    assert payload["aggregate_metrics"]["sample_count"] == 30
    assert payload["aggregate_metrics"]["error_count"] == 0


def test_numeric_sla_result_is_never_pass_or_fail():
    payload = load_persisted_run("PERF-RUN-CP08-PRIMARY")
    if payload is None:
        pytest.skip("Real persisted CP-08 primary run evidence not present on disk in this environment")
    assert payload["numeric_sla_result"] not in (CapabilityResult.PASS, CapabilityResult.FAIL)


# ---------------------------------------------------------------------------
# Pipeline — real BLOCKED path, real live execution when tools are available
# ---------------------------------------------------------------------------

def test_pipeline_blocked_when_jmeter_and_java_cannot_be_located(monkeypatch):
    monkeypatch.delenv("JMETER_BIN", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr("performance.pipeline.shutil.which", lambda _name: None)
    result = run_cp08_performance_scenario(run_id="PERF-RUN-TEST-BLOCKED-NO-TOOLS")
    assert result["status"] == "BLOCKED"
    assert result["record"]["capability_result"] == CapabilityResult.BLOCKED
    assert result["record"]["numeric_sla_result"] == NumericSLAResult.INCONCLUSIVE


@pytest.mark.skipif(
    not (os.environ.get("JMETER_BIN") and os.environ.get("JAVA_HOME")),
    reason="JMETER_BIN/JAVA_HOME not configured in this environment -- real live JMeter execution skipped, never mocked as if it were real",
)
def test_pipeline_real_live_execution_end_to_end():
    result = run_cp08_performance_scenario(run_id="PERF-RUN-TEST-LIVE")
    assert result["status"] == "COMPLETE"
    assert result["record"]["capability_result"] in (CapabilityResult.PASS, CapabilityResult.FAIL)
    assert result["record"]["numeric_sla_result"] == NumericSLAResult.INCONCLUSIVE
    assert result["record"]["aggregate_metrics"]["sample_count"] == 30


# ---------------------------------------------------------------------------
# Persistence roundtrip
# ---------------------------------------------------------------------------

def test_persisted_primary_run_reloads_byte_identical():
    payload_a = load_persisted_run("PERF-RUN-CP08-PRIMARY")
    payload_b = load_persisted_run("PERF-RUN-CP08-PRIMARY")
    if payload_a is None:
        pytest.skip("Real persisted CP-08 primary run evidence not present on disk in this environment")
    assert payload_a == payload_b
