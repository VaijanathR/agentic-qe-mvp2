"""
Tests for automation/playwright/ -- the new, additive Post-MVP2 Enhancement
01 Playwright POM foundation. Deterministic, real-corpus-backed unit tests
for the locator-fallback and data-access layers (no live browser required);
the real, live browser test itself lives in
automation/playwright/tests/test_enh01_registration.py and is run
separately against the real SUT (see the enhancement report for its
results -- never mocked here or there).
"""
from __future__ import annotations

import pytest

from automation.playwright.data_access import (
    DatasetNotFoundError,
    RequiredFieldMissingError,
    load_dataset,
)
from automation.playwright.locators import (
    LocatorCandidate,
    REGISTRATION_FORM_CANDIDATES,
    resolve_with_fallback,
)


# ---------------------------------------------------------------------------
# Locator fallback
# ---------------------------------------------------------------------------

def test_resolve_with_fallback_uses_primary_when_it_succeeds():
    candidates = [
        LocatorCandidate("ID", "#a", "test", 1),
        LocatorCandidate("LABEL", "label=A", "test", 2),
    ]
    result = resolve_with_fallback("field", candidates, lambda c: c.priority == 1)
    assert result.resolved_candidate["priority"] == 1
    assert result.used_fallback is False
    assert len(result.attempted) == 1


def test_resolve_with_fallback_falls_back_when_primary_fails():
    candidates = [
        LocatorCandidate("ID", "#a", "test", 1),
        LocatorCandidate("LABEL", "label=A", "test", 2),
    ]
    result = resolve_with_fallback("field", candidates, lambda c: c.priority == 2)
    assert result.resolved_candidate["priority"] == 2
    assert result.used_fallback is True
    assert len(result.attempted) == 2
    assert result.attempted[0]["outcome"] == "FAILED"
    assert result.attempted[1]["outcome"] == "SUCCESS"


def test_resolve_with_fallback_reports_full_failure_when_no_candidate_resolves():
    candidates = [LocatorCandidate("ID", "#a", "test", 1)]
    result = resolve_with_fallback("field", candidates, lambda c: False)
    assert result.resolved_candidate is None
    assert result.used_fallback is False
    assert len(result.attempted) == 1
    assert result.attempted[0]["outcome"] == "FAILED"


def test_resolve_with_fallback_never_silently_skips_a_failed_attempt():
    """Every attempt, success or failure, must be recorded -- this is the
    'no silent self-healing' governance requirement (sec. 20)."""
    calls = []

    def try_candidate(c):
        calls.append(c.priority)
        return c.priority == 3

    candidates = [LocatorCandidate("ID", f"#c{i}", "test", i) for i in (1, 2, 3)]
    result = resolve_with_fallback("field", candidates, try_candidate)
    assert calls == [1, 2, 3]
    assert len(result.attempted) == 3
    assert [a["outcome"] for a in result.attempted] == ["FAILED", "FAILED", "SUCCESS"]


def test_registration_form_candidates_are_real_evidence_backed_not_invented():
    for field_name, candidates in REGISTRATION_FORM_CANDIDATES.items():
        assert len(candidates) >= 2, f"{field_name} should have multiple evidence-backed candidates"
        priorities = [c.priority for c in candidates]
        assert priorities == sorted(priorities), f"{field_name} candidates must be in priority order"
        for c in candidates:
            assert c.source.startswith("live capture:"), f"{field_name} candidate {c} is not marked as real, live-captured evidence"


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------

def test_load_dataset_real_blank_validation_dataset():
    ds = load_dataset("TD-TC-REQ-REG-01-01-02", required_fields=["first_name", "last_name", "email", "password", "confirm_password"])
    assert ds.testcase_id == "TC-REQ-REG-01-01"
    assert ds.fields["first_name"] == ""


def test_load_dataset_missing_raises_not_found():
    with pytest.raises(DatasetNotFoundError):
        load_dataset("TD-DOES-NOT-EXIST-EVER")


def test_load_dataset_missing_required_field_raises():
    with pytest.raises(RequiredFieldMissingError):
        load_dataset("TD-TC-REQ-REG-01-01-02", required_fields=["field_that_does_not_exist"])
