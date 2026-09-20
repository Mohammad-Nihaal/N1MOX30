from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsSnapshot
from app.models.connected_account import ConnectedAccount
from app.models.user import User


def get_creator_context(
    *,
    db: Session,
    current_user: User,
    platform: str,
) -> dict:
    """
    Build creator intelligence context for AI generation.

    Uses:
    - Connected creator account
    - Latest analytics snapshot
    - Previous analytics snapshot
    - Channel growth changes
    """

    normalized_platform = platform.lower().strip()

    # =================================================
    # CONNECTED ACCOUNT
    # =================================================

    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.platform == normalized_platform,
            ConnectedAccount.is_active.is_(True),
            ConnectedAccount.is_authorized.is_(True),
        )
        .first()
    )

    if not account:
        return {
            "has_connected_account": False,
            "platform": normalized_platform,
            "channel_name": None,
            "channel_id": None,
            "analytics": None,
        }

    # =================================================
    # ANALYTICS SNAPSHOTS
    # =================================================

    snapshots = (
        db.query(AnalyticsSnapshot)
        .filter(
            AnalyticsSnapshot.connected_account_id
            == account.id,
            AnalyticsSnapshot.platform
            == normalized_platform,
        )
        .order_by(
            AnalyticsSnapshot.recorded_at.desc()
        )
        .limit(2)
        .all()
    )

    latest_snapshot = (
        snapshots[0]
        if snapshots
        else None
    )

    previous_snapshot = (
        snapshots[1]
        if len(snapshots) > 1
        else None
    )

    analytics_context = None

    if latest_snapshot:

        views_change = 0
        followers_change = 0
        likes_change = 0
        comments_change = 0

        if previous_snapshot:

            views_change = (
                latest_snapshot.views
                - previous_snapshot.views
            )

            followers_change = (
                latest_snapshot.followers
                - previous_snapshot.followers
            )

            likes_change = (
                latest_snapshot.likes
                - previous_snapshot.likes
            )

            comments_change = (
                latest_snapshot.comments
                - previous_snapshot.comments
            )

        analytics_context = {
            "latest_views": latest_snapshot.views,
            "latest_followers": (
                latest_snapshot.followers
            ),
            "latest_likes": latest_snapshot.likes,
            "latest_comments": (
                latest_snapshot.comments
            ),
            "views_change": views_change,
            "followers_change": followers_change,
            "likes_change": likes_change,
            "comments_change": comments_change,
            "snapshots_available": len(
                snapshots
            ),
        }

    # =================================================
    # FINAL CREATOR CONTEXT
    # =================================================

    return {
        "has_connected_account": True,
        "platform": normalized_platform,
        "channel_name": account.account_name,
        "channel_id": (
            account.platform_account_id
        ),
        "analytics": analytics_context,
    }