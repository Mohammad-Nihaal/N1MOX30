from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

QUEUE_STORAGE = (
    PROJECT_ROOT
    / "storage"
    / "publishing_queue"
)

QUEUE_STORAGE.mkdir(
    parents=True,
    exist_ok=True,
)


def now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def enqueue_publish(
    user_id: int,
    account_id: str,
    video_path: str,
    metadata: dict,
    max_attempts: int = 3,
) -> dict:

    job = {
        "job_id": f"pub_{uuid.uuid4().hex}",
        "user_id": user_id,
        "account_id": account_id,
        "video_path": video_path,
        "metadata": metadata,
        "status": "queued",
        "attempts": 0,
        "max_attempts": max_attempts,
        "created_at": now(),
        "updated_at": now(),
        "last_error": None,
        "result": None,
    }

    path = QUEUE_STORAGE / (
        f"{job['job_id']}.json"
    )

    path.write_text(
        json.dumps(
            job,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return job


def update_job(
    job_id: str,
    **updates,
) -> dict | None:

    path = QUEUE_STORAGE / f"{job_id}.json"

    if not path.exists():
        return None

    job = json.loads(
        path.read_text(encoding="utf-8")
    )

    job.update(updates)
    job["updated_at"] = now()

    path.write_text(
        json.dumps(
            job,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return job


def get_job(
    job_id: str,
) -> dict | None:

    path = QUEUE_STORAGE / f"{job_id}.json"

    if not path.exists():
        return None

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def execute_publish_job(
    job: dict,
    access_token: str | None = None,
) -> dict:

    from app.services.publishing.youtube import (
        upload_video,
    )

    attempts = int(
        job.get("attempts", 0)
    ) + 1

    updated = update_job(
        job["job_id"],
        status="processing",
        attempts=attempts,
    )

    if not access_token:

        return update_job(
            job["job_id"],
            status=(
                "retry_pending"
                if attempts < job["max_attempts"]
                else "failed"
            ),
            last_error="authorization_required",
        ) or updated

    result = upload_video(
        access_token=access_token,
        video_path=job["video_path"],
        metadata=job["metadata"],
    )

    if result.get("status") == "published":

        return update_job(
            job["job_id"],
            status="published",
            result=result,
            last_error=None,
        ) or job

    return update_job(
        job["job_id"],
        status=(
            "retry_pending"
            if attempts < job["max_attempts"]
            else "failed"
        ),
        result=result,
        last_error=result.get("error"),
    ) or job