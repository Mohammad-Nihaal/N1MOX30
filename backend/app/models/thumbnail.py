from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    content_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("content.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="youtube",
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1280,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=720,
    )

    title_text: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    concept: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    visual_direction: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    background_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    foreground_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    text_style: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    composition: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    curiosity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    readability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    visual_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    ctr_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    image_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="local",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned",
    )

    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )