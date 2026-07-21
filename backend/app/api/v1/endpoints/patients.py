"""
Patient API Endpoints.
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from app.services.patient_service import PatientService

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


def get_patient_service(db: Session) -> PatientService:
    """
    Returns PatientService instance.
    """
    repository = PatientRepository(db)
    return PatientService(repository)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
):
    service = get_patient_service(db)
    return service.create_patient(patient)


@router.get(
    "",
    response_model=list[PatientResponse],
)
def list_patients(
    db: Session = Depends(get_db),
):
    service = get_patient_service(db)
    return service.list_patients()


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    service = get_patient_service(db)

    try:
        return service.get_patient(patient_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: str,
    patient: PatientUpdate,
    db: Session = Depends(get_db),
):
    service = get_patient_service(db)

    try:
        return service.update_patient(
            patient_id,
            patient,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    service = get_patient_service(db)

    try:
        service.delete_patient(patient_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc