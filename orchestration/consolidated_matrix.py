"""
Agentic QE Orchestration -- Consolidated Coverage Matrix (Orchestration
Expansion instruction, sec. 15).

Builds the required matrix (Requirement | Risk | Dependency | Testcase |
Dataset | Automation | Orchestrated | Executed | Result | Evidence | RCA
| Replan | Governance) strictly from real, persisted journal(s) and the
real requirement coverage matrix -- never claims a requirement was
"orchestrated" unless it genuinely passed through
`Orchestrator.run()`/`run_batch()` in this session, per sec. 15's own
explicit distinction (`not selected` / `selected` / `generated` /
`automation-ready` / `blocked` / `executed` / `PASS` / `FAIL` /
`INCONCLUSIVE` / `HUMAN_REVIEW_REQUIRED`).

Deliberately excludes any CONTROLLED TEST FAILURE orchestration_id: that
fixture's testcase is tagged with a real requirement_id (REQ-BRW-01, for
traceability) purely so it can feed real RCA, but it is a synthetic,
clearly-marked fixture, never a real coverage data point -- merging it
into this matrix would overwrite/conflate a real PASS with a
deliberately-engineered failure under the same requirement row, which
would misrepresent the requirement's real disposition. Report the
controlled-failure demonstration in its own, separate, clearly-labeled
section instead (never inside this matrix).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from orchestration.journal import load_journal
from reporting.requirement_coverage import REQUIREMENT_COVERAGE


class OrchestratedStatus:
    NOT_SELECTED = "NOT_SELECTED"
    SELECTED = "SELECTED"
    GENERATED = "GENERATED"
    AUTOMATION_READY = "AUTOMATION_READY"
    BLOCKED = "BLOCKED"
    EXECUTED = "EXECUTED"


def build_matrix(orchestration_ids: List[str]) -> List[Dict]:
    """Merges the real summaries of every listed, real, persisted
    orchestration journal into one row per requirement covered by ANY
    of them, plus a `NOT_SELECTED` row for every other requirement in
    the real 35-requirement coverage matrix (so the output always totals
    exactly 35 rows -- never silently omitting a requirement, sec. 15)."""
    journals = [load_journal(oid) for oid in orchestration_ids]
    journals = [j for j in journals if j is not None]

    covered_by_req: Dict[str, Dict] = {}
    for j in journals:
        summary = j.get("summary") or {}
        selected = summary.get("selected_requirements") or []
        completed = set(summary.get("completed_requirement_ids") or [])
        for rid in selected:
            row = covered_by_req.setdefault(rid, {
                "requirement_id": rid,
                "orchestration_id": j["orchestration_id"],
                "risk": (summary.get("risk") or {}).get(rid),
                "dependency": None,
                "testcase_ids": [],
                "dataset_ids": [],
                "automation_ids": [],
                "orchestrated": OrchestratedStatus.SELECTED,
                "executed": rid in completed,
                "result": None,
                "evidence_references": [],
                "rca": (summary.get("rca") or {}).get(rid),
                "replan": (summary.get("replan") or {}).get(rid),
                "governance": (summary.get("governance_decision") or {}).get(rid),
            })
            plan = summary.get("execution_plan") or {}
            for category, ids in plan.items():
                if rid in ids:
                    row["dependency"] = category
            if rid in completed:
                row["orchestrated"] = OrchestratedStatus.EXECUTED
                exec_ids = summary.get("execution_ids") or []
                row["execution_ids"] = exec_ids
            failures = summary.get("failures") or {}
            if rid in failures:
                row["result"] = failures[rid]
            elif rid in completed:
                row["result"] = "PASS"

    rows: List[Dict] = []
    all_req_ids = {r.requirement_id for r in REQUIREMENT_COVERAGE}
    for rid in sorted(all_req_ids):
        if rid in covered_by_req:
            rows.append(covered_by_req[rid])
        else:
            coverage = next(r for r in REQUIREMENT_COVERAGE if r.requirement_id == rid)
            rows.append({
                "requirement_id": rid,
                "orchestration_id": None,
                "risk": None,
                "dependency": None,
                "testcase_ids": list(coverage.testcase_ids),
                "dataset_ids": list(coverage.dataset_ids),
                "automation_ids": list(coverage.automation_ids),
                "orchestrated": OrchestratedStatus.NOT_SELECTED,
                "executed": False,
                "result": None,
                "evidence_references": [],
                "rca": None,
                "replan": None,
                "governance": None,
            })
    return rows


def summarize(rows: List[Dict]) -> Dict:
    return {
        "total_requirements": len(rows),
        "orchestrated_count": sum(1 for r in rows if r["orchestrated"] != OrchestratedStatus.NOT_SELECTED),
        "executed_count": sum(1 for r in rows if r["executed"]),
        "passed_count": sum(1 for r in rows if r["result"] == "PASS"),
        "not_selected_count": sum(1 for r in rows if r["orchestrated"] == OrchestratedStatus.NOT_SELECTED),
    }
