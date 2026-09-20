from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.automation_workflow import AutomationWorkflow
from app.models.user import User
from app.permissions.permission_service import ActionPermissionService
from app.schemas.action_permission import (
    ActionApprovalRequest,
    ActionPermissionRequest,
    ActionPermissionResponse,
    ActionRejectionRequest,
    WorkflowPermissionResponse,
)

router = APIRouter(
    prefix="/action-permissions",
    tags=["Action Permissions"],
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
    response_model=WorkflowPermissionResponse,
)
def get_workflow_permissions(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = ActionPermissionService(db)

    # These defaults are intentionally conservative until creator preferences
    # are connected directly to the permission layer.
    return service.workflow_permissions(
        workflow=workflow,
        require_publish_approval=True,
        require_content_approval=False,
    )


@router.post(
    "/{workflow_id}/evaluate",
    response_model=ActionPermissionResponse,
)
def evaluate_action(
    workflow_id: str,
    payload: ActionPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = ActionPermissionService(db)

    result = service.evaluate_action(
        workflow=workflow,
        action=payload.action,
        require_publish_approval=True,
        require_content_approval=False,
    )

    return {
        "workflow_id": str(workflow.id),
        **result,
    }


@router.post(
    "/{workflow_id}/request",
    response_model=ActionPermissionResponse,
)
def request_action_approval(
    workflow_id: str,
    payload: ActionPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = ActionPermissionService(db)

    evaluation = service.evaluate_action(
        workflow=workflow,
        action=payload.action,
        require_publish_approval=True,
        require_content_approval=False,
    )

    if not evaluation["approval_required"]:
        return {
            "workflow_id": str(workflow.id),
            **evaluation,
        }

    return service.request_approval(
        workflow=workflow,
        action=payload.action,
        reason=evaluation.get("reason"),
    )


@router.post(
    "/{workflow_id}/approve",
    response_model=ActionPermissionResponse,
)
def approve_action(
    workflow_id: str,
    payload: ActionApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = ActionPermissionService(db)

    return service.approve_action(
        workflow=workflow,
        action=payload.action,
    )


@router.post(
    "/{workflow_id}/reject",
    response_model=ActionPermissionResponse,
)
def reject_action(
    workflow_id: str,
    payload: ActionRejectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workflow = _get_workflow(workflow_id, current_user, db)

    service = ActionPermissionService(db)

    return service.reject_action(
        workflow=workflow,
        action=payload.action,
        reason=payload.reason,
    )
