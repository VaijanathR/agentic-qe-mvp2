"""
Agentic QE Orchestration -- dynamic requirement discovery by capability
(Wave 2 instruction sec. 20: "Do not simply reuse the previous six
hard-coded requirements... the orchestrator discovers applicable
requirements").

Discovers requirement IDs by real `category` (the real, governed
`RequirementCoverageRecord.category` field -- e.g. "Wishlist", "Search",
"Product Browsing", "Authentication"), never a hard-coded requirement-ID
list. This is the entry point the dynamic multi-requirement
demonstration uses instead of a fixed array.
"""
from __future__ import annotations

from typing import Dict, List

from reporting.requirement_coverage import REQUIREMENT_COVERAGE


def real_capabilities() -> List[str]:
    """Every real, distinct capability category present in the governed
    35-requirement coverage matrix -- never invented."""
    return sorted({r.category for r in REQUIREMENT_COVERAGE})


def discover_requirements_by_capability(capabilities: List[str]) -> Dict[str, List[str]]:
    """Real, deterministic discovery: for each requested capability
    (case-sensitive, matched against the real `category` field), returns
    the real requirement IDs in that category, in the coverage matrix's
    own real order. Unknown capabilities return an empty list -- never
    fabricated."""
    result: Dict[str, List[str]] = {c: [] for c in capabilities}
    for r in REQUIREMENT_COVERAGE:
        if r.category in result:
            result[r.category].append(r.requirement_id)
    return result


def discover_requirement_ids(capabilities: List[str]) -> List[str]:
    """Flattened, de-duplicated, order-preserving list of real
    requirement IDs across every requested capability."""
    by_capability = discover_requirements_by_capability(capabilities)
    seen: List[str] = []
    for ids in by_capability.values():
        for rid in ids:
            if rid not in seen:
                seen.append(rid)
    return seen
