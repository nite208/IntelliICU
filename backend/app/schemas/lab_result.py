"""
Pydantic schemas for Laboratory Results.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LabResultBase(BaseModel):
    """
    Base Lab Result Schema.
    """

    admission_id: str

    hemoglobin: float = Field(..., gt=0)
    wbc: float = Field(..., gt=0)
    platelets: float = Field(..., gt=0)

    creatinine: float = Field(..., gt=0)
    bun: float = Field(..., gt=0)

    sodium: float = Field(..., gt=0)
    potassium: float = Field(..., gt=0)
    chloride: float = Field(..., gt=0)

    lactate: float = Field(..., gt=0)

    ph: float = Field(..., gt=0)

    pao2: float = Field(..., gt=0)

    paco2: float = Field(..., gt=0)


class LabResultCreate(LabResultBase):
    pass


class LabResultUpdate(BaseModel):

    hemoglobin: float | None = None
    wbc: float | None = None
    platelets: float | None = None

    creatinine: float | None = None
    bun: float | None = None

    sodium: float | None = None
    potassium: float | None = None
    chloride: float | None = None

    lactate: float | None = None

    ph: float | None = None

    pao2: float | None = None

    paco2: float | None = None


class LabResultResponse(LabResultBase):

    id: UUID | str

    collected_at: datetime

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)