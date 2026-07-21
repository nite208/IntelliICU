"""
Clinical AI Response Schemas
"""

from typing import List

from pydantic import BaseModel, Field


class SummaryInfo(BaseModel):
    overall_condition: str = Field(..., example="Critical")
    confidence: float = Field(..., example=0.96)
    clinical_reasoning: str = Field(..., example="Sepsis assessment indicates significant physiological stress.")
    priority_actions: List[str] = Field(default_factory=list, example=["Critical Sepsis Risk Alert"])


class Contributor(BaseModel):
    feature: str = Field(..., example="Lactate")
    impact: float = Field(..., example=0.34)
    reason: str = Field(..., example="Elevated blood lactate level.")


class ExplainabilityInfo(BaseModel):
    positive_contributors: List[Contributor] = Field(default_factory=list)
    negative_contributors: List[Contributor] = Field(default_factory=list)


class RiskProgressInfo(BaseModel):
    current_risk: float = Field(..., example=0.93)
    previous_risk: float = Field(..., example=0.86)
    change: float = Field(..., example=0.07)
    trend: str = Field(..., example="Increasing")


class RecommendationInfo(BaseModel):
    priority: str = Field(..., example="HIGH")
    title: str = Field(..., example="Critical Sepsis Risk Alert")
    description: str = Field(..., example="Initiate full sepsis protocol.")

class EvidenceSource(BaseModel):
    title: str
    organization: str
    document_type: str
    page: int
    relevance: float
    summary: str


class ClinicalAIResponse(BaseModel):
    summary: SummaryInfo
    explainability: ExplainabilityInfo
    risk_progress: RiskProgressInfo
    recommendations: List[RecommendationInfo]
    sources: List[EvidenceSource]