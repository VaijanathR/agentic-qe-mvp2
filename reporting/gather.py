"""
CP-MVP2-09 — deterministic, read-only aggregation of persisted CP01-CP08
evidence into the facts the Unified Final QE Report is built from.

This module NEVER computes a PASS/FAIL/conclusion itself, invents a count,
or reinterprets a stored status. It only loads, counts, and groups facts
already recorded by upstream, frozen pipelines -- no LLM, no inference. Every
function is read-only: it imports each capability's existing `persist.py`
(or, for the real execution corpus under `runs/`, reads the same
`final_result.json` files `rca/ingest.py` already reads) and never writes
anything.

Real-vs-fixture distinction (frozen spec sec. 4/21): `runs/` also contains
executions produced by this project's own pytest suites (synthetic
testcase_ids like `TC-X`, `TC-X-01`, `TC-TEST-01`, execution_ids like
`T1`..`T9`, `EXEC-ISOLATION-01`, `T-UNRESOLVED`) that are test-tooling
fixtures, not real QE evidence. `gather_real_execution_results()` excludes
these deterministically by requiring `testcase_id` to be one of the actually
persisted, real testcase_ids (`testcases.persist.list_persisted_testcase_ids()`)
-- never by a hardcoded id list -- so it stays correct as the real corpus
grows.
"""
from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

import automation.multi_locator.persist as ml_automation_persist
import automation.persist as automation_persist
import dependencies.persist as dependencies_persist
import performance.persist as performance_persist
import rbtp.persist as rbtp_persist
import rca.persist as rca_persist
import testcases.persist as testcases_persist
import testdata.persist as testdata_persist
import traceability.automation as traceability_automation
import traceability.req_testcase as traceability_req_testcase
import traceability.testcase_testdata as traceability_testcase_testdata
from persistence.envelope import REPO_ROOT, load_latest

RUNS_ROOT = REPO_ROOT / "runs"


# ---------------------------------------------------------------------------
# CP03 — testcases
# ---------------------------------------------------------------------------

def gather_testcases() -> Dict:
    ids = testcases_persist.list_persisted_testcase_ids()
    records = [testcases_persist.load_persisted_testcase(i) for i in ids]
    records = [r for r in records if r is not None]
    req_to_testcases: Dict[str, List[str]] = {}
    for r in records:
        for req_id in r.get("requirement_ids", []):
            req_to_testcases.setdefault(req_id, []).append(r["testcase_id"])
    scenario_types = Counter(r.get("scenario_type") for r in records)
    governance_statuses = Counter(r.get("governance_status") for r in records)
    return {
        "count": len(records),
        "testcase_ids": sorted(ids),
        "requirement_ids_referenced": sorted(req_to_testcases.keys()),
        "requirement_to_testcase_ids": req_to_testcases,
        "scenario_type_breakdown": dict(scenario_types),
        "governance_status_breakdown": dict(governance_statuses),
    }


# ---------------------------------------------------------------------------
# CP04 — test data
# ---------------------------------------------------------------------------

def gather_testdata() -> Dict:
    ids = testdata_persist.list_persisted_dataset_ids()
    records = []
    for i in ids:
        payload = load_latest(testdata_persist.BASE_DIR, i)
        if payload is not None:
            records.append(payload)
    validation_statuses = Counter(r.get("validation_status") for r in records)
    data_categories = Counter(r.get("data_category") for r in records)
    testcase_to_data: Dict[str, List[str]] = {}
    for r in records:
        testcase_to_data.setdefault(r.get("testcase_id"), []).append(r.get("data_set_id"))
    return {
        "count": len(records),
        "data_set_ids": sorted(ids),
        "validation_status_breakdown": dict(validation_statuses),
        "data_category_breakdown": dict(data_categories),
        "testcase_to_data_set_ids": testcase_to_data,
    }


def _list_ids(base_dir: Path) -> List[str]:
    if not base_dir.exists():
        return []
    return sorted(p.name for p in base_dir.iterdir() if p.is_dir() and (p / "latest.json").exists())


# ---------------------------------------------------------------------------
# RBTP (Risk-Based Test Prioritization) and Dependency/Reusability Matrix
# ---------------------------------------------------------------------------

def gather_rbtp() -> Dict:
    ids = _list_ids(rbtp_persist.BASE_DIR)
    records = [load_latest(rbtp_persist.BASE_DIR, i) for i in ids]
    records = [r for r in records if r is not None]
    priorities = Counter(r.get("priority") for r in records)
    return {"count": len(records), "rbtp_ids": sorted(ids), "priority_breakdown": dict(priorities)}


def gather_dependencies() -> Dict:
    ids = _list_ids(dependencies_persist.BASE_DIR)
    records = [load_latest(dependencies_persist.BASE_DIR, i) for i in ids]
    records = [r for r in records if r is not None]
    return {
        "count": len(records),
        "matrix_ids": sorted(ids),
        "edge_counts": {r.get("matrix_id"): len(r.get("edges", [])) for r in records},
    }


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

def gather_traceability() -> Dict:
    req_ids = _list_ids(traceability_req_testcase.BASE_DIR)
    req_records = [load_latest(traceability_req_testcase.BASE_DIR, i) for i in req_ids]
    req_records = [r for r in req_records if r is not None]

    td_ids = _list_ids(traceability_testcase_testdata.BASE_DIR)
    td_records = [load_latest(traceability_testcase_testdata.BASE_DIR, i) for i in td_ids]
    td_records = [r for r in td_records if r is not None]

    auto_ids = _list_ids(traceability_automation.BASE_DIR)
    auto_records = [load_latest(traceability_automation.BASE_DIR, i) for i in auto_ids]
    auto_records = [r for r in auto_records if r is not None]

    return {
        "req_to_testcase_batches": req_ids,
        "req_to_testcase": [r.get("coverage") for r in req_records],
        "testcase_to_testdata_batches": td_ids,
        "automation_batches": auto_ids,
    }


# ---------------------------------------------------------------------------
# CP05 — automation
# ---------------------------------------------------------------------------

def gather_automation() -> Dict:
    """Distinguishes committed (git-tracked) automation evidence from
    additional real, on-disk-only artifacts -- the CR-001-era persistence
    decision deliberately did not commit `automation/generated/PW-*`
    (frozen spec sec. 9 requires this distinction be preserved, never
    hidden)."""
    all_ids = _list_ids(automation_persist.BASE_DIR)
    records = {i: load_latest(automation_persist.BASE_DIR, i) for i in all_ids}
    records = {k: v for k, v in records.items() if v is not None}
    governance_statuses = Counter(r.get("validation_status") for r in records.values())

    ml_ids = _list_ids(ml_automation_persist.BASE_DIR)
    ml_records = {i: load_latest(ml_automation_persist.BASE_DIR, i) for i in ml_ids}
    ml_records = {k: v for k, v in ml_records.items() if v is not None}

    return {
        "standard_automation_ids": sorted(all_ids),
        "standard_automation_count": len(records),
        "standard_governance_status_breakdown": dict(governance_statuses),
        "multi_locator_automation_ids": sorted(ml_ids),
        "multi_locator_automation_count": len(ml_records),
    }


# ---------------------------------------------------------------------------
# CP06 — real browser execution (runs/, additive, intentionally not
# git-tracked per this repository's own .gitignore -- real, but local-disk
# only; see sec. 9's own note above)
# ---------------------------------------------------------------------------

def gather_real_execution_results() -> Dict:
    real_testcase_ids = set(testcases_persist.list_persisted_testcase_ids())
    seen: Dict[str, Dict] = {}
    for path in sorted(glob.glob(str(RUNS_ROOT / "*" / "*" / "*" / "*" / "final_result.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if d.get("testcase_id") not in real_testcase_ids:
            continue
        seen[d["execution_id"]] = d

    status_breakdown = Counter(d["overall_status"] for d in seen.values())
    not_executed_reasons = Counter(
        tuple(d.get("notes") or []) for d in seen.values() if d["overall_status"] == "NOT_EXECUTED"
    )
    return {
        "count": len(seen),
        "status_breakdown": dict(status_breakdown),
        "not_executed_reason_breakdown": {str(k): v for k, v in not_executed_reasons.items()},
        "records": [
            {
                "execution_id": eid,
                "testcase_id": d["testcase_id"],
                "automation_id": d["automation_id"],
                "requirement_ids": d.get("requirement_ids", []),
                "overall_status": d["overall_status"],
                "failure_classification": d.get("failure_classification"),
                "notes": d.get("notes", []),
            }
            for eid, d in sorted(seen.items())
        ],
    }


# ---------------------------------------------------------------------------
# CP07 — RCA / replanning / governance
# ---------------------------------------------------------------------------

def gather_rca() -> Dict:
    rca_ids = _list_ids(rca_persist.RCA_BASE_DIR)
    replan_ids = _list_ids(rca_persist.REPLANNING_BASE_DIR)
    gov_ids = _list_ids(rca_persist.GOVERNANCE_BASE_DIR)

    rca_records = [rca_persist.load_persisted_rca(i) for i in rca_ids]
    rca_records = [r for r in rca_records if r is not None]
    replan_records = [rca_persist.load_persisted_replanning(i) for i in replan_ids]
    replan_records = [r for r in replan_records if r is not None]
    gov_records = [rca_persist.load_persisted_governance(i) for i in gov_ids]
    gov_records = [r for r in gov_records if r is not None]

    return {
        "rca_count": len(rca_records),
        "rca_summaries": [
            {
                "rca_id": r["rca_id"],
                "execution_id": r["execution_id"],
                "confidence": r["confidence"],
                "final_rca_classification": r["final_rca_classification"],
                "final_rca_subtype": r["final_rca_subtype"],
            }
            for r in rca_records
        ],
        "replanning_count": len(replan_records),
        "replanning_decision_breakdown": dict(Counter(r["decision"] for r in replan_records)),
        "governance_count": len(gov_records),
        "governance_decision_breakdown": dict(Counter(r["decision"] for r in gov_records)),
        "governance_guard_all_passed": all(r["prohibited_change_guard_passed"] for r in gov_records) if gov_records else None,
        "cr002_status_breakdown": dict(Counter(r["cr002_status"] for r in gov_records)),
    }


# ---------------------------------------------------------------------------
# CP08 — performance
# ---------------------------------------------------------------------------

def gather_performance() -> Dict:
    ids = performance_persist.list_persisted_run_ids()
    records = {i: performance_persist.load_persisted_run(i) for i in ids}
    records = {k: v for k, v in records.items() if v is not None}
    return {
        "run_count": len(records),
        "run_ids": sorted(records.keys()),
        "runs": {
            rid: {
                "capability_result": r["capability_result"],
                "numeric_sla_result": r["numeric_sla_result"],
                "aggregate_metrics": r["aggregate_metrics"],
            }
            for rid, r in records.items()
        },
    }


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def gather_all() -> Dict:
    return {
        "testcases": gather_testcases(),
        "testdata": gather_testdata(),
        "rbtp": gather_rbtp(),
        "dependencies": gather_dependencies(),
        "traceability": gather_traceability(),
        "automation": gather_automation(),
        "execution": gather_real_execution_results(),
        "rca": gather_rca(),
        "performance": gather_performance(),
    }
