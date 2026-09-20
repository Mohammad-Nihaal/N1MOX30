from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class VideoPerformance(Base):
    """
    Stores performance information for individual
    creator videos imported from supported platforms.
    """

    __tablename__ = "video_performance"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ---------------------------------------------
    # ACCOUNT RELATIONSHIP
    # ---------------------------------------------

    connected_account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("connected_accounts.id"),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------
    # PLATFORM INFORMATION
    # ---------------------------------------------

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    platform_video_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------
    # VIDEO INFORMATION
    # ---------------------------------------------

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    # ---------------------------------------------
    # PERFORMANCE METRICS
    # ---------------------------------------------

    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    comments: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ---------------------------------------------
    # METADATA
    # ---------------------------------------------

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    video_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # ---------------------------------------------
    # SYNC INFORMATION
    # ---------------------------------------------

    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
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