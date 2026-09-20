from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.models.batch11 import Plan, ProviderCredential
from app.models.user import User
from app.services.batch11.platform_service import (
    check_entitlement,
    consume_ai_units,
    current_ai_usage,
    ensure_subscription,
    get_plan_for_user,
    save_provider_key,
    seed_plans,
)


router = APIRouter(
    prefix="/platform",
    tags=["Platform"],
)


class ProviderKeyRequest(BaseModel):
    provider: str = Field(
        min_length=2,
        max_length=50,
    )
    api_key: str = Field(
        min_length=8,
        max_length=4096,
    )
    label: str = Field(
        default="Default",
        min_length=1,
        max_length=100,
    )


class UsageRequest(BaseModel):
    units: int = Field(
        default=1,
        ge=1,
        le=1000,
    )
    provider: str = Field(
        default="auto",
        min_length=2,
        max_length=50,
    )
    operation: str = Field(
        default="ai_generation",
        min_length=2,
        max_length=100,
    )


@router.get("/plans")
def list_plans(
    db: Session = Depends(get_db),
):
    seed_plans(db)

    plans = (
        db.query(Plan)
        .filter(
            Plan.is_active.is_(True)
        )
        .order_by(
            Plan.price_minor.asc()
        )
        .all()
    )

    return [
        {
            "code": plan.code,
            "name": plan.name,
            "price_minor": plan.price_minor,
            "currency": plan.currency,
            "monthly_ai_units": plan.monthly_ai_units,
            "monthly_video_units": plan.monthly_video_units,
            "monthly_storage_mb": plan.monthly_storage_mb,
            "max_connected_accounts": plan.max_connected_accounts,
            "entitlements": plan.entitlements,
        }
        for plan in plans
    ]


@router.get("/subscription")
def subscription(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    sub = ensure_subscription(
        db,
        current_user.id,
    )

    plan = get_plan_for_user(
        db,
        current_user.id,
    )

    return {
        "subscription_id": sub.id,
        "status": sub.status,
        "provider": sub.provider,
        "period_start": sub.current_period_start,
        "period_end": sub.current_period_end,
        "plan": {
            "code": plan.code,
            "name": plan.name,
            "price_minor": plan.price_minor,
            "currency": plan.currency,
            "monthly_ai_units": plan.monthly_ai_units,
            "monthly_video_units": plan.monthly_video_units,
            "monthly_storage_mb": plan.monthly_storage_mb,
            "max_connected_accounts": plan.max_connected_accounts,
            "entitlements": plan.entitlements,
        },
    }


@router.get("/usage")
def usage(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    plan = get_plan_for_user(
        db,
        current_user.id,
    )

    used = current_ai_usage(
        db,
        current_user.id,
    )

    return {
        "plan": plan.code,
        "ai": {
            "used": used,
            "limit": plan.monthly_ai_units,
            "remaining": max(
                plan.monthly_ai_units - used,
                0,
            ),
        },
        "video": {
            "limit": plan.monthly_video_units,
        },
        "storage_mb": {
            "limit": plan.monthly_storage_mb,
        },
    }


@router.post("/usage/consume")
def consume_usage(
    payload: UsageRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    ledger = consume_ai_units(
        db,
        current_user.id,
        payload.units,
        payload.provider,
        payload.operation,
    )

    return {
        "status": "recorded",
        "usage_id": ledger.id,
        "units": ledger.units,
    }


@router.get("/entitlements/{feature}")
def entitlement(
    feature: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return {
        "feature": feature,
        "enabled": check_entitlement(
            db,
            current_user.id,
            feature,
        ),
    }


@router.post("/providers/key")
def store_provider_key(
    payload: ProviderKeyRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    if not check_entitlement(
        db,
        current_user.id,
        "byok",
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "BYOK is not available "
                "on your current plan."
            ),
        )

    credential = save_provider_key(
        db,
        current_user.id,
        payload.provider,
        payload.api_key,
        payload.label,
    )

    return {
        "id": credential.id,
        "provider": credential.provider,
        "label": credential.label,
        "active": credential.is_active,
        "message": "API key stored securely.",
    }


@router.get("/providers")
def providers(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    credentials = (
        db.query(ProviderCredential)
        .filter(
            ProviderCredential.user_id
            == current_user.id,
            ProviderCredential.is_active.is_(True),
        )
        .all()
    )

    return [
        {
            "id": credential.id,
            "provider": credential.provider,
            "label": credential.label,
            "active": credential.is_active,
            "last_validated_at": (
                credential.last_validated_at
            ),
        }
        for credential in credentials
    ]


@router.get("/payments/status")
def payment_status(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    sub = ensure_subscription(
        db,
        current_user.id,
    )

    return {
        "payment_system": (
            "provider-independent"
        ),
        "provider": sub.provider,
        "subscription_status": sub.status,
        "currency": settings.billing_currency
        if False
        else "INR",
        "checkout_ready": False,
        "webhook_ready": True,
    }
