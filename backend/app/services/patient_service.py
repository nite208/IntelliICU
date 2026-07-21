"""
Patient Service.
"""

from uuid import uuid4

from fastapi import HTTPException, status

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.base_service import BaseService


class PatientService(BaseService[Patient]):
    """
    Business logic for Patient.
    """

    def __init__(self, repository: PatientRepository):
        super().__init__(repository)

    def create_patient(
        self,
        patient_data: PatientCreate,
    ) -> Patient:
        """
        Create a new patient.
        Automatically generates Hospital Patient ID.
        """

        hospital_patient_id = f"INT-{str(uuid4())[:8].upper()}"

        patient = Patient(
            hospital_patient_id=hospital_patient_id,
            **patient_data.model_dump(),
        )

        return self.repository.create(patient)

    def get_patient(
        self,
        patient_id: str,
    ) -> Patient:
        """
        Get patient by ID.
        """

        patient = self.repository.get_by_id(patient_id)

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        return patient

    def update_patient(
        self,
        patient_id: str,
        patient_data: PatientUpdate,
    ) -> Patient:
        """
        Update patient.
        """

        patient = self.get_patient(patient_id)

        for field, value in patient_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(patient, field, value)

        return self.repository.update(patient)

    def delete_patient(
        self,
        patient_id: str,
    ):
        """
        Delete patient.
        """

        patient = self.get_patient(patient_id)

        self.repository.delete(patient)

    def list_patients(self):
        """
        List all patients.
        """

        return self.repository.get_all()