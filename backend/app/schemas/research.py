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


ResearchStatus = Literal[
    "completed",
    "failed",
]


# =================================================
# RESEARCH REQUEST
# =================================================


class ResearchRequest(BaseModel):
    """
    Request for AI-powered topic research.
    """

    platform: PlatformType

    topic: str = Field(
        min_length=3,
        max_length=500,
    )


# =================================================
# GENERATE CONTENT FROM RESEARCH
# =================================================


class GenerateContentFromResearchRequest(BaseModel):
    """
    Request for generating AI content from
    an existing research record.
    """

    content_type: str = Field(
        default="youtube short",
        min_length=2,
        max_length=100,
    )

    tone: str = Field(
        default="engaging",
        min_length=2,
        max_length=100,
    )

    opportunity_index: int = Field(
        default=0,
        ge=0,
    )


# =================================================
# RESEARCH RESPONSE
# =================================================


class ResearchResponse(BaseModel):
    """
    Complete research result returned after analysis.
    """

    research_id: str

    platform: str

    topic: str

    keywords: list[str]

    audience_angles: list[str]

    content_opportunities: list[str]

    competitor_insights: list[str]

    research_summary: str

    opportunity_score: float | None

    trend_score: float | None

    provider: str | None

    research_status: ResearchStatus

    created_at: datetime


# =================================================
# RESEARCH HISTORY
# =================================================


class ResearchHistoryResponse(BaseModel):
    """
    Single research record for research history.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    platform: str

    topic: str

    keywords: list[str]

    audience_angles: list[str]

    content_opportunities: list[str]

    competitor_insights: list[str]

    research_summary: str | None

    opportunity_score: float | None

    trend_score: float | None

    provider: str | None

    research_status: str

    error_message: str | None

    created_at: datetime

    updated_at: datetime


class ResearchListResponse(BaseModel):
    """
    Paginated research history.
    """

    total: int

    research: list[ResearchHistoryResponse]