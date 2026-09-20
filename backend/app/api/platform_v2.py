from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.services.batch11.billing_service import (
    activate_subscription,
    cancel_subscription,
    create_checkout_intent,
)
from app.services.batch11.communication_service import (
    create_notification,
    mark_notification_read,
)
from app.services.batch11.provider_router import (
    choose_provider,
)
from app.services.batch11.security_hardening import (
    validate_production_secrets,
)


router = APIRouter(
    prefix="/platform/v2",
    tags=["Platform Production"],
)


class ProviderRouteRequest(BaseModel):
    requested_provider: str | None = None
    primary_provider: str | None = None
    fallback_provider: str | None = None


class CheckoutRequest(BaseModel):
    plan_code: str
    currency: str = "INR"


class ActivationRequest(BaseModel):
    plan_code: str
    provider: str = "abstract"
    provider_subscription_id: str | None = None


class NotificationRequest(BaseModel):
    title: str
    message: str
    notification_type: str = Field(
        default="info",
        max_length=50,
    )


@router.get("/security/status")
def security_status():
    problems = validate_production_secrets(
        settings
    )

    return {
        "environment": settings.environment,
        "production_ready": (
            len(problems) == 0
            if settings.environment == "production"
            else False
        ),
        "checks": problems,
        "rate_limit": {
            "configured": True,
            "scope": "process",
        },
    }


@router.post("/providers/route")
def route_provider(
    payload: ProviderRouteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = choose_provider(
        db=db,
        user_id=current_user.id,
        requested=payload.requested_provider,
        primary=payload.primary_provider,
        fallback=payload.fallback_provider,
    )

    return {
        "provider": decision.provider,
        "source": decision.source,
        "available": decision.available,
        "reason": decision.reason,
    }


@router.post("/billing/checkout")
def billing_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = create_checkout_intent(
        db=db,
        user_id=current_user.id,
        plan_code=payload.plan_code,
        currency=payload.currency,
    )

    create_notification(
        db=db,
        user_id=current_user.id,
        title="Checkout created",
        message=(
            f"Checkout intent created for "
            f"{payload.plan_code}."
        ),
        notification_type="billing",
    )

    return {
        "transaction_id": transaction.id,
        "status": transaction.status,
        "plan_code": transaction.plan_code,
        "currency": transaction.currency,
        "provider": transaction.provider,
    }


@router.post("/billing/activate")
def billing_activate(
    payload: ActivationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = activate_subscription(
        db=db,
        user_id=current_user.id,
        plan_code=payload.plan_code,
        provider=payload.provider,
        provider_subscription_id=(
            payload.provider_subscription_id
        ),
    )

    create_notification(
        db=db,
        user_id=current_user.id,
        title="Subscription activated",
        message=(
            f"Your {payload.plan_code} subscription "
            f"is active."
        ),
        notification_type="billing",
    )

    return {
        "subscription_id": subscription.id,
        "plan_code": subscription.plan_code,
        "status": subscription.status,
        "expires_at": subscription.expires_at,
    }


@router.post("/billing/cancel")
def billing_cancel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = cancel_subscription(
        db=db,
        user_id=current_user.id,
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="No subscription found.",
        )

    create_notification(
        db=db,
        user_id=current_user.id,
        title="Subscription cancelled",
        message=(
            "Your subscription cancellation "
            "has been recorded."
        ),
        notification_type="billing",
    )

    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
    }


@router.get("/notifications")
def notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(100)
        .all()
    )

    return [
        {
            "id": row.id,
            "title": row.title,
            "message": row.message,
            "notification_type": row.notification_type,
            "is_read": row.is_read,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/notifications")
def create_user_notification(
    payload: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = create_notification(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
    )

    return {
        "id": notification.id,
        "status": "created",
    }


@router.post(
    "/notifications/{notification_id}/read"
)
def read_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = mark_notification_read(
        db=db,
        user_id=current_user.id,
        notification_id=notification_id,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    return {
        "status": "read",
        "notification_id": notification_id,
    }
