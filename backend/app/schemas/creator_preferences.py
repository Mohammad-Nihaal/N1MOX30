from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreatorPreferencesBase(BaseModel):
    preferred_content_types: str | None = None
    preferred_formats: str | None = None
    preferred_topics: str | None = None
    avoided_topics: str | None = None

    preferred_tone: str | None = None
    preferred_language: str | None = None
    brand_voice: str | None = None

    target_audience: str | None = None
    audience_level: str | None = None
    audience_interests: str | None = None

    primary_platform: str | None = None
    enabled_platforms: str | None = None

    default_aspect_ratio: str = Field(
        default="16:9",
    )

    default_video_style: str | None = None
    default_caption_style: str | None = None
    default_thumbnail_style: str | None = None

    creativity_level: int = Field(
        default=70,
        ge=0,
        le=100,
    )

    research_depth: int = Field(
        default=70,
        ge=0,
        le=100,
    )

    personalization_level: int = Field(
        default=90,
        ge=0,
        le=100,
    )

    automation_level: int = Field(
        default=70,
        ge=0,
        le=100,
    )

    auto_generate_titles: bool = True
    auto_generate_description: bool = True
    auto_generate_hashtags: bool = True
    auto_generate_thumbnail: bool = True
    auto_generate_subtitles: bool = True
    auto_quality_review: bool = True

    require_publish_approval: bool = True
    require_content_approval: bool = False

    preferred_timezone: str | None = None
    preferred_posting_times: str | None = None

    preferred_voice_provider: str | None = None
    preferred_voice_id: str | None = None
    voice_style: str | None = None

    notes: str | None = None


class CreatorPreferencesCreate(
    CreatorPreferencesBase,
):
    pass


class CreatorPreferencesUpdate(
    CreatorPreferencesBase,
):
    preferred_content_types: str | None = None
    preferred_formats: str | None = None
    preferred_topics: str | None = None
    avoided_topics: str | None = None

    preferred_tone: str | None = None
    preferred_language: str | None = None
    brand_voice: str | None = None

    target_audience: str | None = None
    audience_level: str | None = None
    audience_interests: str | None = None

    primary_platform: str | None = None
    enabled_platforms: str | None = None

    default_aspect_ratio: str | None = None
    default_video_style: str | None = None
    default_caption_style: str | None = None
    default_thumbnail_style: str | None = None

    creativity_level: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    research_depth: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    personalization_level: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    automation_level: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    auto_generate_titles: bool | None = None
    auto_generate_description: bool | None = None
    auto_generate_hashtags: bool | None = None
    auto_generate_thumbnail: bool | None = None
    auto_generate_subtitles: bool | None = None
    auto_quality_review: bool | None = None

    require_publish_approval: bool | None = None
    require_content_approval: bool | None = None

    preferred_timezone: str | None = None
    preferred_posting_times: str | None = None

    preferred_voice_provider: str | None = None
    preferred_voice_id: str | None = None
    voice_style: str | None = None

    notes: str | None = None


class CreatorPreferencesResponse(
    CreatorPreferencesBase,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime


class CreatorPreferencesContext(
    BaseModel,
):
    """
    Compact preference representation intended for
    AI generation and workflow orchestration.
    """

    content: dict
    audience: dict
    platforms: dict
    ai_behavior: dict
    workflow: dict
    approval: dict
    scheduling: dict
    voice: dict