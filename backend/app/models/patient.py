"""
Enterprise Patient Model.
"""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Patient(Base):
    """
    Master patient record.
    """

    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    hospital_patient_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    blood_group: Mapped[str | None] = mapped_column(
        String(5),
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
    )

    email: Mapped[str | None] = mapped_column(
        String(120),
    )

    address: Mapped[str | None] = mapped_column(
        String(300),
    )

    emergency_contact: Mapped[str | None] = mapped_column(
        String(120),
    )

    height_cm: Mapped[float | None] = mapped_column(
        Float,
    )

    weight_kg: Mapped[float | None] = mapped_column(
        Float,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    admissions = relationship(
        "Admission",
        back_populates="patient",
        cascade="all, delete-orphan",
    )