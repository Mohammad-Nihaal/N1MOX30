from __future__ import annotations

import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import requests

YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def _token_for_account(account_id: int) -> str | None:
    """
    Resolve a YouTube access token using the existing N1MOX30
    token-store implementation without assuming a particular
    configuration object or function signature.
    """

    candidates = [
        "app.services.creator_accounts.secure_token_store",
        "app.services.creator_accounts.token_store",
    ]

    for module_name in candidates:
        try:
            import importlib

            module = importlib.import_module(module_name)

            functions = [
                "get_token",
                "get_access_token",
                "load_token",
                "retrieve_token",
            ]

            for function_name in functions:
                function = getattr(module, function_name, None)

                if not callable(function):
                    continue

                attempts = [
                    lambda: function(account_id),
                    lambda: function(
                        account_id=account_id
                    ),
                    lambda: function(
                        account_id=account_id,
                        platform="youtube",
                    ),
                    lambda: function(
                        account_id=account_id,
                        provider="youtube",
                    ),
                ]

                for attempt in attempts:
                    try:
                        token = attempt()
                    except TypeError:
                        continue
                    except Exception:
                        token = None

                    if isinstance(token, dict):
                        token = (
                            token.get("access_token")
                            or token.get("accessToken")
                            or token.get("token")
                        )

                    if token:
                        return str(token)

        except Exception:
            continue

    return None

def youtube_upload_ready() -> dict[str, Any]:
    """
    Runtime readiness check.

    Real publishing is intentionally disabled unless the explicit
    N1MOX_ALLOW_REAL_PUBLISH environment variable is enabled.
    """

    publishing_enabled = (
        os.getenv(
            "N1MOX_ALLOW_REAL_PUBLISH",
            "false",
        ).lower()
        == "true"
    )

    return {
        "configured": True,
        "token_security_ready": True,
        "publishing_enabled": publishing_enabled,
        "ready": publishing_enabled,
    }

def _metadata(
    title: str,
    description: str,
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
) -> dict[str, Any]:

    privacy = str(privacy_status or "private").lower()

    if privacy not in {"private", "unlisted", "public"}:
        privacy = "private"

    clean_title = str(title or "N1MOX30 Video").strip()[:100]
    clean_description = str(description or "").strip()

    # YouTube rejects < and > in title/description.
    clean_title = clean_title.replace("<", "").replace(">", "")
    clean_description = clean_description.replace("<", "").replace(">", "")

    # Description limit is 5000 bytes.
    while len(clean_description.encode("utf-8")) > 5000:
        clean_description = clean_description[:-1]

    clean_tags = []

    for tag in tags or []:
        value = str(tag).strip()
        if value and value not in clean_tags:
            clean_tags.append(value)

    return {
        "snippet": {
            "title": clean_title,
            "description": clean_description,
            "categoryId": str(category_id or "22"),
            "tags": clean_tags,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }


def _video_path(video_path: str | os.PathLike[str]) -> Path:
    path = Path(video_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Video file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Video path is not a file: {path}")

    if path.stat().st_size <= 0:
        raise ValueError(f"Video file is empty: {path}")

    return path

# Retry/backoff handling is intentionally explicit for transient YouTube failures.

def publish_video(
    *,
    account_id: int,
    video_path: str | os.PathLike[str],
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
    timeout_seconds: int = 120,
    chunk_size: int = 8 * 1024 * 1024,
    max_retries: int = 3,
) -> dict[str, Any]:

    readiness = youtube_upload_ready()

    if not readiness["ready"]:
        return {
            "status": "blocked",
            "reason": "real_publish_not_ready",
            "readiness": readiness,
        }

    path = _video_path(video_path)

    token = _token_for_account(account_id)

    if not token:
        return {
            "status": "authorization_required",
            "reason": "youtube_access_token_missing",
        }

    metadata = _metadata(
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status=privacy_status,
    )

    mime_type = mimetypes.guess_type(path.name)[0] or "video/mp4"
    file_size = path.stat().st_size

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Length": str(file_size),
        "X-Upload-Content-Type": mime_type,
    }

    params = {
        "uploadType": "resumable",
        "part": "snippet,status",
    }

    # ----------------------------------------------
    # Step 1: create resumable upload session
    # ----------------------------------------------

    try:
        response = requests.post(
            YOUTUBE_UPLOAD_URL,
            params=params,
            headers=headers,
            json=metadata,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        return {
            "status": "failed",
            "reason": "upload_session_request_failed",
            "error": str(exc),
        }

    if response.status_code not in (200, 201):
        return {
            "status": "failed",
            "reason": "upload_session_creation_failed",
            "http_status": response.status_code,
            "response": response.text[:2000],
        }

    upload_url = response.headers.get("Location")

    if not upload_url:
        return {
            "status": "failed",
            "reason": "youtube_upload_location_missing",
        }

    # ----------------------------------------------
    # Step 2: upload binary file in resumable chunks
    # ----------------------------------------------

    uploaded = 0
    retries = 0

    try:
        with path.open("rb") as file:

            while uploaded < file_size:

                file.seek(uploaded)

                remaining = file_size - uploaded
                current_size = min(chunk_size, remaining)

                data = file.read(current_size)

                if not data:
                    raise RuntimeError(
                        "Unexpected end of video file during upload."
                    )

                end = uploaded + len(data) - 1

                upload_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Length": str(len(data)),
                    "Content-Type": mime_type,
                    "Content-Range": (
                        f"bytes {uploaded}-{end}/{file_size}"
                    ),
                }

                while True:
                    try:
                        upload_response = requests.put(
                            upload_url,
                            headers=upload_headers,
                            data=data,
                            timeout=timeout_seconds,
                        )

                    except requests.RequestException as exc:

                        if retries >= max_retries:
                            return {
                                "status": "failed",
                                "reason": "youtube_upload_network_error",
                                "error": str(exc),
                                "uploaded_bytes": uploaded,
                                "total_bytes": file_size,
                            }

                        retries += 1
                        time.sleep(min(2 ** retries, 8))
                        continue

                    # Complete.
                    if upload_response.status_code in (200, 201):

                        try:
                            result = upload_response.json()
                        except Exception:
                            result = {}

                        video_id = result.get("id")

                        if not video_id:
                            return {
                                "status": "failed",
                                "reason": "youtube_upload_missing_video_id",
                                "response": upload_response.text[:2000],
                            }

                        return {
                            "status": "published",
                            "video_id": video_id,
                            "watch_url": (
                                f"https://www.youtube.com/watch?v={video_id}"
                            ),
                            "privacy_status": metadata["status"][
                                "privacyStatus"
                            ],
                            "bytes_uploaded": file_size,
                            "total_bytes": file_size,
                        }

                    # Upload accepted but incomplete.
                    if upload_response.status_code == 308:

                        range_header = upload_response.headers.get("Range")

                        if range_header:
                            try:
                                uploaded = (
                                    int(
                                        range_header.split("-")[-1]
                                    ) + 1
                                )
                            except Exception:
                                uploaded = end + 1
                        else:
                            uploaded = end + 1

                        retries = 0
                        break

                    # Retryable server/network response.
                    if upload_response.status_code in {
                        429,
                        500,
                        502,
                        503,
                        504,
                    }:

                        if retries >= max_retries:
                            return {
                                "status": "failed",
                                "reason": "youtube_upload_retry_limit",
                                "http_status": upload_response.status_code,
                                "uploaded_bytes": uploaded,
                                "total_bytes": file_size,
                                "response": upload_response.text[:2000],
                            }

                        retries += 1
                        time.sleep(min(2 ** retries, 8))
                        continue

                    # Permanent error.
                    return {
                        "status": "failed",
                        "reason": "youtube_upload_rejected",
                        "http_status": upload_response.status_code,
                        "uploaded_bytes": uploaded,
                        "total_bytes": file_size,
                        "response": upload_response.text[:2000],
                    }

    except Exception as exc:
        return {
            "status": "failed",
            "reason": "youtube_upload_exception",
            "error": str(exc),
            "uploaded_bytes": uploaded,
            "total_bytes": file_size,
        }


def prepare_real_publish(
    user_id=None,
    account_id=None,
    video_path="",
    title="N1MOX30 Creator Video",
    description="",
    tags=None,
    category_id="22",
    privacy_status="private",
    **kwargs,
) -> dict[str, Any]:
    """Prepare a real YouTube publish safely."""

    try:
        path = _video_path(video_path)
    except (FileNotFoundError, OSError):
        path = Path(video_path).expanduser().resolve()
        return {
            "status": "asset_missing",
            "message": "Video asset does not exist.",
            "video_path": str(path),
        }

    if not path.exists():
        return {
            "status": "asset_missing",
            "message": "Video asset does not exist.",
            "video_path": str(path),
        }

    if path.stat().st_size <= 0:
        return {
            "status": "asset_invalid",
            "message": "Video asset is empty.",
            "video_path": str(path),
        }

    token = _token_for_account(account_id)

    if not token:
        return {
            "status": "authorization_required",
            "message": "YouTube authorization/token is required.",
            "account_id": account_id,
        }

    readiness = youtube_upload_ready()

    if not readiness.get("ready"):
        return {
            "status": "blocked",
            "message": readiness.get(
                "message",
                "Real YouTube publishing is disabled.",
            ),
            "account_id": account_id,
        }

    metadata = _metadata(
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status=privacy_status,
    )

    return {
        "status": "ready_for_real_upload",
        "account_id": account_id,
        "user_id": user_id,
        "video_path": str(path),
        "metadata": metadata,
    }

def publish_metadata(*args, **kwargs) -> dict[str, Any]:
    """
    Backward-compatible alias.

    Metadata-only publishing is intentionally redirected to the
    real media upload implementation.
    """
    return publish_video(*args, **kwargs)

