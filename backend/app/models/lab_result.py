"""
Enterprise Laboratory Result Model.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LabResult(Base):
    """
    ICU Laboratory Result.
    """

    __tablename__ = "lab_results"

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

    hemoglobin: Mapped[float] = mapped_column(Float)

    wbc: Mapped[float] = mapped_column(Float)

    platelets: Mapped[float] = mapped_column(Float)

    creatinine: Mapped[float] = mapped_column(Float)

    bun: Mapped[float] = mapped_column(Float)

    sodium: Mapped[float] = mapped_column(Float)

    potassium: Mapped[float] = mapped_column(Float)

    chloride: Mapped[float] = mapped_column(Float)

    lactate: Mapped[float] = mapped_column(Float)

    ph: Mapped[float] = mapped_column(Float)

    pao2: Mapped[float] = mapped_column(Float)

    paco2: Mapped[float] = mapped_column(Float)

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )