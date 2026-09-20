import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    creator_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    niche: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    target_audience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    creator_goals: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_platforms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_style: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    preferred_tone: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    posting_preferences: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ai_preferences: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )