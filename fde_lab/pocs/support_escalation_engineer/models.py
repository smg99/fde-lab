from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class IssueClassification(str, Enum):
    PRODUCT_BUG = "PRODUCT_BUG"
    CUSTOMER_CONFIGURATION = "CUSTOMER_CONFIGURATION"
    INTEGRATION_ISSUE = "INTEGRATION_ISSUE"
    DATA_ISSUE = "DATA_ISSUE"
    ENVIRONMENT_ISSUE = "ENVIRONMENT_ISSUE"
    UNKNOWN = "UNKNOWN"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

class Reproducibility(str, Enum):
    REPRODUCIBLE = "REPRODUCIBLE"
    NOT_REPRODUCIBLE = "NOT_REPRODUCIBLE"

@dataclass
class Evidence:
    source: str
    observation: str
    relevance: str
    confidence: str

@dataclass
class ReproductionResult:
    status: Reproducibility
    steps: List[str]
    expected: str
    observed: str

@dataclass
class Issue:
    title: str
    classification: IssueClassification
    severity: Severity
    reproducibility: Reproducibility

@dataclass
class EscalationReport:
    customer: str
    issue: Issue
    summary: str
    facts: List[str]
    observations: List[str]
    hypotheses: List[str]
    reproduction: ReproductionResult
    evidence: List[Evidence]
    recommended_next_steps: List[str]

    def to_dict(self) -> dict:
        return {
            "customer": self.customer,
            "issue": {
                "title": self.issue.title,
                "classification": self.issue.classification.value,
                "severity": self.issue.severity.value,
                "reproducibility": self.issue.reproducibility.value
            },
            "summary": self.summary,
            "facts": self.facts,
            "observations": self.observations,
            "hypotheses": self.hypotheses,
            "reproduction": {
                "status": self.reproduction.status.value,
                "steps": self.reproduction.steps,
                "expected": self.reproduction.expected,
                "observed": self.reproduction.observed
            },
            "evidence": [
                {
                    "source": e.source,
                    "observation": e.observation,
                    "relevance": e.relevance,
                    "confidence": e.confidence
                } for e in self.evidence
            ],
            "recommended_next_steps": self.recommended_next_steps
        }
