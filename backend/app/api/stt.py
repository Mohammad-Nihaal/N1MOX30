from fastapi import APIRouter, Depends, File, UploadFile
from app.api.dependencies import get_current_user
from app.models.user import User
from app.voice.stt.stt_service import STTService

import os
import tempfile


router = APIRouter(
    prefix="/voice/stt",
    tags=["Voice Speech-to-Text"],
)

service = STTService()


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    suffix = os.path.splitext(audio.filename or "")[1] or ".audio"

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = await audio.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        result = service.transcribe(temp_path)

        return {
            **result,
            "filename": audio.filename,
            "content_type": audio.content_type,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/health")
def stt_health(
    current_user: User = Depends(get_current_user),
):
    return service.health()
