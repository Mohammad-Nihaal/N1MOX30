from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreatorIntelligenceRequest(BaseModel):
    creator_name: str | None = None
    niche: str | None = None
    sub_niches: list[str] = Field(default_factory=list)
    target_audience: str | None = None
    platforms: list[str] = Field(default_factory=list)
    preferred_formats: list[str] = Field(default_factory=list)
    preferred_topics: list[str] = Field(default_factory=list)
    avoided_topics: list[str] = Field(default_factory=list)
    tone: str | None = None
    language: str | None = None
    content_goals: list[str] = Field(default_factory=list)
    performance_data: list[dict[str, Any]] = Field(default_factory=list)
    additional_context: dict[str, Any] = Field(default_factory=dict)


class CreatorIdentity(BaseModel):
    creator_name: str
    niche: str
    target_audience: str
    language: str
    tone: str


class AudienceIntelligence(BaseModel):
    target_audience: str
    likely_interests: list[str] = Field(default_factory=list)
    needs: list[str] = Field(default_factory=list)


class ContentIntelligence(BaseModel):
    preferred_formats: list[str] = Field(default_factory=list)
    preferred_topics: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)


class PerformanceIntelligence(BaseModel):
    total_videos: int = 0
    average_views: float = 0.0
    average_watch_time: float = 0.0
    average_retention: float = 0.0
    average_ctr: float = 0.0
    average_engagement: float = 0.0


class Recommendation(BaseModel):
    category: str
    priority: str
    title: str
    description: str


class PersistedCreatorContext(BaseModel):
    profile_loaded: bool = False
    preferences_loaded: bool = False
    memory_count: int = 0
    memory: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] = Field(default_factory=dict)
    ai_preferences: dict[str, Any] = Field(default_factory=dict)
    content_style: str | None = None
    brand_voice: str | None = None


class CreatorIntelligenceResponse(BaseModel):
    creator_identity: CreatorIdentity
    audience: AudienceIntelligence
    content: ContentIntelligence
    performance: PerformanceIntelligence
    recommendations: list[Recommendation] = Field(default_factory=list)
    intelligence_score: float = 0.0
    summary: str
    additional_context: dict[str, Any] = Field(default_factory=dict)
    generated_at: str
