from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.creator_preferences import (
    CreatorPreferencesCreate,
    CreatorPreferencesResponse,
    CreatorPreferencesUpdate,
)
from app.services.creator_preferences.preference_service import (
    creator_preference_service,
)

router = APIRouter(
    prefix="/creator-preferences",
    tags=["Creator Preferences"],
)


@router.get(
    "",
    response_model=CreatorPreferencesResponse,
)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return creator_preference_service.get_or_create(
        db=db,
        user_id=str(current_user.id),
    )


@router.post(
    "",
    response_model=CreatorPreferencesResponse,
    status_code=201,
)
def create_preferences(
    data: CreatorPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return creator_preference_service.create(
            db=db,
            user_id=str(current_user.id),
            data=data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.patch(
    "",
    response_model=CreatorPreferencesResponse,
)
def update_preferences(
    data: CreatorPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = creator_preference_service.get_or_create(
        db=db,
        user_id=str(current_user.id),
    )

    return creator_preference_service.update(
        db=db,
        preferences=preferences,
        data=data,
    )


@router.get("/context")
def get_preferences_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "user_id": str(current_user.id),
        "preferences": creator_preference_service.get_context(
            db=db,
            user_id=str(current_user.id),
        ),
    }


@router.get("/health")
def creator_preferences_health():
    return {
        "service": "creator-preferences",
        "status": "ready",
    }
