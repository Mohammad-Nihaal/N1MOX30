from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.models.user import User
from app.voice.understanding.voice_understanding_service import (
    VoiceUnderstandingService,
)


router = APIRouter(
    prefix="/voice/understanding",
    tags=["Voice AI Understanding"],
)

service = VoiceUnderstandingService()


class VoiceUnderstandingRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)


class VoiceUnderstandingResponse(BaseModel):
    success: bool
    transcript: str
    intent: str
    action: str | None = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    confidence: float = 0.0


@router.post(
    "/understand",
    response_model=VoiceUnderstandingResponse,
)
def understand_voice_command(
    payload: VoiceUnderstandingRequest,
    current_user: User = Depends(get_current_user),
):
    result = service.understand(
        transcript=payload.transcript,
        context=payload.context,
    )

    return VoiceUnderstandingResponse(**result)


@router.get("/health")
def understanding_health(
    current_user: User = Depends(get_current_user),
):
    return service.health()
