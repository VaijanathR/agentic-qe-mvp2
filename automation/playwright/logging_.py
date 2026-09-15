"""
Post-MVP2 Enhancement 01 -- Playwright execution logging (governing
instruction sec. 23/24).

Every real execution is recorded with enough structured detail to permit
reconstruction of the execution: identity (Execution/Requirement/Testcase/
Dataset/Automation IDs), environment (browser, browser version, worker
ID), timing, step results, final status, failure classification, error
detail, locator-resolution/fallback detail, and evidence references.
Persisted via the unmodified, shared `persistence/envelope.py`, matching
this project's established pattern -- never fabricated, never a mock
result presented as real.
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from automation.playwright.config import EXECUTIONS_ROOT
from persistence.envelope import list_artifact_ids, load_latest, persist_artifact


class ExecutionStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class StepLogEntry:
    step_order: int
    description: str
    status: str
    locator_resolution: Optional[Dict] = None
    error_detail: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionLogRecord:
    execution_id: str
    requirement_ids: List[str]
    testcase_id: str
    dataset_id: str
    automation_id: str
    browser: str
    browser_version: str
    environment: str
    worker_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    steps: List[Dict] = field(default_factory=list)
    final_status: str = ExecutionStatus.NOT_EXECUTED
    failure_category: Optional[str] = None
    error_detail: Optional[str] = None
    evidence_references: List[str] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def persist_execution_log(record: ExecutionLogRecord) -> Dict:
    return persist_artifact(
        EXECUTIONS_ROOT,
        artifact_id=record.execution_id,
        payload=record.to_dict(),
        generator="automation.playwright (Post-MVP2 Enhancement 01, real, non-mocked execution)",
        provenance={"testcase_id": record.testcase_id, "dataset_id": record.dataset_id},
    )


def load_execution_log(execution_id: str) -> Optional[Dict]:
    return load_latest(EXECUTIONS_ROOT, execution_id)


def list_execution_log_ids() -> List[str]:
    return list_artifact_ids(EXECUTIONS_ROOT)


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
