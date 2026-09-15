"""
Agentic QE Orchestration -- Test Data Selection / Generation (governing
instruction sec. 19, 20).

Selection-first, mirroring `testcase_orchestration.py`: reuses whichever
real dataset already exists (Enhancement-02's `enh02_testdata.py` corpus,
via the testcase's own `dataset_ids`, then the frozen CP-MVP2-04
persisted corpus via `testdata.persist`) before ever generating anything
new. Generation, when genuinely required, goes through the frozen,
unmodified CP-MVP2-04 pipeline (`testdata.pipeline.run_cp_mvp2_04`),
defaulting to `StubTestDataClient` (deterministic, non-fabricating).

Data governance (sec. 20): before any state-changing generation this
module records whether the underlying testcase already implies a
permanent-state action (read-only vs. mutating), never creates SUT state
itself (this module produces field VALUES only -- no browser action).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.lib.retrieval import KnowledgeBase
from llm.test_data_client import StubTestDataClient, TestDataLLMClient
from orchestration.safe_persistence import safe_load_latest
from testdata.persist import BASE_DIR as TESTDATA_BASE_DIR
from testdata.persist import list_persisted_dataset_ids
from testdata.pipeline import run_cp_mvp2_04


def _enh02_dataset_declared(testcase_id: str) -> Optional[List[str]]:
    """Returns the Enhancement-02 corpus's own declared `dataset_ids`
    for `testcase_id` if that testcase exists there (possibly an empty
    list, meaning "no dataset required by design" -- e.g.
    ENH02-TC-REQ-BRW-01-CATEGORY-GRID is a pure navigation/observation
    testcase), or None if the testcase is not from that corpus at all."""
    from automation.playwright.enh02_testcases import ENH02_TESTCASES

    for e in ENH02_TESTCASES:
        if e["testcase_id"] == testcase_id:
            return list(e.get("dataset_ids", []))
    return None


def select_or_generate(
    testcase_id: str,
    kb: Optional[KnowledgeBase] = None,
    llm: Optional[TestDataLLMClient] = None,
    governed_testcase=None,
) -> Dict:
    declared = _enh02_dataset_declared(testcase_id)
    if declared is not None:
        if declared:
            return {
                "testcase_id": testcase_id,
                "mode": "REUSE",
                "corpus_source": "Enhancement-02 real test data corpus",
                "dataset_ids": declared,
                "generated": None,
            }
        return {
            "testcase_id": testcase_id,
            "mode": "NOT_REQUIRED",
            "corpus_source": "Enhancement-02 real testcase corpus (declares zero datasets by design)",
            "dataset_ids": [],
            "generated": None,
        }

    persisted_by_tc = []
    for did in list_persisted_dataset_ids():
        payload = safe_load_latest(TESTDATA_BASE_DIR, did)
        if (payload or {}).get("testcase_id") == testcase_id:
            persisted_by_tc.append(did)
    if persisted_by_tc:
        return {
            "testcase_id": testcase_id,
            "mode": "REUSE",
            "corpus_source": "CP-MVP2-04 persisted corpus",
            "dataset_ids": persisted_by_tc,
            "generated": None,
        }

    if governed_testcase is None:
        return {
            "testcase_id": testcase_id,
            "mode": "BLOCKED",
            "corpus_source": None,
            "dataset_ids": [],
            "note": "No existing dataset found and no governed_testcase was supplied to generate from.",
        }

    kb = kb or KnowledgeBase.load()
    llm = llm or StubTestDataClient()
    report = run_cp_mvp2_04(kb, llm, [governed_testcase])

    return {
        "testcase_id": testcase_id,
        "mode": "GENERATE",
        "corpus_source": "newly generated via CP-MVP2-04 pipeline",
        "generator": llm.model_name,
        "generated": report,
        "dataset_ids": [d["data_set_id"] for d in report.get("governed_datasets", [])] if "governed_datasets" in report else [],
    }
