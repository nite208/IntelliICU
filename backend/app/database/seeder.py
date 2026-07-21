import logging
from datetime import date, datetime, timedelta
from app.database.session import SessionLocal
from app.models.patient import Patient
from app.models.admission import Admission
from app.models.vital_sign import VitalSign
from app.models.lab_result import LabResult
from app.database.models import DBUser, DBRole, DBDepartment, DBPermission, DBAlert, DBTimelineEvent
from app.repositories.rbac_repository import MOCK_ROLES, MOCK_PERMISSIONS
from app.repositories.user_repository import MOCK_USERS

logger = logging.getLogger("app.database")

def seed_database_if_empty():
    """
    Purges placeholder patients and seeds the database with 10 high-fidelity ICU patients,
    roles, departments, users, alerts, and timeline logs.
    """
    db = SessionLocal()
    try:
        # 1. Clean up "string string" or other dummy test data to avoid pollution
        placeholders = db.query(Patient).filter(
            (Patient.first_name.ilike("%string%")) | 
            (Patient.last_name.ilike("%string%"))
        ).all()
        if placeholders:
            logger.info(f"🗑 Purging {len(placeholders)} placeholder patients...")
            for p in placeholders:
                adms = db.query(Admission).filter(Admission.patient_id == p.id).all()
                for adm in adms:
                    db.query(VitalSign).filter(VitalSign.admission_id == adm.id).delete()
                    db.query(LabResult).filter(LabResult.admission_id == adm.id).delete()
                    db.delete(adm)
                db.delete(p)
            db.commit()

        # 2. Seed default permissions if empty
        if db.query(DBPermission).count() == 0:
            logger.info("🌱 Seeding permissions...")
            perms = []
            for name, mock_perm in MOCK_PERMISSIONS.items():
                perms.append(DBPermission(
                    id=mock_perm.id,
                    name=mock_perm.name,
                    description=mock_perm.description
                ))
            db.add_all(perms)
            db.commit()

        # 3. Seed default roles if empty
        if db.query(DBRole).count() == 0:
            logger.info("🌱 Seeding roles and matching permissions...")
            roles = []
            for name, mock_role in MOCK_ROLES.items():
                role_db = DBRole(
                    id=mock_role.id,
                    name=mock_role.name
                )
                db_perms = db.query(DBPermission).filter(DBPermission.name.in_(mock_role.permissions)).all()
                role_db.permissions = db_perms
                roles.append(role_db)
            db.add_all(roles)
            db.commit()

        # 4. Seed default departments if empty
        if db.query(DBDepartment).count() == 0:
            logger.info("🌱 Seeding departments...")
            d1 = DBDepartment(id="dept-1", name="Administration", description="Hospital admin department")
            d2 = DBDepartment(id="dept-2", name="Medical ICU", description="Intensive Care Unit")
            db.add_all([d1, d2])
            db.commit()

        # 5. Seed default users if empty
        if db.query(DBUser).count() == 0:
            logger.info("🌱 Seeding admin and default clinical users...")
            users = []
            for username, mock_user in MOCK_USERS.items():
                users.append(DBUser(
                    id=mock_user["id"],
                    username=mock_user["username"],
                    email=mock_user["email"],
                    hashed_password=mock_user["hashed_password"],
                    role=mock_user["role"],
                    department=mock_user.get("department"),
                    is_active=mock_user["is_active"]
                ))
            db.add_all(users)
            db.commit()

        # 6. Seed 10 realistic ICU patient profiles if count is less than 10
        if db.query(Patient).count() < 10:
            logger.info("🌱 Wiping and seeding 10 high-fidelity ICU patients...")
            from sqlalchemy import text
            try:
                db.execute(text("DELETE FROM predictions"))
            except Exception:
                pass
            db.query(DBAlert).delete()
            db.query(DBTimelineEvent).delete()
            db.query(VitalSign).delete()
            db.query(LabResult).delete()
            db.query(Admission).delete()
            db.query(Patient).delete()
            db.commit()

            patients_data = [
                {"id": "ICU-10248", "first": "Amelia", "last": "Chen", "dob": date(1959, 1, 12), "gender": "Female", "status": "Critical", "diag": "Septic Shock", "bed": "MICU-04"},
                {"id": "ICU-10251", "first": "James", "last": "Wilson", "dob": date(1972, 4, 18), "gender": "Male", "status": "Serious", "diag": "Sepsis", "bed": "MICU-07"},
                {"id": "ICU-10263", "first": "Sophia", "last": "Garcia", "dob": date(1953, 9, 22), "gender": "Female", "status": "Stable", "diag": "Recovery", "bed": "MICU-11"},
                {"id": "ICU-10264", "first": "Robert", "last": "Miller", "dob": date(1968, 11, 5), "gender": "Male", "status": "Critical", "diag": "Acute Renal Failure", "bed": "MICU-01"},
                {"id": "ICU-10265", "first": "Mary", "last": "Davis", "dob": date(1959, 7, 30), "gender": "Female", "status": "Serious", "diag": "Pneumonia", "bed": "MICU-02"},
                {"id": "ICU-10266", "first": "John", "last": "Rodriguez", "dob": date(1981, 3, 14), "gender": "Male", "status": "Stable", "diag": "Post-op Monitoring", "bed": "MICU-03"},
                {"id": "ICU-10267", "first": "Linda", "last": "Martinez", "dob": date(1964, 5, 25), "gender": "Female", "status": "Critical", "diag": "Peritonitis", "bed": "MICU-05"},
                {"id": "ICU-10268", "first": "William", "last": "Hernandez", "dob": date(1953, 12, 10), "gender": "Male", "status": "Serious", "diag": "COPD Exacerbation", "bed": "MICU-06"},
                {"id": "ICU-10269", "first": "Elizabeth", "last": "Lopez", "dob": date(1976, 8, 5), "gender": "Female", "status": "Stable", "diag": "Cellulitis", "bed": "MICU-08"},
                {"id": "ICU-10270", "first": "David", "last": "Gonzalez", "dob": date(1957, 10, 20), "gender": "Male", "status": "Critical", "diag": "Cardiogenic Shock", "bed": "MICU-09"},
            ]

            for i, p_info in enumerate(patients_data):
                p = Patient(
                    id=p_info["id"],
                    hospital_patient_id=p_info["id"],
                    first_name=p_info["first"],
                    last_name=p_info["last"],
                    date_of_birth=p_info["dob"],
                    gender=p_info["gender"],
                    status=p_info["status"],
                )
                db.add(p)
                db.commit()

                adm = Admission(
                    id=f"adm-{p_info['id'].split('-')[1]}",
                    patient_id=p_info["id"],
                    admission_number=f"ADM-{p_info['id'].split('-')[1]}",
                    diagnosis=p_info["diag"],
                    doctor_name="Dr. Sarah Johnson",
                    ward="Medical ICU",
                    bed_number=p_info["bed"],
                )
                db.add(adm)
                db.commit()

                # Vitals setup based on status severity
                if p_info["status"] == "Critical":
                    hr, spo2, temp, rr, sbp, dbp = 130.0, 89.0, 39.1, 29.0, 84.0, 50.0
                    lactate, wbc, platelets, creatinine, bun = 4.2, 18.5, 115.0, 2.2, 28.0
                elif p_info["status"] == "Serious":
                    hr, spo2, temp, rr, sbp, dbp = 106.0, 94.0, 38.1, 23.0, 105.0, 68.0
                    lactate, wbc, platelets, creatinine, bun = 2.6, 13.5, 140.0, 1.6, 21.0
                else:
                    hr, spo2, temp, rr, sbp, dbp = 74.0, 98.0, 36.8, 16.0, 120.0, 76.0
                    lactate, wbc, platelets, creatinine, bun = 1.2, 8.1, 185.0, 1.0, 14.0

                v = VitalSign(
                    id=f"vit-{p_info['id'].split('-')[1]}",
                    admission_id=adm.id,
                    heart_rate=hr,
                    systolic_bp=sbp,
                    diastolic_bp=dbp,
                    respiratory_rate=rr,
                    spo2=spo2,
                    temperature=temp,
                    glasgow_coma_scale=15,
                    urine_output_ml=55.0,
                )
                db.add(v)

                l = LabResult(
                    id=f"lab-{p_info['id'].split('-')[1]}",
                    admission_id=adm.id,
                    hemoglobin=10.8,
                    wbc=wbc,
                    platelets=platelets,
                    creatinine=creatinine,
                    bun=bun,
                    sodium=139.0,
                    potassium=4.1,
                    chloride=102.0,
                    lactate=lactate,
                    ph=7.34,
                    pao2=82.0,
                    paco2=39.0,
                )
                db.add(l)
                db.commit()

        # 7. Seed active alerts if empty
        if db.query(DBAlert).count() == 0:
            logger.info("🌱 Seeding alerts...")
            alerts = [
                DBAlert(
                    id="SEPSIS-ICU-10248",
                    patient_id="ICU-10248",
                    patient_name="Amelia Chen",
                    bed="MICU-04",
                    severity="CRITICAL",
                    status="ACTIVE",
                    title="Critical Sepsis Risk",
                    message="Sepsis probability 93.0%",
                ),
                DBAlert(
                    id="SPO2-ICU-10248",
                    patient_id="ICU-10248",
                    patient_name="Amelia Chen",
                    bed="MICU-04",
                    severity="HIGH",
                    status="ACTIVE",
                    title="Low Oxygen Saturation",
                    message="SpO₂ dropped to 89.0%",
                ),
                DBAlert(
                    id="TEMP-ICU-10264",
                    patient_id="ICU-10264",
                    patient_name="Robert Miller",
                    bed="MICU-01",
                    severity="MEDIUM",
                    status="ACTIVE",
                    title="Fever Alert",
                    message="Temperature: 38.9°C",
                ),
                DBAlert(
                    id="SEPSIS-ICU-10267",
                    patient_id="ICU-10267",
                    patient_name="Linda Martinez",
                    bed="MICU-05",
                    severity="CRITICAL",
                    status="ACTIVE",
                    title="Sepsis Risk Warning",
                    message="Sepsis risk score 91.0%",
                ),
            ]
            db.add_all(alerts)
            db.commit()

        # 8. Seed timeline events if empty
        if db.query(DBTimelineEvent).count() == 0:
            logger.info("🌱 Seeding timeline events...")
            now = datetime.utcnow()
            events = [
                DBTimelineEvent(
                    id="ev-10248-1",
                    patient_id="ICU-10248",
                    timestamp=now - timedelta(hours=3),
                    time="17:00",
                    type="Clinical",
                    title="ICU Admission",
                    description="Admitted from Emergency Department with Septic Shock.",
                    actor="System",
                    metadata_json={"diagnosis": "Septic Shock", "ward": "Medical ICU"}
                ),
                DBTimelineEvent(
                    id="ev-10248-2",
                    patient_id="ICU-10248",
                    timestamp=now - timedelta(hours=2),
                    time="18:00",
                    type="Medication",
                    title="Antibiotics Initiated",
                    description="Broad-spectrum IV Meropenem administered.",
                    actor="Dr. Sarah Johnson",
                    metadata_json={"route": "IV", "dose": "1g"}
                ),
                DBTimelineEvent(
                    id="ev-10251-1",
                    patient_id="ICU-10251",
                    timestamp=now - timedelta(hours=4),
                    time="16:00",
                    type="Clinical",
                    title="ICU Admission",
                    description="Admitted with suspected severe pulmonary sepsis.",
                    actor="System",
                    metadata_json={"diagnosis": "Sepsis", "ward": "Medical ICU"}
                ),
            ]
            db.add_all(events)
            db.commit()

        logger.info("✅ Seeder run complete!")
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
