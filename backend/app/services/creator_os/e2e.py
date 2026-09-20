from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from app.services.creator_os.pipeline import CREATOR_OS_STAGES
from app.services.creator_os.production_executor import execute_creator_os
from app.services.analytics.history import calculate_trends
from app.services.publishing.durable_queue import enqueue
from app.services.publishing.real_youtube_publish import (
    prepare_real_publish,
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _stage_status(job, stage):
    return stage in job.get("completed_stages", [])


def build_e2e_job(
    user_id: int,
    topic: str,
):
    return {
        "job_id": uuid.uuid4().hex,
        "user_id": user_id,
        "topic": topic,
        "status": "created",
        "created_at": _now(),
        "completed_stages": [],
        "results": {},
    }


def run_creator_os_e2e(
    user_id: int,
    topic: str,
):
    job = build_e2e_job(
        user_id,
        topic,
    )

    result = execute_creator_os(job)

    video_result = result.get(
        "results",
        {},
    ).get(
        "video",
        {},
    )

    metadata = result.get(
        "results",
        {},
    ).get(
        "metadata",
        {},
    )

    publishing = result.get(
        "results",
        {},
    ).get(
        "publishing",
        {},
    )

    video_path = (
        video_result.get("video")
        if isinstance(video_result, dict)
        else None
    )

    if video_path:
        result["real_publish_boundary"] = prepare_real_publish(
            user_id=user_id,
            account_id="default",
            video_path=video_path,
            title=metadata.get(
                "title",
                topic,
            ) if isinstance(metadata, dict) else topic,
            description=metadata.get(
                "description",
                "",
            ) if isinstance(metadata, dict) else "",
            tags=metadata.get(
                "keywords",
                [],
            ) if isinstance(metadata, dict) else [],
        )

    result["e2e"] = {
        "total_stages": len(CREATOR_OS_STAGES),
        "completed_stages": len(
            set(result.get("completed_stages", []))
        ),
        "stage_order": result.get(
            "completed_stages",
            [],
        ),
        "expected_order": CREATOR_OS_STAGES,
        "all_stages_complete": (
            result.get("completed_stages", [])
            == CREATOR_OS_STAGES
        ),
        "video_available": bool(video_path),
        "publishing_result": publishing,
        "verified_at": _now(),
    }

    return result


def build_publish_queue(
    e2e_result: dict[str, Any],
    account_id: str,
):
    results = e2e_result.get(
        "results",
        {},
    )

    video = results.get(
        "video",
        {},
    )

    metadata = results.get(
        "metadata",
        {},
    )

    video_path = (
        video.get("video")
        if isinstance(video, dict)
        else None
    )

    if not video_path:
        return {
            "status": "asset_missing",
            "message": "No rendered video is available.",
        }

    job_id = e2e_result.get(
        "job_id",
        uuid.uuid4().hex,
    )

    return enqueue(
        job_id=job_id,
        user_id=e2e_result["user_id"],
        account_id=account_id,
        payload={
            "video_path": video_path,
            "title": metadata.get(
                "title",
                e2e_result["topic"],
            ),
            "description": metadata.get(
                "description",
                "",
            ),
            "tags": metadata.get(
                "keywords",
                [],
            ),
            "privacy_status": "private",
        },
    )


def e2e_summary(result):
    e2e = result.get(
        "e2e",
        {},
    )

    return {
        "status": result.get(
            "status",
            "unknown",
        ),
        "job_id": result.get(
            "job_id"
        ),
        "topic": result.get(
            "topic"
        ),
        "stages": e2e.get(
            "total_stages",
            len(CREATOR_OS_STAGES),
        ),
        "completed": e2e.get(
            "completed_stages",
            0,
        ),
        "all_stages_complete": e2e.get(
            "all_stages_complete",
            False,
        ),
        "video_available": e2e.get(
            "video_available",
            False,
        ),
        "publish_boundary": result.get(
            "real_publish_boundary",
            {},
        ),
        "analytics": calculate_trends(
            result.get("user_id", 0)
        ),
    }