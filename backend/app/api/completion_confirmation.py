from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.completion.confirmation_service import CompletionConfirmationService
from app.core.database import get_db
from app.models.user import User
from app.schemas.completion_confirmation import (
    CompletionConfirmationRequest,
    CompletionConfirmationResponse,
)

router = APIRouter(
    prefix="/completion-confirmation",
    tags=["Completion Confirmation"],
)


@router.post(
    "",
    response_model=CompletionConfirmationResponse,
)
def confirm_completion(
    payload: CompletionConfirmationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CompletionConfirmationService(db)

    try:
        result = service.confirm(
            workflow_id=payload.workflow_id,
            user_id=current_user.id,
            force=payload.force,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return result


@router.get(
    "/{workflow_id}",
    response_model=CompletionConfirmationResponse,
)
def get_completion_confirmation(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CompletionConfirmationService(db)

    try:
        result = service.confirm(
            workflow_id=workflow_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return result