from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.automation.workflow_types import WorkflowStage
from app.core.database import get_db
from app.models.user import User
from app.orchestration.central_workflow_engine import (
    CentralWorkflowEngine,
)
from app.schemas.central_workflow import (
    CentralWorkflowActionResponse,
    CentralWorkflowCreate,
    CentralWorkflowDetailResponse,
    CentralWorkflowResponse,
)


router = APIRouter(
    prefix="/central-workflow",
    tags=["Central Workflow"],
)


def _workflow_response(
    workflow,
) -> CentralWorkflowResponse:
    return CentralWorkflowResponse.model_validate(
        workflow,
    )


def _detail_response(
    detail: dict,
) -> CentralWorkflowDetailResponse:
    workflow = detail["workflow"]

    steps = [
        {
            "id": step.id,
            "workflow_id": step.workflow_id,
            "stage": step.stage,
            "step_order": step.step_order,
            "status": step.status,
            "attempts": step.attempts,
            "input_data": step.input_data,
            "output_data": step.output_data,
            "error_message": step.error_message,
            "started_at": step.started_at,
            "completed_at": step.completed_at,
        }
        for step in detail["steps"]
    ]

    return CentralWorkflowDetailResponse(
        id=workflow.id,
        user_id=workflow.user_id,
        command=workflow.command,
        platform=workflow.platform,
        topic=workflow.topic,
        status=workflow.status,
        current_stage=workflow.current_stage,
        progress=workflow.progress,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        steps=steps,
        context=detail["context"],
        policy=detail["policy"].as_dict(),
    )


# ----------------------------------------------------------------------
# Prepare workflow
# ----------------------------------------------------------------------


@router.post(
    "/prepare",
    response_model=CentralWorkflowDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def prepare_workflow(
    payload: CentralWorkflowCreate,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    """
    Create a workflow and prepare creator-aware execution
    context and policy.
    """

    engine = CentralWorkflowEngine(
        db=db,
    )

    detail = engine.prepare(
        user_id=current_user.id,
        command=payload.command,
        platform=payload.platform,
        topic=payload.topic,
    )

    return _detail_response(
        {
            "workflow": detail["workflow"],
            "steps": engine.get_steps(
                workflow_id=detail["workflow"].id,
            ),
            "context": detail["context"],
            "policy": detail["policy"],
        }
    )


# ----------------------------------------------------------------------
# Run workflow
# ----------------------------------------------------------------------


@router.post(
    "/{workflow_id}/run",
    response_model=CentralWorkflowDetailResponse,
)
def run_workflow(
    workflow_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    """
    Execute a centrally managed workflow.
    """

    engine = CentralWorkflowEngine(
        db=db,
    )

    try:
        engine.run(
            workflow_id=workflow_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    detail = engine.get_detail(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    return _detail_response(
        detail,
    )


# ----------------------------------------------------------------------
# Get workflow
# ----------------------------------------------------------------------


@router.get(
    "/{workflow_id}",
    response_model=CentralWorkflowDetailResponse,
)
def get_workflow(
    workflow_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    engine = CentralWorkflowEngine(
        db=db,
    )

    detail = engine.get_detail(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    return _detail_response(
        detail,
    )


# ----------------------------------------------------------------------
# Status
# ----------------------------------------------------------------------


@router.get(
    "/{workflow_id}/status",
)
def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    engine = CentralWorkflowEngine(
        db=db,
    )

    result = engine.status(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    return result


# ----------------------------------------------------------------------
# Retry
# ----------------------------------------------------------------------


@router.post(
    "/{workflow_id}/retry/{stage}",
    response_model=CentralWorkflowDetailResponse,
)
def retry_workflow_stage(
    workflow_id: str,
    stage: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    """
    Retry a failed workflow stage.
    """

    try:
        workflow_stage = WorkflowStage(
            stage,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown workflow stage: {stage}"
            ),
        ) from exc

    engine = CentralWorkflowEngine(
        db=db,
    )

    try:
        engine.retry(
            workflow_id=workflow_id,
            user_id=current_user.id,
            stage=workflow_stage,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    detail = engine.get_detail(
        workflow_id=workflow_id,
        user_id=current_user.id,
    )

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    return _detail_response(
        detail,
    )