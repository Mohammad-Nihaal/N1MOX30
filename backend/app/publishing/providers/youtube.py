from __future__ import annotations

import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import httpx

from app.publishing.providers.base import (
    PublishRequest,
    PublishResult,
    PublishingProvider,
)


YOUTUBE_UPLOAD_URL = (
    "https://www.googleapis.com/upload/youtube/v3/videos"
)

YOUTUBE_THUMBNAIL_URL = (
    "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
)

CHUNK_SIZE = 8 * 1024 * 1024

RETRIABLE_STATUS_CODES = {
    500,
    502,
    503,
    504,
}


class YouTubePublishingProvider(PublishingProvider):
    """
    YouTube publishing adapter.

    Uses Google's resumable upload protocol so large rendered
    videos can be uploaded in chunks and resumed after transient
    network failures.
    """

    platform = "youtube"

    def publish(
        self,
        *,
        access_token: str,
        request: PublishRequest,
    ) -> PublishResult:
        video_path = Path(request.video_path)

        if not video_path.exists():
            raise ValueError(
                f"Video file does not exist: {video_path}"
            )

        if not video_path.is_file():
            raise ValueError(
                f"Video path is not a file: {video_path}"
            )

        file_size = video_path.stat().st_size

        if file_size <= 0:
            raise ValueError("Video file is empty.")

        privacy_status = str(
            request.privacy_status or "private"
        ).strip().lower()

        allowed_privacy = {
            "private",
            "public",
            "unlisted",
        }

        if privacy_status not in allowed_privacy:
            raise ValueError(
                "privacy_status must be private, public, or unlisted."
            )

        metadata: dict[str, Any] = {
            "snippet": {
                "title": str(request.title or "").strip(),
                "description": str(
                    request.description or ""
                ),
                "categoryId": str(
                    request.category_id or "22"
                ),
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        if not metadata["snippet"]["title"]:
            raise ValueError(
                "YouTube publishing requires a title."
            )

        tags = [
            str(tag).strip().lstrip("#")
            for tag in (request.tags or [])
            if str(tag).strip()
        ]

        if tags:
            metadata["snippet"]["tags"] = tags

        if request.publish_at:
            metadata["status"]["publishAt"] = request.publish_at
            metadata["status"]["privacyStatus"] = "private"

        mime_type = (
            mimetypes.guess_type(str(video_path))[0]
            or "video/mp4"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": mime_type,
        }

        params = {
            "uploadType": "resumable",
            "part": "snippet,status",
        }

        with httpx.Client(timeout=120.0) as client:
            session_response = client.post(
                YOUTUBE_UPLOAD_URL,
                params=params,
                headers=headers,
                json=metadata,
            )

            self._raise_for_api_error(
                session_response,
                "Unable to start YouTube upload.",
            )

            upload_url = session_response.headers.get(
                "Location"
            )

            if not upload_url:
                raise ValueError(
                    "YouTube did not return a resumable upload URL."
                )

            response_data = self._upload_file(
                client=client,
                upload_url=upload_url,
                access_token=access_token,
                video_path=video_path,
                mime_type=mime_type,
            )

        video_id = response_data.get("id")

        if not video_id:
            raise ValueError(
                "YouTube upload completed without returning a video ID."
            )

        result = PublishResult(
            platform="youtube",
            status="published",
            external_id=video_id,
            url=(
                f"https://www.youtube.com/watch?v={video_id}"
            ),
            response=response_data,
        )

        if request.thumbnail_path:
            thumbnail_result = self.set_thumbnail(
                access_token=access_token,
                external_id=video_id,
                thumbnail_path=request.thumbnail_path,
            )

            if result.response is None:
                result.response = {}

            result.response["thumbnail"] = thumbnail_result

        return result

    def set_thumbnail(
        self,
        *,
        access_token: str,
        external_id: str,
        thumbnail_path: str,
    ) -> dict[str, Any]:
        path = Path(thumbnail_path)

        if not path.exists() or not path.is_file():
            raise ValueError(
                f"Thumbnail file does not exist: {path}"
            )

        file_size = path.stat().st_size

        if file_size <= 0:
            raise ValueError("Thumbnail file is empty.")

        if file_size > 50 * 1024 * 1024:
            raise ValueError(
                "YouTube thumbnails must be 50 MB or smaller."
            )

        mime_type = (
            mimetypes.guess_type(str(path))[0]
            or "image/png"
        )

        if mime_type not in {
            "image/jpeg",
            "image/png",
            "application/octet-stream",
        }:
            raise ValueError(
                "Thumbnail must be JPEG or PNG."
            )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": mime_type,
            "Content-Length": str(file_size),
        }

        params = {
            "videoId": external_id,
        }

        with path.open("rb") as image_file:
            response = httpx.post(
                YOUTUBE_THUMBNAIL_URL,
                params=params,
                headers=headers,
                content=image_file.read(),
                timeout=120.0,
            )

        self._raise_for_api_error(
            response,
            "Unable to set YouTube thumbnail.",
        )

        return response.json()

    def _upload_file(
        self,
        *,
        client: httpx.Client,
        upload_url: str,
        access_token: str,
        video_path: Path,
        mime_type: str,
    ) -> dict[str, Any]:
        total_size = video_path.stat().st_size
        position = 0
        retry_count = 0

        while position < total_size:
            chunk_end = min(
                position + CHUNK_SIZE,
                total_size,
            )

            length = chunk_end - position

            with video_path.open("rb") as video_file:
                video_file.seek(position)
                chunk = video_file.read(length)

            headers = {
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Content-Length": str(length),
                "Content-Type": mime_type,
                "Content-Range": (
                    f"bytes {position}-{chunk_end - 1}/"
                    f"{total_size}"
                ),
            }

            try:
                response = client.put(
                    upload_url,
                    headers=headers,
                    content=chunk,
                )
            except httpx.RequestError:
                if retry_count >= 5:
                    raise ValueError(
                        "YouTube upload failed after multiple "
                        "network retries."
                    )

                retry_count += 1
                time.sleep(min(2 ** retry_count, 30))
                continue

            if response.status_code in RETRIABLE_STATUS_CODES:
                if retry_count >= 5:
                    self._raise_for_api_error(
                        response,
                        "YouTube upload failed after retries.",
                    )

                retry_count += 1
                time.sleep(min(2 ** retry_count, 30))
                continue

            if response.status_code == 308:
                retry_count = 0

                range_header = response.headers.get(
                    "Range"
                )

                if range_header:
                    try:
                        uploaded_end = int(
                            range_header.split("-")[-1]
                        )
                        position = uploaded_end + 1
                    except (ValueError, IndexError):
                        position = chunk_end
                else:
                    position = chunk_end

                continue

            if response.status_code in {
                200,
                201,
            }:
                return response.json()

            self._raise_for_api_error(
                response,
                "YouTube video upload failed.",
            )

        raise ValueError(
            "YouTube upload ended without a final response."
        )

    @staticmethod
    def _raise_for_api_error(
        response: httpx.Response,
        prefix: str,
    ) -> None:
        if response.is_success:
            return

        message = ""

        try:
            payload = response.json()
            error = payload.get("error", {})

            if isinstance(error, dict):
                message = str(
                    error.get("message") or ""
                )

                reason = ""

                errors = error.get("errors") or []

                if errors and isinstance(
                    errors,
                    list,
                ):
                    first = errors[0]

                    if isinstance(first, dict):
                        reason = str(
                            first.get("reason") or ""
                        )

                if reason:
                    message = (
                        f"{message} ({reason})"
                    ).strip()
        except Exception:
            message = ""

        if not message:
            message = response.text[:500]

        raise ValueError(
            f"{prefix} HTTP {response.status_code}: {message}"
        )
