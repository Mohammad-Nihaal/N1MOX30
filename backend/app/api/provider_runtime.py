from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch14.provider_runtime import execute_runtime_with_fallback

router = APIRouter(
    prefix="/platform/v4/runtime",
    tags=["Provider Runtime"],
)

class RuntimeRequest(BaseModel):
    prompt: str
    provider: str | None = None

@router.post("/execute")
def execute_runtime_route(
    request: RuntimeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = execute_runtime_with_fallback(
        db,
        str(current_user.id),
        request.prompt,
        request.provider,
    )

    return {
        "success": result.success,
        "provider": result.provider,
        "content": result.content,
        "fallback_used": result.fallback_used,
        "error": result.error,
    }

