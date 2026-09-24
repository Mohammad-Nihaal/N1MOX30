from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CommunicationMessage(Base):
    __tablename__ = "communication_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False, default="inbound")
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="general")
    sender: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    subject: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ClipJob(Base):
    __tablename__ = "clip_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    requested_formats: Mapped[list] = mapped_column(JSON, default=lambda: ["9:16", "1:1", "16:9"], nullable=False)
    pipeline: Mapped[list] = mapped_column(JSON, default=lambda: [
        "transcription", "moment_detection", "hook_detection", "clip_selection",
        "reframing", "captions", "brand_styling", "audio_processing",
        "vertical_formatting", "qc", "ready_to_publish"
    ], nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
