from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.thumbnail import Thumbnail
from app.models.user import User
from app.schemas.thumbnail import (
    ThumbnailGenerateRequest,
    ThumbnailGenerateResponse,
    ThumbnailRenderRequest,
    ThumbnailResponse,
    ThumbnailScore,
    ThumbnailSelectResponse,
)
from app.services.thumbnails.thumbnail_service import (
    ThumbnailService,
)


router = APIRouter(
    prefix="/thumbnails",
    tags=["Thumbnails"],
)

service = ThumbnailService()


def _to_response(
    thumbnail: Thumbnail,
) -> ThumbnailResponse:
    return ThumbnailResponse(
        id=thumbnail.id,
        content_id=thumbnail.content_id,
        name=thumbnail.name,
        platform=thumbnail.platform,
        width=thumbnail.width,
        height=thumbnail.height,
        title_text=thumbnail.title_text,
        concept=thumbnail.concept,
        visual_direction=thumbnail.visual_direction,
        background_prompt=thumbnail.background_prompt,
        foreground_prompt=thumbnail.foreground_prompt,
        text_style=thumbnail.text_style,
        composition=thumbnail.composition,
        score=ThumbnailScore(
            curiosity=thumbnail.curiosity_score,
            readability=thumbnail.readability_score,
            visual=thumbnail.visual_score,
            ctr=thumbnail.ctr_score,
            overall=thumbnail.overall_score,
        ),
        image_path=thumbnail.image_path,
        provider=thumbnail.provider,
        status=thumbnail.status,
        is_selected=thumbnail.is_selected,
        created_at=thumbnail.created_at.isoformat(),
        updated_at=thumbnail.updated_at.isoformat(),
    )


@router.post(
    "/generate",
    response_model=ThumbnailGenerateResponse,
)
def generate_thumbnails(
    request: ThumbnailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thumbnails, best_id = service.generate_concepts(
        db,
        user_id=current_user.id,
        content_id=request.content_id,
        title=request.title,
        topic=request.topic,
        platform=request.platform,
        concept_count=request.concept_count,
        style=request.style,
        visual_subject=request.visual_subject,
        additional_context=request.additional_context,
    )

    return ThumbnailGenerateResponse(
        thumbnails=[
            _to_response(item)
            for item in thumbnails
        ],
        best_thumbnail_id=best_id,
        metadata={
            "provider": "local",
            "concept_count": len(thumbnails),
            "platform": request.platform,
            "mode": "provider_neutral",
        },
    )


@router.post(
    "/render",
    response_model=ThumbnailResponse,
)
def render_thumbnail(
    request: ThumbnailRenderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        thumbnail = service.render(
            db,
            thumbnail_id=request.thumbnail_id,
            user_id=current_user.id,
            background_path=request.background_path,
            foreground_path=request.foreground_path,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _to_response(thumbnail)


@router.post(
    "/{thumbnail_id}/select",
    response_model=ThumbnailSelectResponse,
)
def select_thumbnail(
    thumbnail_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        thumbnail = service.select(
            db,
            thumbnail_id=thumbnail_id,
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return ThumbnailSelectResponse(
        thumbnail=_to_response(thumbnail),
    )


@router.get(
    "",
    response_model=list[ThumbnailResponse],
)
def list_thumbnails(
    content_id: Optional[str] = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Thumbnail)
        .filter(
            Thumbnail.user_id == current_user.id,
        )
    )

    if content_id:
        query = query.filter(
            Thumbnail.content_id == content_id,
        )

    thumbnails = (
        query
        .order_by(
            Thumbnail.overall_score.desc(),
            Thumbnail.created_at.desc(),
        )
        .all()
    )

    return [
        _to_response(item)
        for item in thumbnails
    ]


@router.get(
    "/{thumbnail_id}",
    response_model=ThumbnailResponse,
)
def get_thumbnail(
    thumbnail_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thumbnail = (
        db.query(Thumbnail)
        .filter(
            Thumbnail.id == thumbnail_id,
            Thumbnail.user_id == current_user.id,
        )
        .first()
    )

    if thumbnail is None:
        raise HTTPException(
            status_code=404,
            detail="Thumbnail not found",
        )

    return _to_response(thumbnail)