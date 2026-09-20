from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.assistant_memory import (
    AssistantMemory,
)


# =================================================
# SAVE MEMORY
# =================================================


def save_memory(
    *,
    db: Session,
    user_id: str,
    role: str,
    message: str,
    memory_type: str = "conversation",
    action_name: str | None = None,
    action_status: str | None = None,
) -> AssistantMemory:
    """
    Save a N1MOX30 assistant memory.
    """

    memory = AssistantMemory(
        user_id=user_id,
        role=role,
        message=message,
        memory_type=memory_type,
        action_name=action_name,
        action_status=action_status,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


# =================================================
# GET RECENT CONVERSATION
# =================================================


def get_recent_conversation(
    *,
    db: Session,
    user_id: str,
    limit: int = 20,
) -> list[AssistantMemory]:
    """
    Get recent assistant conversation history.

    Returned in chronological order so it can
    be sent directly to the AI provider.
    """

    limit = min(
        max(limit, 1),
        100,
    )

    memories = (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.user_id == user_id,
            AssistantMemory.memory_type == "conversation",
        )
        .order_by(
            AssistantMemory.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return list(
        reversed(memories)
    )


# =================================================
# SAVE IMPORTANT MEMORY
# =================================================


def save_important_memory(
    *,
    db: Session,
    user_id: str,
    message: str,
) -> AssistantMemory:
    """
    Save important long-term creator information.

    Examples:
    - Creator preferences
    - Future goals
    - Project information
    - Workflow preferences
    """

    return save_memory(
        db=db,
        user_id=user_id,
        role="system",
        message=message,
        memory_type="important",
    )


# =================================================
# GET IMPORTANT MEMORIES
# =================================================


def get_important_memories(
    *,
    db: Session,
    user_id: str,
    limit: int = 20,
) -> list[AssistantMemory]:
    """
    Retrieve important long-term memories.
    """

    limit = min(
        max(limit, 1),
        100,
    )

    return (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.user_id == user_id,
            AssistantMemory.memory_type == "important",
        )
        .order_by(
            AssistantMemory.created_at.desc()
        )
        .limit(limit)
        .all()
    )


# =================================================
# GET USER MEMORIES
# =================================================


def get_all_memories(
    *,
    db: Session,
    user_id: str,
    limit: int = 50,
) -> list[AssistantMemory]:
    """
    Get all memories belonging to one user.
    """

    limit = min(
        max(limit, 1),
        100,
    )

    return (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.user_id == user_id,
        )
        .order_by(
            AssistantMemory.created_at.desc()
        )
        .limit(limit)
        .all()
    )


# =================================================
# DELETE MEMORY
# =================================================


def delete_memory(
    *,
    db: Session,
    user_id: str,
    memory_id: str,
) -> bool:
    """
    Delete one memory belonging to the user.
    """

    memory = (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.id == memory_id,
            AssistantMemory.user_id == user_id,
        )
        .first()
    )

    if not memory:
        return False

    db.delete(memory)
    db.commit()

    return True