"""
Post-MVP2 Enhancement 02 — test data for the new testcase corpus
(`enh02_testcases.py`). Synthetic, non-secret values only (per SRS
sec. 10: "Any future test data must use clearly synthetic values, not
real personal information"). `ENH02-TD-REG-05-01`'s email is generated
fresh at import time with a real, monotonically-unique timestamp suffix,
because it is the ONE real, one-time account this enhancement creates
(see `enh01_testcases.py`... `enh02_testcases.py`'s own
ENH02-TC-REQ-REG-05-AUTO-LOGIN docstring) -- re-importing this module in
a later, separate real run naturally produces a fresh unique email,
exactly matching the real registration-uniqueness rule (SRS sec. 10)
rather than colliding with a stale, hard-coded one.

**Real finding, this task:** REQ-AUTH-02's own quoted message ("The
credentials provided are incorrect") is real, live-verified to appear
only for a *registered* email with a wrong password. A non-existent
email instead produces a different, real message ("No customer account
found."). There is therefore no standalone, account-independent dataset
for REQ-AUTH-02 here -- its real automation (in
`automation/playwright/tests/test_enh02_shared_account.py`) reuses the
one real, shared account's email with a deliberately wrong password,
chained after `ENH02-TC-REQ-REG-05-AUTO-LOGIN`.
"""
from __future__ import annotations

import time

_SHARED_ACCOUNT_SUFFIX = int(time.time() * 1000)
_SHARED_ACCOUNT_EMAIL = f"enh02.shared.{_SHARED_ACCOUNT_SUFFIX}@example.test"
_SHARED_ACCOUNT_PASSWORD = "Enh02-Synthetic-Pw1"

ENH02_TESTDATA = [
    {
        "dataset_id": "ENH02-TD-REG-02-01",
        "testcase_id": "ENH02-TC-REQ-REG-02-MISMATCH",
        "requirement_ids": ["REQ-REG-02"],
        "data_category": "NEGATIVE",
        "purpose": "Valid identity fields, mismatched passwords",
        "fields": {
            "first_name": "Synthetic-FirstName",
            "last_name": "Synthetic-LastName",
            "email": f"enh02.reg02.{int(time.time() * 1000)}@example.test",
            "password": "Synthetic-Pw-One-1",
            "confirm_password": "Synthetic-Pw-Two-2",
        },
    },
    {
        "dataset_id": "ENH02-TD-REG-03-01",
        "testcase_id": "ENH02-TC-REQ-REG-03-MALFORMED-EMAIL",
        "requirement_ids": ["REQ-REG-03"],
        "data_category": "NEGATIVE",
        "purpose": "Valid identity fields, malformed email",
        "fields": {
            "first_name": "Synthetic-FirstName",
            "last_name": "Synthetic-LastName",
            "email": "not-an-email",
            "password": "Synthetic-Pw-1",
            "confirm_password": "Synthetic-Pw-1",
        },
    },
    {
        "dataset_id": "ENH02-TD-REG-05-01",
        "testcase_id": "ENH02-TC-REQ-REG-05-AUTO-LOGIN",
        "requirement_ids": ["REQ-REG-05", "REQ-REG-04", "REQ-AUTH-01", "REQ-AUTH-02", "REQ-AUTH-03", "REQ-ACCT-01", "REQ-CART-05", "REQ-PWR-01"],
        "data_category": "POSITIVE",
        "purpose": "The one, real, shared account this enhancement creates -- reused read-only by every dependent testcase.",
        "fields": {
            "first_name": "Enh02Shared",
            "last_name": "SyntheticUser",
            "email": _SHARED_ACCOUNT_EMAIL,
            "password": _SHARED_ACCOUNT_PASSWORD,
            "confirm_password": _SHARED_ACCOUNT_PASSWORD,
        },
    },
    {
        "dataset_id": "ENH02-TD-SRCH-01-01",
        "testcase_id": "ENH02-TC-REQ-SRCH-01-VALID-KEYWORD",
        "requirement_ids": ["REQ-SRCH-01"],
        "data_category": "POSITIVE",
        "purpose": "A real, known keyword expected to match existing products.",
        "fields": {"search_term": "book"},
    },
    {
        "dataset_id": "ENH02-TD-SRCH-02-01",
        "testcase_id": "ENH02-TC-REQ-SRCH-02-NO-RESULTS",
        "requirement_ids": ["REQ-SRCH-02"],
        "data_category": "NEGATIVE",
        "purpose": "A nonsense keyword guaranteed to match nothing.",
        "fields": {"search_term": "zzzznoresultxyz123"},
    },
]


def shared_account_credentials() -> dict:
    """Returns the one real, shared account's credentials -- the same
    values used by ENH02-TD-REG-05-01, exposed directly for tests that
    need to authenticate as this account without re-loading the dataset."""
    return {"email": _SHARED_ACCOUNT_EMAIL, "password": _SHARED_ACCOUNT_PASSWORD}


def persist_all() -> None:
    """Persists every ENH02 dataset via the shared, unmodified
    `persistence/envelope.py`, under a new, additive base dir
    (`automation/playwright/generated/testdata/`) -- making this new
    corpus a real, governed, persisted artifact rather than an in-memory
    dict only, exactly like every other capability in this project since
    CR-001. Idempotent: byte-identical re-persistence reuses the existing
    version (envelope.py's own content-hash rule)."""
    from persistence.envelope import REPO_ROOT, persist_artifact

    base_dir = REPO_ROOT / "automation" / "playwright" / "generated" / "testdata"
    for ds in ENH02_TESTDATA:
        persist_artifact(
            base_dir,
            artifact_id=ds["dataset_id"],
            payload=ds,
            generator="automation.playwright.enh02_testdata (Post-MVP2 Enhancement 02)",
            provenance={"testcase_id": ds["testcase_id"]},
        )
