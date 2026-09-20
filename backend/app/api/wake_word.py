from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.models.user import User
from app.voice.wake_word.wake_word_service import WakeWordService


router = APIRouter(
    prefix="/voice/wake-word",
    tags=["Voice Wake Word"],
)

service = WakeWordService()


class WakeWordDetectRequest(BaseModel):
    text: str = Field(..., min_length=1)


class WakeWordDetectResponse(BaseModel):
    detected: bool
    wake_word: str | None = None
    command: str = ""
    confidence: float = 0.0


@router.post("/detect", response_model=WakeWordDetectResponse)
def detect_wake_word(
    payload: WakeWordDetectRequest,
    current_user: User = Depends(get_current_user),
):
    result = service.detect(payload.text)
    return WakeWordDetectResponse(**result)


@router.get("/config")
def wake_word_config(
    current_user: User = Depends(get_current_user),
):
    return service.get_configuration()
