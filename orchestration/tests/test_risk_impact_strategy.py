"""Tests for orchestration/risk.py, impact.py, test_strategy.py --
reuse of the real CR-001 RBTP / Dependency Matrix pipelines."""
from __future__ import annotations

from orchestration import impact, risk, test_strategy
from rbtp.schema import RiskLevel


def test_risk_assessment_for_known_requirement_uses_enh02_corpus():
    result = risk.assess("REQ-BRW-01")
    assert result["corpus_source"] == "Enhancement-02 real testcase corpus (adapted)"
    assert result["records"]


def test_risk_assessment_for_unknown_requirement_is_disclosed_not_fabricated():
    result = risk.assess("REQ-DOES-NOT-EXIST-999")
    assert result["records"] == []
    assert result["corpus_source"] is None


def test_risk_unknown_dimensions_never_silently_upgraded():
    result = risk.assess("REQ-BRW-01")
    rec = result["records"][0]
    assert rec["risk_likelihood"] == RiskLevel.UNKNOWN
    assert rec["change_impact"] == RiskLevel.UNKNOWN
    assert rec["defect_history"] == RiskLevel.UNKNOWN
    assert rec["dependency_impact"] == RiskLevel.UNKNOWN


def test_impact_analysis_for_known_requirement():
    result = impact.analyze("REQ-BRW-01")
    assert "ENH02-TC-REQ-BRW-01-CATEGORY-GRID" in result["directly_impacted_testcase_ids"]
    assert result["performance_relevant"] is True
    assert "PERF-REQ-BRW-01-catalog-browse" in result["performance_testcase_ids"]


def test_impact_analysis_for_unknown_requirement_is_disclosed():
    result = impact.analyze("REQ-DOES-NOT-EXIST-999")
    assert result["directly_impacted_testcase_ids"] == []
    assert result["corpus_source"] is None


def test_strategy_reports_covered_and_missing_scenario_types():
    result = test_strategy.determine_strategy("REQ-BRW-01")
    assert "POSITIVE" in result["covered_scenario_types"]
    assert "ALTERNATE" in result["missing_scenario_types"]
    assert "EXCEPTIONAL" in result["missing_scenario_types"]
