"""
Pydantic schemas for ICU Admission.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdmissionBase(BaseModel):
    patient_id: str

    diagnosis: str = Field(..., max_length=300)

    doctor_name: str = Field(..., max_length=100)

    ward: str = Field(..., max_length=50)

    bed_number: str = Field(..., max_length=20)


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionUpdate(BaseModel):
    diagnosis: str | None = None
    doctor_name: str | None = None
    ward: str | None = None
    bed_number: str | None = None
    status: str | None = None


class AdmissionResponse(AdmissionBase):
    id: str

    admission_number: str

    status: str

    admitted_at: datetime

    discharged_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)