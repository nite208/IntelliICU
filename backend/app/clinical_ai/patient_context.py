"""
Enterprise Patient Context Builder
"""


class PatientContextBuilder:
    """
    Builds a unified patient context for AI processing.
    """

    @staticmethod
    def build(
        patient: dict,
        admission: dict,
        vitals: dict,
        labs: dict,
        prediction: dict,
    ) -> dict:

        return {
            "patient": patient,
            "admission": admission,
            "vitals": vitals,
            "labs": labs,
            "prediction": prediction,
        }