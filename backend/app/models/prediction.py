"""
AI Prediction Model.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prediction(Base):
    """
    Stores AI-generated clinical predictions.
    """

    __tablename__ = "predictions"

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

    prediction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    recommendation: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(30),
        default="v1.0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )