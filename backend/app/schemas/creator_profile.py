from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =================================================
# CREATOR PROFILE BASE
# =================================================


class CreatorProfileBase(BaseModel):
    """
    Shared creator profile fields used for
    onboarding and profile updates.
    """

    creator_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    niche: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    target_audience: str | None = Field(
        default=None,
        max_length=5000,
    )

    creator_goals: str | None = Field(
        default=None,
        max_length=5000,
    )

    preferred_platforms: str | None = Field(
        default=None,
        max_length=2000,
    )

    content_style: str | None = Field(
        default=None,
        max_length=255,
    )

    preferred_tone: str | None = Field(
        default=None,
        max_length=255,
    )

    posting_preferences: str | None = Field(
        default=None,
        max_length=5000,
    )

    ai_preferences: str | None = Field(
        default=None,
        max_length=5000,
    )


# =================================================
# CREATOR ONBOARDING REQUEST
# =================================================


class CreatorProfileCreate(
    CreatorProfileBase
):
    """
    Initial creator onboarding profile.
    """

    creator_name: str = Field(
        min_length=2,
        max_length=255,
    )


# =================================================
# CREATOR PROFILE UPDATE
# =================================================


class CreatorProfileUpdate(
    CreatorProfileBase
):
    """
    Update creator profile and AI preferences.
    """

    pass


# =================================================
# CREATOR PROFILE RESPONSE
# =================================================


class CreatorProfileResponse(
    CreatorProfileBase
):
    """
    Creator profile returned to frontend and AI.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    created_at: datetime

    updated_at: datetime