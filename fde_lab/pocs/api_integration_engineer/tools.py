import os
import json
from typing import Dict, Any, List

from fde_lab.tools.base import Tool
from fde_lab.pocs.api_integration_engineer.models import ValidationResult, SimulatedResponse

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_commerce", scenario, filename)

class ApiSpecReaderTool(Tool):
    @property
    def name(self) -> str: return "read_api_spec"
    @property
    def description(self) -> str: return "Reads the API specification."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "api_spec.json"), "r") as f:
            return json.load(f)

class ConfigReaderTool(Tool):
    @property
    def name(self) -> str: return "read_customer_config"
    @property
    def description(self) -> str: return "Reads the customer's integration configuration."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "customer_config.json"), "r") as f:
            return json.load(f)

class RequestValidatorTool(Tool):
    @property
    def name(self) -> str: return "validate_request"
    @property
    def description(self) -> str: return "Validates a request payload against the API spec."
    
    def execute(self, **kwargs) -> dict:
        payload = kwargs.get("payload", {})
        spec_req = kwargs.get("spec_req", {})
        
        errors = []
        if spec_req and spec_req.get("type") == "object":
            required = spec_req.get("required", [])
            properties = spec_req.get("properties", {})
            
            for req_field in required:
                if req_field not in payload:
                    errors.append(f"Missing required field: {req_field}")
                    
            for key in payload:
                if key not in properties:
                    errors.append(f"Unexpected field in request: {key}")
                    
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

class ApiSimulatorTool(Tool):
    @property
    def name(self) -> str: return "simulate_api_call"
    @property
    def description(self) -> str: return "Simulates an API call."
    
    def execute(self, **kwargs) -> SimulatedResponse:
        endpoint = kwargs.get("endpoint")
        method = kwargs.get("method")
        payload = kwargs.get("payload", {})
        token = kwargs.get("token", "")
        
        # 1. Auth check
        if not token or token == "":
            return SimulatedResponse(
                status_code=401,
                payload={"error": "Unauthorized", "message": "Missing or invalid bearer token"},
                headers={"Content-Type": "application/json"}
            )
            
        # 2. Rate limit check for api-error scenario (simulated by a specific email)
        if payload.get("email") == "ratelimit@example.com":
            return SimulatedResponse(
                status_code=429,
                payload={"error": "Too Many Requests", "message": "Rate limit exceeded. Try again in 60s."},
                headers={"Content-Type": "application/json", "Retry-After": "60"}
            )
            
        # 3. Handle specific endpoints
        if endpoint == "/customers" and method == "POST":
            # Very basic schema simulation
            if "customer_email" in payload:
                return SimulatedResponse(
                    status_code=400,
                    payload={"error": "Bad Request", "message": "Missing required field: email"},
                    headers={"Content-Type": "application/json"}
                )
                
            return SimulatedResponse(
                status_code=201,
                payload={"id": "cust_88192", "email": payload.get("email", "unknown@example.com")},
                headers={"Content-Type": "application/json"}
            )
            
        return SimulatedResponse(
            status_code=404,
            payload={"error": "Not Found"},
            headers={"Content-Type": "application/json"}
        )

class IntegrationReportTool(Tool):
    @property
    def name(self) -> str: return "write_integration_artifacts"
    @property
    def description(self) -> str: return "Writes the integration report and example to disk."
    
    def execute(self, **kwargs) -> dict:
        report = kwargs["report"]
        
        os.makedirs("output", exist_ok=True)
        
        with open("output/api-integration-report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        if report.get("example"):
            with open("output/integration-example.json", "w") as f:
                json.dump(report["example"], f, indent=2)
                
        # Build human readable text
        txt = f"API Integration Analysis\n-------------------------\n\n"
        txt += f"Customer: {report.get('customer')}\n"
        txt += f"API: {report.get('api_name')}\n\n"
        
        def sym(status): return "✓" if status == "success" else "✗"
        
        txt += f"API discovery ........ {sym(report.get('discovery_status'))}\n"
        txt += f"Authentication ........ {sym(report.get('auth_status'))}\n"
        txt += f"Endpoint validation ... {sym(report.get('endpoint_status'))}\n"
        txt += f"Request validation .... {sym(report.get('request_validation_status'))}\n"
        txt += f"Response validation ... {sym(report.get('response_validation_status'))}\n\n"
        
        txt += f"Endpoints analyzed: {report.get('endpoints_analyzed')}\n\n"
        
        txt += "Integration risks:\n"
        for risk in report.get("integration_risks", []):
            txt += f"⚠ {risk}\n"
            
        txt += "\nRecommended approach:\n"
        for rec in report.get("recommended_approach", []):
            txt += f"- {rec}\n"
            
        txt += "\nGenerated:\n./output/api-integration-report.json\n"
        if report.get("example"):
            txt += "./output/integration-example.json\n"
            
        return {
            "report_path": "output/api-integration-report.json",
            "example_path": "output/integration-example.json" if report.get("example") else None,
            "human_output": txt
        }
