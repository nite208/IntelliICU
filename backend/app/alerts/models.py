from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"


class ICUAlert(BaseModel):
    id: str

    patient_id: str

    patient_name: str

    bed: str

    severity: AlertSeverity

    status: AlertStatus = AlertStatus.ACTIVE

    title: str

    message: str

    created_at: datetime

    updated_at: datetime