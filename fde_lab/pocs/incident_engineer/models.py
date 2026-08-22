from typing import List, Optional
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    """Structured evidence item collected during an investigation."""
    id: int
    source: str = Field(description="Where did this information come from? (e.g., git, logs)")
    time: str = Field(description="When did it occur?")
    observation: str = Field(description="What was observed?")
    relevance: str = Field(description="Why is it relevant?")

class IncidentReport(BaseModel):
    """A concise professional incident report."""
    summary: str
    impact: str
    timeline: List[str]
    observed_evidence: List[Evidence]
    likely_root_cause: str
    confidence: str = Field(description="High, Medium, or Low")
    reason: str = Field(description="Explanation of the confidence rating based on facts vs inference.")
    recommended_immediate_action: str
    recommended_follow_up: str
