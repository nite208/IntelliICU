"""
Clinical AI API
"""

from fastapi import APIRouter

from app.clinical_ai.clinical_ai_service import ClinicalAIService
from app.schemas.clinical_ai import ClinicalAIRequest
from app.schemas.clinical_ai_response import ClinicalAIResponse

router = APIRouter(
    prefix="/clinical-ai",
    tags=["Clinical AI"],
)

service = ClinicalAIService()


@router.post(
    "/",
    response_model=ClinicalAIResponse,
    summary="Analyze Patient",
    description="""
Runs the complete Clinical AI pipeline.

Pipeline:
React Frontend
      ↓
FastAPI Endpoint
      ↓
ClinicalAIService
      ↓
Patient Context Builder
      ↓
Prediction + RAG + Qwen LLM
      ↓
Evidence-based Recommendation
      ↓
Structured Clinical Response
""",
)
def analyze_patient(request: ClinicalAIRequest):
    """
    Analyze a patient using the Clinical AI pipeline.
    """

    result = service.analyze(
        patient=request.patient.model_dump(),
        admission=request.admission.model_dump(),
        vitals=request.vitals.model_dump(),
        labs=request.labs.model_dump(),
        prediction=request.prediction.model_dump(),
    )

    return result