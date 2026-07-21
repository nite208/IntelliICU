"""
Live ICU Data Simulator
"""

import asyncio
import random
from datetime import datetime

from app.websocket.manager import manager
from app.alerts.manager import manager as alert_manager
from app.alerts.models import AlertSeverity
from app.services.timeline_engine import timeline_engine
import uuid
from app.database.session import SessionLocal
from app.models.patient import Patient
from app.models.admission import Admission
from app.models.vital_sign import VitalSign
from app.models.lab_result import LabResult
from app.telemetry.trend_engine import telemetry_engine


class ICUSimulator:
    """
    Enterprise ICU Simulator
    Simulates dashboard metrics and patient status updates.
    """

    def __init__(self):

        self.dashboard = {
            "total_patients": 48,
            "critical_patients": 12,
            "bed_occupancy": 85.7,
            "active_alerts": 7,
            "available_beds": 8,
            "icu_capacity": 56,
        }

        self.patients = [
            {
                "id": "ICU-10248",
                "name": "Amelia Chen",
                "age": 67,
                "gender": "Female",
                "bed": "MICU-04",
                "status": "Critical",
                "risk_level": "HIGH",
                "risk_score": 0.93,
                "heart_rate": 132,
                "spo2": 89,
                "temperature": 39.2,
                "respiratory_rate": 31,
                "systolic_bp": 82,
                "diastolic_bp": 48,
                "lactate": 4.6,
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
                "heart_rate": 108,
                "spo2": 95,
                "temperature": 38.2,
                "respiratory_rate": 24,
                "systolic_bp": 104,
                "diastolic_bp": 66,
                "lactate": 2.7,
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
                "heart_rate": 76,
                "spo2": 98,
                "temperature": 36.8,
                "respiratory_rate": 17,
                "systolic_bp": 122,
                "diastolic_bp": 78,
                "lactate": 1.2,
            },
            {
                "id": "ICU-10264",
                "name": "Robert Miller",
                "age": 58,
                "gender": "Male",
                "bed": "MICU-01",
                "status": "Critical",
                "risk_level": "HIGH",
                "risk_score": 0.88,
                "heart_rate": 125,
                "spo2": 91,
                "temperature": 38.9,
                "respiratory_rate": 28,
                "systolic_bp": 86,
                "diastolic_bp": 52,
                "lactate": 3.9,
            },
            {
                "id": "ICU-10265",
                "name": "Mary Davis",
                "age": 67,
                "gender": "Female",
                "bed": "MICU-02",
                "status": "Serious",
                "risk_level": "MEDIUM",
                "risk_score": 0.65,
                "heart_rate": 112,
                "spo2": 93,
                "temperature": 38.4,
                "respiratory_rate": 25,
                "systolic_bp": 98,
                "diastolic_bp": 60,
                "lactate": 2.9,
            },
            {
                "id": "ICU-10266",
                "name": "John Rodriguez",
                "age": 45,
                "gender": "Male",
                "bed": "MICU-03",
                "status": "Stable",
                "risk_level": "LOW",
                "risk_score": 0.15,
                "heart_rate": 72,
                "spo2": 99,
                "temperature": 36.6,
                "respiratory_rate": 15,
                "systolic_bp": 118,
                "diastolic_bp": 74,
                "lactate": 1.1,
            },
            {
                "id": "ICU-10267",
                "name": "Linda Martinez",
                "age": 62,
                "gender": "Female",
                "bed": "MICU-05",
                "status": "Critical",
                "risk_level": "HIGH",
                "risk_score": 0.91,
                "heart_rate": 128,
                "spo2": 90,
                "temperature": 39.1,
                "respiratory_rate": 30,
                "systolic_bp": 84,
                "diastolic_bp": 50,
                "lactate": 4.3,
            },
            {
                "id": "ICU-10268",
                "name": "William Hernandez",
                "age": 73,
                "gender": "Male",
                "bed": "MICU-06",
                "status": "Serious",
                "risk_level": "MEDIUM",
                "risk_score": 0.58,
                "heart_rate": 105,
                "spo2": 94,
                "temperature": 38.0,
                "respiratory_rate": 22,
                "systolic_bp": 106,
                "diastolic_bp": 68,
                "lactate": 2.5,
            },
            {
                "id": "ICU-10269",
                "name": "Elizabeth Lopez",
                "age": 50,
                "gender": "Female",
                "bed": "MICU-08",
                "status": "Stable",
                "risk_level": "LOW",
                "risk_score": 0.22,
                "heart_rate": 80,
                "spo2": 97,
                "temperature": 37.0,
                "respiratory_rate": 18,
                "systolic_bp": 124,
                "diastolic_bp": 80,
                "lactate": 1.4,
            },
            {
                "id": "ICU-10270",
                "name": "David Gonzalez",
                "age": 69,
                "gender": "Male",
                "bed": "MICU-09",
                "status": "Critical",
                "risk_level": "HIGH",
                "risk_score": 0.85,
                "heart_rate": 122,
                "spo2": 92,
                "temperature": 38.7,
                "respiratory_rate": 26,
                "systolic_bp": 88,
                "diastolic_bp": 54,
                "lactate": 3.6,
            },
        ]

        self.alerts = []
        self.last_vitals_log = {}

    async def start(self):

        print("=" * 60)
        print("SIMULATOR: ICU Live Simulator Started")
        print("=" * 60)

        while True:

            self._update_dashboard()
            self._update_patients()
            self._generate_alerts()
            await manager.ping_all()

            timestamp = datetime.now().strftime("%H:%M:%S")

            await manager.broadcast_dashboard(
                {
                    "type": "dashboard_update",
                    "timestamp": timestamp,
                    "data": self.dashboard,
                }
            )

            for patient in self.patients:
                try:
                    patient["telemetry_trends"] = telemetry_engine.build_telemetry_trends_payload(
                        patient["id"]
                    )
                except Exception:
                    patient["telemetry_trends"] = {}

            await manager.broadcast(
                {
                    "type": "patients_update",
                    "timestamp": timestamp,
                    "data": self.patients,
                }
            )
            
            await manager.broadcast_alerts(
                {
                    "type": "alerts_update",
                    "timestamp": timestamp,
                     "data": [
                         alert.model_dump(mode="json")
                         for alert in alert_manager.active_alerts()
                     ],
                }
            )
            
            for patient in self.patients:
                await manager.broadcast_patient(
                    patient["id"],
                    {
                        "type": "patient_update",
                        "timestamp": timestamp,
                        "data": patient,
                        "telemetry_trends": patient["telemetry_trends"],
                    }
                )

            await asyncio.sleep(2)

    def _update_dashboard(self):

        self.dashboard["total_patients"] = max(
            40,
            min(
                56,
                self.dashboard["total_patients"] + random.randint(-1, 1),
            ),
        )

        self.dashboard["critical_patients"] = max(
            5,
            min(
                20,
                self.dashboard["critical_patients"] + random.randint(-1, 1),
            ),
        )

        self.dashboard["active_alerts"] = max(
            0,
            min(
                15,
                self.dashboard["active_alerts"] + random.randint(-1, 1),
            ),
        )

        self.dashboard["available_beds"] = (
            self.dashboard["icu_capacity"]
            - self.dashboard["total_patients"]
        )

        self.dashboard["bed_occupancy"] = round(
            (
                self.dashboard["total_patients"]
                / self.dashboard["icu_capacity"]
            )
            * 100,
            1,
        )

    def _update_patients(self):

        for patient in self.patients:
            old_level = patient["risk_level"]

            # Update risk score
            delta = random.uniform(-0.03, 0.03)

            patient["risk_score"] = round(
                max(
                    0.05,
                    min(
                        0.99,
                        patient["risk_score"] + delta,
                    ),
                ),
                2,
            )

            # Update risk level
            if patient["risk_score"] >= 0.80:
                patient["risk_level"] = "HIGH"
                patient["status"] = "Critical"

            elif patient["risk_score"] >= 0.50:
                patient["risk_level"] = "MEDIUM"
                patient["status"] = "Serious"

            else:
                patient["risk_level"] = "LOW"
                patient["status"] = "Stable"

            if old_level != patient["risk_level"]:
                timeline_engine.add_event(
                    patient_id=patient["id"],
                    event_type="AI",
                    title="Sepsis Risk Level Changed",
                    description=f"Sepsis risk level transitioned from {old_level} to {patient['risk_level']}.",
                    actor="System",
                    metadata={"old_level": old_level, "new_level": patient["risk_level"]}
                )

            # Live Vital Signs
            patient["heart_rate"] = max(
                45,
                min(
                    180,
                    patient["heart_rate"] + random.randint(-3, 3),
                ),
            )

            patient["spo2"] = max(
                80,
                min(
                    100,
                    patient["spo2"] + random.randint(-1, 1),
                ),
            )

            patient["temperature"] = round(
                max(
                    35.5,
                    min(
                        41.0,
                        patient["temperature"] + random.uniform(-0.2, 0.2),
                    ),
                ),
                1,
            )

            patient["respiratory_rate"] = max(
                10,
                min(
                    40,
                    patient["respiratory_rate"] + random.randint(-2, 2),
                ),
            )

            patient["systolic_bp"] = max(
                70,
                min(
                    180,
                    patient["systolic_bp"] + random.randint(-3, 3),
                ),
            )

            patient["diastolic_bp"] = max(
                40,
                min(
                    120,
                    patient["diastolic_bp"] + random.randint(-2, 2),
                ),
            )

            patient["lactate"] = round(
                max(
                    0.5,
                    min(
                        8.0,
                        patient["lactate"] + random.uniform(-0.2, 0.2),
                    ),
                ),
                1,
            )

            # Log vitals telemetry update periodically (every 20 seconds)
            now = datetime.now()
            last_log = self.last_vitals_log.get(patient["id"])
            if last_log is None or (now - last_log).total_seconds() >= 20:
                self.last_vitals_log[patient["id"]] = now
                desc = f"Telemetry updated: HR: {patient['heart_rate']} bpm, SpO2: {patient['spo2']}%, BP: {patient['systolic_bp']}/{patient['diastolic_bp']} mmHg"
                timeline_engine.add_event(
                    patient_id=patient["id"],
                    event_type="Clinical",
                    title="Telemetry Vital Signs Update",
                    description=desc,
                    actor="System",
                    metadata={
                        "heart_rate": patient["heart_rate"],
                        "spo2": patient["spo2"],
                        "systolic_bp": patient["systolic_bp"],
                        "diastolic_bp": patient["diastolic_bp"]
                    }
                )

            # Ingest into the telemetry trend engine (in-memory, non-blocking)
            try:
                telemetry_engine.ingest(
                    patient_id=patient["id"],
                    vitals={
                        "heart_rate":       patient["heart_rate"],
                        "systolic_bp":      patient["systolic_bp"],
                        "diastolic_bp":     patient["diastolic_bp"],
                        "respiratory_rate": patient["respiratory_rate"],
                        "spo2":             patient["spo2"],
                        "temperature":      patient["temperature"],
                    },
                    patient_name=patient.get("name", ""),
                )
            except Exception:
                pass

            # Write-through to database to maintain PostgreSQL as source of truth
            try:
                db = SessionLocal()
                try:
                    adm = db.query(Admission).filter(Admission.patient_id == patient["id"]).first()
                    if adm:
                        # Sync status
                        p_db = db.query(Patient).filter(Patient.id == patient["id"]).first()
                        if p_db:
                            p_db.status = patient["status"]
                            
                        # Add new VitalSign record
                        v_db = VitalSign(
                            id=f"vit-{str(uuid.uuid4())[:8]}",
                            admission_id=adm.id,
                            heart_rate=float(patient["heart_rate"]),
                            systolic_bp=float(patient["systolic_bp"]),
                            diastolic_bp=float(patient["diastolic_bp"]),
                            respiratory_rate=float(patient["respiratory_rate"]),
                            spo2=float(patient["spo2"]),
                            temperature=float(patient["temperature"]),
                            glasgow_coma_scale=15,
                            urine_output_ml=50.0,
                        )
                        db.add(v_db)
                        
                        # Sync lactate
                        l_db = db.query(LabResult).filter(LabResult.admission_id == adm.id).order_by(LabResult.collected_at.desc()).first()
                        if l_db:
                            l_db.lactate = float(patient["lactate"])
                            
                    db.commit()
                finally:
                    db.close()
            except Exception:
                pass

    def _generate_alerts(self):
        for patient in self.patients:
            if patient["risk_score"] >= 0.90:
                alert_manager.create_alert(
                alert_id=f"SEPSIS-{patient['id']}",
                patient_id=patient["id"],
                patient_name=patient["name"],
                bed=patient["bed"],
                severity=AlertSeverity.CRITICAL,
                title="Critical Sepsis Risk",
                message=(
                    f"Sepsis probability "
                    f"{patient['risk_score'] * 100:.1f}%"
                ),
            )
            if patient["spo2"] < 90:
                alert_manager.create_alert(
                alert_id=f"SPO2-{patient['id']}",
                patient_id=patient["id"],
                patient_name=patient["name"],
                bed=patient["bed"],
                severity=AlertSeverity.HIGH,
                title="Low Oxygen Saturation",
                message=f"SpO2 dropped to {patient['spo2']}%",
            )
            if patient["temperature"] >= 39:
                alert_manager.create_alert(
                alert_id=f"TEMP-{patient['id']}",
                patient_id=patient["id"],
                patient_name=patient["name"],
                bed=patient["bed"],
                severity=AlertSeverity.MEDIUM,
                title="High Temperature",
                message=f"Temperature {patient['temperature']}°C",
            )
            if patient["systolic_bp"] < 90:
                alert_manager.create_alert(
                alert_id=f"BP-{patient['id']}",
                patient_id=patient["id"],
                patient_name=patient["name"],
                bed=patient["bed"],
                severity=AlertSeverity.HIGH,
                title="Hypotension",
                message=(
                    f"BP "
                    f"{patient['systolic_bp']}/"
                    f"{patient['diastolic_bp']}"
                ),
            )
        self.dashboard["active_alerts"] = len(
            alert_manager.active_alerts()
    )


simulator = ICUSimulator()