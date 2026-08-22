import pytest
from fde_lab.pocs.configuration_engineer.agent import ConfigurationEngineerAgent

def test_configuration_normal_scenario():
    agent = ConfigurationEngineerAgent()
    report = agent.run("normal")
    assert report.status == "valid"
    assert len(report.issues) == 0
    assert report.risk.requires_approval is False
    assert report.changes_applied is False

def test_configuration_missing_required_scenario():
    agent = ConfigurationEngineerAgent()
    report = agent.run("missing-required")
    assert report.status == "needs_changes"
    assert len(report.issues) > 0
    assert any(i.issue_type == "missing" for i in report.issues)
    assert any("provider" in i.path for i in report.issues)

def test_configuration_invalid_values_scenario():
    agent = ConfigurationEngineerAgent()
    report = agent.run("invalid-values")
    assert report.status == "needs_changes"
    assert any(i.issue_type == "invalid" for i in report.issues)

def test_configuration_conflicting_config_scenario():
    agent = ConfigurationEngineerAgent()
    report = agent.run("conflicting-config")
    assert report.status == "needs_changes"
    assert any(i.issue_type == "conflict" for i in report.issues)
    # Check that it identifies the legacy_api conflict
    assert any("legacy_api" in i.path for i in report.issues)

def test_configuration_unsafe_change_scenario():
    agent = ConfigurationEngineerAgent()
    report = agent.run("unsafe-change")
    assert report.status == "needs_changes"
    assert report.risk.level == "HIGH"
    assert report.action_required is True
    assert report.changes_applied is False
