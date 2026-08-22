from typing import Any, Dict
from fde_lab.tools.base import Tool

class BaseScenarioTool(Tool):
    """Base tool that accepts a scenario parameter."""
    def __init__(self, scenario: str = "known"):
        self.scenario = scenario

class LogSearchTool(BaseScenarioTool):
    @property
    def name(self) -> str:
        return "search_application_logs"
        
    @property
    def description(self) -> str:
        return "Search application logs for a specific service. Input: service_name."
        
    def execute(self, service_name: str = "checkout-api", **kwargs) -> Any:
        if self.scenario == "inconclusive":
            return {
                "service": service_name,
                "logs": [
                    "14:30:58 INFO checkout-api request received",
                    "14:31:02 INFO checkout-api request received",
                    "14:32:04 ERROR checkout request failed status=500"
                ],
                "note": "Logs are truncated or missing due to logging infrastructure failure."
            }
            
        # Known incident scenario
        return {
            "service": service_name,
            "logs": [
                "14:30:58 INFO checkout-api request received",
                "14:31:02 INFO payment authorization successful",
                "14:31:12 INFO checkout-api request received",
                "14:31:14 INFO payment authorization successful",
                "14:32:03 ERROR database connection timeout",
                "14:32:04 ERROR checkout request failed status=500",
                "14:32:07 ERROR database connection timeout"
            ]
        }

class DeploymentHistoryTool(BaseScenarioTool):
    @property
    def name(self) -> str:
        return "get_deployment_history"
        
    @property
    def description(self) -> str:
        return "Get recent deployment history for the environment."
        
    def execute(self, **kwargs) -> Any:
        return {
            "deployments": [
                {"id": "#181", "time": "13:20", "status": "successful"},
                {"id": "#182", "time": "13:47", "status": "successful"},
                {"id": "#183", "time": "14:10", "status": "successful"},
                {"id": "#184", "time": "14:31", "status": "successful"},
            ]
        }

class GitHistoryTool(BaseScenarioTool):
    @property
    def name(self) -> str:
        return "get_git_history"
        
    @property
    def description(self) -> str:
        return "Get git history and commit details for a deployment. Input: deployment_id."
        
    def execute(self, deployment_id: str = "#184", **kwargs) -> Any:
        if self.scenario == "inconclusive":
            return {
                "deployment": deployment_id,
                "commit": "unknown",
                "author": "unknown",
                "time": "14:30",
                "changes": [
                    "Minor typo fixes in README",
                    "Update dependencies"
                ]
            }

        if deployment_id == "#184":
            return {
                "deployment": deployment_id,
                "commit": "a84f21c",
                "author": "demo-user",
                "time": "14:30",
                "changes": [
                    "database connection pool configuration"
                ]
            }
        return {"error": "Deployment not found"}

class MetricsTool(BaseScenarioTool):
    @property
    def name(self) -> str:
        return "get_metrics"
        
    @property
    def description(self) -> str:
        return "Get time-series metrics for the environment."
        
    def execute(self, **kwargs) -> Any:
        if self.scenario == "inconclusive":
            return {
                "metrics": [
                    {"time": "14:30", "checkout_errors": "normal"},
                    {"time": "14:32", "checkout_http_500": "spike"}
                ]
            }

        return {
            "metrics": [
                {"time": "14:30", "checkout_errors": "normal"},
                {"time": "14:31", "event": "deployment #184"},
                {"time": "14:32", "database_connections": "100%"},
                {"time": "14:32", "checkout_http_500": "spike"},
                {"time": "14:33", "checkout_latency": "spike"}
            ]
        }

class ServiceHealthTool(BaseScenarioTool):
    @property
    def name(self) -> str:
        return "get_service_health"
        
    @property
    def description(self) -> str:
        return "Get current health status of all services."
        
    def execute(self, **kwargs) -> Any:
        if self.scenario == "inconclusive":
            return {
                "checkout-api": {"status": "degraded"},
                "payment-api": {"status": "healthy"},
                "user-api": {"status": "healthy"},
                "database": {"status": "healthy"}
            }

        return {
            "checkout-api": {"status": "degraded"},
            "payment-api": {"status": "healthy"},
            "user-api": {"status": "healthy"},
            "database": {
                "status": "healthy",
                "connection_pool": "exhausted"
            }
        }
