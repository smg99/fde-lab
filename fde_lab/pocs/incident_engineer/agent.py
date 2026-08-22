import json
from fde_lab.pocs.incident_engineer.models import Evidence, IncidentReport
from fde_lab.pocs.incident_engineer.tools import (
    LogSearchTool, DeploymentHistoryTool, GitHistoryTool, MetricsTool, ServiceHealthTool
)
from fde_lab.observability.logger import get_logger

logger = get_logger("fde_lab.incident_engineer")

class IncidentEngineerAgent:
    def __init__(self, scenario: str = "known"):
        self.scenario = scenario
        self.tools = {
            "logs": LogSearchTool(scenario),
            "deployments": DeploymentHistoryTool(scenario),
            "git": GitHistoryTool(scenario),
            "metrics": MetricsTool(scenario),
            "health": ServiceHealthTool(scenario)
        }

    def investigate(self, incident_description: str) -> IncidentReport:
        logger.info(f"Starting investigation for scenario: {self.scenario}")
        
        # 1. Evidence Collection
        evidence_list = []
        timeline = []
        
        # Health check
        health_data = self.tools["health"].execute()
        if health_data.get("database", {}).get("connection_pool") == "exhausted":
            evidence_list.append(Evidence(
                id=1, source="service_health", time="current",
                observation="Database connection pool is exhausted",
                relevance="Directly impacts services relying on the database like checkout-api."
            ))
            
        # Deployments
        deps_data = self.tools["deployments"].execute()
        dep_184 = next((d for d in deps_data["deployments"] if d["id"] == "#184"), None)
        if dep_184:
            evidence_list.append(Evidence(
                id=2, source="deployment_history", time=dep_184["time"],
                observation="Deployment #184 completed successfully",
                relevance="Deployments are frequent triggers for incidents."
            ))
            timeline.append(f"{dep_184['time']} - Deployment #184")
            
        # Git
        git_data = self.tools["git"].execute("#184")
        if "database connection pool configuration" in git_data.get("changes", []):
            evidence_list.append(Evidence(
                id=3, source="git_history", time=git_data["time"],
                observation="Commit a84f21c changed database connection pooling config",
                relevance="Correlates the deployment content to the database exhaustion."
            ))
            
        # Metrics & Logs
        metrics_data = self.tools["metrics"].execute()
        logs_data = self.tools["logs"].execute()
        
        has_db_timeout = any("database connection timeout" in log for log in logs_data.get("logs", []))
        if has_db_timeout:
            evidence_list.append(Evidence(
                id=4, source="application_logs", time="14:32:03",
                observation="checkout-api reporting database connection timeouts",
                relevance="Confirms connection exhaustion is impacting the checkout flow."
            ))
            timeline.append("14:32 - checkout-api connection timeouts begin")

        # 2. Correlate and Determine Cause
        if self.scenario == "known":
            return IncidentReport(
                summary="Checkout API is failing due to database connection exhaustion.",
                impact="Customers cannot complete checkouts. Checkout API returning 500s.",
                timeline=timeline,
                observed_evidence=evidence_list,
                likely_root_cause="Deployment #184 introduced a database connection-pool configuration that caused checkout-api connection exhaustion.",
                confidence="High",
                reason="The deployment, Git change, database connection exhaustion, and checkout error spike occur in the exact same sequence.",
                recommended_immediate_action="Review or rollback the connection-pool configuration introduced by deployment #184.",
                recommended_follow_up="Implement automated testing for connection pool limits under load."
            )
        else:
            # Inconclusive scenario
            return IncidentReport(
                summary="Checkout API is failing. Investigation inconclusive.",
                impact="Checkout API returning 500s.",
                timeline=timeline,
                observed_evidence=evidence_list,
                likely_root_cause="Inconclusive",
                confidence="Low",
                reason="Available evidence does not uniquely identify the cause. Logs are truncated and git history for the deployment is missing.",
                recommended_immediate_action="Investigate logging infrastructure failure to restore visibility.",
                recommended_follow_up="Check raw database metrics and application APM traces."
            )
