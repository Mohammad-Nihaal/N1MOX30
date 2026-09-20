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
from app.schemas.creator_profile import (
    CreatorProfileCreate,
    CreatorProfileResponse,
    CreatorProfileUpdate,
)
from app.services.creator_profile_service import (
    create_or_update_creator_profile,
    get_creator_profile,
    update_creator_profile,
)


# =================================================
# ROUTER
# =================================================


router = APIRouter(
    prefix="/creator-profile",
    tags=["Creator Profile"],
)


# =================================================
# GET MY CREATOR PROFILE
# =================================================


@router.get(
    "/me",
    response_model=CreatorProfileResponse,
)
def get_my_creator_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the authenticated user's creator profile.
    """

    profile = get_creator_profile(
        db=db,
        user_id=current_user.id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found.",
        )

    return profile


# =================================================
# CREATE CREATOR PROFILE
# =================================================


@router.post(
    "",
    response_model=CreatorProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_creator_profile(
    profile_data: CreatorProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create the authenticated user's creator profile.
    """

    existing_profile = get_creator_profile(
        db=db,
        user_id=current_user.id,
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Creator profile already exists. "
                "Use PUT to update it."
            ),
        )

    profile = create_or_update_creator_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_data.model_dump(),
    )

    return profile


# =================================================
# UPDATE CREATOR PROFILE
# =================================================


@router.put(
    "/me",
    response_model=CreatorProfileResponse,
)
def update_my_creator_profile(
    profile_data: CreatorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated user's creator profile.
    """

    profile = get_creator_profile(
        db=db,
        user_id=current_user.id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Creator profile not found. "
                "Create it first."
            ),
        )

    update_data = profile_data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        return profile

    profile = update_creator_profile(
        db=db,
        profile=profile,
        update_data=update_data,
    )

    return profile