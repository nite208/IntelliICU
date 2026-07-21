"""
Prediction Service.
"""

from app.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import PredictionCreate
from app.services.base_service import BaseService


class PredictionService(BaseService[Prediction]):
    """
    Service for AI Predictions.
    """

    def __init__(self, repository: PredictionRepository):
        super().__init__(repository)

    def save_prediction(
        self,
        prediction: PredictionCreate,
    ) -> Prediction:

        prediction_db = Prediction(
            **prediction.model_dump()
        )

        return self.repository.create(
            prediction_db
        )

    def list_predictions(self):
        return self.repository.get_all()

    def get_predictions_by_admission(
        self,
        admission_id: str,
    ):
        return self.repository.get_by_admission_id(
            admission_id
        )