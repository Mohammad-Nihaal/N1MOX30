from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.creator_memory import CreatorMemory


class CreatorMemoryService:
    """
    Long-term memory service for N1MOX30.

    This service intentionally contains no creator usage quotas.
    Storage and retrieval can grow with the creator's history.
    """

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create_memory(
        *,
        db: Session,
        user_id: str,
        memory_type: str,
        memory_key: str,
        memory_value: str,
        source: str = "user",
        importance_score: int = 5,
        confidence_score: float = 1.0,
    ) -> CreatorMemory:

        memory = CreatorMemory(
            user_id=user_id,
            memory_type=memory_type.strip(),
            memory_key=memory_key.strip(),
            memory_value=memory_value.strip(),
            source=source.strip(),
            importance_score=importance_score,
            confidence_score=confidence_score,
            is_active=True,
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    # =========================================================
    # UPSERT / LEARN
    # =========================================================

    @staticmethod
    def learn_memory(
        *,
        db: Session,
        user_id: str,
        memory_type: str,
        memory_key: str,
        memory_value: str,
        source: str = "ai",
        importance_score: int = 5,
        confidence_score: float = 1.0,
    ) -> CreatorMemory:

        existing = (
            db.query(CreatorMemory)
            .filter(
                CreatorMemory.user_id == user_id,
                CreatorMemory.memory_type == memory_type,
                CreatorMemory.memory_key == memory_key,
            )
            .order_by(
                CreatorMemory.updated_at.desc()
            )
            .first()
        )

        if existing:
            existing.memory_value = memory_value.strip()
            existing.source = source.strip()
            existing.importance_score = importance_score
            existing.confidence_score = confidence_score
            existing.is_active = True

            db.commit()
            db.refresh(existing)

            return existing

        return CreatorMemoryService.create_memory(
            db=db,
            user_id=user_id,
            memory_type=memory_type,
            memory_key=memory_key,
            memory_value=memory_value,
            source=source,
            importance_score=importance_score,
            confidence_score=confidence_score,
        )

    # =========================================================
    # GET ONE
    # =========================================================

    @staticmethod
    def get_memory(
        *,
        db: Session,
        user_id: str,
        memory_id: str,
    ) -> CreatorMemory | None:

        return (
            db.query(CreatorMemory)
            .filter(
                CreatorMemory.id == memory_id,
                CreatorMemory.user_id == user_id,
            )
            .first()
        )

    # =========================================================
    # GET LIST
    # =========================================================

    @staticmethod
    def get_memories(
        *,
        db: Session,
        user_id: str,
        limit: int | None = None,
        offset: int = 0,
        memory_type: str | None = None,
        active_only: bool = True,
    ) -> tuple[list[CreatorMemory], int]:

        query = db.query(CreatorMemory).filter(
            CreatorMemory.user_id == user_id
        )

        if active_only:
            query = query.filter(
                CreatorMemory.is_active.is_(True)
            )

        if memory_type:
            query = query.filter(
                CreatorMemory.memory_type == memory_type
            )

        total = query.count()

        query = query.order_by(
            CreatorMemory.importance_score.desc(),
            CreatorMemory.confidence_score.desc(),
            CreatorMemory.updated_at.desc(),
        )

        if offset > 0:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all(), total

    # =========================================================
    # SEARCH
    # =========================================================

    @staticmethod
    def search_memories(
        *,
        db: Session,
        user_id: str,
        search_query: str,
        active_only: bool = True,
    ) -> list[CreatorMemory]:

        query_text = search_query.strip()

        if not query_text:
            return []

        pattern = f"%{query_text}%"

        query = db.query(CreatorMemory).filter(
            CreatorMemory.user_id == user_id,
            or_(
                CreatorMemory.memory_type.ilike(pattern),
                CreatorMemory.memory_key.ilike(pattern),
                CreatorMemory.memory_value.ilike(pattern),
                CreatorMemory.source.ilike(pattern),
            ),
        )

        if active_only:
            query = query.filter(
                CreatorMemory.is_active.is_(True)
            )

        return (
            query.order_by(
                CreatorMemory.importance_score.desc(),
                CreatorMemory.confidence_score.desc(),
                CreatorMemory.updated_at.desc(),
            )
            .all()
        )

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update_memory(
        *,
        db: Session,
        memory: CreatorMemory,
        update_data: dict,
    ) -> CreatorMemory:

        for field, value in update_data.items():

            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()

            setattr(memory, field, value)

        db.commit()
        db.refresh(memory)

        return memory

    # =========================================================
    # DEACTIVATE
    # =========================================================

    @staticmethod
    def deactivate_memory(
        *,
        db: Session,
        memory: CreatorMemory,
    ) -> CreatorMemory:

        memory.is_active = False

        db.commit()
        db.refresh(memory)

        return memory

    # =========================================================
    # REACTIVATE
    # =========================================================

    @staticmethod
    def reactivate_memory(
        *,
        db: Session,
        memory: CreatorMemory,
    ) -> CreatorMemory:

        memory.is_active = True

        db.commit()
        db.refresh(memory)

        return memory

    # =========================================================
    # AI CONTEXT
    # =========================================================

    @staticmethod
    def get_memory_context(
        *,
        db: Session,
        user_id: str,
        memory_type: str | None = None,
    ) -> list[dict]:

        query = db.query(CreatorMemory).filter(
            CreatorMemory.user_id == user_id,
            CreatorMemory.is_active.is_(True),
        )

        if memory_type:
            query = query.filter(
                CreatorMemory.memory_type == memory_type
            )

        memories = (
            query.order_by(
                CreatorMemory.importance_score.desc(),
                CreatorMemory.confidence_score.desc(),
                CreatorMemory.updated_at.desc(),
            )
            .all()
        )

        return [
            {
                "id": memory.id,
                "memory_type": memory.memory_type,
                "memory_key": memory.memory_key,
                "memory_value": memory.memory_value,
                "source": memory.source,
                "importance_score": memory.importance_score,
                "confidence_score": memory.confidence_score,
            }
            for memory in memories
        ]


# =============================================================
# BACKWARD-COMPATIBLE FUNCTIONS
# =============================================================

def create_memory(**kwargs):
    return CreatorMemoryService.create_memory(**kwargs)


def learn_memory(**kwargs):
    return CreatorMemoryService.learn_memory(**kwargs)


def get_memory(**kwargs):
    return CreatorMemoryService.get_memory(**kwargs)


def get_memories(**kwargs):
    return CreatorMemoryService.get_memories(**kwargs)


def search_memories(**kwargs):
    return CreatorMemoryService.search_memories(**kwargs)


def update_memory(**kwargs):
    return CreatorMemoryService.update_memory(**kwargs)


def deactivate_memory(**kwargs):
    return CreatorMemoryService.deactivate_memory(**kwargs)


def reactivate_memory(**kwargs):
    return CreatorMemoryService.reactivate_memory(**kwargs)


def get_memory_context(**kwargs):
    return CreatorMemoryService.get_memory_context(**kwargs)