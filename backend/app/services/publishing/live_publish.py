from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.creator_accounts.token_store import load_token
from app.services.publishing.youtube import (
    upload_video,
    build_upload_metadata,
)
from app.services.publishing.queue import (
    enqueue_publish,
    execute_publish_job,
)


def publish_to_youtube(
    user_id: int,
    account_id: str,
    video_path: str,
    title: str,
    description: str="",
    tags: list[str] | None=None,
    privacy_status: str="private",
) -> dict[str,Any]:

    path=Path(video_path)

    if not path.exists():
        return {
            "status":"failed",
            "error":"Video file does not exist.",
        }

    token=load_token(account_id)

    if not token:
        return {
            "status":"authorization_required",
            "account_id":account_id,
        }

    access_token=token.get("access_token")

    if not access_token:
        return {
            "status":"authorization_required",
            "account_id":account_id,
        }

    metadata=build_upload_metadata(
        title=title,
        description=description,
        tags=tags or [],
        privacy_status=privacy_status,
    )

    result=upload_video(
        access_token=access_token,
        video_path=str(path),
        metadata=metadata,
    )

    return {
        "status":result.get("status"),
        "account_id":account_id,
        "video_id":result.get("video_id"),
        "url":(
            f"https://www.youtube.com/watch?v={result['video_id']}"
            if result.get("video_id")
            else None
        ),
        "error":result.get("error"),
    }


def queue_youtube_publish(
    user_id: int,
    account_id: str,
    video_path: str,
    metadata: dict,
) -> dict[str,Any]:

    return enqueue_publish(
        user_id=user_id,
        account_id=account_id,
        video_path=video_path,
        metadata=metadata,
    )


def execute_queued_publish(
    job: dict,
) -> dict[str,Any]:

    token=load_token(
        job.get("account_id","")
    )

    access_token=(
        token.get("access_token")
        if token
        else None
    )

    return execute_publish_job(
        job,
        access_token=access_token,
    )