"""
Post-MVP2 Enhancement 01/02 -- test-data access layer (backlog item E-16 /
governing instruction sec. 16).

Automation never hard-codes a business dataset. It loads a dataset strictly
by `Dataset ID`, checking two real, persisted, authoritative-for-automation
sources in order -- never the human-consumable `.xlsx` workbook (which is a
generated view, not a source; see `testmgmt/generate_workbooks.py`'s own
module docstring for the full provenance rule):

1. The frozen, MVP2-baseline `testdata/generated/` JSON corpus (CP04,
   via the unmodified `testdata.persist` module) -- its payload shape
   stores fields as a list of `{field_name, field_value}` dicts.
2. The new, additive Enhancement-02 dataset corpus, persisted via the
   same shared `persistence/envelope.py` under
   `automation/playwright/generated/testdata/` (`enh02_testdata.py`'s
   own `persist_all()`) -- its payload shape stores fields as a plain
   `{field_name: field_value}` dict directly.

This is what prevents the Excel/JSON "two uncontrolled sources of truth"
problem the governing instruction (sec. 12) warns against -- both real
corpora remain governed, persisted JSON; nothing is ever read from Excel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import testdata.persist as testdata_persist
from persistence.envelope import REPO_ROOT, load_latest

_ENH02_TESTDATA_BASE_DIR = REPO_ROOT / "automation" / "playwright" / "generated" / "testdata"


class DatasetNotFoundError(LookupError):
    pass


class RequiredFieldMissingError(ValueError):
    pass


@dataclass
class ResolvedDataset:
    data_set_id: str
    testcase_id: str
    requirement_ids: list
    fields: Dict[str, str]
    raw: Dict


def load_dataset(data_set_id: str, required_fields: Optional[list] = None) -> ResolvedDataset:
    """Loads a real, persisted dataset by ID. Raises DatasetNotFoundError
    if it does not exist -- never silently fabricates one. Validates that
    every field in `required_fields` is present, raising
    RequiredFieldMissingError otherwise (fail fast, never proceed with an
    incomplete dataset)."""
    payload = testdata_persist.load_persisted_dataset(data_set_id)
    if payload is not None:
        fields = {f["field_name"]: f["field_value"] for f in payload.get("fields", [])}
    else:
        payload = load_latest(_ENH02_TESTDATA_BASE_DIR, data_set_id)
        if payload is None:
            raise DatasetNotFoundError(f"No persisted dataset for data_set_id={data_set_id!r}")
        fields = dict(payload.get("fields", {}))

    if required_fields:
        missing = [f for f in required_fields if f not in fields]
        if missing:
            raise RequiredFieldMissingError(
                f"Dataset {data_set_id!r} is missing required field(s) {missing} needed by this automation."
            )

    return ResolvedDataset(
        data_set_id=payload.get("data_set_id") or payload.get("dataset_id"),
        testcase_id=payload.get("testcase_id"),
        requirement_ids=payload.get("requirement_ids", []),
        fields=fields,
        raw=payload,
    )
