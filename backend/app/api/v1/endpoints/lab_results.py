"""
Laboratory Results API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories.lab_result_repository import LabResultRepository
from app.schemas.lab_result import (
    LabResultCreate,
    LabResultResponse,
    LabResultUpdate,
)
from app.services.lab_result_service import LabResultService

router = APIRouter(
    prefix="/lab-results",
    tags=["Laboratory Results"],
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
    return LabResultService(
        LabResultRepository(db)
    )


@router.post(
    "",
    response_model=LabResultResponse,
    status_code=201,
)
def create_lab_result(
    lab: LabResultCreate,
    service: LabResultService = Depends(get_service),
):
    return service.create_lab_result(lab)


@router.get(
    "",
    response_model=list[LabResultResponse],
)
def list_lab_results(
    service: LabResultService = Depends(get_service),
):
    return service.list_lab_results()


@router.get(
    "/{lab_result_id}",
    response_model=LabResultResponse,
)
def get_lab_result(
    lab_result_id: str,
    service: LabResultService = Depends(get_service),
):
    return service.get_lab_result(lab_result_id)


@router.get(
    "/admission/{admission_id}",
    response_model=list[LabResultResponse],
)
def get_admission_lab_results(
    admission_id: str,
    service: LabResultService = Depends(get_service),
):
    return service.get_admission_lab_results(admission_id)


@router.put(
    "/{lab_result_id}",
    response_model=LabResultResponse,
)
def update_lab_result(
    lab_result_id: str,
    lab: LabResultUpdate,
    service: LabResultService = Depends(get_service),
):
    return service.update_lab_result(
        lab_result_id,
        lab,
    )


@router.delete(
    "/{lab_result_id}",
    status_code=204,
)
def delete_lab_result(
    lab_result_id: str,
    service: LabResultService = Depends(get_service),
):
    service.delete_lab_result(lab_result_id)