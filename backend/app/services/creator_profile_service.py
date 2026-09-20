from sqlalchemy.orm import Session

from app.models.creator_profile import CreatorProfile


# =================================================
# GET CREATOR PROFILE
# =================================================


def get_creator_profile(
    *,
    db: Session,
    user_id: str,
) -> CreatorProfile | None:
    """
    Get the creator profile belonging to a user.
    """

    return (
        db.query(CreatorProfile)
        .filter(
            CreatorProfile.user_id == user_id
        )
        .first()
    )


# =================================================
# CREATE CREATOR PROFILE
# =================================================


def create_creator_profile(
    *,
    db: Session,
    user_id: str,
    creator_name: str,
    niche: str | None = None,
    target_audience: str | None = None,
    creator_goals: str | None = None,
    preferred_platforms: str | None = None,
    content_style: str | None = None,
    preferred_tone: str | None = None,
    posting_preferences: str | None = None,
    ai_preferences: str | None = None,
) -> CreatorProfile:
    """
    Create a new creator profile for a user.
    """

    profile = CreatorProfile(
        user_id=user_id,
        creator_name=creator_name,
        niche=niche,
        target_audience=target_audience,
        creator_goals=creator_goals,
        preferred_platforms=preferred_platforms,
        content_style=content_style,
        preferred_tone=preferred_tone,
        posting_preferences=posting_preferences,
        ai_preferences=ai_preferences,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


# =================================================
# UPDATE CREATOR PROFILE
# =================================================


def update_creator_profile(
    *,
    db: Session,
    profile: CreatorProfile,
    update_data: dict,
) -> CreatorProfile:
    """
    Update only the fields provided by the user.
    """

    for field, value in update_data.items():
        setattr(
            profile,
            field,
            value,
        )

    db.commit()
    db.refresh(profile)

    return profile


# =================================================
# CREATE OR UPDATE CREATOR PROFILE
# =================================================


def create_or_update_creator_profile(
    *,
    db: Session,
    user_id: str,
    profile_data: dict,
) -> CreatorProfile:
    """
    Create profile if it does not exist.
    Otherwise update the existing profile.
    """

    profile = get_creator_profile(
        db=db,
        user_id=user_id,
    )

    if profile:

        return update_creator_profile(
            db=db,
            profile=profile,
            update_data=profile_data,
        )

    return create_creator_profile(
        db=db,
        user_id=user_id,
        **profile_data,
    )