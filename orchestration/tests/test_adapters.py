"""
Tests for the two structural adapters this package adds:
`execution_result_adapter.py` (Enhancement-01/02 ExecutionLogRecord ->
CP-06 ExecutionResult) and `enh02_adapter.py` (Enhancement-02 testcase
corpus -> CP-03 GovernedTestcase). Both are pure, deterministic
field-mapping code -- no Playwright/real SUT required to test them.
"""
from __future__ import annotations

from orchestration.enh02_adapter import governed_testcases_for_requirement
from orchestration.execution_result_adapter import _infer_action_type, adapt_and_persist
from testcases.schema import GovernanceStatus, ScenarioType


def test_action_type_inference_from_real_business_step_descriptions():
    from automation.schema import ActionType

    assert _infer_action_type("Navigate to the Books top-level category") == ActionType.NAVIGATE
    assert _infer_action_type("Fill real account email") == ActionType.FILL
    assert _infer_action_type("Observe the resulting page for a rendered product grid") == ActionType.ASSERT
    assert _infer_action_type("Select 'Checkout as Guest'") == ActionType.CLICK


def test_adapt_and_persist_maps_a_real_shaped_execution_log():
    fake_log = {
        "execution_id": "TEST-ADAPTER-EXEC-0001",
        "requirement_ids": ["REQ-BRW-01"],
        "testcase_id": "ENH02-TC-REQ-BRW-01-CATEGORY-GRID",
        "dataset_id": "NO-DATASET",
        "automation_id": "ENH02-PW-TC-REQ-BRW-01-CATEGORY-GRID",
        "browser": "chromium",
        "browser_version": "999.0.0.0",
        "environment": "Windows",
        "worker_id": "test",
        "start_time": "2026-01-01T00:00:00+00:00",
        "end_time": "2026-01-01T00:00:05+00:00",
        "duration_seconds": 5.0,
        "steps": [
            {"step_order": 1, "description": "Navigate to the Books top-level category", "status": "PASS"},
            {"step_order": 2, "description": "Observe the resulting page for a rendered product grid", "status": "PASS"},
        ],
        "final_status": "PASS",
        "failure_category": None,
        "error_detail": None,
        "evidence_references": [],
        "generation_metadata": {},
    }
    persisted = adapt_and_persist(fake_log)
    assert persisted["execution_id"] == "TEST-ADAPTER-EXEC-0001"
    assert "path" in persisted

    from rca.ingest import load_execution_result

    reloaded = load_execution_result("TEST-ADAPTER-EXEC-0001")
    assert reloaded is not None
    assert reloaded["overall_status"] == "PASS"
    assert reloaded["testcase_id"] == "ENH02-TC-REQ-BRW-01-CATEGORY-GRID"
    assert len(reloaded["step_results"]) == 2


def test_enh02_adapter_preserves_real_business_steps_verbatim():
    governed = governed_testcases_for_requirement("REQ-BRW-01")
    assert len(governed) == 1
    g = governed[0]
    assert g.governance_status == GovernanceStatus.ACCEPTED
    assert g.testcase.scenario_type == ScenarioType.POSITIVE
    assert g.testcase.test_steps  # non-empty, real business steps
    assert any("Books" in step for step in g.testcase.test_steps)
