from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.voice.assistant import (
    execute_voice_command,
    save_voice_command,
    execute_voice_action,
)


router = APIRouter(
    prefix="/platform/v10/voice",
    tags=["voice-assistant"],
)


class VoiceCommandRequest(BaseModel):
    user_id: int = Field(default=1, ge=1)
    text: str = Field(min_length=1, max_length=5000)
    workflow_state: dict = Field(default_factory=dict)


@router.get("/status")
def voice_status():
    return {
        "status": "available",
        "assistant": "N1MOX",
        "wake_phrase": "Hey N1MOX",
        "input": ["text", "speech-ready"],
        "version": "34-39",
    }


@router.post("/command")
def voice_command(payload: VoiceCommandRequest):
    result = execute_voice_command(
        user_id=payload.user_id,
        text=payload.text,
        workflow_state=payload.workflow_state,
    )

    result["artifact"] = save_voice_command(result)

    return result


@router.post("/understand")
def understand(payload: VoiceCommandRequest):
    result = execute_voice_command(
        user_id=payload.user_id,
        text=payload.text,
        workflow_state=payload.workflow_state,
    )

    return {
        "status": result["status"],
        "command": result["command"],
        "action": result["action"],
        "message": result["message"],
    }
@router.post("/execute")
def execute_voice(payload: VoiceCommandRequest):
    command_result = execute_voice_command(
        user_id=payload.user_id,
        text=payload.text,
        workflow_state=payload.workflow_state,
    )

    execution = execute_voice_action(
        user_id=payload.user_id,
        command_result=command_result,
    )

    command_result["execution"] = execution
    command_result["artifact"] = save_voice_command(command_result)

    return command_result