import base64
import hashlib
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.batch11 import (
    AIUsageLedger,
    Plan,
    ProviderCredential,
    Subscription,
)
from app.models.notification import Notification


PLANS = {
    "free": {
        "name": "Free",
        "price_minor": 0,
        "monthly_ai_units": 100,
        "monthly_video_units": 5,
        "monthly_storage_mb": 1024,
        "max_connected_accounts": 2,
        "entitlements": {
            "creator_os": True,
            "ai_studio": True,
            "automation": True,
            "analytics": True,
            "youtube": True,
            "byok": False,
            "advanced_automation": False,
            "priority_generation": False,
        },
    },
    "creator": {
        "name": "Creator",
        "price_minor": 99900,
        "monthly_ai_units": 1000,
        "monthly_video_units": 30,
        "monthly_storage_mb": 10240,
        "max_connected_accounts": 5,
        "entitlements": {
            "creator_os": True,
            "ai_studio": True,
            "automation": True,
            "analytics": True,
            "youtube": True,
            "byok": True,
            "advanced_automation": True,
            "priority_generation": False,
        },
    },
    "pro": {
        "name": "Pro",
        "price_minor": 249900,
        "monthly_ai_units": 5000,
        "monthly_video_units": 100,
        "monthly_storage_mb": 51200,
        "max_connected_accounts": 15,
        "entitlements": {
            "creator_os": True,
            "ai_studio": True,
            "automation": True,
            "analytics": True,
            "youtube": True,
            "byok": True,
            "advanced_automation": True,
            "priority_generation": True,
        },
    },
    "business": {
        "name": "Business / Studio",
        "price_minor": 999900,
        "monthly_ai_units": 25000,
        "monthly_video_units": 500,
        "monthly_storage_mb": 204800,
        "max_connected_accounts": 100,
        "entitlements": {
            "creator_os": True,
            "ai_studio": True,
            "automation": True,
            "analytics": True,
            "youtube": True,
            "byok": True,
            "advanced_automation": True,
            "priority_generation": True,
            "team_workspace": True,
        },
    },
}


def _fernet() -> Fernet:
    if settings.encryption_key:
        key = settings.encryption_key.encode()
    else:
        digest = hashlib.sha256(
            settings.secret_key.encode()
        ).digest()
        key = base64.urlsafe_b64encode(digest)

    return Fernet(key)


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(
        value.encode()
    ).decode()


def decrypt_secret(value: str) -> str:
    return _fernet().decrypt(
        value.encode()
    ).decode()


def seed_plans(db: Session) -> None:
    changed = False

    for code, definition in PLANS.items():
        plan = (
            db.query(Plan)
            .filter(Plan.code == code)
            .first()
        )

        if plan:
            continue

        db.add(
            Plan(
                code=code,
                name=definition["name"],
                price_minor=definition["price_minor"],
                currency=settings.billing_currency,
                monthly_ai_units=definition["monthly_ai_units"],
                monthly_video_units=definition["monthly_video_units"],
                monthly_storage_mb=definition["monthly_storage_mb"],
                max_connected_accounts=definition["max_connected_accounts"],
                entitlements=definition["entitlements"],
            )
        )
        changed = True

    if changed:
        db.commit()


def ensure_subscription(
    db: Session,
    user_id: str,
) -> Subscription:
    seed_plans(db)

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .first()
    )

    if subscription:
        return subscription

    plan = (
        db.query(Plan)
        .filter(
            Plan.code == settings.default_plan
        )
        .first()
    )

    if not plan:
        raise RuntimeError(
            "Default plan does not exist."
        )

    now = datetime.utcnow()

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status="active",
        provider="internal",
        current_period_start=now,
        current_period_end=(
            now + timedelta(days=30)
        ),
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_plan_for_user(
    db: Session,
    user_id: str,
) -> Plan:
    subscription = ensure_subscription(
        db,
        user_id,
    )

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:
        raise RuntimeError(
            "Subscription plan not found."
        )

    return plan


def check_entitlement(
    db: Session,
    user_id: str,
    feature: str,
) -> bool:
    plan = get_plan_for_user(
        db,
        user_id,
    )

    return bool(
        (plan.entitlements or {}).get(
            feature,
            False,
        )
    )


def current_ai_usage(
    db: Session,
    user_id: str,
) -> int:
    start = datetime.utcnow().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = (
        db.query(
            func.coalesce(
                func.sum(
                    AIUsageLedger.units
                ),
                0,
            )
        )
        .filter(
            AIUsageLedger.user_id == user_id,
            AIUsageLedger.created_at >= start,
        )
        .scalar()
    )

    return int(result or 0)


def consume_ai_units(
    db: Session,
    user_id: str,
    units: int,
    provider: str,
    operation: str,
) -> AIUsageLedger:
    plan = get_plan_for_user(
        db,
        user_id,
    )

    used = current_ai_usage(
        db,
        user_id,
    )

    if used + units > plan.monthly_ai_units:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "AI_QUOTA_EXCEEDED",
                "used": used,
                "requested": units,
                "limit": plan.monthly_ai_units,
                "plan": plan.code,
            },
        )

    ledger = AIUsageLedger(
        user_id=user_id,
        provider=provider,
        operation=operation,
        units=units,
    )

    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return ledger


def save_provider_key(
    db: Session,
    user_id: str,
    provider: str,
    api_key: str,
    label: str = "Default",
) -> ProviderCredential:
    provider = provider.strip().lower()

    existing = (
        db.query(ProviderCredential)
        .filter(
            ProviderCredential.user_id == user_id,
            ProviderCredential.provider == provider,
            ProviderCredential.is_active.is_(True),
        )
        .first()
    )

    encrypted = encrypt_secret(
        api_key.strip()
    )

    if existing:
        existing.encrypted_api_key = encrypted
        existing.label = label
        existing.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing)

        return existing

    credential = ProviderCredential(
        user_id=user_id,
        provider=provider,
        encrypted_api_key=encrypted,
        label=label,
    )

    db.add(credential)
    db.commit()
    db.refresh(credential)

    return credential


def get_provider_key(
    db: Session,
    user_id: str,
    provider: str,
) -> str | None:
    credential = (
        db.query(ProviderCredential)
        .filter(
            ProviderCredential.user_id == user_id,
            ProviderCredential.provider == provider.lower(),
            ProviderCredential.is_active.is_(True),
        )
        .first()
    )

    if not credential:
        return None

    return decrypt_secret(
        credential.encrypted_api_key
    )


def notify(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
