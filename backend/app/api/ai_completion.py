from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai_completion import (
    AICompletionCreate,
    AICompletionReject,
    AICompletionResponse,
)
from app.services.ai_completion_service import (
    AICompletionService,
)


router = APIRouter(
    prefix="/ai-completions",
    tags=["AI Completions"],
)


@router.post(
    "",
    response_model=AICompletionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ai_completion(
    completion_data: AICompletionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new AI completion awaiting user confirmation.
    """

    service = AICompletionService(db)

    completion = service.create_completion(
        user_id=current_user.id,
        generation_id=completion_data.generation_id,
        workflow_id=completion_data.workflow_id,
        project_id=completion_data.project_id,
        content_type=completion_data.content_type,
        title=completion_data.title,
        content=completion_data.content,
    )

    return completion


@router.get(
    "",
    response_model=list[AICompletionResponse],
)
def get_ai_completions(
    completion_status: str | None = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return AI completions belonging to the current user.
    """

    service = AICompletionService(db)

    return service.get_completions(
        user_id=current_user.id,
        status=completion_status,
        limit=limit,
    )


@router.get(
    "/generation/{generation_id}",
    response_model=AICompletionResponse,
)
def get_completion_by_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the AI completion connected
    to a specific AI generation.
    """

    service = AICompletionService(db)

    completion = (
        service.get_completion_by_generation(
            generation_id=generation_id,
            user_id=current_user.id,
        )
    )

    if completion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "AI completion for this generation "
                "was not found."
            ),
        )

    return completion


@router.get(
    "/{completion_id}",
    response_model=AICompletionResponse,
)
def get_ai_completion(
    completion_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return one AI completion.
    """

    service = AICompletionService(db)

    completion = service.get_completion(
        completion_id=completion_id,
        user_id=current_user.id,
    )

    if completion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI completion not found.",
        )

    return completion


@router.post(
    "/{completion_id}/approve",
    response_model=AICompletionResponse,
)
def approve_ai_completion(
    completion_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve an AI completion.
    """

    service = AICompletionService(db)

    try:
        return service.approve_completion(
            completion_id=completion_id,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/{completion_id}/reject",
    response_model=AICompletionResponse,
)
def reject_ai_completion(
    completion_id: str,
    rejection_data: AICompletionReject,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reject an AI completion.
    """

    service = AICompletionService(db)

    try:
        return service.reject_completion(
            completion_id=completion_id,
            user_id=current_user.id,
            rejection_reason=(
                rejection_data.rejection_reason
            ),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error