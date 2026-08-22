from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class CustomerRequirement:
    description: str

@dataclass
class Gap:
    description: str
    impact: str

@dataclass
class Conflict:
    description: str
    recommendation: str

@dataclass
class Component:
    name: str

@dataclass
class Connection:
    source: str
    target: str
    description: str

@dataclass
class Architecture:
    components: List[Component]
    connections: List[Connection]

@dataclass
class Phase:
    name: str
    objective: str
    tasks: List[str]

@dataclass
class Risk:
    description: str
    severity: str
    mitigation: str

@dataclass
class Assumption:
    description: str

@dataclass
class CustomerQuestion:
    question: str

@dataclass
class SolutionReport:
    status: str # "ready", "needs_customer_input", "conflict_detected"
    scenario: str
    requirements: List[str]
    observations: List[str]
    constraints: List[str]
    gaps: List[Gap]
    conflicts: List[Conflict]
    architecture: Architecture
    implementation_plan: List[Phase]
    risks: List[Risk]
    assumptions: List[Assumption]
    customer_questions: List[CustomerQuestion]
    confidence: str
    requires_customer_input: bool

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "scenario": self.scenario,
            "requirements": self.requirements,
            "observations": self.observations,
            "constraints": self.constraints,
            "gaps": [{"description": g.description, "impact": g.impact} for g in self.gaps],
            "conflicts": [{"description": c.description, "recommendation": c.recommendation} for c in self.conflicts],
            "architecture": {
                "components": [c.name for c in self.architecture.components] if self.architecture else [],
                "connections": [{"source": c.source, "target": c.target, "description": c.description} for c in self.architecture.connections] if self.architecture else []
            },
            "implementation_plan": [
                {
                    "name": p.name,
                    "objective": p.objective,
                    "tasks": p.tasks
                } for p in self.implementation_plan
            ],
            "risks": [
                {
                    "description": r.description,
                    "severity": r.severity,
                    "mitigation": r.mitigation
                } for r in self.risks
            ],
            "assumptions": [a.description for a in self.assumptions],
            "customer_questions": [q.question for q in self.customer_questions],
            "confidence": self.confidence,
            "requires_customer_input": self.requires_customer_input
        }
