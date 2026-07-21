"""
Enterprise Alert Manager

Responsible for:
- Creating alerts
- Preventing duplicates
- Updating existing alerts
- Resolving alerts
- Returning active alerts
"""

from datetime import datetime

from app.alerts.models import (
    ICUAlert,
    AlertSeverity,
)
from app.alerts.repository import repository


class AlertManager:

    def create_alert(
        self,
        *,
        alert_id: str,
        patient_id: str,
        patient_name: str,
        bed: str,
        severity: AlertSeverity,
        title: str,
        message: str,
    ):

        # Prevent duplicate active alerts
        existing = repository.get(alert_id)

        if existing:

            existing.severity = severity
            existing.title = title
            existing.message = message
            existing.updated_at = datetime.now()

            return existing

        alert = ICUAlert(
            id=alert_id,
            patient_id=patient_id,
            patient_name=patient_name,
            bed=bed,
            severity=severity,
            title=title,
            message=message,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.add(alert)

        return alert

    def acknowledge(self, alert_id: str):

        repository.acknowledge(alert_id)

    def resolve(self, alert_id: str):

        repository.resolve(alert_id)

        repository.cleanup()

    def escalate(self, alert_id: str):

        repository.escalate(alert_id)

    def active_alerts(self):

        return repository.active()

    def all_alerts(self):

        return repository.get_all()


manager = AlertManager()