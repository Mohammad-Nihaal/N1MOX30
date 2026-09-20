from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.publishing.providers.base import PublishRequest, PublishResult, PublishingProvider


class InstagramPublishingProvider(PublishingProvider):
    platform = "instagram"

    def _graph(self, path: str, token: str, params: dict[str, Any] | None = None):
        url = f"https://graph.facebook.com/{settings.instagram_graph_version}/{path.lstrip('/')}"
        params = dict(params or {})
        params["access_token"] = token
        response = httpx.post(url, params=params, timeout=60)
        if response.status_code >= 400:
            raise ValueError(f"Instagram API {response.status_code}: {response.text[:800]}")
        return response.json()

    def publish(self, *, access_token: str, request: PublishRequest) -> PublishResult:
        if not request.media_url:
            raise ValueError("Instagram publishing requires a publicly reachable media_url.")
        account_id = (request.platform_options or {}).get("instagram_account_id")
        if not account_id:
            raise ValueError("Instagram account id is required.")
        requested = (request.platform_options or {}).get("instagram_media_type")
        media_type = requested or ("REELS" if request.media_type == "video" else "IMAGE")
        params = {
            "media_type": media_type,
            "caption": request.description or request.title,
            "access_token": access_token,
        }
        if media_type in {"REELS", "STORIES"}:
            params["video_url" if request.media_type == "video" else "image_url"] = request.media_url
        else:
            params["image_url"] = request.media_url
        container = self._graph(str(account_id) + "/media", access_token, params)
        creation_id = container.get("id")
        if not creation_id:
            raise ValueError(f"Instagram container creation failed: {container}")
        publish = self._graph(str(account_id) + "/media_publish", access_token, {"creation_id": creation_id})
        external_id = publish.get("id") or creation_id
        return PublishResult(
            platform=self.platform,
            status="published",
            external_id=external_id,
            url=f"https://www.instagram.com/",
            response={"container": container, "publish": publish},
        )

    def set_thumbnail(self, *, access_token: str, external_id: str, thumbnail_path: str) -> dict[str, Any]:
        return {"status": "not_supported", "platform": self.platform}
