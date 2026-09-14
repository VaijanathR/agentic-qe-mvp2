"""
CP-MVP2-CR-001 Batch 1 — deterministic RBTP risk-factor evidence.

Every function here derives one risk factor from a real, citable source
already present in this project (a testcase's own already-governed
`priority` field, or the governed Knowledge Base's requirement text /
journey membership) — never an invented score. Where no such source
exists at all (defect history, change history, likelihood modelling,
dependency impact at RBTP-generation time), `rbtp/generate.py` sets the
factor to `RiskLevel.UNKNOWN` directly; this module is not asked to
guess those.
"""
from __future__ import annotations

from typing import List, Tuple

from knowledge.lib.retrieval import KnowledgeBase
from rbtp.schema import RiskLevel
from testcases.schema import GovernedTestcase

#: Real-evidence keyword scan: terms whose presence in an APPROVED
#: requirement's own text is a citable signal of security relevance.
#: Confirmed present in the real SRS corpus, e.g. REQ-REG-01
#: ("Password", "Confirm password"), REQ-AUTH-01/02 ("password"),
#: REQ-PAY-01/02/03 ("payment"). Deliberately narrow: generic "account"
#: and bare "card" were tried and rejected during this batch's own
#: testing -- both produce real false positives in this corpus (e.g.
#: REQ-WISH-03's "...without requiring an account" is explicitly the
#: ABSENCE of an account requirement, not a security concern; "card"
#: alone would match "Gift Card" mentions unrelated to payment
#: security) -- so only the more specific, lower-false-positive terms
#: are kept.
SECURITY_RELEVANT_TERMS = (
    "password", "credential", "authenticat", "login", "cvv",
    "credit card", "payment",
)

#: Fixed, disclosed mapping from an approved journey (Approved SRS §2.1)
#: to a customer-impact tier: J-01/J-02 culminate in a placed order
#: (highest customer impact); J-03/J-04 affect cart contents/config but
#: do not themselves place an order; J-05 (wishlist) is the lowest-impact
#: approved journey. This is a governance-defined heuristic over real
#: journey structure, not a per-instance invention.
JOURNEY_CUSTOMER_IMPACT = {
    "J-01": RiskLevel.HIGH,
    "J-02": RiskLevel.HIGH,
    "J-03": RiskLevel.MEDIUM,
    "J-04": RiskLevel.MEDIUM,
    "J-05": RiskLevel.LOW,
}

_IMPACT_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.UNKNOWN: -1}


def business_criticality_from_testcase(gtc: GovernedTestcase) -> Tuple[str, str]:
    """Evidence source: the testcase's own already-governed `priority`
    field (HIGH/MEDIUM/LOW), assigned during CP-MVP2-03 generation and
    validated by `testcases.validate.validate_schema` — a real, existing
    field, not a new score invented here."""
    p = gtc.testcase.priority
    if p in (RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW):
        return p, f"testcase.priority={p!r}"
    return RiskLevel.UNKNOWN, f"testcase.priority={p!r} did not resolve to a known risk level"


def security_impact_from_evidence(kb: KnowledgeBase, requirement_ids: List[str]) -> Tuple[str, str]:
    """Deterministic keyword scan over the REAL, governed requirement
    text already retrieved via `KnowledgeBase.by_id()` — HIGH if a
    security-relevant term is found, LOW if the scan ran and found
    nothing (a checked, negative result — distinct from UNKNOWN, which
    means no check was possible at all)."""
    matched: List[str] = []
    for rid in requirement_ids:
        for hit in kb.by_id(rid):
            if hit["content_type"] != "requirement":
                continue
            text_lower = hit["text"].lower()
            for term in SECURITY_RELEVANT_TERMS:
                if term in text_lower and term not in matched:
                    matched.append(term)
    if matched:
        return RiskLevel.HIGH, f"security-relevant terms matched in requirement evidence text: {matched}"
    return RiskLevel.LOW, "requirement evidence text scanned; no security-relevant term matched"


def customer_impact_from_journey(kb: KnowledgeBase, requirement_ids: List[str]) -> Tuple[str, str]:
    """Evidence source: the real, approved journey membership
    (Approved SRS §2.1) already carried on each requirement chunk,
    mapped through the fixed `JOURNEY_CUSTOMER_IMPACT` table above."""
    best = RiskLevel.UNKNOWN
    best_journeys: List[str] = []
    for rid in requirement_ids:
        for hit in kb.by_id(rid):
            if hit["content_type"] != "requirement":
                continue
            for jid in hit.get("journey_id", []):
                tier = JOURNEY_CUSTOMER_IMPACT.get(jid)
                if tier is None:
                    continue
                best_journeys.append(jid)
                if _IMPACT_ORDER[tier] > _IMPACT_ORDER.get(best, -1):
                    best = tier
    if not best_journeys:
        return RiskLevel.UNKNOWN, "no approved journey membership found for these requirement IDs"
    return best, (
        f"derived from approved journey membership {sorted(set(best_journeys))} "
        "via the fixed, disclosed journey->customer-impact tier mapping above"
    )
