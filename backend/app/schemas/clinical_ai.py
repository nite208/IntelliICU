"""
Clinical AI Request & Response Schemas
"""

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    id: str = Field(..., example="ICU-10248")
    name: str = Field(..., example="Amelia Chen")
    age: int = Field(..., example=67)
    gender: str = Field(..., example="Female")


class AdmissionInfo(BaseModel):
    bed: str = Field(..., example="MICU-04")
    diagnosis: str = Field(..., example="Septic Shock")


class VitalSigns(BaseModel):
    heart_rate: float = Field(..., example=132)
    systolic_bp: float = Field(..., example=82)
    diastolic_bp: float = Field(..., example=48)
    respiratory_rate: float = Field(..., example=31)
    spo2: float = Field(..., example=89)
    temperature: float = Field(..., example=39.2)


class LabResults(BaseModel):
    lactate: float = Field(..., example=4.6)
    wbc: float = Field(..., example=18.2)
    creatinine: float = Field(..., example=2.1)


class PredictionInfo(BaseModel):
    risk_score: float = Field(..., example=0.93)
    risk_level: str = Field(..., example="HIGH")


class ClinicalAIRequest(BaseModel):
    patient: PatientInfo
    admission: AdmissionInfo
    vitals: VitalSigns
    labs: LabResults
    prediction: PredictionInfo