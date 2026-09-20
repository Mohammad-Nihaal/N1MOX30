from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


AspectRatio = Literal["16:9", "9:16", "1:1", "4:5"]


class TimelineClip(BaseModel):
    id: str
    track_id: str

    media_asset_id: str | None = None

    clip_type: Literal[
        "video",
        "image",
        "audio",
        "voice",
        "caption",
        "text",
        "overlay",
        "transition",
    ] = "video"

    name: str = "Untitled Clip"

    start_time: float = Field(default=0.0, ge=0.0)
    end_time: float = Field(default=0.0, ge=0.0)

    source_start: float = Field(default=0.0, ge=0.0)
    source_end: float | None = Field(default=None, ge=0.0)

    layer: int = Field(default=0, ge=0)

    volume: float = Field(default=1.0, ge=0.0, le=2.0)

    opacity: float = Field(default=1.0, ge=0.0, le=1.0)

    x: float = 0.0
    y: float = 0.0

    width: float | None = Field(default=None, gt=0.0)
    height: float | None = Field(default=None, gt=0.0)

    rotation: float = 0.0

    playback_rate: float = Field(default=1.0, gt=0.0)

    text: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value: float) -> float:
        if value < 0:
            raise ValueError("end_time cannot be negative")
        return value


class TimelineTrack(BaseModel):
    id: str
    name: str

    track_type: Literal[
        "video",
        "audio",
        "voice",
        "caption",
        "overlay",
        "text",
    ] = "video"

    order: int = 0
    muted: bool = False
    locked: bool = False
    visible: bool = True

    clips: list[TimelineClip] = Field(default_factory=list)


class VideoTimelineDocument(BaseModel):
    version: int = 1

    aspect_ratio: AspectRatio = "16:9"

    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)

    fps: int = Field(default=30, gt=0, le=120)

    duration_seconds: float = Field(default=0.0, ge=0.0)

    background_color: str = "#000000"

    tracks: list[TimelineTrack] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class VideoTimelineCreate(BaseModel):
    name: str = Field(default="Untitled Timeline", min_length=1, max_length=255)

    content_id: str | None = None

    aspect_ratio: AspectRatio = "16:9"

    fps: int = Field(default=30, gt=0, le=120)

    background_color: str = "#000000"

    metadata: dict[str, Any] = Field(default_factory=dict)


class VideoTimelineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)

    aspect_ratio: AspectRatio | None = None

    fps: int | None = Field(default=None, gt=0, le=120)

    background_color: str | None = None

    status: str | None = None

    timeline: VideoTimelineDocument | None = None

    metadata: dict[str, Any] | None = None


class VideoTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    content_id: str | None

    name: str

    aspect_ratio: str
    width: int
    height: int

    duration_seconds: float
    fps: int

    background_color: str

    status: str
    version: int
    is_locked: bool

    timeline: VideoTimelineDocument

    created_at: datetime
    updated_at: datetime


class TimelineClipCreate(BaseModel):
    track_id: str

    media_asset_id: str | None = None

    clip_type: Literal[
        "video",
        "image",
        "audio",
        "voice",
        "caption",
        "text",
        "overlay",
        "transition",
    ] = "video"

    name: str = "Untitled Clip"

    start_time: float = Field(default=0.0, ge=0.0)
    end_time: float = Field(default=0.0, ge=0.0)

    source_start: float = Field(default=0.0, ge=0.0)
    source_end: float | None = Field(default=None, ge=0.0)

    layer: int = Field(default=0, ge=0)

    volume: float = Field(default=1.0, ge=0.0, le=2.0)
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)

    x: float = 0.0
    y: float = 0.0

    width: float | None = Field(default=None, gt=0.0)
    height: float | None = Field(default=None, gt=0.0)

    rotation: float = 0.0

    playback_rate: float = Field(default=1.0, gt=0.0)

    text: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineTrackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    track_type: Literal[
        "video",
        "audio",
        "voice",
        "caption",
        "overlay",
        "text",
    ] = "video"

    order: int = 0

    muted: bool = False
    locked: bool = False
    visible: bool = True