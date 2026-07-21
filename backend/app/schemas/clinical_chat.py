"""
Pydantic schemas for Clinical Copilot Chat.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ClinicalChatRequest(BaseModel):
    """
    Validation schema for Chat Request input.
    """
    patient_id: str = Field(..., description="Unique ID of the patient to query", example="ICU-10248")
    question: str = Field(..., description="Clinical question to ask the Copilot", example="What is the sepsis risk score and how are the vitals?")

class ClinicalChatResponse(BaseModel):
    """
    Validation schema for Chat Response (supports Phase 10.1, 10.2, 10.3, and 10.4 models).
    """
    # Legacy fields (optional for backward compatibility)
    summary: Optional[str] = Field(default=None, description="High-level diagnostic or clinical summary answering the question")
    findings: List[str] = Field(default_factory=list, description="Key clinical findings extracted from context")
    risk: Optional[str] = Field(default=None, description="Calculated or predicted patient risk level or concern")
    
    # Explainable AI fields
    reasoning: Optional[str] = Field(default=None, description="Clinical reasoning explaining the prediction")
    risk_drivers: List[str] = Field(default_factory=list, description="Physiological parameters acting as risk contributors")
    abnormal_vitals: List[str] = Field(default_factory=list, description="Vitals outside normal reference limits")
    abnormal_labs: List[str] = Field(default_factory=list, description="Lab values outside standard chemistry bounds")
    
    # RAG / Guideline fields
    answer: Optional[str] = Field(default=None, description="Guideline-backed diagnostic or treatment answer")
    guideline: Optional[str] = Field(default=None, description="Name of the clinical practice guideline referenced")
    source: Optional[str] = Field(default=None, description="Publishing organization or journal source")
    publication_year: Optional[int] = Field(default=None, description="Year of guideline publication")
    
    # Shared response fields
    recommendations: List[str] = Field(default_factory=list, description="Recommended clinical actions or pathways")
    evidence: List[str] = Field(default_factory=list, description="Evidence references or data values justifying findings")
    confidence: float = Field(..., description="LLM/reasoning/retrieval engine confidence score (0.0 to 1.0)")
    context: dict = Field(default_factory=dict, description="Full rich clinical context compiled for the patient")
