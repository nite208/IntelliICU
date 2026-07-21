"""
Enterprise Clinical AI Service
"""

from app.services.clinical_summary_service import ClinicalSummaryEngine
from app.services.explainability_service import ExplainabilityEngine
from app.services.recommendation_service import RecommendationEngine
from app.services.risk_progress_service import RiskProgressEngine


class ClinicalAIEngine:
    """
    Enterprise AI Orchestrator.
    Coordinates all AI engines for the Patient Clinical Workspace.
    """

    @staticmethod
    def generate(patient_data: dict) -> dict:
        recommendations = RecommendationEngine.generate(patient_data)

        explainability = ExplainabilityEngine.generate(patient_data)

        risk_progress = RiskProgressEngine.generate(patient_data)

        summary = ClinicalSummaryEngine.generate(
            patient_data,
            recommendations,
        )

        return {
            "summary": summary,
            "explainability": explainability,
            "risk_progress": risk_progress,
            "recommendations": recommendations,
        }