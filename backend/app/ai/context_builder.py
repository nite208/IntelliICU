"""
Clinical Context Builder
"""

from sqlalchemy.orm import Session

from app.repositories.admission_repository import AdmissionRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.vital_sign_repository import VitalSignRepository
from app.repositories.lab_result_repository import LabResultRepository
from app.repositories.prediction_repository import PredictionRepository


class ContextBuilder:
    """
    Builds the complete clinical context required by the AI system.
    """

    def __init__(self, db: Session):

        self.admission_repo = AdmissionRepository(db)
        self.patient_repo = PatientRepository(db)
        self.vital_repo = VitalSignRepository(db)
        self.lab_repo = LabResultRepository(db)
        self.prediction_repo = PredictionRepository(db)

    def build(
        self,
        admission_id: str,
    ) -> dict:

        admission = self.admission_repo.get_by_id(
            admission_id
        )

        if admission is None:
            raise ValueError(
                "Admission not found."
            )

        patient = self.patient_repo.get_by_id(
            admission.patient_id
        )

        vitals = self.vital_repo.get_latest_by_admission_id(
            admission_id
        )

        labs = self.lab_repo.get_latest_by_admission_id(
            admission_id
        )

        prediction = self.prediction_repo.get_latest_by_admission_id(
            admission_id
        )

        return {
            "patient": patient,
            "admission": admission,
            "vitals": vitals,
            "labs": labs,
            "prediction": prediction,
        }