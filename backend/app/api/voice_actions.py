from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.voice.actions.voice_action_service import VoiceActionService
from app.voice.understanding.voice_understanding_service import (
    VoiceUnderstandingService,
)

router = APIRouter(
    prefix="/voice/actions",
    tags=["Voice Actions"],
)


class VoiceActionRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class VoiceActionResponse(BaseModel):
    executed: bool = False
    action: str | None = None
    status: str = "not_executed"
    message: str
    workflow_id: str | None = None
    progress: int | float | None = None
    current_stage: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/execute",
    response_model=VoiceActionResponse,
)
def execute_voice_action(
    payload: VoiceActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    understanding = VoiceUnderstandingService().understand(
        payload.transcript,
        context=payload.context,
    )

    result = VoiceActionService(db).execute(
        user_id=str(current_user.id),
        intent=understanding,
    )

    return VoiceActionResponse(
        executed=bool(result.get("executed", False)),
        action=result.get("action") or understanding.get("intent"),
        status=(
            "completed"
            if result.get("executed")
            else "not_executed"
        ),
        message=str(
            result.get(
                "message",
                "No workflow action was executed.",
            )
        ),
        workflow_id=result.get("workflow_id"),
        progress=result.get("progress"),
        current_stage=result.get("current_stage"),
        data={
            key: value
            for key, value in result.items()
            if key
            not in {
                "executed",
                "action",
                "message",
                "workflow_id",
                "progress",
                "current_stage",
            }
        },
    )


@router.get("/health")
def voice_actions_health(
    current_user: User = Depends(get_current_user),
):
    return {
        "enabled": True,
        "layer": "voice_commands_to_actions",
        "workflow_integration": True,
    }
