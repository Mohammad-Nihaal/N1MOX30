from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.creator_memory import CreatorMemory
from app.models.creator_preferences import CreatorPreferences
from app.models.creator_profile import CreatorProfile
from app.schemas.creator_intelligence import (
    AudienceIntelligence,
    ContentIntelligence,
    CreatorIdentity,
    CreatorIntelligenceRequest,
    CreatorIntelligenceResponse,
    PerformanceIntelligence,
    Recommendation,
)


class CreatorIntelligenceService:
    def analyze(self, db: Session, user_id: str, request: CreatorIntelligenceRequest) -> CreatorIntelligenceResponse:
        merged_request = self._merge_creator_context(db, user_id, request)
        identity = self._build_creator_identity(merged_request)
        audience = self._build_audience_intelligence(merged_request)
        content = self._build_content_intelligence(merged_request)
        performance = self._build_performance_intelligence(merged_request)
        recommendations = self._build_recommendations(merged_request, performance)
        score = self._calculate_intelligence_score(merged_request, performance)
        summary = self._build_summary(merged_request, identity, audience, content, performance, recommendations)

        return CreatorIntelligenceResponse(
            creator_identity=identity,
            audience=audience,
            content=content,
            performance=performance,
            recommendations=recommendations,
            intelligence_score=score,
            summary=summary,
            additional_context=merged_request.additional_context,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _merge_creator_context(self, db: Session, user_id: str, request: CreatorIntelligenceRequest) -> CreatorIntelligenceRequest:
        profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
        preferences = db.query(CreatorPreferences).filter(CreatorPreferences.user_id == user_id).first()
        memories = (
            db.query(CreatorMemory)
            .filter(CreatorMemory.user_id == user_id, CreatorMemory.is_active.is_(True))
            .order_by(CreatorMemory.importance_score.desc(), CreatorMemory.created_at.desc())
            .all()
        )

        if not request.creator_name and profile:
            request.creator_name = getattr(profile, "creator_name", None)
        if not request.niche and profile:
            request.niche = getattr(profile, "niche", None)
        if not request.target_audience and profile:
            request.target_audience = getattr(profile, "target_audience", None)

        if not request.tone:
            request.tone = getattr(preferences, "preferred_tone", None) if preferences else None
            if not request.tone and profile:
                request.tone = getattr(profile, "preferred_tone", None)

        if not request.language:
            request.language = getattr(preferences, "preferred_language", None) if preferences else None
            request.language = request.language or "English"

        if not request.platforms:
            if preferences:
                request.platforms = self._string_to_list(getattr(preferences, "enabled_platforms", None))
            if not request.platforms and profile:
                request.platforms = self._string_to_list(getattr(profile, "preferred_platforms", None))

        if not request.preferred_formats and preferences:
            request.preferred_formats = self._string_to_list(getattr(preferences, "preferred_formats", None))
        if not request.preferred_topics and preferences:
            request.preferred_topics = self._string_to_list(getattr(preferences, "preferred_topics", None))
        if not request.avoided_topics and preferences:
            request.avoided_topics = self._string_to_list(getattr(preferences, "avoided_topics", None))

        additional_context = dict(request.additional_context or {})
        persisted: dict[str, Any] = {
            "profile_loaded": profile is not None,
            "preferences_loaded": preferences is not None,
            "memory_count": len(memories),
            "memory": [],
        }

        if profile:
            persisted["profile"] = {
                "creator_name": getattr(profile, "creator_name", None),
                "niche": getattr(profile, "niche", None),
                "target_audience": getattr(profile, "target_audience", None),
                "content_style": getattr(profile, "content_style", None),
                "preferred_tone": getattr(profile, "preferred_tone", None),
            }

        if preferences:
            persisted["ai_preferences"] = {
                "creativity_level": getattr(preferences, "creativity_level", None),
                "research_depth": getattr(preferences, "research_depth", None),
                "personalization_level": getattr(preferences, "personalization_level", None),
                "automation_level": getattr(preferences, "automation_level", None),
            }
            persisted["content_style"] = getattr(preferences, "default_video_style", None)
            persisted["brand_voice"] = getattr(preferences, "brand_voice", None)

        persisted["memory"] = [
            {
                "id": str(memory.id),
                "memory_type": memory.memory_type,
                "memory_key": memory.memory_key,
                "memory_value": memory.memory_value,
                "source": memory.source,
                "importance_score": memory.importance_score,
                "confidence_score": memory.confidence_score,
                "is_active": memory.is_active,
            }
            for memory in memories
        ]

        additional_context["persisted_creator_context"] = persisted
        request.additional_context = additional_context
        return request

    def _build_creator_identity(self, request: CreatorIntelligenceRequest) -> CreatorIdentity:
        return CreatorIdentity(
            creator_name=request.creator_name or "Creator",
            niche=request.niche or "General Content",
            target_audience=request.target_audience or "General audience",
            language=request.language or "English",
            tone=request.tone or "Engaging and conversational",
        )

    def _build_audience_intelligence(self, request: CreatorIntelligenceRequest) -> AudienceIntelligence:
        interests = list(request.preferred_topics or []) or ["Content creation"]
        needs = ["Useful and engaging content", "Clear explanations", "Strong audience retention"]
        if request.target_audience:
            needs.insert(0, f"Content relevant to {request.target_audience}")
        return AudienceIntelligence(
            target_audience=request.target_audience or "General audience",
            likely_interests=interests,
            needs=needs,
        )

    def _build_content_intelligence(self, request: CreatorIntelligenceRequest) -> ContentIntelligence:
        formats = list(request.preferred_formats or []) or ["Educational", "Storytelling", "Short-form"]
        topics = list(request.preferred_topics or [])
        platforms = list(request.platforms or []) or ["YouTube"]
        if not topics and request.niche:
            topics = [request.niche]
        return ContentIntelligence(preferred_formats=formats, preferred_topics=topics, platforms=platforms)

    def _build_performance_intelligence(self, request: CreatorIntelligenceRequest) -> PerformanceIntelligence:
        data = request.performance_data or []
        if not data:
            return PerformanceIntelligence()
        views, watch_times, retention, ctr, engagement = [], [], [], [], []
        for item in data:
            if not isinstance(item, dict):
                continue
            views.append(self._safe_float(item.get("views", 0)))
            watch_times.append(self._safe_float(item.get("watch_time", 0)))
            retention.append(self._safe_float(item.get("retention", 0)))
            ctr.append(self._safe_float(item.get("ctr", 0)))
            engagement.append(self._safe_float(item.get("engagement", 0)))
        return PerformanceIntelligence(
            total_videos=len(data),
            average_views=self._average(views),
            average_watch_time=self._average(watch_times),
            average_retention=self._average(retention),
            average_ctr=self._average(ctr),
            average_engagement=self._average(engagement),
        )

    def _build_recommendations(self, request: CreatorIntelligenceRequest, performance: PerformanceIntelligence) -> list[Recommendation]:
        recommendations: list[Recommendation] = []
        if request.preferred_topics:
            recommendations.append(Recommendation(category="content", priority="high", title="Build around your preferred topics", description="Create content around your established topic preferences while testing different angles and hooks."))
        if request.preferred_formats:
            recommendations.append(Recommendation(category="format", priority="medium", title="Use your preferred formats", description="Prioritize the formats stored in your creator preferences and compare their performance over time."))
        recommendations.append(Recommendation(category="retention", priority="high", title="Strengthen the opening", description="Use a strong opening hook, establish the value quickly, and remove unnecessary setup."))
        if request.creator_name:
            recommendations.append(Recommendation(category="personalization", priority="medium", title="Apply creator-specific context", description="Keep future content aligned with the creator profile, preferences, audience, brand voice, and learned memory."))
        if request.platforms:
            recommendations.append(Recommendation(category="platform", priority="medium", title="Adapt content per platform", description="Use platform-specific hooks, pacing, metadata, aspect ratios, and publishing strategies."))
        if performance.total_videos == 0:
            recommendations.append(Recommendation(category="analytics", priority="medium", title="Start collecting performance data", description="Once videos are published, use views, watch time, retention, CTR, and engagement to improve future decisions."))
        return recommendations

    def _calculate_intelligence_score(self, request: CreatorIntelligenceRequest, performance: PerformanceIntelligence) -> float:
        score = 0.0
        for condition, points in [
            (bool(request.creator_name), 10), (bool(request.niche), 10),
            (bool(request.target_audience), 10), (bool(request.platforms), 10),
            (bool(request.preferred_formats), 10), (bool(request.preferred_topics), 10),
            (bool(request.tone), 5), (bool(request.language), 5),
        ]:
            if condition:
                score += points
        persisted = (request.additional_context or {}).get("persisted_creator_context", {})
        if persisted.get("profile_loaded"):
            score += 10
        if persisted.get("preferences_loaded"):
            score += 10
        if persisted.get("memory_count", 0) > 0:
            score += 10
        return round(min(score, 100.0), 2)

    def _build_summary(self, request: CreatorIntelligenceRequest, identity: CreatorIdentity, audience: AudienceIntelligence, content: ContentIntelligence, performance: PerformanceIntelligence, recommendations: list[Recommendation]) -> str:
        platform_text = ", ".join(content.platforms) if content.platforms else "YouTube"
        topic_text = ", ".join(content.preferred_topics[:3]) if content.preferred_topics else identity.niche
        memory_count = ((request.additional_context or {}).get("persisted_creator_context", {}).get("memory_count", 0))
        return (f"N1MOX30 has personalized the creator strategy for {identity.creator_name}, focused on {identity.niche}. "
                f"The current strategy is aligned with {platform_text}, with emphasis on {topic_text}. "
                f"The creator context includes {memory_count} active long-term memory item(s), and {len(recommendations)} recommendations were generated.")

    @staticmethod
    def _string_to_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if "," in value:
                return [item.strip() for item in value.split(",") if item.strip()]
            if "\n" in value:
                return [item.strip() for item in value.splitlines() if item.strip()]
            return [value]
        return [str(value)]

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _average(values: list[float]) -> float:
        return round(sum(values) / len(values), 2) if values else 0.0


creator_intelligence_service = CreatorIntelligenceService()
