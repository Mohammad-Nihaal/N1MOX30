from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VideoTimeline(Base):
    __tablename__ = "video_timelines"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("content.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Untitled Timeline",
    )

    aspect_ratio: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="16:9",
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1920,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1080,
    )

    duration_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    fps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    background_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#000000",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    timeline_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )