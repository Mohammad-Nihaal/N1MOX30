from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.batch21.production_pipeline import (
    create_production_job,
    production_progress,
    run_production_job,
)


router = APIRouter(
    prefix="/platform/v8/production",
    tags=["Batch 21 Production"],
)


class ProductionCreateRequest(BaseModel):
    user_id: int = 1
    topic: str = Field(min_length=1)
    provider: str | None = None
    stages: list[str] | None = None
    research: dict[str, Any] = {}


class ProductionRunRequest(BaseModel):
    job: dict[str, Any]


@router.post("/create")
def create(request: ProductionCreateRequest):
    try:
        return create_production_job(
            user_id=request.user_id,
            topic=request.topic,
            provider=request.provider,
            stages=request.stages,
            research=request.research,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/run")
def run(request: ProductionRunRequest):
    try:
        return run_production_job(request.job)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/progress")
def progress(request: ProductionRunRequest):
    return production_progress(request.job)
