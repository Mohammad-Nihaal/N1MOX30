from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.creator_profile import CreatorProfile
from app.services.creator_memory_service import (
    get_memory_context,
)


# =================================================
# CREATOR PROFILE CONTEXT
# =================================================


def get_creator_profile_context(
    *,
    db: Session,
    user_id: str,
) -> dict | None:
    """
    Get the creator's saved profile and convert it
    into compact context for the N1MOX30 AI Assistant.
    """

    profile = (
        db.query(CreatorProfile)
        .filter(
            CreatorProfile.user_id == user_id,
        )
        .first()
    )

    if not profile:
        return None

    return {
        "creator_name": profile.creator_name,
        "niche": profile.niche,
        "target_audience": profile.target_audience,
        "creator_goals": profile.creator_goals,
        "preferred_platforms": (
            profile.preferred_platforms
        ),
        "content_style": profile.content_style,
        "preferred_tone": profile.preferred_tone,
        "posting_preferences": (
            profile.posting_preferences
        ),
        "ai_preferences": profile.ai_preferences,
    }


# =================================================
# CONNECTED ACCOUNT CONTEXT
# =================================================


def get_connected_account_context(
    *,
    db: Session,
    user_id: str,
) -> list[dict]:
    """
    Get active connected creator accounts.
    """

    from app.models.connected_account import (
        ConnectedAccount,
    )

    accounts = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.is_active.is_(True),
        )
        .all()
    )

    return [
        {
            "platform": account.platform,
            "account_name": account.account_name,
            "platform_account_id": (
                account.platform_account_id
            ),
            "is_authorized": account.is_authorized,
        }
        for account in accounts
    ]


# =================================================
# ANALYTICS CONTEXT
# =================================================


def get_analytics_context(
    *,
    db: Session,
    user_id: str,
) -> list[dict]:
    """
    Get the latest analytics for the creator's
    connected accounts.
    """

    from app.models.analytics import (
        AnalyticsSnapshot,
    )
    from app.models.connected_account import (
        ConnectedAccount,
    )

    accounts = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.is_active.is_(True),
        )
        .all()
    )

    analytics_context = []

    for account in accounts:

        snapshot = (
            db.query(AnalyticsSnapshot)
            .filter(
                AnalyticsSnapshot.connected_account_id
                == account.id,
            )
            .order_by(
                AnalyticsSnapshot.recorded_at.desc(),
            )
            .first()
        )

        if snapshot:

            analytics_context.append(
                {
                    "platform": account.platform,
                    "account_name": (
                        account.account_name
                    ),
                    "views": snapshot.views,
                    "likes": snapshot.likes,
                    "comments": snapshot.comments,
                    "followers": snapshot.followers,
                    "recorded_at": (
                        snapshot.recorded_at.isoformat()
                    ),
                }
            )

    return analytics_context


# =================================================
# COMPLETE PERSONAL CONTEXT
# =================================================


def build_personal_ai_context(
    *,
    db: Session,
    user_id: str,
) -> dict:
    """
    Build the complete personalized context used by
    the N1MOX30 Personal Creator AI Assistant.

    Combines:
    - Creator Profile
    - Long-Term Memory
    - Connected Platforms
    - Latest Analytics
    """

    creator_profile = (
        get_creator_profile_context(
            db=db,
            user_id=user_id,
        )
    )

    memories = get_memory_context(
        db=db,
        user_id=user_id,
        limit=30,
    )

    connected_accounts = (
        get_connected_account_context(
            db=db,
            user_id=user_id,
        )
    )

    analytics = get_analytics_context(
        db=db,
        user_id=user_id,
    )

    return {
        "creator_profile": creator_profile,
        "memories": memories,
        "connected_accounts": (
            connected_accounts
        ),
        "analytics": analytics,
    }


# =================================================
# BUILD ASSISTANT SYSTEM INSTRUCTIONS
# =================================================


def build_assistant_instructions(
    *,
    personal_context: dict,
) -> str:
    """
    Convert personalized creator data into compact
    instructions for the N1MOX30 AI Assistant.
    """

    profile = personal_context.get(
        "creator_profile"
    )

    memories = personal_context.get(
        "memories",
        [],
    )

    accounts = personal_context.get(
        "connected_accounts",
        [],
    )

    analytics = personal_context.get(
        "analytics",
        [],
    )

    instructions = [
        "You are N1MOX30, a professional personal "
        "AI assistant for content creators.",
        "",
        "Your job is to help the creator make better "
        "content decisions, save time, understand "
        "performance, and manage their workflow.",
        "",
        "Use the creator's saved information whenever "
        "it is relevant.",
        "",
        "Do not invent analytics or account data.",
        "If information is unavailable, clearly say so.",
    ]

    if profile:

        instructions.extend(
            [
                "",
                "CREATOR PROFILE:",
            ]
        )

        for key, value in profile.items():

            if value:

                readable_key = (
                    key.replace(
                        "_",
                        " ",
                    ).title()
                )

                instructions.append(
                    f"- {readable_key}: {value}"
                )

    if memories:

        instructions.extend(
            [
                "",
                "LONG-TERM CREATOR MEMORY:",
            ]
        )

        for memory in memories:

            instructions.append(
                f"- {memory['key']}: "
                f"{memory['value']}"
            )

    if accounts:

        instructions.extend(
            [
                "",
                "CONNECTED PLATFORMS:",
            ]
        )

        for account in accounts:

            instructions.append(
                f"- {account['platform']}: "
                f"{account['account_name']}"
            )

    if analytics:

        instructions.extend(
            [
                "",
                "LATEST ANALYTICS:",
            ]
        )

        for item in analytics:

            instructions.append(
                f"- {item['platform']} "
                f"({item['account_name']}): "
                f"{item['views']} views, "
                f"{item['likes']} likes, "
                f"{item['comments']} comments, "
                f"{item['followers']} followers"
            )

    return "\n".join(
        instructions
    )