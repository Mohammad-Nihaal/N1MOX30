import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AssistantConversation(Base):
    """
    Stores conversations between the creator
    and the N1MOX30 Personal Creator AI Assistant.
    """

    __tablename__ = "assistant_conversations"

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

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    conversation_type: Mapped[str] = mapped_column(
        String(100),
        default="chat",
        nullable=False,
        index=True,
    )

    action_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    action_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    context_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )