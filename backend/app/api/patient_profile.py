from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.patient import Patient
from app.models.lab_result import LabResult
from app.websocket.simulator import simulator

router = APIRouter(
    prefix="/patient",
    tags=["Patient Profile"],
)


@router.get("/{patient_id}")
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Get complete patient profile from DB with simulator overlay.
    """
    try:
        # Fetch from PostgreSQL
        p = db.query(Patient).filter(Patient.id == patient_id).first()
        if p is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
            )
            
        sim_p = next(
            (
                sp
                for sp in simulator.patients
                if sp["id"] == patient_id
            ),
            None,
        )

        adm = p.admissions[0] if p.admissions else None
        labs_db = db.query(LabResult).filter(LabResult.admission_id == adm.id).order_by(LabResult.collected_at.desc()).first() if adm else None

        patient_data = {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "age": 67, # Fallback age
            "gender": p.gender,
            "bed": adm.bed_number if adm else "-",
            "status": p.status,
            "risk_level": "LOW",
            "risk_score": 0.1,
        }
        
        if sim_p:
            patient_data.update({
                "status": sim_p.get("status", p.status),
                "risk_level": sim_p.get("risk_level", "LOW"),
                "risk_score": sim_p.get("risk_score", 0.1),
                "lactate": sim_p.get("lactate", 1.2),
            })

        return {
            "patient": patient_data,

            "labs": {
                "WBC": labs_db.wbc if labs_db else 16.4,
                "Lactate": patient_data.get("lactate", labs_db.lactate if labs_db else 4.6),
                "Creatinine": labs_db.creatinine if labs_db else 1.7,
                "Platelets": labs_db.platelets if labs_db else 132.0,
                "CRP": 118,
                "Procalcitonin": 5.8,
            },

            "medications": [
                "Meropenem",
                "Norepinephrine",
                "Paracetamol",
                "Normal Saline",
            ],

            "clinical_notes": [
                "Patient admitted with septic shock.",
                "Broad-spectrum antibiotics started.",
                "Hypotension persists despite fluids.",
            ],

            "recommendations": [
                "Repeat lactate in 2 hours.",
                "Continue broad-spectrum antibiotics.",
                "Maintain MAP > 65 mmHg.",
                "Monitor urine output hourly.",
            ],
        }
    except Exception as e:
        # Fallback to local simulator patient list
        patient = next(
            (
                p
                for p in simulator.patients
                if p["id"] == patient_id
            ),
            None,
        )

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
            )

        return {
            "patient": patient,

            "labs": {
                "WBC": 16.4,
                "Lactate": patient["lactate"],
                "Creatinine": 1.7,
                "Platelets": 132,
                "CRP": 118,
                "Procalcitonin": 5.8,
            },

            "medications": [
                "Meropenem",
                "Norepinephrine",
                "Paracetamol",
                "Normal Saline",
            ],

            "clinical_notes": [
                "Patient admitted with septic shock.",
                "Broad-spectrum antibiotics started.",
                "Hypotension persists despite fluids.",
            ],

            "recommendations": [
                "Repeat lactate in 2 hours.",
                "Continue broad-spectrum antibiotics.",
                "Maintain MAP > 65 mmHg.",
                "Monitor urine output hourly.",
            ],
        }