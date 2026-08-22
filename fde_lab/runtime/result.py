from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class WorkerError:
    code: str
    message: str
    stage: str
    recoverable: bool
    suggested_action: str

@dataclass
class ArtifactEnvelope:
    path: str
    type: str
    description: str

@dataclass
class WorkerResult:
    schema_version: str = "0.1"
    worker: Dict[str, str] = field(default_factory=dict)
    status: str = "failed"
    summary: str = ""
    facts: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    artifacts: List[ArtifactEnvelope] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[WorkerError] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class SideEffectMetadata:
    filesystem: bool = False
    network: bool = False
    credentials: bool = False
    production: bool = False
    destructive: bool = False
    external_systems: bool = False

@dataclass
class EnvironmentRequirements:
    node: bool = False
    python: bool = False
    docker: bool = False

@dataclass
class Example:
    command: str
    purpose: str

@dataclass
class WorkerManifest:
    schema_version: str = "0.1"
    name: str = ""
    version: str = ""
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    side_effects: SideEffectMetadata = field(default_factory=SideEffectMetadata)
    requirements: EnvironmentRequirements = field(default_factory=EnvironmentRequirements)
    examples: List[Example] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        d = asdict(self)
        
        d["exit_codes"] = {
            "SUCCESS": 0,
            "FAILURE": 1,
            "INVALID_INPUT": 2,
            "ENV_PROBLEM": 3,
            "POLICY_REFUSAL": 4,
            "INCONCLUSIVE": 5
        }
        
        d["outputs"]["WorkerResult"] = {
            "type": "object",
            "description": "Standard FDE Lab result envelope",
            "properties": {
                "schema_version": {"type": "string"},
                "worker": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"}
                    }
                },
                "status": {"type": "string", "description": "Worker execution status (e.g., success, inconclusive, failure)"},
                "summary": {"type": "string"},
                "facts": {"type": "array", "items": {"type": "string"}},
                "actions": {"type": "array", "items": {"type": "string"}},
                "artifacts": {
                    "type": "array", 
                    "items": {
                        "type": "object", 
                        "properties": {
                            "path": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "warnings": {"type": "array", "items": {"type": "string"}},
                "errors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"},
                            "stage": {"type": "string"},
                            "recoverable": {"type": "boolean"},
                            "suggested_action": {"type": "string"}
                        }
                    }
                },
                "next_steps": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["schema_version", "worker", "status", "summary", "facts", "actions", "artifacts", "warnings", "errors", "next_steps"]
        }
        
        return d
