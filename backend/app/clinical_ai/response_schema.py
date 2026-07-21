"""
Clinical AI Response Schema
"""

from pydantic import BaseModel


class ClinicalAIResponse(BaseModel):

    risk_score: float

    risk_level: str

    clinical_recommendation: str

    sources: list