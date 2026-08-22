from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class InspectionResult:
    runtime: str
    runtime_version: str
    dependency_file: str
    entrypoint: str
    port: int
    health_endpoint: str
    configuration_file: str
    
@dataclass
class DeploymentConfig:
    application: str
    runtime: str
    runtime_version: str
    container: Dict[str, str]
    port: int
    health_endpoint: str
    entrypoint: str

@dataclass
class DeploymentReport:
    application: str
    runtime: str
    deployment_tech: str
    image: str
    port: int
    health_endpoint: str
    
    build_status: str = "PENDING"
    deployment_status: str = "PENDING"
    health_status: str = "PENDING"
    functional_status: str = "PENDING"
    
    generated_artifacts: List[str] = field(default_factory=list)
    failure_stage: Optional[str] = None
    failure_cause: Optional[str] = None
    recommended_action: Optional[str] = None
    cleanup_status: str = "PENDING"
