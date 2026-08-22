from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class UserRecord(BaseModel):
    email: str
    name: str
    role: str

class CustomerRequirements(BaseModel):
    customer: Dict[str, str]
    features: Dict[str, bool]
    integrations: Dict[str, Dict[str, Any]]
    users: List[UserRecord] = []

class ProductCapabilities(BaseModel):
    roles: List[str]
    features: List[str]
    integrations: List[str]

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []

class MappingResult(BaseModel):
    missing: List[str] = []
    unsupported: List[str] = []
    satisfied_count: int = 0
    total_count: int = 0
    status: str = "READY" # READY, INCOMPLETE, BLOCKED

class NormalizedConfig(BaseModel):
    customer: Dict[str, str]
    users: List[Dict[str, str]]
    features: Dict[str, bool]
    integrations: Dict[str, Any]

class OnboardingReport(BaseModel):
    customer_name: str
    requirements: CustomerRequirements
    validation: ValidationResult
    mapping: MappingResult
    config: Optional[NormalizedConfig] = None
    config_path: Optional[str] = None
    checklist_path: Optional[str] = None
    report_path: Optional[str] = None
