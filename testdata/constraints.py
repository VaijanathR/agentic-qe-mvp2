"""
CP-MVP2-04 — deterministic requirement-derived constraint table.

Per the frozen docs/CP-MVP2-04-SPECIFICATION-v1.0.md sec. 8: constraints
are "extracted, never invented." This module is the deterministic-code
representation of that extraction: a small, explicit, hand-authored
table keyed by requirement ID, where every entry cites the exact
Approved SRS section/business-rule/negative-case it comes from. This is
the same "never let an LLM decide authority/constraints" discipline
knowledge/lib/schema.py already applies to source-authority ranking
(CP-MVP2-02 governance rule #10) — here applied to test-data
constraints instead of retrieval ranking.

A requirement ID with NO entry here is not silently assumed unconstrained
— testdata.generate treats a missing profile as `INSUFFICIENT_EVIDENCE`
(spec sec. 9/18), never as "anything goes." Extending this table to a
new requirement is itself a disclosed, evidenced act (a future revision
citing the SRS text), never an LLM inference.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from testdata.schema import BoundaryClassification, UniquenessRequirement, ValueType


@dataclass
class FieldSpec:
    field_name: str
    value_type: str
    mandatory: bool
    uniqueness_requirement: str = UniquenessRequirement.UNIQUENESS_UNKNOWN
    allowed_values: Optional[List[str]] = None
    dependency_reference: Optional[str] = None


@dataclass
class ConstraintProfile:
    requirement_id: str
    evidence_note: str
    field_specs: List[FieldSpec]
    #: name -> {field overrides + a literal, evidence-grounded documented
    #: example}. Used for EXCEPTIONAL/INVALID category generation instead
    #: of ever asking the LLM to invent an invalid example.
    documented_exceptional: Dict[str, Dict] = field(default_factory=dict)
    #: a single documented boundary case, or None if the Approved SRS
    #: states no boundary for this requirement (spec sec. 7.4 — no
    #: boundary may be fabricated where none is evidenced).
    documented_boundary: Optional[Dict] = None
    #: a single documented alternate-path case, or None.
    documented_alternate: Optional[Dict] = None


# ---------------------------------------------------------------------------
# REQ-REG-01..04 — Registration (requirements/MVP2_SRS_v1.0_APPROVED.md §6.1, §7, §8.1)
# ---------------------------------------------------------------------------
_REGISTRATION = ConstraintProfile(
    requirement_id="REQ-REG-01",
    evidence_note=(
        "REQ-REG-01 (mandatory fields), REQ-REG-02 (password/confirm match), "
        "REQ-REG-03 (email format), REQ-REG-04/Business Rule #1 (email uniqueness), "
        "NEG-01..04 (documented negative cases)."
    ),
    field_specs=[
        FieldSpec("first_name", ValueType.STRING, mandatory=True),
        FieldSpec("last_name", ValueType.STRING, mandatory=True),
        FieldSpec("email", ValueType.EMAIL, mandatory=True, uniqueness_requirement=UniquenessRequirement.MUST_BE_UNIQUE),
        FieldSpec("password", ValueType.STRING, mandatory=True),
        FieldSpec("confirm_password", ValueType.STRING, mandatory=True, dependency_reference="password"),
    ],
    documented_exceptional={
        "all_fields_blank": {
            "evidence": "NEG-01",
            "blank_fields": ["first_name", "last_name", "email", "password", "confirm_password"],
        },
        "password_mismatch": {
            "evidence": "NEG-02/REQ-REG-02",
            "override_fields": {"confirm_password": "__DELIBERATELY_DIFFERENT_FROM_PASSWORD__"},
        },
        "malformed_email": {
            "evidence": "NEG-03/REQ-REG-03",
            # literal evidence text from the Approved SRS's own Evidence Basis cell
            "override_fields": {"email": "not-an-email"},
        },
        "duplicate_email": {
            "evidence": "NEG-04/REQ-REG-04/Business Rule #1",
            # the point of this dataset IS reuse; the field must be
            # classified MAY_REUSE for this specific documented case,
            # never MUST_BE_UNIQUE, and it must literally equal a prior
            # accepted registration's email to be a real duplicate test.
            "uniqueness_override": {"email": UniquenessRequirement.MAY_REUSE},
        },
    },
)

# ---------------------------------------------------------------------------
# REQ-ACO-03 — Billing/Shipping address (Approved SRS §6.10)
# ---------------------------------------------------------------------------
_ADDRESS = ConstraintProfile(
    requirement_id="REQ-ACO-03",
    evidence_note="REQ-ACO-03: mandatory vs. optional address fields, directly enumerated.",
    field_specs=[
        FieldSpec("first_name", ValueType.STRING, mandatory=True),
        FieldSpec("last_name", ValueType.STRING, mandatory=True),
        FieldSpec("email", ValueType.EMAIL, mandatory=True),
        FieldSpec("country", ValueType.STRING, mandatory=True),
        FieldSpec("city", ValueType.STRING, mandatory=True),
        FieldSpec("address1", ValueType.STRING, mandatory=True),
        FieldSpec("zip_postal_code", ValueType.STRING, mandatory=True),
        FieldSpec("phone_number", ValueType.STRING, mandatory=True),
        FieldSpec("company", ValueType.STRING, mandatory=False),
        FieldSpec("address2", ValueType.STRING, mandatory=False),
        FieldSpec("fax_number", ValueType.STRING, mandatory=False),
    ],
    documented_exceptional={
        "mandatory_field_blank": {
            "evidence": "REQ-ACO-03 acceptance criteria (\"required fields left blank... progression blocked\")",
            "blank_fields": ["address1"],
        },
    },
)

# ---------------------------------------------------------------------------
# REQ-PAY-01 — Payment method selection (Approved SRS §6.12)
# ---------------------------------------------------------------------------
_PAYMENT_METHOD = ConstraintProfile(
    requirement_id="REQ-PAY-01",
    evidence_note="REQ-PAY-01: four payment methods directly observed and enumerated.",
    field_specs=[
        FieldSpec(
            "payment_method",
            ValueType.ENUM,
            mandatory=True,
            allowed_values=["Cash On Delivery", "Check / Money Order", "Credit Card", "Purchase Order"],
        ),
    ],
)

# ---------------------------------------------------------------------------
# REQ-CART-03 / NEG-07 — Cart quantity boundary (Approved SRS §6.7, §7)
# ---------------------------------------------------------------------------
_CART_QUANTITY = ConstraintProfile(
    requirement_id="REQ-CART-03",
    evidence_note="REQ-CART-03/NEG-07: quantity=0 is a directly documented boundary (treated as removal, not error).",
    field_specs=[
        FieldSpec("quantity", ValueType.INTEGER, mandatory=True),
    ],
    documented_boundary={
        "evidence": "REQ-CART-03/NEG-07",
        "field_name": "quantity",
        "field_value": 0,
        "boundary_classification": BoundaryClassification.MIN_BOUNDARY,
    },
)


_PROFILES: Dict[str, ConstraintProfile] = {
    "REQ-REG-01": _REGISTRATION,
    "REQ-ACO-03": _ADDRESS,
    "REQ-PAY-01": _PAYMENT_METHOD,
    "REQ-CART-03": _CART_QUANTITY,
}


def get_constraint_profile(requirement_id: str) -> Optional[ConstraintProfile]:
    """Returns the deterministic, evidence-cited constraint profile for a
    requirement ID, or None if no profile has yet been authored for it.
    None is a governance signal (spec sec. 9 INSUFFICIENT_EVIDENCE), never
    treated as "no constraints apply.\""""
    return _PROFILES.get(requirement_id)
