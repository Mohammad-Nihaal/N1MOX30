from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import httpx

from app.publishing.providers.base import PublishRequest, PublishResult, PublishingProvider


class XPublishingProvider(PublishingProvider):
    platform = "x"
    MEDIA_ENDPOINT = "https://api.x.com/2/media/upload"
    POST_ENDPOINT = "https://api.x.com/2/tweets"

    def _post(self, token: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            self.POST_ENDPOINT, json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=30,
        )
        if response.status_code >= 400:
            raise ValueError(f"X API {response.status_code}: {response.text[:800]}")
        return response.json()

    def _upload_video(self, token: str, video_path: str) -> str:
        path = Path(video_path)
        total = path.stat().st_size
        headers = {"Authorization": f"Bearer {token}"}
        init = httpx.post(
            self.MEDIA_ENDPOINT,
            params={"command": "INIT", "media_type": "video/mp4", "total_bytes": total, "media_category": "tweet_video"},
            headers=headers, timeout=30,
        )
        if init.status_code >= 400:
            raise ValueError(f"X media INIT {init.status_code}: {init.text[:800]}")
        media_id = str((init.json().get("data") or {}).get("id") or "")
        if not media_id:
            raise ValueError("X media INIT did not return a media id.")

        with path.open("rb") as handle:
            segment = 0
            while True:
                chunk = handle.read(4 * 1024 * 1024)
                if not chunk:
                    break
                response = httpx.post(
                    self.MEDIA_ENDPOINT,
                    data={"command": "APPEND", "media_id": media_id, "segment_index": segment},
                    files={"media": (path.name, chunk, "video/mp4")},
                    headers=headers, timeout=120,
                )
                if response.status_code >= 300:
                    raise ValueError(f"X media APPEND {response.status_code}: {response.text[:800]}")
                segment += 1

        finalize = httpx.post(
            self.MEDIA_ENDPOINT,
            params={"command": "FINALIZE", "media_id": media_id},
            headers=headers, timeout=30,
        )
        if finalize.status_code >= 400:
            raise ValueError(f"X media FINALIZE {finalize.status_code}: {finalize.text[:800]}")
        info = (finalize.json().get("data") or {}).get("processing_info")
        deadline = time.time() + 180
        while info and info.get("state") not in {"succeeded", "failed"} and time.time() < deadline:
            time.sleep(max(1, int(info.get("check_after_secs", 1))))
            status = httpx.get(
                self.MEDIA_ENDPOINT, params={"command": "STATUS", "media_id": media_id},
                headers=headers, timeout=30,
            )
            if status.status_code >= 400:
                raise ValueError(f"X media STATUS {status.status_code}: {status.text[:800]}")
            info = (status.json().get("data") or {}).get("processing_info")
        if info and info.get("state") != "succeeded":
            raise ValueError(f"X media processing failed or timed out: {info}")
        return media_id

    def publish(self, *, access_token: str, request: PublishRequest) -> PublishResult:
        options = request.platform_options or {}
        thread = options.get("thread") or []
        media_ids = [str(x) for x in (options.get("media_ids") or [])[:4]]
        if request.video_path and Path(request.video_path).exists() and not media_ids:
            media_ids = [self._upload_video(access_token, request.video_path)]
        first_text = str(thread[0] if thread else (request.description or request.title))[:280]
        payload: dict[str, Any] = {"text": first_text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
        first = self._post(access_token, payload)
        first_id = (first.get("data") or {}).get("id")
        replies = []
        previous_id = first_id
        for item in thread[1:]:
            reply = self._post(access_token, {"text": str(item)[:280], "reply": {"in_reply_to_tweet_id": previous_id}})
            previous_id = (reply.get("data") or {}).get("id") or previous_id
            replies.append(reply)
        return PublishResult(
            platform=self.platform, status="published", external_id=first_id,
            url=f"https://x.com/i/web/status/{first_id}" if first_id else None,
            response={"first": first, "replies": replies, "media_ids": media_ids},
        )

    def set_thumbnail(self, *, access_token: str, external_id: str, thumbnail_path: str) -> dict[str, Any]:
        return {"status": "not_supported", "platform": self.platform}
