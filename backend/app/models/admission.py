"""
ICU Admission Model.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Admission(Base):
    """
    ICU Admission.
    """

    __tablename__ = "admissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )

    admission_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    diagnosis: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    doctor_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    ward: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    bed_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ADMITTED",
    )

    admitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    discharged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
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

    patient = relationship(
        "Patient",
        back_populates="admissions",
    )