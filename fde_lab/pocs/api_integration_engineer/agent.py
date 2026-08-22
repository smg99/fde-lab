import logging
from typing import Dict, Any, List

from fde_lab.pocs.api_integration_engineer.models import (
    IntegrationReport, IntegrationExample
)
from fde_lab.pocs.api_integration_engineer.tools import (
    ApiSpecReaderTool, ConfigReaderTool, RequestValidatorTool,
    ApiSimulatorTool, IntegrationReportTool
)

logger = logging.getLogger("fde_lab.pocs.api_integration_engineer.agent")

class ApiIntegrationEngineerAgent:
    def __init__(self):
        self.spec_tool = ApiSpecReaderTool()
        self.config_tool = ConfigReaderTool()
        self.req_validator = RequestValidatorTool()
        self.simulator = ApiSimulatorTool()
        self.reporter = IntegrationReportTool()
        
    def run(self, scenario: str) -> IntegrationReport:
        logger.info(f"Starting API Integration Engineer for scenario: {scenario}")
        
        spec = self.spec_tool.execute(scenario=scenario)
        config = self.config_tool.execute(scenario=scenario)
        
        discovery_status = "success" if spec else "failure"
        endpoints_analyzed = len(spec.get("endpoints", []))
        
        auth_status = "success"
        endpoint_status = "success"
        req_status = "success"
        res_status = "success"
        
        risks = []
        recommendations = []
        
        # Static Analysis
        auth_type = spec.get("authentication", {}).get("type")
        if auth_type == "bearer":
            risks.append("Bearer token required. Ensure secure storage.")
            recommendations.append("Store API credentials outside source control.")
            
        for ep in spec.get("endpoints", []):
            if "429" in ep.get("status_codes", {}):
                risks.append(f"429 rate limiting must be handled on {ep['path']}.")
                if "Implement retry/backoff for 429" not in recommendations:
                    recommendations.append("Implement retry/backoff for 429.")
            if "409" in ep.get("status_codes", {}):
                risks.append(f"409 conflict response must be handled on {ep['path']}.")
                if "Handle 409 as an idempotency conflict" not in recommendations:
                    recommendations.append("Handle 409 as an idempotency conflict.")
                    
        # Simulate customer request
        sample_req = config.get("sample_request", {})
        token = config.get("auth_token", "")
        
        if not token:
            auth_status = "failure"
            risks.append("Authentication token is missing or empty.")
            
        # Find matching endpoint in spec
        matched_ep = None
        for ep in spec.get("endpoints", []):
            if ep["path"] == sample_req.get("endpoint") and ep["method"] == sample_req.get("method"):
                matched_ep = ep
                break
                
        if not matched_ep:
            endpoint_status = "failure"
            risks.append(f"Endpoint {sample_req.get('method')} {sample_req.get('endpoint')} not found in API spec.")
        else:
            # Validate payload
            val_res = self.req_validator.execute(
                payload=sample_req.get("payload", {}),
                spec_req=matched_ep.get("request", {})
            )
            
            if not val_res["is_valid"]:
                req_status = "failure"
                for err in val_res["errors"]:
                    risks.append(f"Request validation error: {err}")
                    
            # Execute simulation
            sim_res = self.simulator.execute(
                endpoint=sample_req.get("endpoint"),
                method=sample_req.get("method"),
                payload=sample_req.get("payload", {}),
                token=token
            )
            
            if sim_res.status_code == 401:
                auth_status = "failure"
                risks.append("API rejected the authentication token (401 Unauthorized).")
                recommendations.append("Verify and rotate API credentials.")
            elif sim_res.status_code == 400:
                req_status = "failure"
                risks.append(f"API rejected the request payload (400 Bad Request): {sim_res.payload}")
                recommendations.append("Correct the request schema mapping.")
            elif sim_res.status_code == 429:
                res_status = "failure"
                risks.append("API returned a 429 Rate Limited error.")
                recommendations.append("Implement exponential backoff.")
            elif sim_res.status_code >= 500:
                res_status = "failure"
                risks.append(f"API returned a server error ({sim_res.status_code}).")
            else:
                pass # 200/201 success
                
        recommendations.append("Validate response schema before persistence.")
        
        example = IntegrationExample(
            authentication={"type": spec.get("authentication", {}).get("type", "unknown")},
            headers={"Content-Type": "application/json", spec.get("authentication", {}).get("header", "Authorization"): "Bearer <TOKEN>"},
            endpoints=[
                {
                    "method": ep["method"],
                    "path": ep["path"],
                    "request_mapping": ep.get("request", {}),
                    "response_mapping": ep.get("response", {})
                }
                for ep in spec.get("endpoints", [])
            ]
        )
        
        report = IntegrationReport(
            customer="Acme Commerce",
            api_name=spec.get("api_name", "Unknown API"),
            discovery_status=discovery_status,
            auth_status=auth_status,
            endpoint_status=endpoint_status,
            request_validation_status=req_status,
            response_validation_status=res_status,
            endpoints_analyzed=endpoints_analyzed,
            integration_risks=list(set(risks)),
            recommended_approach=list(set(recommendations)),
            example=example
        )
        
        paths = self.reporter.execute(report=report.to_dict())
        report.report_path = paths["report_path"]
        report.example_path = paths["example_path"]
        report.human_output = paths["human_output"]
        
        return report
