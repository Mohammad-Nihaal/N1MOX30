from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsSnapshot
from app.models.connected_account import ConnectedAccount
from app.services.youtube_service import (
    get_youtube_channel_details,
    refresh_youtube_access_token,
)


def access_token_needs_refresh(
    token_expires_at: datetime | None,
) -> bool:
    """Return True when the OAuth access token needs refreshing."""

    if token_expires_at is None:
        return True

    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(
            tzinfo=timezone.utc
        )

    return token_expires_at <= datetime.now(timezone.utc)


def refresh_account_token_if_needed(
    connected_account: ConnectedAccount,
    db: Session,
) -> ConnectedAccount:
    """Refresh the YouTube access token when it has expired."""

    if not access_token_needs_refresh(
        connected_account.token_expires_at
    ):
        return connected_account

    refreshed_token = refresh_youtube_access_token(
        connected_account.refresh_token
    )

    connected_account.access_token = (
        refreshed_token["access_token"]
    )

    connected_account.token_expires_at = (
        refreshed_token["token_expires_at"]
    )

    db.commit()
    db.refresh(connected_account)

    return connected_account


def create_youtube_snapshot(
    connected_account: ConnectedAccount,
    db: Session,
) -> AnalyticsSnapshot:
    """Fetch current YouTube channel data and save a snapshot."""

    connected_account = refresh_account_token_if_needed(
        connected_account,
        db,
    )

    if not connected_account.access_token:
        raise ValueError(
            "YouTube access token is missing."
        )

    channel = get_youtube_channel_details(
        connected_account.access_token
    )

    snapshot = AnalyticsSnapshot(
        connected_account_id=connected_account.id,
        platform="youtube",
        views=int(channel.get("view_count") or 0),
        followers=int(channel.get("subscriber_count") or 0),
        likes=0,
        comments=0,
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot


def create_snapshots_for_all_youtube_accounts(
    db: Session,
) -> dict:
    """Create analytics snapshots for all active YouTube accounts."""

    accounts = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.platform == "youtube",
            ConnectedAccount.is_active.is_(True),
            ConnectedAccount.is_authorized.is_(True),
        )
        .all()
    )

    successful = 0
    failed = []

    for account in accounts:
        try:
            create_youtube_snapshot(
                account,
                db,
            )
            successful += 1

        except Exception as error:
            failed.append(
                {
                    "account_id": account.id,
                    "error": str(error),
                }
            )

    return {
        "total_accounts": len(accounts),
        "successful": successful,
        "failed": failed,
    }