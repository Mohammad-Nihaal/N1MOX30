from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch15.ai_pipeline import run_ai_pipeline

router = APIRouter(
    prefix="/platform/v5/ai",
    tags=["Production AI Pipeline"],
)


class PipelineRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=50000)
    provider: str | None = None
    estimated_units: int = Field(default=1, ge=1, le=1000)
    content_type: str = "text"


@router.post("/generate")
def generate(
    request: PipelineRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = run_ai_pipeline(
        db=db,
        user_id=str(current_user.id),
        prompt=request.prompt,
        requested_provider=request.provider,
        estimated_units=request.estimated_units,
        content_type=request.content_type,
    )

    return {
        "success": result.success,
        "provider": result.provider,
        "content": result.content,
        "units": result.units,
        "fallback_used": result.fallback_used,
        "generation_id": result.generation_id,
        "usage_recorded": result.usage_recorded,
        "error": result.error,
    }

