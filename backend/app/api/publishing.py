from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.publishing.publishing_service import PublishingService
from app.schemas.publishing import (
    PublishPreviewResponse,
    PublishRequest,
    PublishResponse,
)


router = APIRouter(
    prefix="/publishing",
    tags=["Publishing"],
)


@router.get("/health")
def publishing_health():
    return {
        "status": "healthy",
        "service": "N1MOX30 Publishing System",
        "platforms": ["youtube", "instagram", "tiktok", "facebook", "x"],
        "architecture": "provider-neutral",
    }


@router.post(
    "/preview",
    response_model=PublishPreviewResponse,
)
def preview_publish(
    payload: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PublishingService(db)

    try:
        return service.preview(
            user_id=current_user.id,
            platform=payload.platform,
            video_path=payload.video_path,
            title=payload.title,
            description=payload.description,
            tags=payload.tags,
            privacy_status=payload.privacy_status,
            category_id=payload.category_id,
            thumbnail_path=payload.thumbnail_path,
            account_id=payload.account_id,
            media_url=payload.media_url,
            media_type=payload.media_type,
            platform_options=payload.platform_options,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/publish",
    response_model=PublishResponse,
)
def publish_content(
    payload: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PublishingService(db)

    try:
        return service.publish(
            user_id=current_user.id,
            platform=payload.platform,
            video_path=payload.video_path,
            title=payload.title,
            description=payload.description,
            tags=payload.tags,
            privacy_status=payload.privacy_status,
            category_id=payload.category_id,
            thumbnail_path=payload.thumbnail_path,
            publish_at=payload.publish_at,
            account_id=payload.account_id,
            content_id=payload.content_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Publishing failed: {error}",
        ) from error


@router.post("/confirm")
def confirm_publish(
    payload: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return an explicit publish-readiness confirmation without uploading."""
    service = PublishingService(db)
    try:
        preview = service.preview(
            user_id=current_user.id,
            platform=payload.platform,
            video_path=payload.video_path,
            title=payload.title,
            description=payload.description,
            tags=payload.tags,
            privacy_status=payload.privacy_status,
            category_id=payload.category_id,
            thumbnail_path=payload.thumbnail_path,
            account_id=payload.account_id,
            media_url=payload.media_url,
            media_type=payload.media_type,
            platform_options=payload.platform_options,
        )
        return {
            "confirmed": bool(preview.get("ready")),
            "publish_ready": bool(preview.get("ready")),
            "preview": preview,
            "message": "Publishing readiness confirmed; no external upload was performed.",
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
