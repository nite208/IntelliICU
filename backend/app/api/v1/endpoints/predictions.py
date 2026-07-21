"""
AI Prediction API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.predictor import Predictor
from app.database.session import SessionLocal
from app.repositories.lab_result_repository import LabResultRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.vital_sign_repository import VitalSignRepository
from app.schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter(
    prefix="/predictions",
    tags=["AI Predictions"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/generate/{admission_id}",
    response_model=PredictionResponse,
)
def generate_prediction(
    admission_id: str,
    db: Session = Depends(get_db),
):

    vital_repo = VitalSignRepository(db)
    lab_repo = LabResultRepository(db)
    prediction_repo = PredictionRepository(db)

    vital = vital_repo.get_latest_by_admission_id(admission_id)
    lab = lab_repo.get_latest_by_admission_id(admission_id)

    if vital is None:
        raise HTTPException(
            status_code=404,
            detail="Vital signs not found.",
        )

    if lab is None:
        raise HTTPException(
            status_code=404,
            detail="Laboratory results not found.",
        )

    result = Predictor.predict(vital, lab)

    service = PredictionService(prediction_repo)

    prediction = PredictionCreate(
        admission_id=admission_id,
        prediction_type="Sepsis Risk",
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        recommendation=result["recommendation"],
        model_version=result["model_version"],
    )

    return service.save_prediction(prediction)