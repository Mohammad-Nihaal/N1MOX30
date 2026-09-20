from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PublishRequest:
    video_path: str
    title: str
    description: str = ""
    tags: list[str] | None = None
    privacy_status: str = "private"
    category_id: str = "22"
    thumbnail_path: str | None = None
    publish_at: str | None = None
    media_url: str | None = None
    media_type: str = "video"
    platform_options: dict[str, Any] | None = None


@dataclass
class PublishResult:
    platform: str
    status: str
    external_id: str | None = None
    url: str | None = None
    response: dict[str, Any] | None = None
    error: str | None = None


class PublishingProvider:
    """Provider-neutral publishing contract."""

    platform = "unknown"

    def publish(
        self,
        *,
        access_token: str,
        request: PublishRequest,
    ) -> PublishResult:
        raise NotImplementedError

    def set_thumbnail(
        self,
        *,
        access_token: str,
        external_id: str,
        thumbnail_path: str,
    ) -> dict[str, Any]:
        raise NotImplementedError
