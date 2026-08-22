import pytest
from fde_lab.pocs.solution_engineer.agent import SolutionEngineerAgent

def test_solution_normal_scenario():
    agent = SolutionEngineerAgent()
    report = agent.run("normal")
    assert report.status == "ready"
    assert len(report.gaps) == 0
    assert len(report.conflicts) == 0
    assert report.requires_customer_input is False
    assert report.confidence == "HIGH"
    
def test_solution_constrained_environment_scenario():
    agent = SolutionEngineerAgent()
    report = agent.run("constrained-environment")
    assert report.status == "ready"
    assert any("Restricted deployment window" in r.description for r in report.risks)

def test_solution_integration_gap_scenario():
    agent = SolutionEngineerAgent()
    report = agent.run("integration-gap")
    assert report.status == "ready"
    assert len(report.gaps) > 0
    assert any("Payment Provider lacks 'subscription' capability" in g.description for g in report.gaps)

def test_solution_conflicting_requirements_scenario():
    agent = SolutionEngineerAgent()
    report = agent.run("conflicting-requirements")
    assert report.status == "conflict_detected"
    assert len(report.conflicts) > 0
    assert report.requires_customer_input is True

def test_solution_insufficient_information_scenario():
    agent = SolutionEngineerAgent()
    report = agent.run("insufficient-information")
    assert report.status == "needs_customer_input"
    assert report.requires_customer_input is True
    assert len(report.customer_questions) > 0
