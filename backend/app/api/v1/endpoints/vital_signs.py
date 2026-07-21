"""
Vital Signs API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories.vital_sign_repository import VitalSignRepository
from app.schemas.vital_sign import (
    VitalSignCreate,
    VitalSignResponse,
    VitalSignUpdate,
)
from app.services.vital_sign_service import VitalSignService

router = APIRouter(
    prefix="/vital-signs",
    tags=["Vital Signs"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(
    db: Session = Depends(get_db),
):
    return VitalSignService(
        VitalSignRepository(db)
    )


@router.post(
    "",
    response_model=VitalSignResponse,
    status_code=201,
)
def create_vital_sign(
    vital: VitalSignCreate,
    service: VitalSignService = Depends(get_service),
):
    return service.create_vital_sign(vital)


@router.get(
    "",
    response_model=list[VitalSignResponse],
)
def list_vital_signs(
    service: VitalSignService = Depends(get_service),
):
    return service.list_vital_signs()


@router.get(
    "/{vital_sign_id}",
    response_model=VitalSignResponse,
)
def get_vital_sign(
    vital_sign_id: str,
    service: VitalSignService = Depends(get_service),
):
    return service.get_vital_sign(vital_sign_id)


@router.get(
    "/admission/{admission_id}",
    response_model=list[VitalSignResponse],
)
def get_admission_vitals(
    admission_id: str,
    service: VitalSignService = Depends(get_service),
):
    return service.get_admission_vitals(admission_id)


@router.put(
    "/{vital_sign_id}",
    response_model=VitalSignResponse,
)
def update_vital_sign(
    vital_sign_id: str,
    vital: VitalSignUpdate,
    service: VitalSignService = Depends(get_service),
):
    return service.update_vital_sign(
        vital_sign_id,
        vital,
    )


@router.delete(
    "/{vital_sign_id}",
    status_code=204,
)
def delete_vital_sign(
    vital_sign_id: str,
    service: VitalSignService = Depends(get_service),
):
    service.delete_vital_sign(vital_sign_id)