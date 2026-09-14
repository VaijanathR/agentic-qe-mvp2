"""
CP-MVP2-05 — deterministic locator evidence lookup.

Per the frozen docs/CP-MVP2-05-SPECIFICATION-v1.0.md sec. 7.1: DOM/
locator evidence lives in the raw CP-MVP2-01 discovery captures
(`knowledge/historical/discovery_evidence/captures/*.html`), which are
DELIBERATELY excluded from the queryable CP-MVP2-02 `KnowledgeBase` (see
`knowledge/lib/validate.py::check_historical_vs_approved_conflict`).
This module therefore reads those capture files **directly from disk**
— never through `KnowledgeBase.query()`/`by_id()` — and never returns a
locator that was not actually found, by regex search, in the real file
content at call time. Nothing here is a hardcoded guess at what a page
"probably" contains; every returned value is confirmed present in the
cited file when this function runs.

The specification's own sec. 7.1/20 findings (from direct inspection of
the real captures) are encoded here as *where to look*, never as
*invented locator values*:
  - The Billing/Shipping address form (checkout_00.html) uses a stable
    ASP.NET MVC model-binding ID convention: "{Model}_{Property}", e.g.
    id="BillingNewAddress_FirstName" — confirmed present, one per
    REQ-ACO-03 field.
  - The address form's "Continue" submit control uses a CSS class
    ("new-address-next-step-button") that this module's own inspection
    found is NOT unique on that page (Billing.save() and Shipping.save()
    both use it) — an ambiguous locator, per spec sec. 13's "ambiguous
    UI element" disposition, so it is reported UNSUPPORTED, not used.
  - No REQ-REG-01 (registration) capture exists at all.
  - The cart-quantity control's only evidenced form
    (name="itemquantity<item-id>") is item-specific; this module does
    not generalize it without further evidence (spec sec. 20 item 3).
  - Exact per-option payment-method locators were not confirmed (spec
    sec. 20 item 2).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from automation.schema import LocatorStrategy

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURES_DIR = REPO_ROOT / "knowledge" / "historical" / "discovery_evidence" / "captures"

_ADDRESS_CAPTURE_FILE = CAPTURES_DIR / "checkout_00.html"
_ADDRESS_MODEL_PREFIX = "BillingNewAddress"
# Deterministic mapping of governed field_name -> the ASP.NET MVC model
# property name this application's own discovery evidence already
# established (real observed convention, not invented). The actual `id`
# STRING is only ever considered evidenced if a fresh regex search of
# the real file confirms it is present -- this table only says where to
# look, never asserts the value exists.
_ADDRESS_FIELD_TO_PROPERTY = {
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "Email",
    # Country renders as a <select> bound to CountryId, not a text
    # input bound to "Country" -- confirmed by direct inspection of the
    # real capture (id="BillingNewAddress_CountryId" is present;
    # id="BillingNewAddress_Country" is not).
    "country": "CountryId",
    "city": "City",
    "address1": "Address1",
    "address2": "Address2",
    "zip_postal_code": "ZipPostalCode",
    "phone_number": "PhoneNumber",
    "company": "Company",
    "fax_number": "FaxNumber",
}


@dataclass
class LocatorEvidence:
    strategy: str
    value: str
    evidence_source: str


def _read_capture(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="ignore")


def _id_attribute_present(html_text: str, id_value: str) -> bool:
    return re.search(r'id="' + re.escape(id_value) + r'"', html_text) is not None


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def lookup_locator(requirement_id: str, field_name: str) -> Optional[LocatorEvidence]:
    """Returns real, evidenced locator information, or None if no
    confirmed evidence exists for this requirement/field combination.
    None is a governance signal (spec sec. 6.4/13 -> LocatorStatus.UNSUPPORTED),
    never treated as "assume it's fine."""
    if requirement_id == "REQ-ACO-03" and field_name in _ADDRESS_FIELD_TO_PROPERTY:
        html_text = _read_capture(_ADDRESS_CAPTURE_FILE)
        if html_text is None:
            return None
        id_value = f"{_ADDRESS_MODEL_PREFIX}_{_ADDRESS_FIELD_TO_PROPERTY[field_name]}"
        if _id_attribute_present(html_text, id_value):
            return LocatorEvidence(
                strategy=LocatorStrategy.STABLE_ATTRIBUTE,
                value=f"#{id_value}",
                evidence_source=_relative(_ADDRESS_CAPTURE_FILE),
            )
        return None

    # REQ-REG-01: no capture exists at all (spec sec. 20 item 1) -> always None.
    # REQ-CART-03 "quantity": only a fragile, item-specific literal is
    # evidenced (spec sec. 20 item 3) -> always None until a future task
    # establishes and evidences a safe generalized pattern.
    # REQ-PAY-01 "payment_method": option-level locators unconfirmed
    # (spec sec. 20 item 2) -> always None.
    return None


def lookup_submit_locator(requirement_id: str) -> Optional[LocatorEvidence]:
    """Locator for the page-level submit/continue action, if any exists
    and is unambiguous. For REQ-ACO-03, direct inspection of the real
    capture found the "Continue" control's CSS class
    ("new-address-next-step-button") is used by MORE THAN ONE element on
    the same page (Billing.save() and Shipping.save() both), which is
    exactly the "ambiguous UI element" case spec sec. 13 requires be
    reported UNSUPPORTED rather than guessed at (e.g. by picking "the
    first match"). This function verifies that ambiguity is still
    present in the real file at call time before withholding the
    locator, rather than hardcoding the withholding decision blindly."""
    if requirement_id == "REQ-ACO-03":
        html_text = _read_capture(_ADDRESS_CAPTURE_FILE)
        if html_text is None:
            return None
        matches = re.findall(r'class="button-1 new-address-next-step-button"', html_text)
        if len(matches) != 1:
            # 0 matches: no longer evidenced at all. >1 match: still
            # genuinely ambiguous. Either way, UNSUPPORTED.
            return None
        # Exactly one match would mean the ambiguity this specification
        # disclosed no longer holds in the current file -- in that case
        # a real locator could legitimately be returned. As of this
        # implementation, the real file has 2 matches, so this branch is
        # not reached; it is not removed, because re-verifying against
        # the actual file (not a cached assumption) is the entire point
        # of reading it directly each time.
        return LocatorEvidence(
            strategy=LocatorStrategy.STABLE_ATTRIBUTE,
            value=".new-address-next-step-button",
            evidence_source=_relative(_ADDRESS_CAPTURE_FILE),
        )
    return None
