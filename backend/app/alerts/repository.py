"""
Enterprise Alert Repository
Stores and manages ICU alerts in PostgreSQL with mock fallback.
"""

from typing import Dict, List
from datetime import datetime
from app.alerts.models import ICUAlert, AlertStatus, AlertSeverity
from app.database.session import SessionLocal
from app.database.models import DBAlert

def to_pydantic(db_alert: DBAlert) -> ICUAlert:
    return ICUAlert(
        id=db_alert.id,
        patient_id=db_alert.patient_id,
        patient_name=db_alert.patient_name,
        bed=db_alert.bed,
        severity=AlertSeverity(db_alert.severity),
        status=AlertStatus(db_alert.status),
        title=db_alert.title,
        message=db_alert.message,
        created_at=db_alert.created_at,
        updated_at=db_alert.updated_at,
    )

class AlertRepository:
    def __init__(self):
        self._alerts: Dict[str, ICUAlert] = {}

    def add(self, alert: ICUAlert):
        try:
            db = SessionLocal()
            try:
                existing = db.query(DBAlert).filter(DBAlert.id == alert.id).first()
                if existing:
                    existing.status = alert.status.value
                    existing.severity = alert.severity.value
                    existing.title = alert.title
                    existing.message = alert.message
                    existing.updated_at = datetime.utcnow()
                else:
                    db_alert = DBAlert(
                        id=alert.id,
                        patient_id=alert.patient_id,
                        patient_name=alert.patient_name,
                        bed=alert.bed,
                        severity=alert.severity.value,
                        status=alert.status.value,
                        title=alert.title,
                        message=alert.message,
                        created_at=alert.created_at,
                        updated_at=alert.updated_at,
                    )
                    db.add(db_alert)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass
        self._alerts[alert.id] = alert

    def get(self, alert_id: str):
        try:
            db = SessionLocal()
            try:
                db_alert = db.query(DBAlert).filter(DBAlert.id == alert_id).first()
                if db_alert:
                    return to_pydantic(db_alert)
            finally:
                db.close()
        except Exception:
            pass
        return self._alerts.get(alert_id)

    def get_all(self) -> List[ICUAlert]:
        try:
            db = SessionLocal()
            try:
                db_alerts = db.query(DBAlert).all()
                if db_alerts:
                    return [to_pydantic(a) for a in db_alerts]
            finally:
                db.close()
        except Exception:
            pass
        return list(self._alerts.values())

    def remove(self, alert_id: str):
        try:
            db = SessionLocal()
            try:
                db_alert = db.query(DBAlert).filter(DBAlert.id == alert_id).first()
                if db_alert:
                    db.delete(db_alert)
                    db.commit()
            finally:
                db.close()
        except Exception:
            pass
        if alert_id in self._alerts:
            del self._alerts[alert_id]

    def acknowledge(self, alert_id: str):
        try:
            db = SessionLocal()
            try:
                db_alert = db.query(DBAlert).filter(DBAlert.id == alert_id).first()
                if db_alert:
                    db_alert.status = AlertStatus.ACKNOWLEDGED.value
                    db_alert.updated_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
        except Exception:
            pass
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.updated_at = datetime.now()

    def escalate(self, alert_id: str):
        try:
            db = SessionLocal()
            try:
                db_alert = db.query(DBAlert).filter(DBAlert.id == alert_id).first()
                if db_alert:
                    db_alert.status = AlertStatus.ESCALATED.value
                    db_alert.updated_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
        except Exception:
            pass
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ESCALATED
            alert.updated_at = datetime.now()

    def resolve(self, alert_id: str):
        try:
            db = SessionLocal()
            try:
                db_alert = db.query(DBAlert).filter(DBAlert.id == alert_id).first()
                if db_alert:
                    db_alert.status = AlertStatus.RESOLVED.value
                    db_alert.updated_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
        except Exception:
            pass
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.updated_at = datetime.now()

    def active(self) -> List[ICUAlert]:
        try:
            db = SessionLocal()
            try:
                db_alerts = db.query(DBAlert).filter(DBAlert.status != AlertStatus.RESOLVED.value).all()
                return [to_pydantic(a) for a in db_alerts]
            finally:
                db.close()
        except Exception:
            pass
        return [alert for alert in self._alerts.values() if alert.status != AlertStatus.RESOLVED]

    def cleanup(self):
        try:
            db = SessionLocal()
            try:
                db.query(DBAlert).filter(DBAlert.status == AlertStatus.RESOLVED.value).delete()
                db.commit()
            finally:
                db.close()
        except Exception:
            pass
        resolved = []
        for alert in self._alerts.values():
            if alert.status == AlertStatus.RESOLVED:
                resolved.append(alert.id)
        for alert_id in resolved:
            self.remove(alert_id)

repository = AlertRepository()