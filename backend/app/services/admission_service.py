"""
Admission Service.
"""

from uuid import uuid4

from fastapi import HTTPException, status

from app.models.admission import Admission
from app.repositories.admission_repository import AdmissionRepository
from app.schemas.admission import AdmissionCreate, AdmissionUpdate
from app.services.base_service import BaseService


class AdmissionService(BaseService[Admission]):
    """
    Business logic for ICU Admissions.
    """

    def __init__(self, repository: AdmissionRepository):
        super().__init__(repository)

    def create_admission(
        self,
        admission_data: AdmissionCreate,
    ) -> Admission:

        admission = Admission(
            admission_number=f"ADM-{str(uuid4())[:8].upper()}",
            **admission_data.model_dump(),
        )

        return self.repository.create(admission)

    def get_admission(
        self,
        admission_id: str,
    ) -> Admission:

        admission = self.repository.get_by_id(admission_id)

        if admission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admission not found.",
            )

        return admission

    def list_admissions(self):
        return self.repository.get_all()

    def update_admission(
        self,
        admission_id: str,
        admission_data: AdmissionUpdate,
    ):

        admission = self.get_admission(admission_id)

        for field, value in admission_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(admission, field, value)

        return self.repository.update(admission)

    def delete_admission(
        self,
        admission_id: str,
    ):

        admission = self.get_admission(admission_id)

        self.repository.delete(admission)