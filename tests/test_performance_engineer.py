import pytest
from fde_lab.pocs.performance_engineer.agent import PerformanceEngineerAgent

def test_performance_normal_scenario():
    agent = PerformanceEngineerAgent()
    report = agent.run("normal")
    assert report.diagnosis.category == "healthy"
    assert report.diagnosis.confidence == "HIGH"
    assert "healthy" in report.evidence[0]

def test_performance_database_bottleneck_scenario():
    agent = PerformanceEngineerAgent()
    report = agent.run("database-bottleneck")
    assert report.diagnosis.category == "database"
    assert "Q184" in report.evidence[2]

def test_performance_external_api_bottleneck_scenario():
    agent = PerformanceEngineerAgent()
    report = agent.run("external-api-bottleneck")
    assert report.diagnosis.category == "external_api"

def test_performance_application_bottleneck_scenario():
    agent = PerformanceEngineerAgent()
    report = agent.run("application-bottleneck")
    assert report.diagnosis.category == "application"
    assert report.diagnosis.confidence == "HIGH"

def test_performance_inconclusive_scenario():
    agent = PerformanceEngineerAgent()
    report = agent.run("inconclusive")
    assert report.diagnosis.category == "inconclusive"
    assert report.diagnosis.confidence == "LOW"
