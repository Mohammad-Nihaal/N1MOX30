from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.creator_os.pipeline import (
    CREATOR_OS_STAGES,
    create_creator_os_job,
    progress,
)

router = APIRouter(
    prefix="/platform/v12/creator-os",
    tags=["creator-os"],
)

_JOBS: dict[str, dict] = {}


class CreatorJobRequest(BaseModel):
    user_id: int
    topic: str
    platform: str = "youtube"


@router.get("/stages")
def get_stages():
    return {
        "stages": CREATOR_OS_STAGES,
        "total": len(CREATOR_OS_STAGES),
    }


@router.post("/jobs")
def create_job(payload: CreatorJobRequest):
    job = create_creator_os_job(
        user_id=payload.user_id,
        topic=payload.topic,
        platform=payload.platform,
    )

    _JOBS[job["job_id"]] = job

    return job


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = _JOBS.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Creator OS job not found",
        )

    return job


@router.get("/jobs/{job_id}/progress")
def get_job_progress(job_id: str):
    job = _JOBS.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Creator OS job not found",
        )

    return progress(job)