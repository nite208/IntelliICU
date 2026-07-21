"""
Prediction Repository.
"""

from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    """
    Repository for AI Predictions.
    """

    def __init__(self, db: Session):
        super().__init__(Prediction, db)

    def get_by_admission_id(self, admission_id: str):
        return (
            self.db.query(Prediction)
            .filter(
                Prediction.admission_id == admission_id
            )
            .order_by(
                Prediction.created_at.desc()
            )
            .all()
        )