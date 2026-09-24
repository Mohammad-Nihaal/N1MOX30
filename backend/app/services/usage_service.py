from __future__ import annotations

from calendar import monthrange
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.billing.plans import PLANS
from app.models.batch11 import Plan as BillingPlan
from app.models.batch11 import Subscription
from app.models.usage import UsageLedger


METRICS = ("youtube", "clips", "messages", "email", "outlook", "instagram", "x", "tiktok")
UNLIMITED = None


def _calendar_period(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    last_day = monthrange(now.year, now.month)[1]
    end = datetime(now.year, now.month, last_day) + timedelta(days=1)
    return start, end


def _plan_code(db: Session, user_id: str) -> str:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )
    if not subscription or subscription.status not in {"active", "trialing"}:
        return "creator"

    plan = db.query(BillingPlan).filter(BillingPlan.id == subscription.plan_id).first()
    if plan and plan.code in PLANS:
        return plan.code

    return "creator"


def _period(db: Session, user_id: str) -> tuple[datetime, datetime]:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )
    if (
        subscription
        and subscription.status in {"active", "trialing"}
        and subscription.current_period_start
        and subscription.current_period_end
    ):
        return subscription.current_period_start, subscription.current_period_end
    return _calendar_period()


def _limit(plan_code: str, metric: str) -> int | None:
    plan = PLANS.get(plan_code, PLANS["creator"])
    return {
        "youtube": plan.monthly_videos,
        "clips": plan.monthly_clips,
        "messages": plan.monthly_messages,
        "email": plan.monthly_email,
        "outlook": plan.monthly_outlook,
        "instagram": plan.monthly_instagram,
        "x": plan.monthly_x,
        "tiktok": plan.monthly_tiktok,
    }[metric]


def get_usage(db: Session, user_id: str) -> dict[str, Any]:
    plan_code = _plan_code(db, user_id)
    period_start, period_end = _period(db, user_id)

    rows = (
        db.query(UsageLedger)
        .filter(
            UsageLedger.user_id == user_id,
            UsageLedger.period_start == period_start,
        )
        .all()
    )
    by_metric = {row.metric: row.used for row in rows}

    metrics = {}
    for metric in METRICS:
        limit = _limit(plan_code, metric)
        used = int(by_metric.get(metric, 0))
        metrics[metric] = {
            "used": used,
            "limit": limit,
            "remaining": None if limit is None else max(0, limit - used),
            "unlimited": limit is None,
        }

    return {
        "plan": plan_code,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "metrics": metrics,
    }



def assert_available(db: Session, user_id: str, metric: str, units: int = 1) -> None:
    metric = metric.strip().lower()
    if metric not in METRICS:
        raise ValueError(f"Unsupported usage metric: {metric}")
    if units < 1:
        raise ValueError("units must be >= 1")
    plan_code = _plan_code(db, user_id)
    limit = _limit(plan_code, metric)
    if limit is None:
        return
    period_start, period_end = _period(db, user_id)
    row = (
        db.query(UsageLedger)
        .filter(
            UsageLedger.user_id == user_id,
            UsageLedger.metric == metric,
            UsageLedger.period_start == period_start,
        )
        .first()
    )
    used = int(row.used) if row else 0
    if used + units > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "MONTHLY_LIMIT_REACHED",
                "metric": metric,
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
                "period_end": period_end.isoformat(),
                "message": (
                    f"You have reached your monthly {metric} limit. "
                    f"Your allowance resets on {period_end.date().isoformat()}."
                ),
            },
        )

def reserve_usage(
    db: Session,
    user_id: str,
    metric: str,
    units: int = 1,
) -> dict[str, Any]:
    metric = metric.strip().lower()
    if metric not in METRICS:
        raise ValueError(f"Unsupported usage metric: {metric}")
    if units < 1:
        raise ValueError("units must be >= 1")

    plan_code = _plan_code(db, user_id)
    limit = _limit(plan_code, metric)
    period_start, period_end = _period(db, user_id)

    row = (
        db.query(UsageLedger)
        .filter(
            UsageLedger.user_id == user_id,
            UsageLedger.metric == metric,
            UsageLedger.period_start == period_start,
        )
        .first()
    )

    used = int(row.used) if row else 0

    if limit is not None and used + units > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "MONTHLY_LIMIT_REACHED",
                "metric": metric,
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
                "period_end": period_end.isoformat(),
                "message": (
                    f"You have reached your monthly {metric} limit. "
                    f"Your allowance resets on {period_end.date().isoformat()}."
                ),
            },
        )

    if row is None:
        row = UsageLedger(
            user_id=user_id,
            metric=metric,
            period_start=period_start,
            used=units,
        )
        db.add(row)
    else:
        row.used = used + units

    db.commit()
    db.refresh(row)

    return {
        "metric": metric,
        "used": row.used,
        "limit": limit,
        "remaining": None if limit is None else max(0, limit - row.used),
        "period_end": period_end.isoformat(),
    }
