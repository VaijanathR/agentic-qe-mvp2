"""
CP-MVP2-08 — JMeter performance-engineering schema.

`CapabilityResult` is a genuine PASS/FAIL/BLOCKED/NOT_EXECUTED disposition (frozen spec
sec. 8.1). `NumericSLAResult` is deliberately a single-value vocabulary
(`INCONCLUSIVE`) — Approved MVP2 SRS v1.0 sec. 9.2 approves no numeric threshold
for response time, throughput, error rate, baseline load, concurrency, or
availability, so no PASS/FAIL against such a threshold can ever be produced by
this checkpoint (frozen spec sec. 8.2). The two results are structurally
separate fields on `PerformanceRunRecord` — never merged into one "result" field
that could accidentally read as if a numeric SLA had been evaluated.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


class CapabilityResult:
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


ALL_CAPABILITY_RESULTS = {
    CapabilityResult.PASS,
    CapabilityResult.FAIL,
    CapabilityResult.BLOCKED,
    CapabilityResult.NOT_EXECUTED,
}


class NumericSLAResult:
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class SamplerMetrics:
    label: str
    sample_count: int
    error_count: int
    error_percentage: float
    avg_ms: Optional[float]
    median_ms: Optional[float]
    p90_ms: Optional[float]
    min_ms: Optional[float]
    max_ms: Optional[float]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AggregateMetrics:
    sample_count: int
    error_count: int
    error_percentage: float
    avg_ms: Optional[float]
    median_ms: Optional[float]
    p90_ms: Optional[float]
    min_ms: Optional[float]
    max_ms: Optional[float]
    throughput_per_sec: Optional[float]
    test_duration_seconds: Optional[float]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkloadModel:
    virtual_users: int
    ramp_up_seconds: int
    loops_per_user: int
    think_time_ms: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PerformanceEnvironment:
    operating_system: str
    jmeter_version: str
    java_version: str
    target_url: str
    execution_timestamp: str
    workload: WorkloadModel
    reproducibility_note: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["workload"] = self.workload.to_dict()
        return d


@dataclass
class PerformanceRunRecord:
    run_id: str
    scenario_id: str
    requirement_ids: List[str]
    jmx_path: str
    raw_results_path: Optional[str]
    environment: Dict
    aggregate_metrics: Optional[Dict]
    sampler_metrics: List[Dict] = field(default_factory=list)
    capability_result: str = CapabilityResult.NOT_EXECUTED
    capability_result_detail: str = ""
    numeric_sla_result: str = NumericSLAResult.INCONCLUSIVE
    numeric_sla_result_detail: str = ""
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
