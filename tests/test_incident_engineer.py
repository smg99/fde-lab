from fde_lab.pocs.incident_engineer.tools import (
    LogSearchTool, DeploymentHistoryTool, GitHistoryTool, MetricsTool, ServiceHealthTool
)
from fde_lab.pocs.incident_engineer.agent import IncidentEngineerAgent

def test_incident_engineer_tools_known_scenario():
    # Logs
    logs_tool = LogSearchTool("known")
    logs_data = logs_tool.execute("checkout-api")
    assert "database connection timeout" in " ".join(logs_data["logs"])

    # Deployments
    deps_tool = DeploymentHistoryTool("known")
    deps_data = deps_tool.execute()
    assert any(d["id"] == "#184" for d in deps_data["deployments"])

    # Git
    git_tool = GitHistoryTool("known")
    git_data = git_tool.execute("#184")
    assert "database connection pool configuration" in git_data["changes"][0]

    # Metrics
    metrics_tool = MetricsTool("known")
    metrics_data = metrics_tool.execute()
    assert any(m.get("database_connections") == "100%" for m in metrics_data["metrics"])

    # Health
    health_tool = ServiceHealthTool("known")
    health_data = health_tool.execute()
    assert health_data["database"]["connection_pool"] == "exhausted"
    assert health_data["checkout-api"]["status"] == "degraded"

def test_incident_engineer_tools_inconclusive_scenario():
    # Git
    git_tool = GitHistoryTool("inconclusive")
    git_data = git_tool.execute("#184")
    assert git_data["commit"] == "unknown"

    # Health
    health_tool = ServiceHealthTool("inconclusive")
    health_data = health_tool.execute()
    assert "connection_pool" not in health_data["database"]

def test_incident_engineer_agent_known():
    agent = IncidentEngineerAgent("known")
    report = agent.investigate("Checkout API failing")
    
    assert report.confidence == "High"
    assert len(report.observed_evidence) == 4
    assert "connection exhaustion" in report.likely_root_cause.lower()

def test_incident_engineer_agent_inconclusive():
    agent = IncidentEngineerAgent("inconclusive")
    report = agent.investigate("Checkout API failing")
    
    assert report.confidence == "Low"
    assert "Inconclusive" in report.likely_root_cause
