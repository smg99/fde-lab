from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class SimulatedResponse:
    status_code: int
    payload: Dict[str, Any]
    headers: Dict[str, str]

@dataclass
class IntegrationExample:
    authentication: Dict[str, Any]
    headers: Dict[str, str]
    endpoints: List[Dict[str, Any]]

    def to_dict(self) -> dict:
        return {
            "authentication": self.authentication,
            "headers": self.headers,
            "endpoints": self.endpoints
        }

@dataclass
class IntegrationReport:
    customer: str
    api_name: str
    discovery_status: str
    auth_status: str
    endpoint_status: str
    request_validation_status: str
    response_validation_status: str
    endpoints_analyzed: int
    integration_risks: List[str]
    recommended_approach: List[str]
    example: IntegrationExample

    def to_dict(self) -> dict:
        return {
            "customer": self.customer,
            "api_name": self.api_name,
            "discovery_status": self.discovery_status,
            "auth_status": self.auth_status,
            "endpoint_status": self.endpoint_status,
            "request_validation_status": self.request_validation_status,
            "response_validation_status": self.response_validation_status,
            "endpoints_analyzed": self.endpoints_analyzed,
            "integration_risks": self.integration_risks,
            "recommended_approach": self.recommended_approach,
            "example": self.example.to_dict() if self.example else None
        }
