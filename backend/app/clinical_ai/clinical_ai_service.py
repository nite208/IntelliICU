"""
Enterprise Clinical AI Service
"""

from app.services.recommendation_service import RecommendationEngine
from app.services.explainability_service import ExplainabilityEngine
from app.services.risk_progress_service import RiskProgressEngine
from app.services.clinical_summary_service import ClinicalSummaryEngine
from app.services.evidence_service import EvidenceService


class ClinicalAIEngine:
    """
    Engine to orchestrate ClinicalSummaryEngine, RecommendationEngine, ExplainabilityEngine, and RiskProgressEngine.
    """

    @staticmethod
    def generate(patient_data: dict) -> dict:
        """
        Orchestrates all clinical AI engines and returns structured clinical workspace AI data.
        """
        recommendations = RecommendationEngine.generate(patient_data)
        explainability = ExplainabilityEngine.generate(patient_data)
        risk_progress = RiskProgressEngine.generate(patient_data)
        summary = ClinicalSummaryEngine.generate(patient_data, recommendations)
        sources = EvidenceService.generate(patient_data)

        return {
            "summary": summary,
            "explainability": explainability,
            "risk_progress": risk_progress,
            "recommendations": recommendations,
            "sources": sources,
        }


class ClinicalAIService:
    """
    Main AI orchestration service.
    """

    def analyze(
        self,
        patient: dict,
        admission: dict,
        vitals: dict,
        labs: dict,
        prediction: dict,
    ) -> dict:
        """
        Unified clinical analysis method.
        """
        patient_data = {
            "patient": patient,
            "admission": admission,
            "vitals": vitals,
            "labs": labs,
            "prediction": prediction
        }

        return ClinicalAIEngine.generate(patient_data)