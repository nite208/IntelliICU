"""
Vital Sign Repository.
"""

from sqlalchemy.orm import Session

from app.models.vital_sign import VitalSign
from app.repositories.base_repository import BaseRepository


class VitalSignRepository(BaseRepository[VitalSign]):
    """
    Repository for Vital Signs.
    """

    def __init__(self, db: Session):
        super().__init__(VitalSign, db)

    def get_by_admission_id(
        self,
        admission_id: str,
    ):
        """
        Return all vital signs for an admission.
        """
        return (
            self.db.query(VitalSign)
            .filter(
                VitalSign.admission_id == admission_id
            )
            .order_by(
                VitalSign.recorded_at.desc()
            )
            .all()
        )
    def get_latest_by_admission_id(
            self,
            admission_id: str,
            ):
        return (
        self.db.query(VitalSign)
        .filter(
            VitalSign.admission_id == admission_id
        )
        .order_by(
            VitalSign.recorded_at.desc()
        )
        .first()
    )