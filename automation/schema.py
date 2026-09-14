"""
CP-MVP2-05 — deterministic Playwright artifact schema.

Implements the three-level PlaywrightArtifact/PlaywrightStep/
LocatorSpec+Assertion model from the frozen
docs/CP-MVP2-05-SPECIFICATION-v1.0.md sec. 6, for the reason sec. 6.1
documents there: a Playwright scenario is an ordered sequence of
actions, each potentially needing its own locator — a two-level schema
(as used by CP-MVP2-04) cannot represent that. Mirrors the fixed-
vocabulary, dataclass-plus-to_dict() convention already established in
knowledge/lib/schema.py, testcases/schema.py, and testdata/schema.py.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class ActionType:
    NAVIGATE = "NAVIGATE"
    FILL = "FILL"
    CLICK = "CLICK"
    SELECT = "SELECT"
    WAIT = "WAIT"
    ASSERT = "ASSERT"


ALL_ACTION_TYPES = {
    ActionType.NAVIGATE, ActionType.FILL, ActionType.CLICK,
    ActionType.SELECT, ActionType.WAIT, ActionType.ASSERT,
}

#: Action types that target a UI element and are therefore
#: "load-bearing" for the locator-evidence rule (spec sec. 12.1) if a
#: field_name is associated with them.
ELEMENT_TARGETING_ACTION_TYPES = {ActionType.FILL, ActionType.CLICK, ActionType.SELECT}


class LocatorStrategy:
    TEST_ID = "TEST_ID"
    ROLE = "ROLE"
    STABLE_ATTRIBUTE = "STABLE_ATTRIBUTE"
    LABEL = "LABEL"
    UNSUPPORTED = "UNSUPPORTED"


class LocatorStatus:
    EVIDENCED = "EVIDENCED"
    UNSUPPORTED = "UNSUPPORTED"


class AssertionType:
    BUSINESS_REQUIRED = "BUSINESS_REQUIRED"
    TECHNICAL_USEFUL = "TECHNICAL_USEFUL"
    DIAGNOSTIC_OPTIONAL = "DIAGNOSTIC_OPTIONAL"


class SyncStrategy:
    WAIT_FOR_VISIBLE = "WAIT_FOR_VISIBLE"
    WAIT_FOR_NETWORK_IDLE = "WAIT_FOR_NETWORK_IDLE"
    NONE = "NONE"


ALL_SYNC_STRATEGIES = {SyncStrategy.WAIT_FOR_VISIBLE, SyncStrategy.WAIT_FOR_NETWORK_IDLE, SyncStrategy.NONE}


class GovernanceStatus:
    """Reused, not reinvented, per the frozen spec sec. 12 — identical
    vocabulary to testcases.schema.GovernanceStatus / testdata.schema.DataGovernanceStatus."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    UNSUPPORTED_NEEDS_CLARIFICATION = "UNSUPPORTED_NEEDS_CLARIFICATION"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"


COVERAGE_COUNTING_STATUSES = {GovernanceStatus.ACCEPTED, GovernanceStatus.POSSIBLE_DUPLICATE}


@dataclass
class LocatorSpec:
    strategy: str
    value: Optional[str]
    evidence_source: Optional[str]
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Assertion:
    assertion_type: str
    condition: str
    source: str
    counts_toward_coverage: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PlaywrightStep:
    __test__ = False

    step_order: int
    action_type: str
    locator: Optional[LocatorSpec] = None
    input_mapping: Optional[str] = None
    synchronization_strategy: str = SyncStrategy.NONE

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class PlaywrightArtifact:
    __test__ = False

    automation_id: str
    testcase_id: str
    requirement_ids: List[str]
    test_data_set_id: str
    journey_id: Optional[str]
    scenario_type: str
    browser_intent: str
    preconditions: List[str]
    steps: List[PlaywrightStep] = field(default_factory=list)
    assertions: List[Assertion] = field(default_factory=list)
    evidence_requirements: List[str] = field(default_factory=list)
    failure_handling_metadata: Dict[str, Any] = field(default_factory=dict)
    source_attribution: List[Dict] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernedPlaywrightArtifact:
    artifact: PlaywrightArtifact
    governance_status: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"validation_status": self.governance_status, "notes": list(self.reasons)}
        d.update(self.artifact.to_dict())
        return d
