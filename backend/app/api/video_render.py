from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.video_timeline import VideoTimeline
from app.schemas.video_render import (
    RenderEnvironmentResponse,
    VideoRenderResponse,
)
from app.services.video_rendering.render_service import (
    VideoRenderService,
)


router = APIRouter(
    prefix="/video-render",
    tags=["Video Rendering"],
)


# ================================================================
# ENVIRONMENT
# ================================================================

@router.get(
    "/environment",
    response_model=RenderEnvironmentResponse,
)
def rendering_environment(
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = VideoRenderService(
        db=None,
    )

    return service.environment_status()


# ================================================================
# RENDER TIMELINE
# ================================================================

@router.post(
    "/timelines/{timeline_id}",
    response_model=VideoRenderResponse,
)
def render_video_timeline(
    timeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    timeline = (
        db.query(VideoTimeline)
        .filter(
            VideoTimeline.id == timeline_id,
            VideoTimeline.user_id == current_user.id,
        )
        .first()
    )

    if timeline is None:
        raise HTTPException(
            status_code=404,
            detail="Video timeline not found.",
        )

    service = VideoRenderService(
        db=db,
    )

    try:
        result, asset = (
            service.render_timeline(
                timeline,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return VideoRenderResponse(
        success=result.success,
        timeline_id=timeline.id,
        asset_id=(
            asset.id
            if asset
            else None
        ),
        output_path=result.output_path,
        duration_seconds=result.duration_seconds,
        width=result.width,
        height=result.height,
        fps=result.fps,
        file_size_bytes=result.file_size_bytes,
        mime_type=result.mime_type,
        provider=result.provider,
        error_message=result.error_message,
        metadata=result.metadata,
    )