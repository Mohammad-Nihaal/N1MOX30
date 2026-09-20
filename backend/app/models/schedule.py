import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContentSchedule(Base):
    __tablename__ = "content_schedules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    content_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("content.id"),
        nullable=False,
        index=True,
    )

    # Optional until a YouTube or Instagram account is connected.
    connected_account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("connected_accounts.id"),
        nullable=True,
        index=True,
    )

    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
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