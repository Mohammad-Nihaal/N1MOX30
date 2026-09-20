from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.batch11 import (
    PaymentCustomer,
    PaymentTransaction,
    Subscription,
)


def ensure_billing_customer(
    db: Session,
    user_id: str,
) -> PaymentCustomer:

    customer = (
        db.query(PaymentCustomer)
        .filter(
            PaymentCustomer.user_id == user_id
        )
        .first()
    )

    if customer:
        return customer

    customer = PaymentCustomer(
        user_id=user_id,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def create_checkout_intent(
    db: Session,
    user_id: str,
    plan_code: str,
    currency: str = "INR",
) -> PaymentTransaction:

    customer = ensure_billing_customer(
        db,
        user_id,
    )

    transaction = PaymentTransaction(
        user_id=user_id,
        customer_id=customer.id,
        plan_code=plan_code,
        currency=currency.upper(),
        status="pending",
        provider="abstract",
        provider_transaction_id=None,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def activate_subscription(
    db: Session,
    user_id: str,
    plan_code: str,
    provider: str = "abstract",
    provider_subscription_id: Optional[str] = None,
) -> Subscription:

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .first()
    )

    now = datetime.utcnow()
    expires = now + timedelta(days=30)

    if subscription is None:
        subscription = Subscription(
            user_id=user_id,
            plan_code=plan_code,
            status="active",
            started_at=now,
            expires_at=expires,
            provider=provider,
            provider_subscription_id=provider_subscription_id,
        )

        db.add(subscription)

    else:
        subscription.plan_code = plan_code
        subscription.status = "active"
        subscription.started_at = now
        subscription.expires_at = expires
        subscription.provider = provider
        subscription.provider_subscription_id = (
            provider_subscription_id
        )

    db.commit()
    db.refresh(subscription)

    return subscription


def cancel_subscription(
    db: Session,
    user_id: str,
) -> Optional[Subscription]:

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .first()
    )

    if subscription is None:
        return None

    subscription.status = "cancelled"

    db.commit()
    db.refresh(subscription)

    return subscription
