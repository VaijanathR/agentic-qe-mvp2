"""
CP-MVP2-08 — deterministic parsing of a real, raw JMeter `.jtl` (CSV) results
file into `SamplerMetrics`/`AggregateMetrics`. Never manufactures a
measurement: every field is computed only from rows actually present in the
file (frozen spec sec. 7 — "Observed measurement -> derived metric ->
interpretation").

Percentile method: nearest-rank (ceil(p * n) - 1 on the sorted list), a
simple, disclosed, deterministic method — not an interpolated percentile.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Optional, Union

from performance.schema import AggregateMetrics, SamplerMetrics


def _percentile(sorted_values: List[float], p: float) -> Optional[float]:
    if not sorted_values:
        return None
    idx = max(0, math.ceil(p * len(sorted_values)) - 1)
    return sorted_values[min(idx, len(sorted_values) - 1)]


def _round(value: Optional[float]) -> Optional[float]:
    return round(value, 3) if value is not None else None


def read_jtl_rows(jtl_path: Union[str, Path]) -> List[Dict[str, str]]:
    path = Path(jtl_path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _stats_for(elapsed_ms: List[float], error_count: int) -> Dict[str, Optional[float]]:
    sample_count = len(elapsed_ms)
    sorted_ms = sorted(elapsed_ms)
    return {
        "sample_count": sample_count,
        "error_count": error_count,
        "error_percentage": _round((error_count / sample_count) * 100.0) if sample_count else 0.0,
        "avg_ms": _round(sum(elapsed_ms) / sample_count) if sample_count else None,
        "median_ms": _round(_percentile(sorted_ms, 0.50)),
        "p90_ms": _round(_percentile(sorted_ms, 0.90)),
        "min_ms": _round(min(elapsed_ms)) if elapsed_ms else None,
        "max_ms": _round(max(elapsed_ms)) if elapsed_ms else None,
    }


def compute_sampler_metrics(rows: List[Dict[str, str]]) -> List[SamplerMetrics]:
    by_label: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)

    results: List[SamplerMetrics] = []
    for label, label_rows in by_label.items():
        elapsed = [float(r["elapsed"]) for r in label_rows]
        errors = sum(1 for r in label_rows if r["success"].lower() != "true")
        stats = _stats_for(elapsed, errors)
        results.append(SamplerMetrics(label=label, **stats))
    return sorted(results, key=lambda s: s.label)


def compute_aggregate_metrics(rows: List[Dict[str, str]]) -> AggregateMetrics:
    elapsed = [float(r["elapsed"]) for r in rows]
    errors = sum(1 for r in rows if r["success"].lower() != "true")
    stats = _stats_for(elapsed, errors)

    if rows:
        start_ts = min(int(r["timeStamp"]) for r in rows)
        end_ts = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
        duration_seconds = max((end_ts - start_ts) / 1000.0, 0.001)
        throughput = _round(len(rows) / duration_seconds)
    else:
        duration_seconds = None
        throughput = None

    return AggregateMetrics(
        **stats,
        throughput_per_sec=throughput,
        test_duration_seconds=_round(duration_seconds) if duration_seconds is not None else None,
    )
