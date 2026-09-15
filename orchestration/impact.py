"""
Agentic QE Orchestration -- Impact Analysis (governing instruction
sec. 14).

Reuses CR-001's real, deterministic Dependency/Reusability Matrix
pipeline unmodified (`dependencies.pipeline.run_dependency_matrix`) to
determine directly/indirectly related testcases (shared journey, shared
precondition, shared requirement, possible duplicate testing -- see
`dependencies.schema.DependencyKind`, reused unmodified). Performance
relevance and regression-scope hints are read from the real requirement
coverage matrix (`reporting.requirement_coverage`), never invented.
"""
from __future__ import annotations

from typing import Dict, List

from orchestration.enh02_adapter import all_governed_testcases as enh02_all_governed_testcases
from orchestration.enh02_adapter import governed_testcases_for_requirement as enh02_governed_testcases
from orchestration.testcase_loader import (
    load_all_persisted_governed_testcases as cp03_all_governed_testcases,
)
from orchestration.testcase_loader import load_governed_testcases_for_requirement as cp03_governed_testcases
from dependencies.pipeline import run_dependency_matrix
from reporting.requirement_coverage import REQUIREMENT_COVERAGE


def analyze(requirement_id: str) -> Dict:
    direct = cp03_governed_testcases(requirement_id)
    corpus_source = "CP-MVP2-03 persisted corpus"
    universe = cp03_all_governed_testcases()
    if not direct:
        direct = enh02_governed_testcases(requirement_id)
        corpus_source = "Enhancement-02 real testcase corpus (adapted)"
        universe = enh02_all_governed_testcases()

    if not direct:
        return {
            "requirement_id": requirement_id,
            "corpus_source": None,
            "directly_impacted_testcase_ids": [],
            "indirectly_impacted_testcase_ids": [],
            "dependency_edges": [],
            "reusable_component_candidates": [],
            "performance_relevant": False,
            "note": "No real, governed testcase exists yet for this requirement -- impact cannot be "
                    "computed from evidence that does not exist.",
        }

    direct_ids = {g.testcase.testcase_id for g in direct}
    result = run_dependency_matrix(universe, matrix_id=f"ORCH-IMPACT-{requirement_id}")
    edges = result["matrix"]["edges"]

    indirect_ids = set()
    relevant_edges = []
    for e in edges:
        if e["testcase_id"] in direct_ids or e["related_testcase_id"] in direct_ids:
            relevant_edges.append(e)
            indirect_ids.add(e["testcase_id"])
            indirect_ids.add(e["related_testcase_id"])
    indirect_ids -= direct_ids

    coverage = next((r for r in REQUIREMENT_COVERAGE if r.requirement_id == requirement_id), None)

    return {
        "requirement_id": requirement_id,
        "corpus_source": corpus_source,
        "directly_impacted_testcase_ids": sorted(direct_ids),
        "indirectly_impacted_testcase_ids": sorted(indirect_ids),
        "dependency_edges": relevant_edges,
        "reusable_component_candidates": result["matrix"]["reusable_component_candidates"],
        "performance_relevant": bool(coverage and coverage.performance_testcase_ids),
        "performance_testcase_ids": list(coverage.performance_testcase_ids) if coverage else [],
        "validation": result["validation"],
        "persisted": result["persisted"],
    }
