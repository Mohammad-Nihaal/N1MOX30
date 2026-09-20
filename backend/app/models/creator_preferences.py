from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CreatorPreferences(Base):
    """
    Structured persistent preferences for a N1MOX30 creator.

    These preferences control how N1MOX30 should create,
    communicate, recommend, schedule, and personalize
    creator workflows.
    """

    __tablename__ = "creator_preferences"

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

    # -------------------------------------------------
    # Content Preferences
    # -------------------------------------------------

    preferred_content_types: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_formats: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_topics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    avoided_topics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_tone: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    preferred_language: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    brand_voice: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------
    # Audience Preferences
    # -------------------------------------------------

    target_audience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    audience_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    audience_interests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------
    # Platform Preferences
    # -------------------------------------------------

    primary_platform: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    enabled_platforms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------
    # Video Preferences
    # -------------------------------------------------

    default_aspect_ratio: Mapped[str] = mapped_column(
        String(20),
        default="16:9",
        nullable=False,
    )

    default_video_style: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    default_caption_style: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    default_thumbnail_style: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # -------------------------------------------------
    # AI Behavior Preferences
    # -------------------------------------------------

    creativity_level: Mapped[int] = mapped_column(
        Integer,
        default=70,
        nullable=False,
    )

    research_depth: Mapped[int] = mapped_column(
        Integer,
        default=70,
        nullable=False,
    )

    personalization_level: Mapped[int] = mapped_column(
        Integer,
        default=90,
        nullable=False,
    )

    automation_level: Mapped[int] = mapped_column(
        Integer,
        default=70,
        nullable=False,
    )

    # -------------------------------------------------
    # Workflow Preferences
    # -------------------------------------------------

    auto_generate_titles: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    auto_generate_description: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    auto_generate_hashtags: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    auto_generate_thumbnail: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    auto_generate_subtitles: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    auto_quality_review: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -------------------------------------------------
    # Approval Preferences
    # -------------------------------------------------

    require_publish_approval: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    require_content_approval: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -------------------------------------------------
    # Scheduling Preferences
    # -------------------------------------------------

    preferred_timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_posting_times: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------
    # Voice Preferences
    # -------------------------------------------------

    preferred_voice_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_voice_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    voice_style: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # -------------------------------------------------
    # General
    # -------------------------------------------------

    notes: Mapped[str | None] = mapped_column(
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