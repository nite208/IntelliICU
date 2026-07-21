"""
Pydantic schemas for Patient.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientBase(BaseModel):
    """
    Base patient schema.
    """

    first_name: str = Field(..., min_length=2, max_length=100)

    last_name: str = Field(..., min_length=2, max_length=100)

    date_of_birth: date

    gender: str = Field(..., max_length=20)

    blood_group: str | None = Field(default=None, max_length=5)

    phone: str | None = Field(default=None, max_length=20)

    email: EmailStr | None = None

    address: str | None = Field(default=None, max_length=300)

    emergency_contact: str | None = Field(
        default=None,
        max_length=120,
    )

    height_cm: float | None = Field(
        default=None,
        gt=0,
    )

    weight_kg: float | None = Field(
        default=None,
        gt=0,
    )


class PatientCreate(PatientBase):
    """
    Schema used while creating a patient.
    """

    pass


class PatientUpdate(BaseModel):
    """
    Schema used while updating a patient.
    """

    first_name: str | None = Field(default=None, min_length=2, max_length=100)

    last_name: str | None = Field(default=None, min_length=2, max_length=100)

    date_of_birth: date | None = None

    gender: str | None = Field(default=None, max_length=20)

    blood_group: str | None = Field(default=None, max_length=5)

    phone: str | None = Field(default=None, max_length=20)

    email: EmailStr | None = None

    address: str | None = Field(default=None, max_length=300)

    emergency_contact: str | None = Field(
        default=None,
        max_length=120,
    )

    height_cm: float | None = Field(
        default=None,
        gt=0,
    )

    weight_kg: float | None = Field(
        default=None,
        gt=0,
    )

    status: str | None = Field(default=None, max_length=20)


class PatientResponse(PatientBase):
    """
    Patient response returned by API.
    """

    id: UUID | str

    hospital_patient_id: str

    status: str

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)