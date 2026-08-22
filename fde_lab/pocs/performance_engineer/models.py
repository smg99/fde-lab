from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

@dataclass
class PerformanceMetrics:
    service: str
    endpoint: str
    request_rate_tps: float
    error_rate_percent: float
    cpu_utilization_percent: float
    memory_utilization_percent: float
    connection_pool_utilization_percent: float

@dataclass
class PerformanceTrace:
    endpoint_p50_ms: float
    endpoint_p95_ms: float
    database_p95_ms: float
    external_api_p95_ms: float
    slowest_query_ms: float
    slowest_query_id: str

@dataclass
class Diagnosis:
    category: str  # e.g., 'database', 'external_api', 'application', 'healthy', 'inconclusive'
    confidence: str # HIGH, MEDIUM, LOW

@dataclass
class PerformanceReport:
    status: str
    scenario: str
    service: str
    diagnosis: Diagnosis
    metrics: Dict[str, Any]
    evidence: List[str]
    contradictory_evidence: List[str]
    impact: Dict[str, str]
    recommendations: List[str]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "scenario": self.scenario,
            "service": self.service,
            "diagnosis": {
                "category": self.diagnosis.category,
                "confidence": self.diagnosis.confidence
            },
            "metrics": self.metrics,
            "evidence": self.evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "impact": self.impact,
            "recommendations": self.recommendations
        }
