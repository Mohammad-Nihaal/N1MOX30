from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.batch13.provider_execution import execute_with_fallback

router = APIRouter(
    prefix="/platform/v4/providers",
    tags=["Provider Execution"]
)

class ExecuteRequest(BaseModel):
    prompt: str
    provider: str | None = None

@router.post("/execute")
def execute(
    request: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = execute_with_fallback(
        db=db,
        user_id=str(current_user.id),
        prompt=request.prompt,
        requested=request.provider,
    )

    return {
        "success": result.success,
        "provider": result.provider,
        "content": result.content,
        "error": result.error,
    }

