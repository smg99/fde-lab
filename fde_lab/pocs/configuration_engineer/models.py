from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

@dataclass
class ConfigurationIssue:
    path: str
    issue_type: str # "missing", "invalid", "conflict"
    description: str
    current_value: Any = None
    expected_value: Any = None

@dataclass
class ProposedChange:
    path: str
    current_value: Any
    proposed_value: Any
    reason: str

@dataclass
class RiskAssessment:
    level: str # "LOW", "MEDIUM", "HIGH"
    reason: str
    requires_approval: bool

@dataclass
class ConfigurationReport:
    status: str # "valid", "needs_changes"
    scenario: str
    customer: str
    environment: str
    observations: List[str]
    issues: List[ConfigurationIssue]
    recommended_changes: List[ProposedChange]
    risk: RiskAssessment
    action_required: bool
    changes_applied: bool

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "scenario": self.scenario,
            "customer": self.customer,
            "environment": self.environment,
            "observations": self.observations,
            "issues": [
                {
                    "path": i.path,
                    "type": i.issue_type,
                    "description": i.description,
                    "current": i.current_value,
                    "expected": i.expected_value
                } for i in self.issues
            ],
            "recommended_changes": [
                {
                    "path": c.path,
                    "current": c.current_value,
                    "proposed": c.proposed_value,
                    "reason": c.reason
                } for c in self.recommended_changes
            ],
            "risk": {
                "level": self.risk.level,
                "reason": self.risk.reason,
                "requires_approval": self.risk.requires_approval
            },
            "action_required": self.action_required,
            "changes_applied": self.changes_applied
        }
