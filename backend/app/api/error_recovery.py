from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.user import User
from app.recovery.error_recovery_service import ErrorRecoveryService
from app.schemas.error_recovery import (
    RecoveryResponse,
    RecoveryStatusResponse,
    StepRecoveryResponse,
)

router = APIRouter(
    prefix="/error-recovery",
    tags=["Error Recovery"],
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
    response_model=RecoveryStatusResponse,
)
def recovery_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(
        workflow_id,
        current_user,
        db,
    )

    service = ErrorRecoveryService(db)

    return service.get_recovery_status(
        workflow
    )


@router.post(
    "/{workflow_id}/recover",
    response_model=RecoveryResponse,
)
def recover_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(
        workflow_id,
        current_user,
        db,
    )

    service = ErrorRecoveryService(db)

    return service.recover_workflow(
        workflow
    )


@router.post(
    "/{workflow_id}/steps/{step_id}/recover",
    response_model=StepRecoveryResponse,
)
def recover_step(
    workflow_id: str,
    step_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(
        workflow_id,
        current_user,
        db,
    )

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

    service = ErrorRecoveryService(db)

    return service.recover_step(
        workflow=workflow,
        step=step,
    )


@router.get(
    "/{workflow_id}/errors",
)
def workflow_errors(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(
        workflow_id,
        current_user,
        db,
    )

    service = ErrorRecoveryService(db)

    return service.inspect_workflow_errors(
        workflow
    )
