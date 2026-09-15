"""
Agentic QE Orchestration -- Test Strategy (governing instruction sec. 16).

Deterministic: given a requirement's real, governed testcase(s) (whatever
real corpus already covers it), reports which of
POSITIVE/ALTERNATE/EXCEPTIONAL are already represented and which are
missing -- the orchestrator's Testcase stage then only needs to consider
generating the missing ones (sec. 16 "prefer compact variants with strong
coverage... avoid unnecessary combinatorial explosion"). Never invents a
scenario type that has no evidence basis; "missing" only means "not yet
represented," not "required" -- whether it is truly required remains a
Testcase Quality Gate / Human decision downstream.
"""
from __future__ import annotations

from typing import Dict, List

from orchestration.enh02_adapter import governed_testcases_for_requirement as enh02_governed_testcases
from orchestration.testcase_loader import load_governed_testcases_for_requirement as cp03_governed_testcases
from testcases.schema import ALL_SCENARIO_TYPES


def determine_strategy(requirement_id: str) -> Dict:
    governed = cp03_governed_testcases(requirement_id)
    corpus_source = "CP-MVP2-03 persisted corpus"
    if not governed:
        governed = enh02_governed_testcases(requirement_id)
        corpus_source = "Enhancement-02 real testcase corpus (adapted)"

    covered = {g.testcase.scenario_type for g in governed}
    missing = sorted(ALL_SCENARIO_TYPES - covered)

    return {
        "requirement_id": requirement_id,
        "corpus_source": corpus_source,
        "existing_testcase_ids": sorted(g.testcase.testcase_id for g in governed),
        "covered_scenario_types": sorted(covered),
        "missing_scenario_types": missing,
        "recommendation": (
            "Reuse existing testcase(s); no generation required."
            if not missing
            else f"Existing testcase(s) cover {sorted(covered) or '(none)'}; "
                 f"{missing} not yet represented -- candidate scenario types for generation, "
                 "subject to the Approved SRS actually justifying each one (never forced)."
        ),
    }
