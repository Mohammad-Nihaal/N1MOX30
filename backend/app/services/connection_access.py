from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.launch_access import has_lifetime_free_access
from app.models.batch11 import Subscription
from app.models.connected_account import ConnectedAccount
from app.models.user import User


PAID_PLANS = {"creator", "pro", "studio"}
OWNER_CONNECTION_LIMIT = 2


def is_owner(user: User) -> bool:
    owner_email = (
        get_settings().n1mox_owner_email or ""
    ).strip().lower()

    current_email = (
        getattr(user, "email", "") or ""
    ).strip().lower()

    return has_lifetime_free_access(current_email) or (bool(owner_email) and current_email == owner_email)


def connection_access(
    db: Session,
    user: User,
) -> dict:
    count = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == user.id,
            ConnectedAccount.is_active.is_(True),
        )
        .count()
    )

    if is_owner(user):
        return {
            "allowed": count < OWNER_CONNECTION_LIMIT,
            "is_owner": True,
            "plan": "studio",
            "connected_count": count,
            "connection_limit": OWNER_CONNECTION_LIMIT,
            "free_owner_slots": OWNER_CONNECTION_LIMIT,
            "reason": (
                "Owner receives two free connected-account slots."
                if count < OWNER_CONNECTION_LIMIT
                else "Owner connection allowance is full."
            ),
        }

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
        )
        .first()
    )

    plan = (
        str(subscription.plan_code).lower()
        if subscription
        else ""
    )

    active = bool(
        subscription
        and subscription.status in {"active", "trialing"}
        and plan in PAID_PLANS
    )

    return {
        "allowed": active,
        "is_owner": False,
        "plan": plan or "free",
        "connected_count": count,
        "connection_limit": None,
        "free_owner_slots": 0,
        "reason": (
            "Active paid plan."
            if active
            else "An active Creator, Pro or Studio subscription is required."
        ),
    }


def require_connection_access(
    db: Session,
    user: User,
) -> dict:
    access = connection_access(db, user)

    if not access["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=access["reason"],
        )

    return access
