from fastapi import APIRouter, HTTPException
from typing import Any

from app.services.creator_os.pipeline import (
    CREATOR_OS_STAGES,
    create_creator_os_job,
    progress,
    complete_stage,
    fail_stage,
)

router = APIRouter(prefix="/platform/v16/creator-os", tags=["Creator OS Live"])


@router.get("/stages")
def get_stages():
    return {
        "status": "ready",
        "stages": CREATOR_OS_STAGES,
        "count": len(CREATOR_OS_STAGES),
    }


@router.post("/jobs")
def create_live_job(user_id: int, topic: str):
    return create_creator_os_job(user_id=user_id, topic=topic)


@router.get("/jobs/{job_id}")
def get_live_job(job_id: str):
    # Creator OS persistence is handled by the service layer.
    # This endpoint exposes a deterministic response boundary.
    return {
        "status": "ready",
        "job_id": job_id,
        "message": "Use the production and Creator OS APIs for persisted job state.",
    }


@router.get("/jobs/{job_id}/progress")
def get_live_progress(job_id: str):
    return progress(job_id)


@router.post("/jobs/{job_id}/complete/{stage}")
def complete_live_stage(job_id: str, stage: str):
    if stage not in CREATOR_OS_STAGES:
        raise HTTPException(status_code=400, detail="Unknown Creator OS stage")
    return complete_stage(job_id, stage)


@router.post("/jobs/{job_id}/fail/{stage}")
def fail_live_stage(job_id: str, stage: str, reason: str = "stage_failed"):
    if stage not in CREATOR_OS_STAGES:
        raise HTTPException(status_code=400, detail="Unknown Creator OS stage")
    return fail_stage(job_id, stage, reason)