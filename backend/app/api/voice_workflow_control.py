from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.voice.control.voice_workflow_control_service import (
    VoiceWorkflowControlService,
)


router = APIRouter(
    prefix="/voice/workflow-control",
    tags=["N1MOX Voice Workflow Control"],
)


def execute_control(
    action: str,
    workflow_id: str,
    current_user: User,
    db: Session,
):
    service = VoiceWorkflowControlService(db)

    try:
        if action == "status":
            return service.status(
                workflow_id=workflow_id,
                user_id=current_user.id,
            )

        if action == "pause":
            return service.pause(
                workflow_id=workflow_id,
                user_id=current_user.id,
            )

        if action == "resume":
            return service.resume(
                workflow_id=workflow_id,
                user_id=current_user.id,
            )

        if action == "cancel":
            return service.cancel(
                workflow_id=workflow_id,
                user_id=current_user.id,
            )

        if action == "retry":
            return service.retry(
                workflow_id=workflow_id,
                user_id=current_user.id,
            )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    raise HTTPException(
        status_code=400,
        detail="Unsupported workflow control action.",
    )


@router.get("/{workflow_id}/status")
def workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return execute_control(
        "status",
        workflow_id,
        current_user,
        db,
    )


@router.post("/{workflow_id}/pause")
def pause_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return execute_control(
        "pause",
        workflow_id,
        current_user,
        db,
    )


@router.post("/{workflow_id}/resume")
def resume_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return execute_control(
        "resume",
        workflow_id,
        current_user,
        db,
    )


@router.post("/{workflow_id}/cancel")
def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return execute_control(
        "cancel",
        workflow_id,
        current_user,
        db,
    )


@router.post("/{workflow_id}/retry")
def retry_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return execute_control(
        "retry",
        workflow_id,
        current_user,
        db,
    )


@router.post("/command")
def workflow_control_command(
    payload: dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    action = str(
        payload.get("action", "")
    ).strip().lower()

    workflow_id = str(
        payload.get("workflow_id", "")
    ).strip()

    if not action:
        raise HTTPException(
            status_code=400,
            detail="Control action is required.",
        )

    if not workflow_id:
        raise HTTPException(
            status_code=400,
            detail="Workflow ID is required.",
        )

    aliases = {
        "pause_workflow": "pause",
        "pause": "pause",
        "resume_workflow": "resume",
        "resume": "resume",
        "continue": "resume",
        "cancel_workflow": "cancel",
        "cancel": "cancel",
        "stop": "cancel",
        "retry_workflow": "retry",
        "retry": "retry",
        "rerun": "retry",
        "workflow_status": "status",
        "status": "status",
    }

    normalized_action = aliases.get(action)

    if normalized_action is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow action: {action}",
        )

    return execute_control(
        normalized_action,
        workflow_id,
        current_user,
        db,
    )


@router.get("/health")
def workflow_control_health():
    return {
        "service": "n1mox_voice_workflow_control",
        "status": "ready",
        "step": 34,
        "controls": [
            "status",
            "pause",
            "resume",
            "cancel",
            "retry",
        ],
    }
