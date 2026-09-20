import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    connected_account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("connected_accounts.id"),
        nullable=False,
        index=True,
    )

    content_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("content.id"),
        nullable=True,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

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

    followers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )