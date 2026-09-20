from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


CREATOR_OS_STAGES = [
    "research",
    "strategy",
    "hooks",
    "script",
    "voice",
    "visuals",
    "video",
    "captions",
    "thumbnail",
    "metadata",
    "quality_check",
    "scheduling",
    "publishing",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_creator_os_job(
    user_id: int,
    topic: str,
    platform: str = "youtube",
) -> dict[str, Any]:
    return {
        "job_id": f"creator_{user_id}_{int(datetime.now().timestamp() * 1000)}",
        "user_id": user_id,
        "topic": topic,
        "platform": platform,
        "status": "created",
        "current_stage": None,
        "completed_stages": [],
        "failed_stages": [],
        "results": {},
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def stage_index(stage: str) -> int:
    try:
        return CREATOR_OS_STAGES.index(stage)
    except ValueError:
        return -1


def progress(job: dict[str, Any]) -> dict[str, Any]:
    completed = [
        s for s in job.get("completed_stages", [])
        if s in CREATOR_OS_STAGES
    ]

    count = len(completed)
    total = len(CREATOR_OS_STAGES)

    return {
        "job_id": job.get("job_id"),
        "status": job.get("status"),
        "current_stage": job.get("current_stage"),
        "completed_count": count,
        "total_stages": total,
        "progress_percent": round((count / total) * 100, 2),
        "completed_stages": completed,
        "remaining_stages": [
            s for s in CREATOR_OS_STAGES
            if s not in completed
        ],
        "failed_stages": job.get("failed_stages", []),
    }


def complete_stage(
    job: dict[str, Any],
    stage: str,
    result: Any,
) -> dict[str, Any]:
    if stage not in CREATOR_OS_STAGES:
        raise ValueError(f"Unknown Creator OS stage: {stage}")

    job.setdefault("results", {})[stage] = result

    if stage not in job.setdefault("completed_stages", []):
        job["completed_stages"].append(stage)

    job["current_stage"] = stage

    if len(job["completed_stages"]) == len(CREATOR_OS_STAGES):
        job["status"] = "completed"
        job["current_stage"] = None
        job["completed_at"] = utc_now()
    else:
        job["status"] = "running"

    job["updated_at"] = utc_now()

    return job


def fail_stage(
    job: dict[str, Any],
    stage: str,
    error: str,
) -> dict[str, Any]:
    if stage not in job.setdefault("failed_stages", []):
        job["failed_stages"].append(stage)

    job["current_stage"] = stage
    job["status"] = "failed"
    job["results"][stage] = {
        "status": "failed",
        "error": error,
    }
    job["updated_at"] = utc_now()

    return job