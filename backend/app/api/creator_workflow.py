from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch16.creator_workflow import (
    CREATOR_STAGES,
    run_creator_stage,
    run_creator_workflow,
)

router = APIRouter(
    prefix="/platform/v6/creator",
    tags=["Creator Workflow"],
)


class StageRequest(BaseModel):
    stage: str
    prompt: str = Field(min_length=1, max_length=50000)
    provider: str | None = None
    estimated_units: int = Field(default=1, ge=1, le=1000)


class WorkflowRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=10000)
    stages: list[str] | None = None
    provider: str | None = None


@router.get("/stages")
def stages():
    return {
        "stages": list(CREATOR_STAGES),
        "count": len(CREATOR_STAGES),
    }


@router.post("/stage")
def execute_stage(
    request: StageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = run_creator_stage(
        db=db,
        user_id=str(current_user.id),
        stage=request.stage,
        prompt=request.prompt,
        provider=request.provider,
        estimated_units=request.estimated_units,
    )

    return {
        "success": result.success,
        "stage": result.stage,
        "provider": result.provider,
        "content": result.content,
        "generation_id": result.generation_id,
        "usage_recorded": result.usage_recorded,
        "fallback_used": result.fallback_used,
        "error": result.error,
    }


@router.post("/workflow")
def execute_workflow(
    request: WorkflowRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return run_creator_workflow(
        db=db,
        user_id=str(current_user.id),
        topic=request.topic,
        stages=request.stages,
        provider=request.provider,
    )

