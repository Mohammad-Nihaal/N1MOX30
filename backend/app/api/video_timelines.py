from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.video_timeline import VideoTimeline
from app.schemas.video_timeline import (
    TimelineClipCreate,
    TimelineTrackCreate,
    VideoTimelineCreate,
    VideoTimelineResponse,
    VideoTimelineUpdate,
)
from app.services.video_timeline_service import VideoTimelineService


router = APIRouter(
    prefix="/video-timelines",
    tags=["Video Timelines"],
)


# ----------------------------------------------------------------------
# Response helper
# ----------------------------------------------------------------------

def serialize_timeline(
    timeline: VideoTimeline,
    service: VideoTimelineService,
) -> VideoTimelineResponse:

    return VideoTimelineResponse(
        id=timeline.id,
        user_id=timeline.user_id,
        content_id=timeline.content_id,
        name=timeline.name,
        aspect_ratio=timeline.aspect_ratio,
        width=timeline.width,
        height=timeline.height,
        duration_seconds=timeline.duration_seconds,
        fps=timeline.fps,
        background_color=timeline.background_color,
        status=timeline.status,
        version=timeline.version,
        is_locked=timeline.is_locked,
        timeline=service.get_document(timeline),
        created_at=timeline.created_at,
        updated_at=timeline.updated_at,
    )


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------

@router.post(
    "",
    response_model=VideoTimelineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_video_timeline(
    payload: VideoTimelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = VideoTimelineService(db)

    timeline = service.create_timeline(
        user_id=str(current_user.id),
        payload=payload,
    )

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Get
# ----------------------------------------------------------------------

@router.get(
    "/{timeline_id}",
    response_model=VideoTimelineResponse,
)
def get_video_timeline(
    timeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Update
# ----------------------------------------------------------------------

@router.put(
    "/{timeline_id}",
    response_model=VideoTimelineResponse,
)
def update_video_timeline(
    timeline_id: str,
    payload: VideoTimelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    try:
        timeline = service.update_timeline(
            timeline=timeline,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Add track
# ----------------------------------------------------------------------

@router.post(
    "/{timeline_id}/tracks",
    response_model=VideoTimelineResponse,
)
def add_timeline_track(
    timeline_id: str,
    payload: TimelineTrackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    try:
        timeline = service.add_track(
            timeline=timeline,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Remove track
# ----------------------------------------------------------------------

@router.delete(
    "/{timeline_id}/tracks/{track_id}",
    response_model=VideoTimelineResponse,
)
def remove_timeline_track(
    timeline_id: str,
    track_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    try:
        timeline = service.remove_track(
            timeline=timeline,
            track_id=track_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Add clip
# ----------------------------------------------------------------------

@router.post(
    "/{timeline_id}/clips",
    response_model=VideoTimelineResponse,
)
def add_timeline_clip(
    timeline_id: str,
    payload: TimelineClipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    try:
        timeline = service.add_clip(
            timeline=timeline,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Remove clip
# ----------------------------------------------------------------------

@router.delete(
    "/{timeline_id}/clips/{clip_id}",
    response_model=VideoTimelineResponse,
)
def remove_timeline_clip(
    timeline_id: str,
    clip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    try:
        timeline = service.remove_clip(
            timeline=timeline,
            clip_id=clip_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Validate
# ----------------------------------------------------------------------

@router.get(
    "/{timeline_id}/validate",
)
def validate_video_timeline(
    timeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    return service.validate_timeline(timeline)


# ----------------------------------------------------------------------
# Lock
# ----------------------------------------------------------------------

@router.post(
    "/{timeline_id}/lock",
    response_model=VideoTimelineResponse,
)
def lock_video_timeline(
    timeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    timeline = service.lock_timeline(timeline)

    return serialize_timeline(timeline, service)


# ----------------------------------------------------------------------
# Unlock
# ----------------------------------------------------------------------

@router.post(
    "/{timeline_id}/unlock",
    response_model=VideoTimelineResponse,
)
def unlock_video_timeline(
    timeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Video timeline not found",
        )

    service = VideoTimelineService(db)

    timeline = service.unlock_timeline(timeline)

    return serialize_timeline(timeline, service)