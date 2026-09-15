"""
Post-MVP2 Enhancement 01 -- multiple evidence-backed locators + governed
runtime fallback (backlog items E-08/E-09).

This is a NEW, clearly-identified post-MVP2 capability. It does NOT modify
CR-002 (`docs/CP-MVP2-CR-002-RUNTIME-LOCATOR-FALLBACK-PROPOSAL.md`), whose
status remains exactly `PROPOSED -- NOT IMPLEMENTED. NOT AUTHORIZED.` for
the CP-06 execution engine that document is scoped to. Fallback here is
scoped ONLY to this new `automation/playwright/` package's own, separate
execution path -- never presented as CR-002 authorization.

Deterministic locator priority (documented per governing instruction
sec. 19):
  1. Real, stable `id` attribute (functionally equivalent to a Test ID --
     this SUT does not expose dedicated `data-testid` attributes, so a
     stable framework-assigned `id`, e.g. `#FirstName`, is the highest-
     confidence, most implementation-independent real selector available).
  2. Accessible label association (`label[for=...]`), which Playwright's
     `get_by_label()` resolves via the real DOM label-input relationship --
     survives an id rename, still tied to real, human-visible page text.
  3. `name` HTML attribute -- a real, stable, form-semantics attribute,
     lowest priority because it is the most implementation-specific of the
     three.

No selector below was invented: all three real candidates per field were
captured from a real, live GET of https://demowebshop.tricentis.com/register
performed during this enhancement's own inspection phase (see the
enhancement report's Environment section for the exact evidence).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class LocatorCandidate:
    locator_type: str          # "ID" | "LABEL" | "NAME" | "ROLE"
    expression: str            # Playwright selector/locator expression
    source: str                 # where the evidence came from
    priority: int                # 1 = highest
    validation_status: str = "ACCEPTED"  # ACCEPTED | UNSUPPORTED_NEEDS_CLARIFICATION

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LocatorResolutionResult:
    field_name: str
    attempted: List[Dict] = field(default_factory=list)  # [{candidate, outcome, error}]
    resolved_candidate: Optional[Dict] = None
    used_fallback: bool = False

    def to_dict(self) -> dict:
        return {
            "field_name": self.field_name,
            "attempted": self.attempted,
            "resolved_candidate": self.resolved_candidate,
            "used_fallback": self.used_fallback,
        }


# Real, evidence-backed candidates for the registration form
# (https://demowebshop.tricentis.com/register, captured live this task).
REGISTRATION_FORM_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "first_name": [
        LocatorCandidate("ID", "#FirstName", "live capture: <input id=\"FirstName\" name=\"FirstName\">", 1),
        LocatorCandidate("LABEL", "label=First name:", "live capture: <label for=\"FirstName\">First name:</label>", 2),
        LocatorCandidate("NAME", "[name='FirstName']", "live capture: <input name=\"FirstName\">", 3),
    ],
    "last_name": [
        LocatorCandidate("ID", "#LastName", "live capture: <input id=\"LastName\" name=\"LastName\">", 1),
        LocatorCandidate("LABEL", "label=Last name:", "live capture: <label for=\"LastName\">Last name:</label>", 2),
        LocatorCandidate("NAME", "[name='LastName']", "live capture: <input name=\"LastName\">", 3),
    ],
    "email": [
        LocatorCandidate("ID", "#Email", "live capture: <input id=\"Email\" name=\"Email\">", 1),
        LocatorCandidate("LABEL", "label=Email:", "live capture: <label for=\"Email\">Email:</label>", 2),
        LocatorCandidate("NAME", "[name='Email']", "live capture: <input name=\"Email\">", 3),
    ],
    "password": [
        LocatorCandidate("ID", "#Password", "live capture: <input id=\"Password\" name=\"Password\">", 1),
        LocatorCandidate("LABEL", "label=Password:", "live capture: <label for=\"Password\">Password:</label>", 2),
        LocatorCandidate("NAME", "[name='Password']", "live capture: <input name=\"Password\">", 3),
    ],
    "confirm_password": [
        LocatorCandidate("ID", "#ConfirmPassword", "live capture: <input id=\"ConfirmPassword\" name=\"ConfirmPassword\">", 1),
        LocatorCandidate("LABEL", "label=Confirm password:", "live capture: <label for=\"ConfirmPassword\">Confirm password:</label>", 2),
        LocatorCandidate("NAME", "[name='ConfirmPassword']", "live capture: <input name=\"ConfirmPassword\">", 3),
    ],
    "register_button": [
        LocatorCandidate("ID", "#register-button", "live capture: <input id=\"register-button\" type=\"submit\">", 1),
        LocatorCandidate("ROLE", "role=button[name='Register']", "live capture: <input type=\"submit\" value=\"Register\">", 2),
    ],
}


def resolve_with_fallback(
    field_name: str,
    candidates: List[LocatorCandidate],
    try_candidate: Callable[[LocatorCandidate], bool],
) -> LocatorResolutionResult:
    """Tries each real candidate in priority order. `try_candidate` must
    return True if the candidate resolved and the intended action
    succeeded, False otherwise -- it must never raise for an ordinary
    "not found" outcome (real errors should still propagate). Every
    attempt (success or failure) is recorded, never silently discarded;
    a fallback that succeeds is explicitly flagged `used_fallback=True`
    and is never presented as a silent, invisible recovery."""
    result = LocatorResolutionResult(field_name=field_name)
    for candidate in sorted(candidates, key=lambda c: c.priority):
        outcome = try_candidate(candidate)
        result.attempted.append({"candidate": candidate.to_dict(), "outcome": "SUCCESS" if outcome else "FAILED"})
        if outcome:
            result.resolved_candidate = candidate.to_dict()
            result.used_fallback = candidate.priority > 1
            return result
    return result
