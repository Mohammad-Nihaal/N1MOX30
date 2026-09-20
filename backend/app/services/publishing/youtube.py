from __future__ import annotations

import json
import mimetypes
import urllib.error
import urllib.request
from pathlib import Path


YOUTUBE_UPLOAD_URL = (
    "https://www.googleapis.com/upload/youtube/v3/videos"
)


def build_upload_metadata(
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy_status: str = "private",
) -> dict:

    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }


def upload_video(
    access_token: str,
    video_path: str,
    metadata: dict,
) -> dict:

    path = Path(video_path)

    if not path.exists():
        return {
            "status": "failed",
            "error": "video_file_not_found",
        }

    if not access_token:
        return {
            "status": "authorization_required",
            "error": "missing_access_token",
        }

    content_type = (
        mimetypes.guess_type(path.name)[0]
        or "video/mp4"
    )

    body = path.read_bytes()

    metadata_bytes = json.dumps(
        metadata,
        ensure_ascii=False,
    ).encode()

    # Multipart request boundary.
    boundary = "N1MOXBoundary"

    multipart = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode() + metadata_bytes + (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + body + (
        f"\r\n--{boundary}--\r\n"
    ).encode()

    url = (
        YOUTUBE_UPLOAD_URL
        + "?part=snippet,status"
    )

    request = urllib.request.Request(
        url,
        data=multipart,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": (
                f"multipart/related; boundary={boundary}"
            ),
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=120,
        ) as response:

            result = json.loads(
                response.read().decode()
            )

        return {
            "status": "published",
            "provider": "youtube",
            "video_id": result.get("id"),
            "response": result,
        }

    except urllib.error.HTTPError as exc:

        try:
            body = exc.read().decode()
        except Exception:
            body = ""

        return {
            "status": "failed",
            "provider": "youtube",
            "http_status": exc.code,
            "error": body or str(exc),
        }

    except Exception as exc:

        return {
            "status": "failed",
            "provider": "youtube",
            "error": str(exc),
        }