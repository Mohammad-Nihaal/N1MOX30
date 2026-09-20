from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.models.user import User
from app.voice.response.voice_response_service import VoiceResponseService


router = APIRouter(
    prefix="/voice/response",
    tags=["Voice Natural Responses"],
)

service = VoiceResponseService()


class VoiceResponseRequest(BaseModel):
    intent: str = Field(..., min_length=1)
    action: str | None = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)


class VoiceResponseResult(BaseModel):
    success: bool
    text: str
    voice_ready: bool
    emotion: str
    speaking_style: str
    provider: str


@router.post(
    "/generate",
    response_model=VoiceResponseResult,
)
def generate_voice_response(
    payload: VoiceResponseRequest,
    current_user: User = Depends(get_current_user),
):
    result = service.generate_response(
        intent=payload.intent,
        action=payload.action,
        parameters=payload.parameters,
        result=payload.result,
    )

    return VoiceResponseResult(**result)


@router.get("/health")
def voice_response_health(
    current_user: User = Depends(get_current_user),
):
    return service.health()
