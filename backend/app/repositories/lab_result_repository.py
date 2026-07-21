"""
Lab Result Repository.
"""

from sqlalchemy.orm import Session

from app.models.lab_result import LabResult
from app.repositories.base_repository import BaseRepository


class LabResultRepository(BaseRepository[LabResult]):

    def __init__(self, db: Session):
        super().__init__(LabResult, db)

    def get_by_admission_id(
        self,
        admission_id: str,
    ):
        return (
            self.db.query(LabResult)
            .filter(
                LabResult.admission_id == admission_id
            )
            .order_by(
                LabResult.collected_at.desc()
            )
            .all()
        )
    def get_latest_by_admission_id(
            self,
            admission_id: str,
            ):
        return (
            self.db.query(LabResult)
            .filter(
            LabResult.admission_id == admission_id
        )
        .order_by(
            LabResult.collected_at.desc()
        )
        .first()
    )