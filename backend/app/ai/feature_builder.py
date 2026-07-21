"""
Feature Builder for IntelliICU Production Model
"""

from app.models.lab_result import LabResult
from app.models.vital_sign import VitalSign


class FeatureBuilder:
    """
    Builds the canonical feature vector used by
    the production ML model.
    """

    @staticmethod
    def build(
        vital: VitalSign,
        lab: LabResult,
    ) -> dict:

        return {

            "heart_rate": vital.heart_rate,
            "systolic_bp": vital.systolic_bp,
            "diastolic_bp": vital.diastolic_bp,
            "respiratory_rate": vital.respiratory_rate,
            "spo2": vital.spo2,
            "temperature": vital.temperature,

            "wbc": lab.wbc,
            "platelets": lab.platelets,
            "creatinine": lab.creatinine,
            "bun": lab.bun,
            "potassium": lab.potassium,
            "chloride": lab.chloride,
            "lactate": lab.lactate,
        }