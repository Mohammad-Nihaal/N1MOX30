from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.voice.voice_gateway import VoiceGateway


router = APIRouter(
    prefix="/voice",
    tags=["N1MOX Voice"],
)


@router.post("/command")
def voice_command(
    payload: dict[str, Any],
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    transcript = str(
        payload.get("transcript", "")
    ).strip()

    if not transcript:
        return {
            "status": "error",
            "message": "Transcript is required.",
        }

    gateway = VoiceGateway(db)

    return gateway.process_text(
        user=current_user,
        transcript=transcript,
        context=payload.get(
            "context",
            {},
        ),
    )


@router.post("/transcript")
def process_transcript(
    payload: dict[str, Any],
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    transcript = str(
        payload.get(
            "transcript",
            "",
        )
    ).strip()

    if not transcript:
        return {
            "status": "error",
            "message": "Transcript is required.",
        }

    gateway = VoiceGateway(db)

    return gateway.process_text(
        user=current_user,
        transcript=transcript,
        context=payload.get(
            "context",
            {},
        ),
    )


@router.get("/health")
def voice_health():
    return {
        "service": "n1mox_voice_gateway",
        "status": "ready",
        "steps": [
            29,
            30,
            31,
            32,
            33,
        ],
    }
