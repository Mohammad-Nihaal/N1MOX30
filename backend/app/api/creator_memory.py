from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.creator_memory import (
    CreateCreatorMemoryRequest,
    CreatorMemoryContextItem,
    CreatorMemoryContextResponse,
    CreatorMemoryListResponse,
    CreatorMemoryResponse,
    CreatorMemorySearchResponse,
    UpdateCreatorMemoryRequest,
)
from app.services.creator_memory_service import (
    CreatorMemoryService,
)


router = APIRouter(
    prefix="/creator-memory",
    tags=["Creator Memory"],
)


# =========================================================
# CREATE MEMORY
# =========================================================

@router.post(
    "",
    response_model=CreatorMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_creator_memory(
    memory_data: CreateCreatorMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CreatorMemoryService.create_memory(
        db=db,
        user_id=current_user.id,
        memory_type=memory_data.memory_type,
        memory_key=memory_data.memory_key,
        memory_value=memory_data.memory_value,
        source=memory_data.source,
        importance_score=memory_data.importance_score,
        confidence_score=memory_data.confidence_score,
    )


# =========================================================
# LEARN / UPSERT MEMORY
# =========================================================

@router.post(
    "/learn",
    response_model=CreatorMemoryResponse,
)
def learn_creator_memory(
    memory_data: CreateCreatorMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a memory or update the existing memory
    with the same type/key.
    """

    return CreatorMemoryService.learn_memory(
        db=db,
        user_id=current_user.id,
        memory_type=memory_data.memory_type,
        memory_key=memory_data.memory_key,
        memory_value=memory_data.memory_value,
        source=memory_data.source,
        importance_score=memory_data.importance_score,
        confidence_score=memory_data.confidence_score,
    )


# =========================================================
# LIST MEMORIES
# =========================================================

@router.get(
    "",
    response_model=CreatorMemoryListResponse,
)
def get_creator_memories(
    limit: int | None = Query(
        default=None,
        ge=1,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    memory_type: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memories, total = CreatorMemoryService.get_memories(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        memory_type=memory_type,
        active_only=active_only,
    )

    return {
        "total": total,
        "memories": memories,
    }


# =========================================================
# SEARCH MEMORIES
# =========================================================

@router.get(
    "/search",
    response_model=CreatorMemorySearchResponse,
)
def search_creator_memories(
    q: str = Query(
        min_length=1,
    ),
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memories = CreatorMemoryService.search_memories(
        db=db,
        user_id=current_user.id,
        search_query=q,
        active_only=active_only,
    )

    return {
        "total": len(memories),
        "query": q,
        "memories": memories,
    }


# =========================================================
# AI MEMORY CONTEXT
# =========================================================

@router.get(
    "/context",
    response_model=CreatorMemoryContextResponse,
)
def get_creator_ai_memory_context(
    memory_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memories = CreatorMemoryService.get_memory_context(
        db=db,
        user_id=current_user.id,
        memory_type=memory_type,
    )

    return {
        "total": len(memories),
        "memories": [
            CreatorMemoryContextItem(**memory)
            for memory in memories
        ],
    }


# =========================================================
# GET SINGLE MEMORY
# =========================================================

@router.get(
    "/{memory_id}",
    response_model=CreatorMemoryResponse,
)
def get_single_creator_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory = CreatorMemoryService.get_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator memory not found.",
        )

    return memory


# =========================================================
# UPDATE MEMORY
# =========================================================

@router.patch(
    "/{memory_id}",
    response_model=CreatorMemoryResponse,
)
def update_creator_memory(
    memory_id: str,
    memory_data: UpdateCreatorMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory = CreatorMemoryService.get_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator memory not found.",
        )

    update_data = memory_data.model_dump(
        exclude_unset=True,
    )

    return CreatorMemoryService.update_memory(
        db=db,
        memory=memory,
        update_data=update_data,
    )


# =========================================================
# DEACTIVATE MEMORY
# =========================================================

@router.post(
    "/{memory_id}/deactivate",
    response_model=CreatorMemoryResponse,
)
def deactivate_creator_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory = CreatorMemoryService.get_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator memory not found.",
        )

    return CreatorMemoryService.deactivate_memory(
        db=db,
        memory=memory,
    )


# =========================================================
# REACTIVATE MEMORY
# =========================================================

@router.post(
    "/{memory_id}/reactivate",
    response_model=CreatorMemoryResponse,
)
def reactivate_creator_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory = CreatorMemoryService.get_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator memory not found.",
        )

    return CreatorMemoryService.reactivate_memory(
        db=db,
        memory=memory,
    )