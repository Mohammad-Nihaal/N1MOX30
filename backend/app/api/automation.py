from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.automation.workflow_types import WorkflowStage
from app.core.database import get_db
from app.models.automation_workflow import AutomationWorkflow
from app.models.user import User
from app.schemas.automation import (
    AutomationStepResponse,
    AutomationWorkflowActionResponse,
    AutomationWorkflowCreate,
    AutomationWorkflowDetailResponse,
    AutomationWorkflowProjectUpdate,
    AutomationWorkflowResponse,
)
from app.services.automation_service import AutomationService


router = APIRouter(
    prefix="/automation",
    tags=["Automation"],
)


def build_workflow_detail(
    service: AutomationService,
    workflow: AutomationWorkflow,
) -> AutomationWorkflowDetailResponse:
    """Build a workflow response including its steps."""

    steps = service.get_workflow_steps(
        workflow_id=workflow.id,
    )

    return AutomationWorkflowDetailResponse(
        id=workflow.id,
        user_id=workflow.user_id,
        project_id=workflow.project_id,
        command=workflow.command,
        platform=workflow.platform,
        topic=workflow.topic,
        status=workflow.status,
        current_stage=workflow.current_stage,
        progress=workflow.progress,
        error_message=workflow.error_message,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        completed_at=workflow.completed_at,
        steps=[
            AutomationStepResponse.model_validate(step)
            for step in steps
        ],
    )


@router.post(
    "/workflows",
    response_model=AutomationWorkflowDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_automation_workflow(
    workflow_data: AutomationWorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new N1MOX30 automation workflow."""

    service = AutomationService(db)

    try:
        workflow = service.create_workflow(
            user_id=current_user.id,
            command=workflow_data.command,
            platform=workflow_data.platform,
            topic=workflow_data.topic,
            project_id=workflow_data.project_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return build_workflow_detail(
        service,
        workflow,
    )


@router.get(
    "/workflows",
    response_model=list[AutomationWorkflowResponse],
)
def get_my_automation_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all automation workflows for the current user."""

    workflows = (
        db.query(AutomationWorkflow)
        .filter(
            AutomationWorkflow.user_id == current_user.id,
        )
        .order_by(
            AutomationWorkflow.created_at.desc()
        )
        .all()
    )

    return workflows


@router.get(
    "/workflows/{workflow_id}",
    response_model=AutomationWorkflowDetailResponse,
)
def get_automation_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return one workflow and all of its steps."""

    service = AutomationService(db)

    workflow = service.get_workflow(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation workflow not found.",
        )

    return build_workflow_detail(
        service,
        workflow,
    )


@router.patch(
    "/workflows/{workflow_id}/project",
    response_model=AutomationWorkflowDetailResponse,
)
def assign_workflow_to_project(
    workflow_id: str,
    project_data: AutomationWorkflowProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Assign a workflow to a project.

    This can also move a workflow from one project
    to another project.
    """

    service = AutomationService(db)

    try:
        workflow = service.assign_workflow_to_project(
            workflow_id=workflow_id,
            project_id=project_data.project_id,
            user_id=current_user.id,
        )

    except ValueError as error:
        message = str(error)

        if message == "Automation workflow not found.":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error

    return build_workflow_detail(
        service,
        workflow,
    )


@router.delete(
    "/workflows/{workflow_id}/project",
    response_model=AutomationWorkflowDetailResponse,
)
def remove_workflow_from_project(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a workflow from its current project."""

    service = AutomationService(db)

    try:
        workflow = service.remove_workflow_from_project(
            workflow_id=workflow_id,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return build_workflow_detail(
        service,
        workflow,
    )


@router.post(
    "/workflows/{workflow_id}/run",
    response_model=AutomationWorkflowActionResponse,
)
def run_automation_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute an automation workflow."""

    service = AutomationService(db)

    try:
        workflow = service.run_workflow(
            workflow_id=workflow_id,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return AutomationWorkflowActionResponse(
        message="Automation workflow execution completed.",
        workflow=build_workflow_detail(
            service,
            workflow,
        ),
    )


@router.post(
    "/workflows/{workflow_id}/retry/{stage}",
    response_model=AutomationWorkflowActionResponse,
)
def retry_automation_stage(
    workflow_id: str,
    stage: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retry a workflow stage."""

    try:
        workflow_stage = WorkflowStage(stage)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown workflow stage: {stage}",
        ) from error

    service = AutomationService(db)

    try:
        workflow = service.retry_step(
            workflow_id=workflow_id,
            user_id=current_user.id,
            stage=workflow_stage,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return AutomationWorkflowActionResponse(
        message=(
            f"Workflow stage '{stage}' has been reset "
            "and execution has resumed."
        ),
        workflow=build_workflow_detail(
            service,
            workflow,
        ),
    )