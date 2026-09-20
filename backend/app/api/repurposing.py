from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/repurposing", tags=["Content Repurposing"])


class RepurposeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    script: str = Field(..., min_length=1)
    topic: str = ""


@router.post("/generate")
def generate_repurposed_content(
    payload: RepurposeRequest,
    current_user: User = Depends(get_current_user),
):
    source = payload.script.strip()
    first = source.split("\n")[0][:180]
    hook = payload.title.strip()
    return {
        "status": "generated",
        "source_title": payload.title,
        "variants": {
            "youtube_long_form": {
                "title": payload.title,
                "description": source[:2000],
                "format": "16:9",
            },
            "youtube_short": {
                "hook": hook,
                "script": f"{hook}\n\n{first}\n\nFollow N1MOX30 for more.",
                "format": "9:16",
            },
            "instagram_reel": {
                "caption": f"{hook}\n\n{first}\n\n#AI #Technology #Creators",
                "format": "9:16",
            },
            "tiktok": {
                "caption": f"{hook} — {first[:220]} #fyp #ai #technology",
                "format": "9:16",
            },
            "x_thread": [
                hook,
                first,
                "The full breakdown is ready. Turn this idea into a repeatable creator workflow with N1MOX30.",
            ],
        },
    }
