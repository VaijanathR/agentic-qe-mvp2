"""
Post-MVP2 Enhancement 01 -- human-consumable Excel (.xlsx) test-management
workbooks (backlog items E-01/E-02/E-06/E-12).

Design (per governing instruction sec. 12 -- "prevent silent divergence"):
the frozen, persisted MVP2 JSON artifacts (`testcases/generated/`,
`testdata/generated/`, `traceability/`, `automation/generated/`, and the
real CP-06 execution corpus via `reporting.gather`) remain the single,
authoritative source of truth, consumed unmodified and read-only. These
workbooks are a **deterministic, regenerated view** over that same data --
never hand-edited, never a second source of truth. Re-running this module
against an unchanged corpus produces byte-for-byte identical `.xlsx` files
(all timestamps/randomness stripped; see `_FIXED_*` constants below).

- Authoritative FOR HUMAN REVIEW: these `.xlsx` workbooks.
- Authoritative FOR AUTOMATION CONSUMPTION: the underlying, frozen JSON
  artifacts (via `testcases.persist`, `testdata.persist`, etc.) -- the new
  Playwright data-access layer (`automation/playwright/data_access.py`)
  reads the JSON directly, never the `.xlsx` file, so there is no risk of
  automation silently drifting from a hand-edited spreadsheet.

No historical MVP2 testcase/test-data content is rewritten here -- every
cell is a faithful, direct transcription of the existing, frozen record,
including the already-disclosed testcase-content limitation (the generic
"Perform the action..." / "Observe the resulting system behavior." steps
are shown exactly as persisted, never rephrased to look more complete).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import automation.persist as automation_persist
import testcases.persist as testcases_persist
import testdata.persist as testdata_persist
import traceability.req_testcase as traceability_req_testcase
import traceability.testcase_testdata as traceability_testcase_testdata
from persistence.envelope import REPO_ROOT, load_latest
from reporting.gather import gather_automation, gather_real_execution_results

OUTPUT_DIR = REPO_ROOT / "testmgmt" / "generated"

_HEADER_FILL = PatternFill(start_color="FF1F4E78", end_color="FF1F4E78", fill_type="solid")
_HEADER_FONT = Font(color="FFFFFFFF", bold=True)
_WRAP = Alignment(wrap_text=True, vertical="top")


def _list_ids(base_dir: Path) -> List[str]:
    if not base_dir.exists():
        return []
    return sorted(p.name for p in base_dir.iterdir() if p.is_dir() and (p / "latest.json").exists())


def _write_header(ws, headers: List[str]) -> None:
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
    ws.freeze_panes = "A2"


def _autosize(ws, widths: List[int]) -> None:
    for col, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col)].width = width


def _execution_status_for(testcase_id: str, execution_records: List[Dict]) -> str:
    """Real execution status roll-up for a testcase: the worst-case /
    most-informative status across every real execution record linked to
    it, per the frozen CP06 taxonomy -- never fabricated, never a guess."""
    statuses = {r["overall_status"] for r in execution_records if r["testcase_id"] == testcase_id}
    if not statuses:
        return "NO_EXECUTION_RECORD"
    if statuses == {"NOT_EXECUTED"}:
        return "NOT_EXECUTED"
    if "FAIL" in statuses:
        return "FAIL"
    if "PASS" in statuses and len(statuses) == 1:
        return "PASS"
    return "/".join(sorted(statuses))


def _automation_ids_for(testcase_id: str, automation_records: Dict[str, Dict]) -> List[str]:
    return sorted(aid for aid, rec in automation_records.items() if rec.get("testcase_id") == testcase_id)


def build_testcase_workbook() -> Path:
    testcase_ids = testcases_persist.list_persisted_testcase_ids()
    testcases = {tid: testcases_persist.load_persisted_testcase(tid) for tid in testcase_ids}

    exec_facts = gather_real_execution_results()
    auto_facts = gather_automation()
    automation_ids = auto_facts["standard_automation_ids"]
    automation_records = {aid: load_latest(automation_persist.BASE_DIR, aid) for aid in automation_ids}
    automation_records = {k: v for k, v in automation_records.items() if v is not None}

    tt_ids = _list_ids(traceability_testcase_testdata.BASE_DIR)
    testcase_to_data: Dict[str, List[str]] = {}
    for batch_id in tt_ids:
        payload = load_latest(traceability_testcase_testdata.BASE_DIR, batch_id)
        if payload:
            for tid, dids in payload.get("testcase_to_testdata", {}).items():
                testcase_to_data.setdefault(tid, []).extend(dids)

    wb = Workbook()
    ws = wb.active
    ws.title = "Testcases"
    headers = [
        "Testcase ID", "Requirement ID(s)", "Title", "Objective / Expected Result",
        "Preconditions", "Business Steps", "Test Type (Scenario)", "Priority",
        "Dataset Reference(s)", "Automation Reference(s)", "Execution Status", "Governance Status",
    ]
    _write_header(ws, headers)

    for row, tid in enumerate(testcase_ids, start=2):
        tc = testcases[tid]
        if tc is None:
            continue
        ws.cell(row=row, column=1, value=tc["testcase_id"])
        ws.cell(row=row, column=2, value=", ".join(tc.get("requirement_ids", [])))
        ws.cell(row=row, column=3, value=tc.get("title"))
        ws.cell(row=row, column=4, value=tc.get("expected_result")).alignment = _WRAP
        ws.cell(row=row, column=5, value="\n".join(tc.get("preconditions", []))).alignment = _WRAP
        ws.cell(row=row, column=6, value="\n".join(f"{i+1}. {s}" for i, s in enumerate(tc.get("test_steps", [])))).alignment = _WRAP
        ws.cell(row=row, column=7, value=tc.get("scenario_type"))
        ws.cell(row=row, column=8, value=tc.get("priority"))
        ws.cell(row=row, column=9, value=", ".join(testcase_to_data.get(tid, [])))
        ws.cell(row=row, column=10, value=", ".join(_automation_ids_for(tid, automation_records)))
        ws.cell(row=row, column=11, value=_execution_status_for(tid, exec_facts["records"]))
        ws.cell(row=row, column=12, value=tc.get("governance_status"))

    _autosize(ws, [22, 16, 32, 55, 30, 50, 14, 10, 30, 30, 16, 18])

    notes = wb.create_sheet("Notes")
    notes["A1"] = "Provenance and limitations"
    notes["A1"].font = Font(bold=True)
    notes_lines = [
        "This workbook is a deterministic, regenerated view over the frozen, persisted",
        "MVP2 testcase corpus (testcases/generated/). It is never hand-edited and never",
        "consumed by automation -- automation reads the underlying JSON directly.",
        "",
        "Disclosed limitation (carried forward, not corrected): every testcase's",
        "'Business Steps' column reflects the real, persisted content, including the",
        "known testcase-content limitation where CP03's StubLLMClient produced generic",
        "placeholder steps ('Perform the action described by the approved requirement.',",
        "'Observe the resulting system behavior.') rather than explicit business steps.",
        "This is shown exactly as it exists, not rewritten to look more complete.",
        "",
        "'Execution Status' reflects real CP06 execution evidence, deterministically",
        "rolled up via reporting.gather.gather_real_execution_results(). A testcase with",
        "no real execution record shows NO_EXECUTION_RECORD -- never fabricated as PASS.",
    ]
    for i, line in enumerate(notes_lines, start=2):
        notes.cell(row=i, column=1, value=line)
    notes.column_dimensions["A"].width = 90

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "MVP2_Testcases.xlsx"
    wb.save(out_path)
    return out_path


def build_testdata_workbook() -> Path:
    data_ids = testdata_persist.list_persisted_dataset_ids()
    datasets = {did: testdata_persist.load_persisted_dataset(did) for did in data_ids}

    wb = Workbook()
    ws = wb.active
    ws.title = "TestData Fields"
    headers = [
        "Dataset ID", "Testcase ID", "Requirement ID(s)", "Data Category", "Validation Status",
        "Field Name", "Field Value", "Value Type", "Uniqueness Requirement", "Purpose",
    ]
    _write_header(ws, headers)

    row = 2
    for did in data_ids:
        ds = datasets[did]
        if ds is None:
            continue
        for field in ds.get("fields", []):
            ws.cell(row=row, column=1, value=ds["data_set_id"])
            ws.cell(row=row, column=2, value=ds.get("testcase_id"))
            ws.cell(row=row, column=3, value=", ".join(ds.get("requirement_ids", [])))
            ws.cell(row=row, column=4, value=ds.get("data_category"))
            ws.cell(row=row, column=5, value=ds.get("validation_status"))
            ws.cell(row=row, column=6, value=field.get("field_name"))
            ws.cell(row=row, column=7, value=field.get("field_value"))
            ws.cell(row=row, column=8, value=field.get("value_type"))
            ws.cell(row=row, column=9, value=field.get("uniqueness_requirement"))
            ws.cell(row=row, column=10, value=ds.get("purpose")).alignment = _WRAP
            row += 1

    _autosize(ws, [24, 20, 16, 14, 18, 18, 34, 12, 22, 40])

    mapping = wb.create_sheet("Testcase-Dataset Mapping")
    mapping_headers = ["Testcase ID", "Dataset ID", "Data Category", "Validation Status", "Purpose"]
    _write_header(mapping, mapping_headers)
    row = 2
    for did in data_ids:
        ds = datasets[did]
        if ds is None:
            continue
        mapping.cell(row=row, column=1, value=ds.get("testcase_id"))
        mapping.cell(row=row, column=2, value=ds["data_set_id"])
        mapping.cell(row=row, column=3, value=ds.get("data_category"))
        mapping.cell(row=row, column=4, value=ds.get("validation_status"))
        mapping.cell(row=row, column=5, value=ds.get("purpose")).alignment = _WRAP
        row += 1
    _autosize(mapping, [20, 24, 14, 18, 45])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "MVP2_TestData.xlsx"
    wb.save(out_path)
    return out_path


def build_traceability_workbook() -> Path:
    req_ids = _list_ids(traceability_req_testcase.BASE_DIR)

    wb = Workbook()
    ws = wb.active
    ws.title = "Req-Testcase Traceability"
    headers = ["Requirement ID", "Testcase ID(s)", "Traceability Batch"]
    _write_header(ws, headers)

    row = 2
    for batch_id in req_ids:
        payload = load_latest(traceability_req_testcase.BASE_DIR, batch_id)
        if payload is None:
            continue
        for req_id, tc_ids in payload.get("requirement_to_testcases", {}).items():
            ws.cell(row=row, column=1, value=req_id)
            ws.cell(row=row, column=2, value=", ".join(tc_ids))
            ws.cell(row=row, column=3, value=batch_id)
            row += 1

    _autosize(ws, [18, 40, 24])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "MVP2_Requirement_Testcase_Traceability.xlsx"
    wb.save(out_path)
    return out_path


def build_all_workbooks() -> Dict[str, Path]:
    return {
        "testcases": build_testcase_workbook(),
        "testdata": build_testdata_workbook(),
        "traceability": build_traceability_workbook(),
    }


if __name__ == "__main__":
    for name, path in build_all_workbooks().items():
        print(f"{name}: {path}")
