from typing import Any

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    severity: str
    category: str
    message: str
    field: str | None = None
    recommendation: str | None = None


class ContentReviewRequest(BaseModel):
    content_id: str | None = None
    title: str = ""
    script: str = ""
    description: str = ""
    hashtags: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0
    video_path: str | None = None
    timeline: dict[str, Any] = Field(default_factory=dict)
    subtitles: list[dict[str, Any]] = Field(default_factory=list)
    thumbnail: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContentReviewResponse(BaseModel):
    ready: bool
    overall_score: float
    quality_level: str
    issues: list[ReviewIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    summary: str
    reviewed_at: str
