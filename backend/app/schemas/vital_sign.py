"""
Pydantic schemas for Vital Signs.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VitalSignBase(BaseModel):
    """
    Base Vital Sign Schema.
    """

    admission_id: str

    heart_rate: float = Field(..., gt=0)

    systolic_bp: float = Field(..., gt=0)

    diastolic_bp: float = Field(..., gt=0)

    respiratory_rate: float = Field(..., gt=0)

    spo2: float = Field(..., ge=0, le=100)

    temperature: float = Field(..., gt=25, lt=45)

    glasgow_coma_scale: int = Field(..., ge=3, le=15)

    urine_output_ml: float = Field(..., ge=0)


class VitalSignCreate(VitalSignBase):
    """
    Create Vital Sign.
    """

    pass


class VitalSignUpdate(BaseModel):
    """
    Update Vital Sign.
    """

    heart_rate: float | None = None
    systolic_bp: float | None = None
    diastolic_bp: float | None = None
    respiratory_rate: float | None = None
    spo2: float | None = None
    temperature: float | None = None
    glasgow_coma_scale: int | None = None
    urine_output_ml: float | None = None


class VitalSignResponse(VitalSignBase):
    """
    Vital Sign Response.
    """

    id: UUID | str

    created_at: datetime

    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)