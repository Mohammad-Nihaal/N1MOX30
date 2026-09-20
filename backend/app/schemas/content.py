from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# =================================================
# PLATFORM TYPES
# =================================================

PlatformType = Literal[
    "youtube",
    "instagram",
]


# =================================================
# CONTENT STATUS
# =================================================

ContentStatus = Literal[
    "draft",
    "ready",
    "scheduled",
    "published",
]


# =================================================
# CONTENT CREATE
# =================================================

class ContentCreate(BaseModel):
    platform: PlatformType

    title: str = Field(
        min_length=2,
        max_length=255,
    )

    idea: str | None = None

    script: str | None = None

    caption: str | None = None

    hashtags: str | None = None

    status: ContentStatus = "draft"


# =================================================
# SAVE DIRECT AI CONTENT
# =================================================

class AIContentSaveRequest(BaseModel):
    """
    Request for saving AI-generated content
    directly into Content Studio.
    """

    platform: PlatformType

    title: str = Field(
        min_length=2,
        max_length=255,
    )

    topic: str = Field(
        min_length=2,
    )

    script: str | None = None

    caption: str | None = None

    hashtags: list[str] | None = None

    status: ContentStatus = "draft"


# =================================================
# SAVE EXISTING AI GENERATION
# =================================================

class SaveGenerationToContentRequest(BaseModel):
    """
    Request for transferring an existing
    AI generation into Content Studio.
    """

    title_index: int = Field(
        default=0,
        ge=0,
    )

    status: ContentStatus = "draft"


# =================================================
# CONTENT UPDATE
# =================================================

class ContentUpdate(BaseModel):
    platform: PlatformType | None = None

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    idea: str | None = None

    script: str | None = None

    caption: str | None = None

    hashtags: str | None = None

    status: ContentStatus | None = None


# =================================================
# CONTENT STATUS UPDATE
# =================================================

class ContentStatusUpdate(BaseModel):
    """
    Update only the workflow status of content.
    """

    status: ContentStatus


# =================================================
# CONTENT RESPONSE
# =================================================

class ContentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    platform: str

    title: str

    idea: str | None

    script: str | None

    caption: str | None

    hashtags: str | None

    status: str

    created_at: datetime

    updated_at: datetime


# =================================================
# CONTENT LIST RESPONSE
# =================================================

class ContentListResponse(BaseModel):
    """
    Paginated Content Studio response.
    """

    total: int

    content: list[ContentResponse]


# =================================================
# CONTENT STATISTICS
# =================================================

class ContentStatisticsResponse(BaseModel):
    """
    Content Studio workflow statistics.
    """

    total_content: int

    draft: int

    ready: int

    scheduled: int

    published: int

    youtube: int

    instagram: int