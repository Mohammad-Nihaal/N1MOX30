from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.content import Content
from app.models.user import User

from app.schemas.content import (
    AIContentSaveRequest,
    ContentCreate,
    ContentListResponse,
    ContentResponse,
    ContentStatisticsResponse,
    ContentStatus,
    ContentStatusUpdate,
    ContentUpdate,
)


router = APIRouter(
    prefix="/content",
    tags=["Content Studio"],
)


# =================================================
# SAVE AI GENERATED CONTENT
# =================================================


@router.post(
    "/from-ai",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_ai_generated_content(
    content_data: AIContentSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save AI-generated content directly
    into Content Studio.
    """

    hashtags_text = None

    if content_data.hashtags:
        hashtags_text = " ".join(
            content_data.hashtags
        )

    content = Content(
        user_id=current_user.id,
        platform=content_data.platform,
        title=content_data.title,
        idea=content_data.topic,
        script=content_data.script,
        caption=content_data.caption,
        hashtags=hashtags_text,
        status=content_data.status,
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return content


# =================================================
# CREATE CONTENT MANUALLY
# =================================================


@router.post(
    "/",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create content manually inside
    Content Studio.
    """

    content = Content(
        user_id=current_user.id,
        platform=content_data.platform,
        title=content_data.title,
        idea=content_data.idea,
        script=content_data.script,
        caption=content_data.caption,
        hashtags=content_data.hashtags,
        status=content_data.status,
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return content


# =================================================
# CONTENT STATISTICS
# =================================================


@router.get(
    "/statistics",
    response_model=ContentStatisticsResponse,
)
def get_content_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return Content Studio statistics
    for the authenticated user.
    """

    content_items = (
        db.query(Content)
        .filter(
            Content.user_id == current_user.id
        )
        .all()
    )

    total_content = len(content_items)

    draft = 0
    ready = 0
    scheduled = 0
    published = 0

    youtube = 0
    instagram = 0

    for item in content_items:

        # -----------------------------
        # STATUS COUNTS
        # -----------------------------

        if item.status == "draft":
            draft += 1

        elif item.status == "ready":
            ready += 1

        elif item.status == "scheduled":
            scheduled += 1

        elif item.status == "published":
            published += 1

        # -----------------------------
        # PLATFORM COUNTS
        # -----------------------------

        if item.platform == "youtube":
            youtube += 1

        elif item.platform == "instagram":
            instagram += 1

    return {
        "total_content": total_content,
        "draft": draft,
        "ready": ready,
        "scheduled": scheduled,
        "published": published,
        "youtube": youtube,
        "instagram": instagram,
    }


# =================================================
# GET CONTENT LIST
# SEARCH + FILTER + PAGINATION
# =================================================


@router.get(
    "/",
    response_model=ContentListResponse,
)
def get_my_content(
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
    ),
    platform: str | None = Query(
        default=None,
    ),
    content_status: ContentStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get Content Studio items.

    Supports:
    - Search
    - Platform filtering
    - Status filtering
    - Pagination
    """

    query = (
        db.query(Content)
        .filter(
            Content.user_id == current_user.id
        )
    )

    # =============================================
    # SEARCH
    # =============================================

    if search:

        search_value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Content.title.ilike(
                    search_value
                ),
                Content.idea.ilike(
                    search_value
                ),
                Content.script.ilike(
                    search_value
                ),
                Content.caption.ilike(
                    search_value
                ),
                Content.hashtags.ilike(
                    search_value
                ),
            )
        )

    # =============================================
    # PLATFORM FILTER
    # =============================================

    if platform:

        query = query.filter(
            Content.platform == platform.lower()
        )

    # =============================================
    # STATUS FILTER
    # =============================================

    if content_status:

        query = query.filter(
            Content.status == content_status
        )

    # =============================================
    # TOTAL
    # =============================================

    total = query.count()

    # =============================================
    # RESULTS
    # =============================================

    content_items = (
        query
        .order_by(
            Content.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "content": content_items,
    }


# =================================================
# GET SINGLE CONTENT
# =================================================


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
)
def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get one Content Studio item.
    """

    content = (
        db.query(Content)
        .filter(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found.",
        )

    return content


# =================================================
# UPDATE CONTENT
# =================================================


@router.put(
    "/{content_id}",
    response_model=ContentResponse,
)
def update_content(
    content_id: str,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a Content Studio item.
    """

    content = (
        db.query(Content)
        .filter(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found.",
        )

    update_data = content_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():

        setattr(
            content,
            field,
            value,
        )

    db.commit()
    db.refresh(content)

    return content


# =================================================
# QUICK STATUS UPDATE
# =================================================


@router.patch(
    "/{content_id}/status",
    response_model=ContentResponse,
)
def update_content_status(
    content_id: str,
    status_data: ContentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update only the workflow status.

    Status flow:

    draft
        ↓
    ready
        ↓
    scheduled
        ↓
    published
    """

    content = (
        db.query(Content)
        .filter(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found.",
        )

    content.status = status_data.status

    db.commit()
    db.refresh(content)

    return content


# =================================================
# DELETE CONTENT
# =================================================


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a Content Studio item.
    """

    content = (
        db.query(Content)
        .filter(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found.",
        )

    db.delete(content)

    db.commit()

    return None