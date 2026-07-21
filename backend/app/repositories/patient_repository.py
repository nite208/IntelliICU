"""
Patient Repository.
"""

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """
    Repository for Patient operations.
    """

    def __init__(self, db: Session):
        super().__init__(Patient, db)

    def get_by_hospital_id(
        self,
        hospital_patient_id: str,
    ) -> Patient | None:

        return (
            self.db.query(Patient)
            .filter(
                Patient.hospital_patient_id == hospital_patient_id
            )
            .first()
        )