import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Research(Base):
    __tablename__ = "research"

    # =============================================
    # IDENTIFICATION
    # =============================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =============================================
    # BASIC RESEARCH
    # =============================================

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    topic: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    # =============================================
    # RESEARCH RESULTS
    # =============================================

    keywords: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    audience_angles: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_opportunities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    competitor_insights: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    research_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =============================================
    # SCORING
    # =============================================

    opportunity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    trend_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # =============================================
    # AI INFORMATION
    # =============================================

    provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    research_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =============================================
    # TIMESTAMPS
    # =============================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )