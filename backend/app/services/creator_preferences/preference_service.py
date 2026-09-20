from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.creator_preferences import CreatorPreferences
from app.schemas.creator_preferences import (
    CreatorPreferencesCreate,
    CreatorPreferencesUpdate,
)


class CreatorPreferenceService:
    """
    Persistent creator preference manager for N1MOX30.
    """

    def get(
        self,
        *,
        db: Session,
        user_id: str,
    ) -> CreatorPreferences | None:
        return (
            db.query(CreatorPreferences)
            .filter(
                CreatorPreferences.user_id == user_id,
            )
            .first()
        )

    def get_or_create(
        self,
        *,
        db: Session,
        user_id: str,
    ) -> CreatorPreferences:
        preferences = self.get(
            db=db,
            user_id=user_id,
        )

        if preferences:
            return preferences

        preferences = CreatorPreferences(
            user_id=user_id,
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        return preferences

    def create(
        self,
        *,
        db: Session,
        user_id: str,
        data: CreatorPreferencesCreate,
    ) -> CreatorPreferences:
        existing = self.get(
            db=db,
            user_id=user_id,
        )

        if existing:
            raise ValueError(
                "Creator preferences already exist.",
            )

        preferences = CreatorPreferences(
            user_id=user_id,
            **data.model_dump(),
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        return preferences

    def update(
        self,
        *,
        db: Session,
        preferences: CreatorPreferences,
        data: CreatorPreferencesUpdate,
    ) -> CreatorPreferences:
        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                preferences,
                field,
                value,
            )

        db.commit()
        db.refresh(preferences)

        return preferences

    def get_context(
        self,
        *,
        db: Session,
        user_id: str,
    ) -> dict:
        preferences = self.get_or_create(
            db=db,
            user_id=user_id,
        )

        return {
            "content": {
                "types": preferences.preferred_content_types,
                "formats": preferences.preferred_formats,
                "topics": preferences.preferred_topics,
                "avoided_topics": preferences.avoided_topics,
                "tone": preferences.preferred_tone,
                "language": preferences.preferred_language,
                "brand_voice": preferences.brand_voice,
            },
            "audience": {
                "target": preferences.target_audience,
                "level": preferences.audience_level,
                "interests": preferences.audience_interests,
            },
            "platforms": {
                "primary": preferences.primary_platform,
                "enabled": preferences.enabled_platforms,
            },
            "ai_behavior": {
                "creativity": preferences.creativity_level,
                "research_depth": preferences.research_depth,
                "personalization": (
                    preferences.personalization_level
                ),
                "automation": preferences.automation_level,
            },
            "workflow": {
                "auto_titles": (
                    preferences.auto_generate_titles
                ),
                "auto_description": (
                    preferences.auto_generate_description
                ),
                "auto_hashtags": (
                    preferences.auto_generate_hashtags
                ),
                "auto_thumbnail": (
                    preferences.auto_generate_thumbnail
                ),
                "auto_subtitles": (
                    preferences.auto_generate_subtitles
                ),
                "auto_quality_review": (
                    preferences.auto_quality_review
                ),
                "video_style": (
                    preferences.default_video_style
                ),
                "caption_style": (
                    preferences.default_caption_style
                ),
                "thumbnail_style": (
                    preferences.default_thumbnail_style
                ),
                "aspect_ratio": (
                    preferences.default_aspect_ratio
                ),
            },
            "approval": {
                "publish": (
                    preferences.require_publish_approval
                ),
                "content": (
                    preferences.require_content_approval
                ),
            },
            "scheduling": {
                "timezone": (
                    preferences.preferred_timezone
                ),
                "posting_times": (
                    preferences.preferred_posting_times
                ),
            },
            "voice": {
                "provider": (
                    preferences.preferred_voice_provider
                ),
                "voice_id": (
                    preferences.preferred_voice_id
                ),
                "style": (
                    preferences.voice_style
                ),
            },
        }


creator_preference_service = CreatorPreferenceService()