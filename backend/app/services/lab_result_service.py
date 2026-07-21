"""
Lab Result Service.
"""

from fastapi import HTTPException, status

from app.models.lab_result import LabResult
from app.repositories.lab_result_repository import LabResultRepository
from app.schemas.lab_result import (
    LabResultCreate,
    LabResultUpdate,
)
from app.services.base_service import BaseService


class LabResultService(BaseService[LabResult]):

    def __init__(self, repository: LabResultRepository):
        super().__init__(repository)

    def create_lab_result(
        self,
        lab_data: LabResultCreate,
    ):
        lab = LabResult(
            **lab_data.model_dump(),
        )

        return self.repository.create(lab)

    def get_lab_result(
        self,
        lab_result_id: str,
    ):

        lab = self.repository.get_by_id(
            lab_result_id
        )

        if lab is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab Result not found.",
            )

        return lab

    def list_lab_results(self):
        return self.repository.get_all()

    def get_admission_lab_results(
        self,
        admission_id: str,
    ):
        return self.repository.get_by_admission_id(
            admission_id
        )

    def update_lab_result(
        self,
        lab_result_id: str,
        lab_data: LabResultUpdate,
    ):

        lab = self.get_lab_result(
            lab_result_id
        )

        for field, value in lab_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(
                lab,
                field,
                value,
            )

        return self.repository.update(lab)

    def delete_lab_result(
        self,
        lab_result_id: str,
    ):

        lab = self.get_lab_result(
            lab_result_id
        )

        self.repository.delete(lab)