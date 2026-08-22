import pytest
from fde_lab.pocs.customer_onboarding_engineer.agent import CustomerOnboardingEngineerAgent

def test_onboarding_normal_scenario():
    agent = CustomerOnboardingEngineerAgent()
    report = agent.run("normal")
    
    assert report.customer_name == "Acme Health"
    assert report.validation.valid is True
    assert report.mapping.status == "READY"
    assert report.mapping.satisfied_count == 5
    assert len(report.mapping.missing) == 0
    assert len(report.mapping.unsupported) == 0
    assert report.config is not None
    assert "admin@acmehealth.com" in str(report.config)

def test_onboarding_incomplete_scenario():
    agent = CustomerOnboardingEngineerAgent()
    report = agent.run("incomplete")
    
    assert report.validation.valid is False
    assert "Duplicate user email" in str(report.validation.errors)
    assert report.mapping.status == "INCOMPLETE"
    assert "Analytics feature configuration" in report.mapping.missing
    assert "Slack integration credentials/configuration" in report.mapping.missing

def test_onboarding_unsupported_scenario():
    agent = CustomerOnboardingEngineerAgent()
    report = agent.run("unsupported")
    
    assert report.validation.valid is True
    assert report.mapping.status == "BLOCKED"
    assert any("salesforce" in s.lower() for s in report.mapping.unsupported)
