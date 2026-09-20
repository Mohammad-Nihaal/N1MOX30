from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.production.engine import (
    create_job,
    execute_production,
    load_job,
    production_progress,
)


router = APIRouter(
    prefix="/platform/v9/production",
    tags=["N1MOX30 Production 22-27"],
)


class ProductionRequest(BaseModel):
    user_id: int = 1
    topic: str = Field(min_length=1)
    provider: str | None = None
    research: dict[str, Any] = {}


class JobRequest(BaseModel):
    job_id: str


@router.post("/create")
def production_create(request: ProductionRequest):
    return create_job(
        user_id=request.user_id,
        topic=request.topic,
        provider=request.provider,
        research=request.research,
    )


@router.post("/run")
def production_run(request: JobRequest):
    try:
        job = load_job(request.job_id)
        return execute_production(job)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{job_id}")
def production_get(job_id: str):
    try:
        return load_job(job_id)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/{job_id}/progress")
def production_progress_route(job_id: str):
    try:
        job = load_job(job_id)
        return production_progress(job)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
