"""
Rule-Based AI Prediction Engine.
"""


class RulesEngine:
    """
    Initial AI engine using clinical rules.

    This will later be replaced by
    XGBoost / LightGBM / Deep Learning.
    """

    @staticmethod
    def predict(features: dict) -> dict:
        """
        Generate a clinical risk prediction.
        """

        score = 0

        # Heart Rate
        if features["heart_rate"] > 100:
            score += 15

        # Oxygen Saturation
        if features["spo2"] < 92:
            score += 20

        # Temperature
        if features["temperature"] > 38.5:
            score += 10

        # Respiratory Rate
        if features["respiratory_rate"] > 22:
            score += 15

        # WBC
        if features["wbc"] > 12:
            score += 10

        # Lactate
        if features["lactate"] > 2:
            score += 20

        # Creatinine
        if features["creatinine"] > 1.5:
            score += 10

        # GCS
        if features["glasgow_coma_scale"] < 13:
            score += 20

        score = min(score, 100)

        if score >= 70:
            risk = "HIGH"

            recommendation = (
                "Immediate ICU physician review. "
                "Consider sepsis protocol and continuous monitoring."
            )

        elif score >= 40:
            risk = "MEDIUM"

            recommendation = (
                "Increase monitoring frequency and repeat laboratory tests."
            )

        else:
            risk = "LOW"

            recommendation = (
                "Continue routine ICU monitoring."
            )

        return {
            "risk_score": score,
            "risk_level": risk,
            "recommendation": recommendation,
        }