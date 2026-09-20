from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.analytics import AnalyticsSnapshot
from app.models.connected_account import ConnectedAccount
from app.models.user import User
from app.services.insights_service import (
    generate_youtube_insights,
)


router = APIRouter(
    prefix="/insights",
    tags=["AI Insights"],
)


def get_authorized_youtube_account(
    current_user: User,
    db: Session,
) -> ConnectedAccount:
    """
    Get the authenticated user's authorized
    YouTube account.
    """

    connected_account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id
            == current_user.id,
            ConnectedAccount.platform
            == "youtube",
            ConnectedAccount.is_active.is_(True),
            ConnectedAccount.is_authorized.is_(True),
        )
        .first()
    )

    if not connected_account:

        raise HTTPException(
            status_code=404,
            detail=(
                "No authorized YouTube account found."
            ),
        )

    return connected_account


@router.get("/youtube")
def get_youtube_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate complete YouTube growth intelligence.

    Includes analytics growth, trends, rule-based
    insights, recommendations, and AI analysis.
    """

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    snapshots = (
        db.query(AnalyticsSnapshot)
        .filter(
            AnalyticsSnapshot.connected_account_id
            == connected_account.id,
            AnalyticsSnapshot.platform
            == "youtube",
            AnalyticsSnapshot.content_id.is_(None),
        )
        .order_by(
            AnalyticsSnapshot.recorded_at.asc()
        )
        .all()
    )

    return generate_youtube_insights(
        snapshots
    )