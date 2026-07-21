"""
Pydantic schemas for AI Predictions.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PredictionBase(BaseModel):
    admission_id: str
    prediction_type: str
    risk_score: float
    risk_level: str
    recommendation: str
    model_version: str = "v1.0"


class PredictionCreate(PredictionBase):
    pass


class PredictionResponse(PredictionBase):
    id: UUID | str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)