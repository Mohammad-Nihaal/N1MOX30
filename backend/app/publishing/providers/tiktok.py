from __future__ import annotations

from typing import Any

import httpx

from app.publishing.providers.base import PublishRequest, PublishResult, PublishingProvider


class TikTokPublishingProvider(PublishingProvider):
    platform = "tiktok"
    base = "https://open.tiktokapis.com/v2"

    def _post(self, path: str, token: str, payload: dict[str, Any]):
        response = httpx.post(
            self.base + path,
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
            timeout=60,
        )
        if response.status_code >= 400:
            raise ValueError(f"TikTok API {response.status_code}: {response.text[:800]}")
        data = response.json()
        err = data.get("error") or {}
        if err and err.get("code") not in (None, "", "ok"):
            raise ValueError(f"TikTok API error: {err}")
        return data

    def publish(self, *, access_token: str, request: PublishRequest) -> PublishResult:
        info = self._post("/post/publish/creator_info/query/", access_token, {})
        creator = info.get("data", {})
        options = request.platform_options or {}
        privacy = options.get("privacy_level") or (creator.get("privacy_level_options") or ["SELF_ONLY"])[0]
        if not request.media_url:
            raise ValueError("TikTok PULL_FROM_URL publishing requires a public verified media_url.")
        payload = {
            "post_info": {
                "title": (request.description or request.title)[:2200],
                "privacy_level": privacy,
                "disable_comment": bool(options.get("disable_comment", False)),
                "disable_duet": bool(options.get("disable_duet", False)),
                "disable_stitch": bool(options.get("disable_stitch", False)),
                "is_aigc": bool(options.get("is_aigc", True)),
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": request.media_url,
            },
        }
        result = self._post("/post/publish/video/init/", access_token, payload)
        publish_id = (result.get("data") or {}).get("publish_id")
        return PublishResult(
            platform=self.platform,
            status="processing",
            external_id=publish_id,
            response=result,
        )

    def set_thumbnail(self, *, access_token: str, external_id: str, thumbnail_path: str) -> dict[str, Any]:
        return {"status": "not_supported", "platform": self.platform}
