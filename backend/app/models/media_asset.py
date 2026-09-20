import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Base


class MediaAsset(Base):
    """
    Represents a reusable media asset inside
    the N1MOX30 video creation pipeline.

    Supported asset types:

    - image
    - video
    - audio
    - overlay
    - thumbnail
    - subtitle

    Asset lifecycle:

    pending
        ↓
    processing
        ↓
    ready

    Or:

    pending / processing
        ↓
    failed
        ↓
    retrying
        ↓
    processing
    """

    __tablename__ = "media_assets"

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

    project_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("projects.id"),
        nullable=True,
        index=True,
    )

    content_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("content.id"),
        nullable=True,
        index=True,
    )

    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    media_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="unknown",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    storage_provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="local",
        index=True,
    )

    storage_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    public_url: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    provider_asset_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        index=True,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_extension: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    frame_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    scene_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    asset_role: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

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

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )