import os
import json
from typing import Dict, Any, List

from fde_lab.tools.base import Tool

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_commerce", scenario, filename)

class CustomerReportTool(Tool):
    @property
    def name(self) -> str: return "inspect_customer_report"
    @property
    def description(self) -> str: return "Reads the customer's initial report."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "customer_report.json"), "r") as f:
            return json.load(f)

class EnvironmentInspectorTool(Tool):
    @property
    def name(self) -> str: return "inspect_environment"
    @property
    def description(self) -> str: return "Reads the customer's environment configuration."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "environment.json"), "r") as f:
            return json.load(f)

class LogSearchTool(Tool):
    @property
    def name(self) -> str: return "search_logs"
    @property
    def description(self) -> str: return "Retrieves application logs related to the issue."
    
    def execute(self, **kwargs) -> list:
        with open(get_demo_data_path(kwargs["scenario"], "application_logs.json"), "r") as f:
            return json.load(f)

class RequestSampleTool(Tool):
    @property
    def name(self) -> str: return "get_request_samples"
    @property
    def description(self) -> str: return "Retrieves sample failing requests."
    
    def execute(self, **kwargs) -> list:
        with open(get_demo_data_path(kwargs["scenario"], "request_samples.json"), "r") as f:
            return json.load(f)

class RecentChangesTool(Tool):
    @property
    def name(self) -> str: return "get_recent_changes"
    @property
    def description(self) -> str: return "Retrieves recent code/config changes in the environment."
    
    def execute(self, **kwargs) -> list:
        with open(get_demo_data_path(kwargs["scenario"], "recent_changes.json"), "r") as f:
            return json.load(f)

class ReproductionTool(Tool):
    @property
    def name(self) -> str: return "attempt_reproduction"
    @property
    def description(self) -> str: return "Simulates a reproduction attempt using provided request samples."
    
    def execute(self, **kwargs) -> dict:
        requests = kwargs.get("requests", [])
        logs = kwargs.get("logs", [])
        
        if not requests or len(requests) == 0:
            return {
                "status": "NOT_REPRODUCIBLE",
                "steps": ["Attempted to reproduce but no specific request payload was found."],
                "expected": "Checkout completes successfully.",
                "observed": "Could not execute reproduction."
            }
            
        req = requests[0]
        payload = req.get("payload", {})
        
        # Simulate normal/product-bug scenario
        if "discount_code" in payload:
            return {
                "status": "REPRODUCIBLE",
                "steps": [
                    f"Send POST to {req.get('endpoint')} with payload: {json.dumps(payload)}"
                ],
                "expected": "Checkout completes with HTTP 200.",
                "observed": f"Checkout fails with HTTP 500. Matches reported issue."
            }
        elif "payment_method" in payload:
            # Simulate customer config issue
            return {
                "status": "REPRODUCIBLE",
                "steps": [
                    f"Send POST to {req.get('endpoint')} with payment payload."
                ],
                "expected": "Checkout completes with HTTP 200.",
                "observed": "Checkout fails with payment authorization error."
            }
        
        return {
            "status": "NOT_REPRODUCIBLE",
            "steps": ["Attempted to send generic request."],
            "expected": "Checkout completes successfully.",
            "observed": "Could not reproduce the exact error."
        }

class EscalationGeneratorTool(Tool):
    @property
    def name(self) -> str: return "generate_escalation"
    @property
    def description(self) -> str: return "Generates the final escalation and reproduction artifacts."
    
    def execute(self, **kwargs) -> dict:
        report = kwargs.get("report")
        
        os.makedirs("output", exist_ok=True)
        
        with open("output/escalation.json", "w") as f:
            json.dump(report, f, indent=2)
            
        with open("output/evidence.json", "w") as f:
            json.dump(report.get("evidence", []), f, indent=2)
            
        rep = report.get("reproduction", {})
        rep_md = f"# Reproduction\n\nResult: **{rep.get('status')}**\n\n## Steps\n"
        for i, step in enumerate(rep.get("steps", [])):
            rep_md += f"{i+1}. {step}\n"
        rep_md += f"\n## Expected\n{rep.get('expected')}\n\n## Observed\n{rep.get('observed')}\n"
        
        with open("output/reproduction.md", "w") as f:
            f.write(rep_md)
            
        esc_md = f"# Engineering Escalation\n\n"
        esc_md += f"## Title\n{report.get('issue', {}).get('title')}\n\n"
        esc_md += f"## Customer Impact\n{report.get('summary')}\n\n"
        esc_md += f"## Classification\n{report.get('issue', {}).get('classification')} (Severity: {report.get('issue', {}).get('severity')})\n\n"
        
        if len(report.get("recommended_next_steps", [])) > 0:
            esc_md += "## Recommended Next Steps\n"
            for step in report.get("recommended_next_steps", []):
                esc_md += f"- {step}\n"
                
        with open("output/escalation-report.md", "w") as f:
            f.write(esc_md)
            
        return {
            "escalation_json_path": "output/escalation.json",
            "evidence_json_path": "output/evidence.json",
            "reproduction_md_path": "output/reproduction.md",
            "escalation_md_path": "output/escalation-report.md"
        }
