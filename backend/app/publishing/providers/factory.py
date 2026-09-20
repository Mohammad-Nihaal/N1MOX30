from __future__ import annotations

from app.publishing.providers.base import PublishingProvider
from app.publishing.providers.youtube import YouTubePublishingProvider
from app.publishing.providers.instagram import InstagramPublishingProvider
from app.publishing.providers.tiktok import TikTokPublishingProvider
from app.publishing.providers.x import XPublishingProvider


class PublishingProviderFactory:
    _providers = {
        "youtube": YouTubePublishingProvider,
        "instagram": InstagramPublishingProvider,
        "tiktok": TikTokPublishingProvider,
        "x": XPublishingProvider,
    }

    @classmethod
    def get(cls, platform: str) -> PublishingProvider:
        normalized = str(platform or "").strip().lower()
        provider_class = cls._providers.get(normalized)
        if not provider_class:
            raise ValueError(f"No publishing provider is configured for platform '{normalized}'.")
        return provider_class()
