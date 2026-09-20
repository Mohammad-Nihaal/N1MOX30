from typing import Any, Optional

from pydantic import BaseModel, Field


class ThumbnailGenerateRequest(BaseModel):
    content_id: Optional[str] = None

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    topic: Optional[str] = None

    platform: str = Field(
        default="youtube",
        min_length=1,
        max_length=50,
    )

    concept_count: int = Field(
        default=4,
        ge=1,
        le=20,
    )

    style: str = Field(
        default="high_ctr",
        min_length=1,
        max_length=100,
    )

    visual_subject: Optional[str] = None

    additional_context: Optional[str] = None


class ThumbnailRenderRequest(BaseModel):
    thumbnail_id: str

    background_path: Optional[str] = None

    foreground_path: Optional[str] = None


class ThumbnailScore(BaseModel):
    curiosity: float
    readability: float
    visual: float
    ctr: float
    overall: float


class ThumbnailResponse(BaseModel):
    id: str
    content_id: Optional[str]
    name: str
    platform: str

    width: int
    height: int

    title_text: Optional[str]

    concept: Optional[str]
    visual_direction: Optional[str]

    background_prompt: Optional[str]
    foreground_prompt: Optional[str]

    text_style: Optional[str]
    composition: Optional[str]

    score: ThumbnailScore

    image_path: Optional[str]

    provider: str
    status: str
    is_selected: bool

    created_at: str
    updated_at: str


class ThumbnailGenerateResponse(BaseModel):
    thumbnails: list[ThumbnailResponse] = Field(
        default_factory=list
    )

    best_thumbnail_id: Optional[str] = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ThumbnailSelectResponse(BaseModel):
    thumbnail: ThumbnailResponse