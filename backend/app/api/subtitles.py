from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.subtitle import (
    SubtitleGenerateRequest,
    SubtitleGenerateResponse,
    SubtitleSegmentResponse,
)
from app.services.subtitles.subtitle_service import (
    SubtitleService,
)


router = APIRouter(
    prefix="/subtitles",
    tags=["Subtitles"],
)


@router.post(
    "/generate",
    response_model=SubtitleGenerateResponse,
)
def generate_subtitles(
    payload: SubtitleGenerateRequest,
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = SubtitleService()

    segments = service.generate(
        text=payload.text,
        duration_seconds=payload.duration_seconds,
    )

    if payload.format == "vtt":
        subtitle_text = service.to_webvtt(
            segments,
        )
    else:
        subtitle_text = service.to_srt(
            segments,
        )

    timeline_clips = []

    if payload.track_id:
        timeline_clips = service.to_timeline_clips(
            segments=segments,
            track_id=payload.track_id,
            style=payload.style,
        )

    return SubtitleGenerateResponse(
        provider=(
            service.provider.provider_name
            if service.provider
            else "deterministic"
        ),
        duration_seconds=payload.duration_seconds,
        segments=[
            SubtitleSegmentResponse(
                id=segment.id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                confidence=segment.confidence,
                words=segment.words,
                metadata=segment.metadata,
            )
            for segment in segments
        ],
        subtitle_text=subtitle_text,
        format=payload.format,
        timeline_clips=timeline_clips,
    )


@router.post(
    "/srt",
    response_class=PlainTextResponse,
)
def generate_srt(
    payload: SubtitleGenerateRequest,
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = SubtitleService()

    segments = service.generate(
        text=payload.text,
        duration_seconds=payload.duration_seconds,
    )

    return service.to_srt(
        segments,
    )


@router.post(
    "/vtt",
    response_class=PlainTextResponse,
)
def generate_vtt(
    payload: SubtitleGenerateRequest,
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = SubtitleService()

    segments = service.generate(
        text=payload.text,
        duration_seconds=payload.duration_seconds,
    )

    return service.to_webvtt(
        segments,
    )


@router.get(
    "/style/default",
)
def default_subtitle_style(
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = SubtitleService()

    return {
        "style": service.default_style(),
    }