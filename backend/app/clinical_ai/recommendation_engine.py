"""
Enterprise Recommendation Engine
"""


class RecommendationEngine:
    """
    Converts AI output into a structured recommendation.
    """

    @staticmethod
    def build(
        clinical_answer: str,
        prediction: dict,
        sources: list,
    ) -> dict:

        risk_score = prediction.get("risk_score", 0)

        if risk_score >= 0.80:
            risk_level = "HIGH"
        elif risk_score >= 0.50:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "clinical_recommendation": clinical_answer,
            "sources": sources,
        }
    