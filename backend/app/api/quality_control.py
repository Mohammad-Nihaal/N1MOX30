from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.user import User
from app.quality_control.quality_control_service import AIQualityControlService
from app.schemas.quality_control import (
    QualityControlResponse,
    StepQualityControlResponse,
)

router = APIRouter(
    prefix="/quality-control",
    tags=["AI Quality Control"],
)


def _get_workflow(
    workflow_id: str,
    current_user: User,
    db: Session,
) -> AutomationWorkflow:
    workflow = (
        db.query(AutomationWorkflow)
        .filter(
            AutomationWorkflow.id == workflow_id,
            AutomationWorkflow.user_id == current_user.id,
        )
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found.",
        )

    return workflow


@router.get(
    "/{workflow_id}",
    response_model=QualityControlResponse,
)
def review_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = AIQualityControlService(db)

    return service.review_workflow(workflow)


@router.get(
    "/{workflow_id}/steps/{step_id}",
    response_model=StepQualityControlResponse,
)
def review_step(
    workflow_id: str,
    step_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    step = (
        db.query(AutomationStep)
        .filter(
            AutomationStep.id == step_id,
            AutomationStep.workflow_id == workflow.id,
        )
        .first()
    )

    if not step:
        raise HTTPException(
            status_code=404,
            detail="Workflow step not found.",
        )

    service = AIQualityControlService(db)

    return service.review_step(step)
