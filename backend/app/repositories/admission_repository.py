"""
Admission Repository.
"""

from sqlalchemy.orm import Session

from app.models.admission import Admission
from app.repositories.base_repository import BaseRepository


class AdmissionRepository(BaseRepository[Admission]):
    """
    Repository for ICU Admission operations.
    """

    def __init__(self, db: Session):
        super().__init__(Admission, db)

    def get_by_admission_number(
        self,
        admission_number: str,
    ) -> Admission | None:
        return (
            self.db.query(Admission)
            .filter(
                Admission.admission_number == admission_number
            )
            .first()
        )

    def get_by_patient_id(
        self,
        patient_id: str,
    ):
        return (
            self.db.query(Admission)
            .filter(
                Admission.patient_id == patient_id
            )
            .all()
        )