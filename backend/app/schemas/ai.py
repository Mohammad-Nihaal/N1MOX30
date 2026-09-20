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
# GENERATION STATUS
# =================================================

GenerationStatus = Literal[
    "completed",
    "failed",
]


# =================================================
# GENERATE CONTENT REQUEST
# =================================================

class GenerateContentRequest(BaseModel):
    """
    Request for generating AI creator content.

    Research integration is optional. When a
    research_id is provided, N1MOX30 uses the
    saved research intelligence to improve the
    generated content.
    """

    platform: PlatformType

    topic: str = Field(
        min_length=3,
        max_length=500,
    )

    content_type: str = Field(
        default="general",
        min_length=2,
        max_length=100,
    )

    tone: str = Field(
        default="engaging",
        min_length=2,
        max_length=100,
    )

    research_id: str | None = None

    opportunity_index: int = Field(
        default=0,
        ge=0,
    )


# =================================================
# CREATOR CONTEXT RESPONSE
# =================================================

class CreatorContextResponse(BaseModel):
    """
    Connected creator/channel context used by AI.
    """

    has_connected_account: bool

    platform: str

    channel_name: str | None = None

    channel_id: str | None = None

    analytics: dict | None = None


# =================================================
# GENERATE CONTENT RESPONSE
# =================================================

class GenerateContentResponse(BaseModel):
    """
    AI content generation result.
    """

    generation_id: str

    platform: str

    topic: str

    content_type: str

    tone: str

    titles: list[str]

    script: str

    caption: str

    hashtags: list[str]

    provider: str | None = None

    generation_status: GenerationStatus

    created_at: datetime

    creator_context: CreatorContextResponse | None = None


# =================================================
# AI GENERATION HISTORY RESPONSE
# =================================================

class AIGenerationResponse(BaseModel):
    """
    Saved AI generation history record.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    platform: str

    topic: str

    content_type: str

    tone: str

    titles: list[str]

    script: str | None

    caption: str | None

    hashtags: list[str]

    provider: str | None

    generation_status: GenerationStatus

    error_message: str | None

    created_at: datetime

    updated_at: datetime


# =================================================
# AI GENERATION LIST RESPONSE
# =================================================

class AIGenerationListResponse(BaseModel):
    """
    Paginated AI generation history.
    """

    total: int

    generations: list[AIGenerationResponse]


# =================================================
# REUSE GENERATION REQUEST
# =================================================

class ReuseGenerationRequest(BaseModel):
    """
    Request for reusing or regenerating previous
    AI content with optional changes.
    """

    topic: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )

    content_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    tone: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    research_id: str | None = None

    opportunity_index: int = Field(
        default=0,
        ge=0,
    )