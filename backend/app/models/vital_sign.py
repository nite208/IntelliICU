"""
Enterprise Vital Sign Model.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class VitalSign(Base):
    """
    ICU Vital Sign Record.
    """

    __tablename__ = "vital_signs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    admission_id: Mapped[str] = mapped_column(
        ForeignKey("admissions.id"),
        nullable=False,
        index=True,
    )

    heart_rate: Mapped[float] = mapped_column(Float, nullable=False)

    systolic_bp: Mapped[float] = mapped_column(Float, nullable=False)

    diastolic_bp: Mapped[float] = mapped_column(Float, nullable=False)

    respiratory_rate: Mapped[float] = mapped_column(Float, nullable=False)

    spo2: Mapped[float] = mapped_column(Float, nullable=False)

    temperature: Mapped[float] = mapped_column(Float, nullable=False)

    glasgow_coma_scale: Mapped[int] = mapped_column(nullable=False)

    urine_output_ml: Mapped[float] = mapped_column(Float, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    