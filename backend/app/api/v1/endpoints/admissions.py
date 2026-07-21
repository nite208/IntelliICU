"""
Admission API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories.admission_repository import AdmissionRepository
from app.schemas.admission import (
    AdmissionCreate,
    AdmissionResponse,
    AdmissionUpdate,
)
from app.services.admission_service import AdmissionService

router = APIRouter(prefix="/admissions", tags=["Admissions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)):
    return AdmissionService(AdmissionRepository(db))


@router.post("", response_model=AdmissionResponse, status_code=201)
def create_admission(
    admission: AdmissionCreate,
    service: AdmissionService = Depends(get_service),
):
    return service.create_admission(admission)


@router.get("", response_model=list[AdmissionResponse])
def list_admissions(
    service: AdmissionService = Depends(get_service),
):
    return service.list_admissions()


@router.get("/{admission_id}", response_model=AdmissionResponse)
def get_admission(
    admission_id: str,
    service: AdmissionService = Depends(get_service),
):
    return service.get_admission(admission_id)


@router.put("/{admission_id}", response_model=AdmissionResponse)
def update_admission(
    admission_id: str,
    admission: AdmissionUpdate,
    service: AdmissionService = Depends(get_service),
):
    return service.update_admission(admission_id, admission)


@router.delete("/{admission_id}", status_code=204)
def delete_admission(
    admission_id: str,
    service: AdmissionService = Depends(get_service),
):
    service.delete_admission(admission_id)