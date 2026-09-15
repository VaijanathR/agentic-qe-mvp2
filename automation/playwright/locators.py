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


# Post-MVP2 Enhancement 02 -- additional real, evidence-backed candidates,
# captured live from the real SUT during this enhancement's own inspection
# phase (login, search, cart, wishlist, checkout, configurable-attribute
# pages).

LOGIN_FORM_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "email": [
        LocatorCandidate("ID", "#Email", "live capture: <input id=\"Email\" name=\"Email\" class=\"email\">", 1),
        LocatorCandidate("NAME", "[name='Email']", "live capture: <input name=\"Email\">", 2),
    ],
    "password": [
        LocatorCandidate("ID", "#Password", "live capture: <input id=\"Password\" name=\"Password\" class=\"password\">", 1),
        LocatorCandidate("NAME", "[name='Password']", "live capture: <input name=\"Password\">", 2),
    ],
    "login_button": [
        LocatorCandidate("CLASS", ".login-button", "live capture: <input type=\"submit\" class=\"button-1 login-button\" value=\"Log in\">", 1),
        LocatorCandidate("ROLE", "role=button[name='Log in']", "live capture: value=\"Log in\"", 2),
    ],
}

SEARCH_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "search_box": [
        LocatorCandidate("ID", "#small-searchterms", "live capture: <input id=\"small-searchterms\" name=\"q\">", 1),
        LocatorCandidate("NAME", "[name='q']", "live capture: <input name=\"q\">", 2),
    ],
    "search_button": [
        LocatorCandidate("CLASS", ".search-box-button", "live capture: <input type=\"submit\" class=\"button-1 search-box-button\">", 1),
    ],
}

WISHLIST_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "add_to_wishlist_button": [
        LocatorCandidate("CLASS", ".add-to-wishlist-button", "live capture: <input id=\"add-to-wishlist-button-53\" class=\"button-2 add-to-wishlist-button\">", 1),
    ],
}

CART_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "add_to_cart_button_album3": [
        LocatorCandidate("ID", "#add-to-cart-button-53", "live capture: <input id=\"add-to-cart-button-53\" type=\"button\">", 1),
    ],
    "qty_input": [
        LocatorCandidate("CLASS", "input.qty-input", "live capture: <input name=\"itemquantity7088492\" class=\"qty-input\">", 1),
    ],
    "remove_checkbox": [
        LocatorCandidate("NAME", "input[name='removefromcart']", "live capture: <input type=\"checkbox\" name=\"removefromcart\">", 1),
    ],
    "update_cart_button": [
        LocatorCandidate("NAME", "input[name='updatecart']", "live capture: <input type=\"submit\" name=\"updatecart\" class=\"update-cart-button\">", 1),
    ],
    "terms_of_service": [
        LocatorCandidate("ID", "#termsofservice", "live capture: <input id=\"termsofservice\" type=\"checkbox\">", 1),
    ],
    "checkout_button": [
        LocatorCandidate("ID", "#checkout", "live capture: <button id=\"checkout\" name=\"checkout\" class=\"button-1 checkout-button\">", 1),
    ],
}

CHECKOUT_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "checkout_as_guest_button": [
        LocatorCandidate("CLASS", ".checkout-as-guest-button", "live capture: <input class=\"button-1 checkout-as-guest-button\" value=\"Checkout as Guest\">", 1),
    ],
}

# Build Your Own Computer -- real, live-discovered mandatory attribute
# (governing instruction sec. 14; discovered this task via a real,
# interactive Playwright session, not merely static HTML inspection --
# see the Enhancement-02 report's "Live discovery" section).
CONFIGURABLE_ATTRIBUTE_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "add_to_cart_button_byoc": [
        LocatorCandidate("ID", "#add-to-cart-button-16", "live capture: <input id=\"add-to-cart-button-16\">", 1),
    ],
    "bar_notification": [
        LocatorCandidate("ID", "#bar-notification", "live capture: real click-triggered notification bar", 1),
    ],
}

PASSWORD_RECOVERY_CANDIDATES: Dict[str, List[LocatorCandidate]] = {
    "email": [
        LocatorCandidate("ID", "#Email", "live capture: password-recovery form real input id=\"Email\"", 1),
    ],
    "recover_button": [
        LocatorCandidate("CLASS", ".password-recovery-button", "live capture: <input type=\"submit\" name=\"send-email\" class=\"button-1 password-recovery-button\" value=\"Recover\">", 1),
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
