"""
Test Clinical AI Service
"""

from pprint import pprint

from app.clinical_ai.clinical_ai_service import ClinicalAIService


def main():

    service = ClinicalAIService()

    patient = {
        "patient_id": "P001",
        "name": "John Doe",
    }

    admission = {
        "admission_number": "ADM001",
    }

    vitals = {
        "heart_rate": 132,
        "systolic_bp": 82,
        "diastolic_bp": 48,
        "respiratory_rate": 32,
        "spo2": 89,
        "temperature": 39.4,
    }

    labs = {
        "lactate": 5.2,
        "wbc": 19.6,
        "creatinine": 2.1,
    }

    prediction = {
        "risk_score": 0.93,
    }

    result = service.analyze(
        patient=patient,
        admission=admission,
        vitals=vitals,
        labs=labs,
        prediction=prediction,
    )

    pprint(result)


if __name__ == "__main__":
    main()