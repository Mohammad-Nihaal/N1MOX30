from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch17.orchestrator import (
    create_orchestration,
    get_orchestration,
    orchestration_progress,
    run_orchestration,
    resume_orchestration,
)

router = APIRouter(
    prefix="/platform/v7/orchestrator",
    tags=["Creator Orchestrator"],
)


class CreateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=10000)
    stages: list[str] | None = None
    provider: str | None = None


@router.post("/create")
def create(
    request: CreateRequest,
    current_user=Depends(get_current_user),
):
    try:
        return create_orchestration(
            user_id=str(current_user.id),
            topic=request.topic,
            stages=request.stages,
            provider=request.provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{workflow_id}")
def get(
    workflow_id: str,
    current_user=Depends(get_current_user),
):
    state = get_orchestration(
        workflow_id,
        str(current_user.id),
    )

    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return state


@router.get("/{workflow_id}/progress")
def progress(
    workflow_id: str,
    current_user=Depends(get_current_user),
):
    result = orchestration_progress(
        workflow_id,
        str(current_user.id),
    )

    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return result


@router.post("/{workflow_id}/run")
def run(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return run_orchestration(
            db=db,
            workflow_id=workflow_id,
            user_id=str(current_user.id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{workflow_id}/resume")
def resume(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return resume_orchestration(
            db=db,
            workflow_id=workflow_id,
            user_id=str(current_user.id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

