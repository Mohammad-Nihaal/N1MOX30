from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch18.persistent_workflow import (
    create_persistent_workflow,
    get_persistent_workflow,
    persistent_progress,
    workflow_to_dict,
)

router = APIRouter(
    prefix="/platform/v8/workflows",
    tags=["Persistent Creator Workflows"],
)


class PersistentWorkflowRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=10000)
    stages: list[str] | None = None
    provider: str | None = None


@router.post("")
def create_workflow(
    request: PersistentWorkflowRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        workflow = create_persistent_workflow(
            db=db,
            user_id=str(current_user.id),
            topic=request.topic,
            stages=request.stages,
            provider=request.provider,
        )
        return workflow_to_dict(workflow)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    workflow = get_persistent_workflow(
        db,
        workflow_id,
        str(current_user.id),
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow_to_dict(workflow)


@router.get("/{workflow_id}/progress")
def get_progress(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    workflow = get_persistent_workflow(
        db,
        workflow_id,
        str(current_user.id),
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return persistent_progress(workflow)
