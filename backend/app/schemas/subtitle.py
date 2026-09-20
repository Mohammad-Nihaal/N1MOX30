from typing import Any

from pydantic import BaseModel, Field


class SubtitleGenerateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    duration_seconds: float = Field(..., gt=0)
    max_words_per_segment: int = Field(default=12, ge=1, le=50)
    language: str = Field(default="en")
    style: dict[str, Any] = Field(default_factory=dict)


class SubtitleSegmentResponse(BaseModel):
    index: int
    start: float
    end: float
    text: str


class SubtitleGenerateResponse(BaseModel):
    segments: list[SubtitleSegmentResponse] = Field(
        default_factory=list
    )
    timeline_clips: list[dict[str, Any]] = Field(
        default_factory=list
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class SubtitleFileResponse(BaseModel):
    format: str
    content: str
    filename: str
    mime_type: str