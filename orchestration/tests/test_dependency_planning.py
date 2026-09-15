"""Tests for orchestration/dependency_planning.py -- the 5-category
dependency-aware execution classification (Orchestration Expansion,
Phase E)."""
from __future__ import annotations

from orchestration.dependency_planning import ExecutionCategory, classify, classify_many


def test_independent_requirement_is_safe_parallel():
    c = classify("REQ-BRW-01")
    assert c.category == ExecutionCategory.SAFE_PARALLEL


def test_chained_wishlist_requirements_are_prerequisite_dependent():
    c2 = classify("REQ-WISH-02")
    assert c2.category == ExecutionCategory.PREREQUISITE_DEPENDENT
    assert c2.prerequisite_requirement_ids == ["REQ-WISH-01"]

    c3 = classify("REQ-WISH-03")
    assert c3.category == ExecutionCategory.PREREQUISITE_DEPENDENT
    assert c3.prerequisite_requirement_ids == ["REQ-WISH-01"]


def test_shared_account_root_requirement_is_exclusive_not_falsely_prerequisite():
    """REQ-REG-05's own notes mention downstream reusers (REQ-REG-04 etc)
    -- must not be misread as REG-05 depending on them."""
    c = classify("REQ-REG-05")
    assert c.category == ExecutionCategory.EXCLUSIVE
    assert c.prerequisite_requirement_ids == []


def test_guest_checkout_completion_is_exclusive_not_falsely_tied_to_authenticated_path():
    """REQ-GCO-03's own precondition text mentions REQ-ACO-01 only for
    comparison ('consistent with REQ-ACO-01's own mechanism'), not as an
    execution-ordering dependency -- must classify EXCLUSIVE (its own
    real, standalone, single-order resource), never a false
    PREREQUISITE_DEPENDENT on REQ-ACO-01."""
    c = classify("REQ-GCO-03")
    assert c.category == ExecutionCategory.EXCLUSIVE


def test_real_ordering_dependency_is_detected_with_evidence():
    c = classify("REQ-ACO-02")
    assert c.category == ExecutionCategory.PREREQUISITE_DEPENDENT
    assert c.prerequisite_requirement_ids == ["REQ-ACO-01"]
    assert "ACO-01" in c.evidence


def test_nonexistent_requirement_is_blocked():
    c = classify("REQ-DOES-NOT-EXIST-999")
    assert c.category == ExecutionCategory.BLOCKED


def test_classify_many_returns_one_entry_per_requirement():
    result = classify_many(["REQ-BRW-01", "REQ-WISH-01", "REQ-WISH-02"])
    assert set(result.keys()) == {"REQ-BRW-01", "REQ-WISH-01", "REQ-WISH-02"}
