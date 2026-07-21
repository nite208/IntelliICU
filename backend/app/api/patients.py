"""
Patients API
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.clinical_ai_service import ClinicalAIEngine
from app.core.dependencies import get_db
from app.models.patient import Patient
from app.models.vital_sign import VitalSign
from app.models.lab_result import LabResult
from app.websocket.simulator import simulator

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)

# ---------------------------------------------------------------------
# Static Fallback In-Memory Patient Data
# ---------------------------------------------------------------------
PATIENTS = [
    {
        "id": "ICU-10248",
        "name": "Amelia Chen",
        "age": 67,
        "gender": "Female",
        "bed": "MICU-04",
        "status": "Critical",
        "risk_level": "HIGH",
        "risk_score": 0.93,
    },
    {
        "id": "ICU-10251",
        "name": "James Wilson",
        "age": 54,
        "gender": "Male",
        "bed": "MICU-07",
        "status": "Serious",
        "risk_level": "MEDIUM",
        "risk_score": 0.61,
    },
    {
        "id": "ICU-10263",
        "name": "Sophia Garcia",
        "age": 73,
        "gender": "Female",
        "bed": "MICU-11",
        "status": "Stable",
        "risk_level": "LOW",
        "risk_score": 0.18,
    },
]


@router.get("/")
def get_patients(
    search: str = None,
    risk_level: str = None,
    status: str = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Return all ICU patients for the dashboard, querying PostgreSQL with search, filters, pagination, and fallback.
    """
    try:
        query = db.query(Patient)
        
        # Search filter
        if search:
            term = f"%{search}%"
            query = query.filter(
                (Patient.first_name.ilike(term)) | 
                (Patient.last_name.ilike(term)) | 
                (Patient.hospital_patient_id.ilike(term))
            )
            
        # Status filter
        if status and status.lower() != "all":
            query = query.filter(Patient.status.ilike(status))

        # Retrieve database matches
        db_patients = query.offset((page - 1) * size).limit(size).all()
        
        result = []
        for p in db_patients:
            # Find active simulator state for live vitals/risks overlay
            sim_p = next((sp for sp in simulator.patients if sp["id"] == p.id), None)
            
            # Resolve bed number from admissions relation
            bed_num = "-"
            if p.admissions:
                bed_num = p.admissions[0].bed_number
                
            p_dict = {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "age": datetime.now().year - p.date_of_birth.year if p.date_of_birth else 67,
                "gender": p.gender,
                "bed": bed_num,
                "status": p.status,
                "risk_level": "LOW",
                "risk_score": 0.1,
            }
            
            # Overlay simulator live parameters
            if sim_p:
                p_dict.update({
                    "status": sim_p.get("status", p.status),
                    "risk_level": sim_p.get("risk_level", "LOW"),
                    "risk_score": sim_p.get("risk_score", 0.1),
                })
                
            # Filter results if risk_level parameter was passed
            if risk_level and risk_level.lower() != "all" and p_dict["risk_level"].lower() != risk_level.lower():
                continue
                
            result.append(p_dict)
        return result
    except Exception as e:
        # Fallback to local hardcoded records if database is offline or unmigrated
        filtered = list(PATIENTS)
        if search:
            term = search.lower()
            filtered = [p for p in filtered if term in p["name"].lower() or term in p["id"].lower()]
        if status and status.lower() != "all":
            filtered = [p for p in filtered if p["status"].lower() == status.lower()]
        if risk_level and risk_level.lower() != "all":
            filtered = [p for p in filtered if p["risk_level"].lower() == risk_level.lower()]
            
        start = (page - 1) * size
        end = start + size
        return filtered[start:end]


@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Enterprise Patient Clinical Workspace API.
    Retrieves complete clinical profile from PostgreSQL, falling back to simulator logic if offline.
    """
    try:
        # Query patient from DB
        p = db.query(Patient).filter(Patient.id == patient_id).first()
        if p is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found.",
            )

        # Get active simulator state for overlay
        sim_p = next((sp for sp in simulator.patients if sp["id"] == patient_id), None)
        
        # Load from DB admission details
        adm = p.admissions[0] if p.admissions else None
        bed_num = adm.bed_number if adm else "-"
        diagnosis = adm.diagnosis if adm else "Septic Shock"
        ward = adm.ward if adm else "Medical ICU"
        doctor = adm.doctor_name if adm else "Dr. Sarah Johnson"
        
        patient_data = {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "age": datetime.now().year - p.date_of_birth.year if p.date_of_birth else 67,
            "gender": p.gender,
            "bed": bed_num,
            "status": p.status,
            "risk_level": "LOW",
            "risk_score": 0.1,
        }
        if sim_p:
            patient_data.update({
                "status": sim_p.get("status", p.status),
                "risk_level": sim_p.get("risk_level", "LOW"),
                "risk_score": sim_p.get("risk_score", 0.1),
            })
            
        # Load latest vitals and labs from DB
        vitals_db = db.query(VitalSign).filter(VitalSign.admission_id == adm.id).order_by(VitalSign.recorded_at.desc()).first() if adm else None
        labs_db = db.query(LabResult).filter(LabResult.admission_id == adm.id).order_by(LabResult.collected_at.desc()).first() if adm else None
        
        vitals_dict = {
            "heart_rate": vitals_db.heart_rate if vitals_db else 132.0,
            "spo2": vitals_db.spo2 if vitals_db else 89.0,
            "temperature": vitals_db.temperature if vitals_db else 39.2,
            "respiratory_rate": vitals_db.respiratory_rate if vitals_db else 31.0,
            "blood_pressure": {
                "systolic": vitals_db.systolic_bp if vitals_db else 82.0,
                "diastolic": vitals_db.diastolic_bp if vitals_db else 48.0,
            },
            "mean_arterial_pressure": int((vitals_db.systolic_bp + 2 * vitals_db.diastolic_bp) / 3) if vitals_db else 59,
        }
        # Overlay live values if simulator matches
        if sim_p:
            vitals_dict.update({
                "heart_rate": sim_p.get("heart_rate", vitals_dict["heart_rate"]),
                "spo2": sim_p.get("spo2", vitals_dict["spo2"]),
                "temperature": sim_p.get("temperature", vitals_dict["temperature"]),
                "respiratory_rate": sim_p.get("respiratory_rate", vitals_dict["respiratory_rate"]),
                "blood_pressure": {
                    "systolic": sim_p.get("systolic_bp", vitals_dict["blood_pressure"]["systolic"]),
                    "diastolic": sim_p.get("diastolic_bp", vitals_dict["blood_pressure"]["diastolic"]),
                },
                "mean_arterial_pressure": int((sim_p.get("systolic_bp", vitals_dict["blood_pressure"]["systolic"]) + 2 * sim_p.get("diastolic_bp", vitals_dict["blood_pressure"]["diastolic"])) / 3),
            })
            
        labs_dict = {
            "WBC": f"{labs_db.wbc} ×10⁹/L" if labs_db else "18.2 ×10⁹/L",
            "Lactate": f"{labs_db.lactate} mmol/L" if labs_db else "4.6 mmol/L",
            "Creatinine": f"{labs_db.creatinine} mg/dL" if labs_db else "2.1 mg/dL",
            "Platelets": f"{labs_db.platelets} ×10⁹/L" if labs_db else "118 ×10⁹/L",
            "Hemoglobin": f"{labs_db.hemoglobin} g/dL" if labs_db else "10.4 g/dL",
            "CRP": "148 mg/L",
            "Procalcitonin": "18.3 ng/mL",
        }
        if sim_p and "lactate" in sim_p:
            labs_dict["Lactate"] = f"{sim_p['lactate']} mmol/L"
            
        res = {
            "patient": patient_data,
            "admission": {
                "diagnosis": diagnosis,
                "unit": ward,
                "bed": bed_num,
                "admission_date": "2026-07-07 09:25",
                "icu_day": 4,
                "attending_physician": doctor,
                "code_status": "Full Code",
            },
            "vitals": vitals_dict,
            "labs": labs_dict,
            "medications": [
                {
                    "name": "Meropenem",
                    "dose": "1 g",
                    "route": "IV",
                    "frequency": "Every 8 Hours",
                },
                {
                    "name": "Norepinephrine",
                    "dose": "0.15 mcg/kg/min",
                    "route": "IV Infusion",
                    "frequency": "Continuous",
                },
                {
                    "name": "Paracetamol",
                    "dose": "1 g",
                    "route": "IV",
                    "frequency": "Every 6 Hours",
                },
            ],
            "clinical_notes": [
                {
                    "time": "08:15",
                    "author": "Dr. Sarah Johnson",
                    "note": "Patient remains hypotensive despite fluid resuscitation.",
                },
                {
                    "time": "09:10",
                    "author": "ICU Nurse",
                    "note": "Urine output improving after vasopressor adjustment.",
                },
                {
                    "time": "10:00",
                    "author": "Critical Care Team",
                    "note": "Continue sepsis bundle and repeat lactate.",
                },
            ],
            "alerts": [
                {
                    "severity": "HIGH",
                    "title": "Hypotension",
                    "message": "Mean arterial pressure below target.",
                },
                {
                    "severity": "MEDIUM",
                    "title": "High Lactate",
                    "message": "Repeat lactate recommended within 4 hours.",
                },
            ],
            "recommendations": [],
            "history": [
                {
                    "time": "08:00",
                    "heart_rate": 128,
                    "spo2": 91,
                    "temperature": 38.8,
                    "respiratory_rate": 28,
                    "map": 64,
                },
                {
                    "time": "09:00",
                    "heart_rate": 129,
                    "spo2": 90,
                    "temperature": 39.0,
                    "respiratory_rate": 29,
                    "map": 62,
                },
                {
                    "time": "10:00",
                    "heart_rate": 131,
                    "spo2": 90,
                    "temperature": 39.1,
                    "respiratory_rate": 30,
                    "map": 61,
                },
                {
                    "time": "11:00",
                    "heart_rate": 130,
                    "spo2": 89,
                    "temperature": 39.2,
                    "respiratory_rate": 30,
                    "map": 60,
                },
                {
                    "time": "12:00",
                    "heart_rate": 132,
                    "spo2": 89,
                    "temperature": 39.2,
                    "respiratory_rate": 31,
                    "map": 59,
                },
            ],
            "ai": {
                "summary": {
                    "overall_condition": "Critical but Hemodynamically Stable",
                    "confidence": 0.96,
                    "clinical_reasoning": (
                        "Persistent hypotension, elevated lactate, "
                        "tachycardia and inflammatory markers indicate "
                        "ongoing septic shock with a high probability "
                        "of clinical deterioration."
                    ),
                    "priority_actions": [
                        "Maintain MAP above 65 mmHg.",
                        "Repeat lactate in 4 hours.",
                        "Continue broad-spectrum antibiotics.",
                        "Monitor renal function and urine output.",
                    ],
                },
                "explainability": {},
                "risk_progress": {},
            },
            "timeline": [
                {
                    "time": "07:45",
                    "type": "Admission",
                    "description": "Patient admitted to Medical ICU.",
                },
                {
                    "time": "08:10",
                    "type": "Medication",
                    "description": "Meropenem initiated.",
                },
                {
                    "time": "08:40",
                    "type": "Alert",
                    "description": "Hypotension alert generated.",
                },
                {
                    "time": "09:15",
                    "type": "Laboratory",
                    "description": "Lactate increased to 4.6 mmol/L.",
                },
                {
                    "time": "10:00",
                    "type": "AI",
                    "description": "AI predicted high risk of septic shock progression.",
                },
            ],
        }
        ai = ClinicalAIEngine.generate(res)
        res["recommendations"] = ai["recommendations"]
        res["ai"]["summary"] = ai["summary"]
        res["ai"]["explainability"] = ai["explainability"]
        res["ai"]["risk_progress"] = ai["risk_progress"]
        return res
    except Exception as e:
        # Fallback to local static object
        patient = next((p for p in PATIENTS if p["id"] == patient_id), None)
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found.")
        
        res = {
            "patient": patient,
            "admission": {
                "diagnosis": "Septic Shock",
                "unit": "Medical ICU",
                "bed": patient["bed"],
                "admission_date": "2026-07-07 09:25",
                "icu_day": 4,
                "attending_physician": "Dr. Sarah Johnson",
                "code_status": "Full Code",
            },
            "vitals": {
                "heart_rate": 132,
                "spo2": 89,
                "temperature": 39.2,
                "respiratory_rate": 31,
                "blood_pressure": {
                    "systolic": 82,
                    "diastolic": 48,
                },
                "mean_arterial_pressure": 59,
            },
            "labs": {
                "WBC": "18.2 ×10⁹/L",
                "Lactate": "4.6 mmol/L",
                "Creatinine": "2.1 mg/dL",
                "Platelets": "118 ×10⁹/L",
                "Hemoglobin": "10.4 g/dL",
                "CRP": "148 mg/L",
                "Procalcitonin": "18.3 ng/mL",
            },
            "medications": [
                {
                    "name": "Meropenem",
                    "dose": "1 g",
                    "route": "IV",
                    "frequency": "Every 8 Hours",
                },
                {
                    "name": "Norepinephrine",
                    "dose": "0.15 mcg/kg/min",
                    "route": "IV Infusion",
                    "frequency": "Continuous",
                },
                {
                    "name": "Paracetamol",
                    "dose": "1 g",
                    "route": "IV",
                    "frequency": "Every 6 Hours",
                },
            ],
            "clinical_notes": [
                {
                    "time": "08:15",
                    "author": "Dr. Sarah Johnson",
                    "note": "Patient remains hypotensive despite fluid resuscitation.",
                },
                {
                    "time": "09:10",
                    "author": "ICU Nurse",
                    "note": "Urine output improving after vasopressor adjustment.",
                },
                {
                    "time": "10:00",
                    "author": "Critical Care Team",
                    "note": "Continue sepsis bundle and repeat lactate.",
                },
            ],
            "alerts": [
                {
                    "severity": "HIGH",
                    "title": "Hypotension",
                    "message": "Mean arterial pressure below target.",
                },
                {
                    "severity": "MEDIUM",
                    "title": "High Lactate",
                    "message": "Repeat lactate recommended within 4 hours.",
                },
            ],
            "recommendations": [],
            "history": [
                {
                    "time": "08:00",
                    "heart_rate": 128,
                    "spo2": 91,
                    "temperature": 38.8,
                    "respiratory_rate": 28,
                    "map": 64,
                },
                {
                    "time": "09:00",
                    "heart_rate": 129,
                    "spo2": 90,
                    "temperature": 39.0,
                    "respiratory_rate": 29,
                    "map": 62,
                },
                {
                    "time": "10:00",
                    "heart_rate": 131,
                    "spo2": 90,
                    "temperature": 39.1,
                    "respiratory_rate": 30,
                    "map": 61,
                },
                {
                    "time": "11:00",
                    "heart_rate": 130,
                    "spo2": 89,
                    "temperature": 39.2,
                    "respiratory_rate": 30,
                    "map": 60,
                },
                {
                    "time": "12:00",
                    "heart_rate": 132,
                    "spo2": 89,
                    "temperature": 39.2,
                    "respiratory_rate": 31,
                    "map": 59,
                },
            ],
            "ai": {
                "summary": {
                    "overall_condition": "Critical but Hemodynamically Stable",
                    "confidence": 0.96,
                    "clinical_reasoning": (
                        "Persistent hypotension, elevated lactate, "
                        "tachycardia and inflammatory markers indicate "
                        "ongoing septic shock with a high probability "
                        "of clinical deterioration."
                    ),
                    "priority_actions": [
                        "Maintain MAP above 65 mmHg.",
                        "Repeat lactate in 4 hours.",
                        "Continue broad-spectrum antibiotics.",
                        "Monitor renal function and urine output.",
                    ],
                },
                "explainability": {},
                "risk_progress": {},
            },
            "timeline": [
                {
                    "time": "07:45",
                    "type": "Admission",
                    "description": "Patient admitted to Medical ICU.",
                },
                {
                    "time": "08:10",
                    "type": "Medication",
                    "description": "Meropenem initiated.",
                },
                {
                    "time": "08:40",
                    "type": "Alert",
                    "description": "Hypotension alert generated.",
                },
                {
                    "time": "09:15",
                    "type": "Laboratory",
                    "description": "Lactate increased to 4.6 mmol/L.",
                },
                {
                    "time": "10:00",
                    "type": "AI",
                    "description": "AI predicted high risk of septic shock progression.",
                },
            ],
        }
        ai = ClinicalAIEngine.generate(res)
        res["recommendations"] = ai["recommendations"]
        res["ai"]["summary"] = ai["summary"]
        res["ai"]["explainability"] = ai["explainability"]
        res["ai"]["risk_progress"] = ai["risk_progress"]
        return res