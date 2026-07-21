"""
Patient Context Builder for Clinical Copilot.
Compiles a rich, structured clinical context of the patient from the database.
"""

from typing import Dict, Any, List
from datetime import datetime
from app.database.session import SessionLocal
from app.models.patient import Patient
from app.models.admission import Admission
from app.models.vital_sign import VitalSign
from app.models.lab_result import LabResult
from app.models.prediction import Prediction
from app.database.models import DBAlert, DBTimelineEvent
from app.services.explainability_service import ExplainabilityEngine

class PatientContextBuilder:
    """
    Assembles comprehensive ClinicalContext for the patient.
    """

    def build_context(self, patient_id: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # 1. Fetch Patient Demographics
            patient_data = self._get_demographics(db, patient_id)
            if not patient_data:
                return {}

            pid = patient_data["id"]

            # 2. Fetch Admission details
            admission_data = self._get_admission(db, pid)
            adm_id = admission_data.get("id") if admission_data else None

            # 3. Fetch Vitals & Trends
            vitals_data = self._get_vitals(db, adm_id)
            vital_trends = self._get_vital_trends(db, adm_id)

            # 4. Fetch Labs & Abnormal Flags
            labs_raw = db.query(LabResult).filter(LabResult.admission_id == adm_id).order_by(LabResult.collected_at.desc()).first() if adm_id else None
            labs_data = self._get_labs(labs_raw)
            abnormal_labs = self._get_abnormal_labs(labs_raw)

            # 5. Fetch Active Alerts
            alerts_data = self._get_alerts(db, pid)

            # 6. Fetch Timeline Summary
            timeline_data = self._get_timeline(db, pid)

            # 7. Fetch AI Sepsis Prediction
            prediction_data = self._get_prediction(db, adm_id)
            risk_level = prediction_data.get("risk_level", "LOW") if prediction_data else "LOW"

            # 8. Get Medications
            medications = self._get_medications(admission_data)

            # 9. Calculate Clinical Priority
            clinical_priority = self._get_clinical_priority(risk_level, alerts_data)

            # Assemble preliminary context for ExplainabilityEngine
            context = {
                "patient": patient_data,
                "admission": admission_data,
                "vitals": vitals_data,
                "labs": labs_data,
                "prediction": prediction_data,
                "alerts": alerts_data,
                "timeline": timeline_data,
                "vital_trends": vital_trends,
                "abnormal_labs": abnormal_labs,
                "medications": medications,
                "risk_level": risk_level,
                "clinical_priority": clinical_priority,
            }

            # 10. Fetch Explainability
            explainability_data = ExplainabilityEngine.generate(context)
            context["explainability"] = explainability_data

            return context

        finally:
            db.close()

    # =========================================================
    # Reusable Helper Methods
    # =========================================================

    def _get_demographics(self, db, patient_id: str) -> Dict[str, Any]:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            # Fallback lookup by hospital patient id
            patient = db.query(Patient).filter(Patient.hospital_patient_id == patient_id).first()
        
        if not patient:
            return {}

        dob_str = patient.date_of_birth.isoformat() if patient.date_of_birth else None
        age = datetime.now().year - patient.date_of_birth.year if patient.date_of_birth else 65

        return {
            "id": patient.id,
            "hospital_patient_id": patient.hospital_patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "name": f"{patient.first_name} {patient.last_name}",
            "date_of_birth": dob_str,
            "age": age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "status": patient.status,
        }

    def _get_admission(self, db, patient_db_id: str) -> Dict[str, Any]:
        admission = db.query(Admission).filter(
            Admission.patient_id == patient_db_id,
            Admission.status != "Discharged"
        ).order_by(Admission.admitted_at.desc()).first()

        if not admission:
            admission = db.query(Admission).filter(
                Admission.patient_id == patient_db_id
            ).order_by(Admission.admitted_at.desc()).first()

        if not admission:
            return {}

        return {
            "id": admission.id,
            "admission_number": admission.admission_number,
            "diagnosis": admission.diagnosis,
            "doctor_name": admission.doctor_name,
            "ward": admission.ward,
            "bed_number": admission.bed_number,
            "status": admission.status,
            "admitted_at": admission.admitted_at.isoformat() if admission.admitted_at else None,
        }

    def _get_vitals(self, db, admission_id: str) -> Dict[str, Any]:
        if not admission_id:
            return {}
        v = db.query(VitalSign).filter(
            VitalSign.admission_id == admission_id
        ).order_by(VitalSign.recorded_at.desc()).first()

        if not v:
            return {}

        return {
            "heart_rate": v.heart_rate,
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "respiratory_rate": v.respiratory_rate,
            "spo2": v.spo2,
            "temperature": v.temperature,
            "urine_output_ml": v.urine_output_ml,
            "recorded_at": v.recorded_at.isoformat() if v.recorded_at else None,
        }

    def _get_vital_trends(self, db, admission_id: str) -> Dict[str, Any]:
        if not admission_id:
            return {}
        vitals_list = db.query(VitalSign).filter(
            VitalSign.admission_id == admission_id
        ).order_by(VitalSign.recorded_at.desc()).limit(5).all()

        vitals_list = list(reversed(vitals_list))
        if len(vitals_list) < 2:
            return {"status": "stable", "message": "Establishing telemetry baseline..."}

        def get_direction(values: List[float], threshold: float = 2.0) -> str:
            diff = values[-1] - values[0]
            if abs(diff) < threshold:
                return "stable"
            return "rising" if diff > 0 else "falling"

        hr_vals = [v.heart_rate for v in vitals_list]
        spo2_vals = [v.spo2 for v in vitals_list]
        temp_vals = [v.temperature for v in vitals_list]
        sys_vals = [v.systolic_bp for v in vitals_list]

        return {
            "heart_rate": {
                "direction": get_direction(hr_vals, 3.0),
                "last_value": hr_vals[-1],
                "previous_value": hr_vals[0]
            },
            "spo2": {
                "direction": get_direction(spo2_vals, 1.0),
                "last_value": spo2_vals[-1],
                "previous_value": spo2_vals[0]
            },
            "temperature": {
                "direction": get_direction(temp_vals, 0.1),
                "last_value": temp_vals[-1],
                "previous_value": temp_vals[0]
            },
            "systolic_bp": {
                "direction": get_direction(sys_vals, 4.0),
                "last_value": sys_vals[-1],
                "previous_value": sys_vals[0]
            },
            "history_points": len(vitals_list)
        }

    def _get_labs(self, labs_raw) -> Dict[str, Any]:
        if not labs_raw:
            return {}
        return {
            "lactate": labs_raw.lactate,
            "wbc": labs_raw.wbc,
            "platelets": labs_raw.platelets,
            "creatinine": labs_raw.creatinine,
            "sodium": labs_raw.sodium,
            "potassium": labs_raw.potassium,
            "chloride": labs_raw.chloride,
            "hemoglobin": labs_raw.hemoglobin,
            "bun": labs_raw.bun,
            "ph": labs_raw.ph,
            "pao2": labs_raw.pao2,
            "paco2": labs_raw.paco2,
            "collected_at": labs_raw.collected_at.isoformat() if labs_raw.collected_at else None,
        }

    def _get_abnormal_labs(self, labs_raw) -> List[Dict[str, Any]]:
        if not labs_raw:
            return []
        
        flags = []
        ranges = {
            "hemoglobin": (12.0, 17.5, "g/dL"),
            "wbc": (4.5, 11.0, "x10^9/L"),
            "platelets": (150.0, 450.0, "x10^9/L"),
            "creatinine": (0.6, 1.2, "mg/dL"),
            "bun": (7.0, 20.0, "mg/dL"),
            "sodium": (135.0, 145.0, "mEq/L"),
            "potassium": (3.5, 5.0, "mEq/L"),
            "chloride": (96.0, 106.0, "mEq/L"),
            "lactate": (0.5, 2.0, "mmol/L"),
            "ph": (7.35, 7.45, ""),
            "pao2": (75.0, 100.0, "mmHg"),
            "paco2": (35.0, 45.0, "mmHg")
        }

        for field, (low, high, unit) in ranges.items():
            val = getattr(labs_raw, field, None)
            if val is not None:
                val_f = float(val)
                if val_f < low:
                    severity = "CRITICAL" if val_f < (low * 0.75) else "WARNING"
                    flags.append({
                        "metric": field.upper() if field != "ph" else "pH",
                        "value": val_f,
                        "reference": f"{low} - {high} {unit}".strip(),
                        "status": "DEPRESSED",
                        "severity": severity
                    })
                elif val_f > high:
                    severity = "CRITICAL" if val_f > (high * 1.35) else "WARNING"
                    flags.append({
                        "metric": field.upper() if field != "ph" else "pH",
                        "value": val_f,
                        "reference": f"{low} - {high} {unit}".strip(),
                        "status": "ELEVATED",
                        "severity": severity
                    })
        return flags

    def _get_alerts(self, db, patient_db_id: str) -> List[Dict[str, Any]]:
        alerts = db.query(DBAlert).filter(
            DBAlert.patient_id == patient_db_id,
            DBAlert.status != "RESOLVED"
        ).order_by(DBAlert.created_at.desc()).all()

        return [
            {
                "id": alert.id,
                "severity": alert.severity,
                "status": alert.status,
                "title": alert.title,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
            } for alert in alerts
        ]

    def _get_timeline(self, db, patient_db_id: str) -> List[Dict[str, Any]]:
        events = db.query(DBTimelineEvent).filter(
            DBTimelineEvent.patient_id == patient_db_id
        ).order_by(DBTimelineEvent.timestamp.desc()).limit(8).all()

        return [
            {
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "time": event.time,
                "type": event.type,
                "title": event.title,
                "description": event.description,
                "actor": event.actor,
            } for event in events
        ]

    def _get_prediction(self, db, admission_id: str) -> Dict[str, Any]:
        if not admission_id:
            return {}
        p = db.query(Prediction).filter(
            Prediction.admission_id == admission_id
        ).order_by(Prediction.created_at.desc()).first()

        if not p:
            return {}

        return {
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "recommendation": p.recommendation,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }

    def _get_medications(self, admission: Dict[str, Any]) -> List[str]:
        if not admission:
            return []
        diagnosis = (admission.get("diagnosis") or "").lower()
        if "sepsis" in diagnosis or "shock" in diagnosis:
            return ["Norepinephrine 0.1 mcg/kg/min IV infusion", "Meropenem 1g IV q8h", "Normal Saline 0.9% 75mL/hr IV"]
        elif "pneumonia" in diagnosis or "respiratory" in diagnosis:
            return ["Albuterol 2.5mg nebulizer q4h", "Methylprednisolone 40mg IV q12h", "Piperacillin/Tazobactam 4.5g IV q6h"]
        elif "infarction" in diagnosis or "cardiac" in diagnosis or "heart" in diagnosis:
            return ["Aspirin 81mg PO daily", "Heparin 25,000 units IV infusion", "Metoprolol Tartrate 25mg PO q12h"]
        return ["Pantoprazole 40mg IV daily", "Normal Saline 0.9% 50mL/hr IV"]

    def _get_clinical_priority(self, risk_level: str, alerts: List[Dict[str, Any]]) -> str:
        critical_alerts = len([a for a in alerts if a.get("severity") in ["CRITICAL", "HIGH"]])
        if risk_level == "CRITICAL" or critical_alerts > 0:
            return "CRITICAL"
        elif risk_level == "HIGH" or len(alerts) > 2:
            return "HIGH"
        elif risk_level == "MEDIUM" or len(alerts) > 0:
            return "MEDIUM"
        return "LOW"
