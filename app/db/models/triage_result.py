from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TriageResult(Base):
    __tablename__ = "triage_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    complexity_label: Mapped[str] = mapped_column(String(20), nullable=False)
    complexity_score: Mapped[float] = mapped_column(Float, nullable=False)

    routing_label: Mapped[str] = mapped_column(String(50), nullable=False)
    routing_confidence: Mapped[float] = mapped_column(Float, nullable=False)

    requires_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    reason_codes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    review_flags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    feature_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    model_version: Mapped[str] = mapped_column(String(100), nullable=False, default="complexity-logreg-v1")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    claim = relationship("Claim", backref="triage")