"""
Vital Sign Service.
"""

from fastapi import HTTPException, status

from app.models.vital_sign import VitalSign
from app.repositories.vital_sign_repository import VitalSignRepository
from app.schemas.vital_sign import (
    VitalSignCreate,
    VitalSignUpdate,
)
from app.services.base_service import BaseService


class VitalSignService(BaseService[VitalSign]):
    """
    Business logic for Vital Signs.
    """

    def __init__(self, repository: VitalSignRepository):
        super().__init__(repository)

    def create_vital_sign(
        self,
        vital_data: VitalSignCreate,
    ) -> VitalSign:
        """
        Create a new Vital Sign record.
        """

        vital = VitalSign(
            **vital_data.model_dump(),
        )

        return self.repository.create(vital)

    def get_vital_sign(
        self,
        vital_sign_id: str,
    ) -> VitalSign:
        """
        Get Vital Sign by ID.
        """

        vital = self.repository.get_by_id(vital_sign_id)

        if vital is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vital Sign not found.",
            )

        return vital

    def list_vital_signs(self):
        """
        List all Vital Signs.
        """

        return self.repository.get_all()

    def get_admission_vitals(
        self,
        admission_id: str,
    ):
        """
        Get all Vital Signs for an Admission.
        """

        return self.repository.get_by_admission_id(
            admission_id
        )

    def update_vital_sign(
        self,
        vital_sign_id: str,
        vital_data: VitalSignUpdate,
    ) -> VitalSign:
        """
        Update Vital Sign.
        """

        vital = self.get_vital_sign(vital_sign_id)

        for field, value in vital_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(vital, field, value)

        return self.repository.update(vital)

    def delete_vital_sign(
        self,
        vital_sign_id: str,
    ):
        """
        Delete Vital Sign.
        """

        vital = self.get_vital_sign(vital_sign_id)

        self.repository.delete(vital)