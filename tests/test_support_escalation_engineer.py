import pytest
from fde_lab.pocs.support_escalation_engineer.agent import SupportEscalationEngineerAgent
from fde_lab.pocs.support_escalation_engineer.models import IssueClassification, Severity, Reproducibility

def test_escalation_normal_scenario():
    agent = SupportEscalationEngineerAgent()
    report = agent.run("normal")
    
    assert report.customer == "Acme Commerce"
    assert report.issue.reproducibility == Reproducibility.REPRODUCIBLE
    assert report.issue.classification == IssueClassification.PRODUCT_BUG
    assert report.issue.severity == Severity.HIGH
    assert report.reproduction.status == Reproducibility.REPRODUCIBLE
    
    assert hasattr(report, "escalation_json_path")
    assert hasattr(report, "evidence_json_path")
    assert hasattr(report, "reproduction_md_path")
    assert hasattr(report, "escalation_md_path")

def test_escalation_not_reproducible_scenario():
    agent = SupportEscalationEngineerAgent()
    report = agent.run("not-reproducible")
    
    assert report.issue.reproducibility == Reproducibility.NOT_REPRODUCIBLE
    assert report.issue.classification == IssueClassification.UNKNOWN
    assert report.issue.severity == Severity.LOW
    assert report.reproduction.status == Reproducibility.NOT_REPRODUCIBLE
    
    # Crucially, the agent should recommend getting more info from the customer
    assert len(report.recommended_next_steps) > 0
    assert any("request ids" in s.lower() for s in report.recommended_next_steps)

def test_escalation_product_bug_scenario():
    agent = SupportEscalationEngineerAgent()
    report = agent.run("product-bug")
    
    assert report.issue.reproducibility == Reproducibility.REPRODUCIBLE
    assert report.issue.classification == IssueClassification.PRODUCT_BUG
    assert report.issue.severity == Severity.HIGH
    
    # Should identify the column issue
    assert any("column" in e.observation.lower() for e in report.evidence)

def test_escalation_customer_configuration_scenario():
    agent = SupportEscalationEngineerAgent()
    report = agent.run("customer-configuration")
    
    assert report.issue.reproducibility == Reproducibility.REPRODUCIBLE
    assert report.issue.classification == IssueClassification.CUSTOMER_CONFIGURATION
    assert report.issue.severity == Severity.MEDIUM
    
    # Should recommend fixing the API key
    assert len(report.recommended_next_steps) > 0
    assert any("api key" in s.lower() for s in report.recommended_next_steps)
