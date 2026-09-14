"""
Multi-locator-candidate schema — a wholly new, additive package.

Does not modify, subclass, or import-and-monkeypatch anything in the
frozen `automation/schema.py` (CP-MVP2-05). Reuses
`automation.schema.LocatorStrategy` (an unmodified, fixed vocabulary)
by value only. See `docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`
for why this package stops at generation/persistence-time and does not
implement any runtime fallback-retry behavior — that would conflict
with the frozen CP-MVP2-06 sec. 14/15 (retry/self-healing prohibitions).

Deterministic priority ordering of locator strategies (Human requirement,
"CONTINUE" instruction sec. 2): TEST_ID > ROLE > LABEL > STABLE_ATTRIBUTE
> other. `automation.schema.LocatorStrategy` does not currently define a
ROLE-with-accessible-name or LABEL strategy value distinct from the ones
already listed there (`TEST_ID`, `ROLE`, `STABLE_ATTRIBUTE`, `LABEL`,
`UNSUPPORTED`) -- all four real strategies are reused verbatim; nothing
new is added to that frozen vocabulary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from automation.schema import LocatorStrategy

#: Deterministic priority order (lower number = tried first), per the
#: Human's own stated preference order. Fixed, not learned, not LLM-proposed.
STRATEGY_PRIORITY = {
    LocatorStrategy.TEST_ID: 1,
    LocatorStrategy.ROLE: 2,
    LocatorStrategy.LABEL: 3,
    LocatorStrategy.STABLE_ATTRIBUTE: 4,
}


class Confidence:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


ALL_CONFIDENCE_LEVELS = {Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW}


class AutomationHealth:
    """Distinguishes "did the business assertion pass" from "did every
    locator resolve on its first, highest-priority candidate" (CR-002
    proposal sec. 3 / CONTINUE instruction sec. 5). Recorded as metadata
    only in this package -- never written into any frozen CP-06
    ExecutionResult field, since that field's meaning is frozen."""

    GREEN = "GREEN"     # every step resolved via its priority-1 candidate
    YELLOW = "YELLOW"   # at least one step would have required a fallback
    RED = "RED"         # at least one load-bearing step has zero candidates


@dataclass
class LocatorCandidate:
    __test__ = False

    priority: int
    strategy: str
    locator: str
    evidence_source: str
    evidence_reference: str
    confidence: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StepLocatorCandidateSet:
    """One load-bearing step's full, priority-ordered candidate list.
    `candidates[0]` (if any) is the "primary" -- the only one real CP-06
    execution in this task ever actually uses."""

    step_order: int
    field_name: Optional[str]
    candidates: List[LocatorCandidate] = field(default_factory=list)
    #: True if the step's ORIGINAL, frozen CP-05-generated single-locator
    #: lookup already found this exact same primary value (i.e. this
    #: step needed no new resolution at all); False if the primary
    #: candidate here was newly resolved by this package where the
    #: frozen CP-05 pipeline itself found only ambiguity/no evidence.
    original_locator_was_evidenced: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MultiLocatorArtifact:
    """Wraps a real, persisted, frozen CP-05 `PlaywrightArtifact` (by
    reference, never by mutation) with an additive locator-candidate
    layer. `source_automation_id` always points back to the real,
    unmodified, frozen-governed automation artifact this was derived
    from -- full traceability preserved; the frozen artifact itself is
    never edited."""

    ml_automation_id: str
    source_automation_id: str
    testcase_id: str
    requirement_ids: List[str]
    test_data_set_id: str
    step_candidate_sets: List[StepLocatorCandidateSet] = field(default_factory=list)
    automation_health: str = AutomationHealth.GREEN
    source_attribution: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class MultiLocatorGovernanceStatus:
    """Reuses the exact same governance vocabulary already established
    at every prior checkpoint (never reinvented)."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNSUPPORTED_NEEDS_CLARIFICATION = "UNSUPPORTED_NEEDS_CLARIFICATION"


@dataclass
class GovernedMultiLocatorArtifact:
    artifact: MultiLocatorArtifact
    governance_status: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"validation_status": self.governance_status, "notes": list(self.reasons)}
        d.update(self.artifact.to_dict())
        return d
