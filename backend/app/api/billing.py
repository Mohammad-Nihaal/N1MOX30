from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/billing", tags=["billing"])

PAYMENT_PROVIDER = os.getenv("N1MOX_PAYMENT_PROVIDER", "razorpay").lower()

PLANS: dict[str, dict[str, Any]] = {
    "creator": {
        "id": "creator",
        "name": "Creator",
        "amount_inr": int(os.getenv("RAZORPAY_CREATOR_AMOUNT_INR", "1599")),
        "videos": 27,
        "clips": 12,
        "messages": 999,
        "email": 999,
        "outlook": 999,
        "instagram": 60,
        "x": 60,
        "tiktok": 60,
        "youtube_min_minutes": 15,
        "youtube_target_minutes": 25,
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "amount_inr": int(os.getenv("RAZORPAY_PRO_AMOUNT_INR", "4099")),
        "videos": 72,
        "clips": 39,
        "messages": 1999,
        "email": 1999,
        "outlook": 1999,
        "instagram": 180,
        "x": 180,
        "tiktok": 180,
        "youtube_min_minutes": 15,
        "youtube_target_minutes": 25,
    },
    "studio": {
        "id": "studio",
        "name": "Studio",
        "amount_inr": int(os.getenv("RAZORPAY_STUDIO_AMOUNT_INR", "10999")),
        "videos": 111,
        "clips": 100,
        "messages": 4499,
        "email": 4499,
        "outlook": 4499,
        "instagram": 360,
        "x": 360,
        "tiktok": 360,
        "youtube_min_minutes": 15,
        "youtube_target_minutes": 25,
    },
}


class CheckoutRequest(BaseModel):
    plan_id: str = Field(min_length=1, max_length=50)
    user_id: str = Field(min_length=1, max_length=200)


class CheckoutResponse(BaseModel):
    provider: str
    order_id: str
    plan_id: str
    amount_inr: int
    amount_minor: int
    currency: str
    status: str
    test_mode: bool


def _db_path() -> Path:
    configured = os.getenv("DATABASE_PATH")

    if configured:
        return Path(configured)

    return Path(__file__).resolve().parents[2] / "n1mox.db"


def _payment_table() -> None:
    db = _db_path()

    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_order_id TEXT,
                provider_payment_id TEXT,
                amount_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        conn.commit()


def _record_payment(
    *,
    user_id: str,
    plan_id: str,
    provider: str,
    provider_order_id: str,
    amount_minor: int,
    status: str,
    provider_payment_id: str | None = None,
) -> str:
    _payment_table()

    payment_id = str(uuid.uuid4())
    now = time.time()

    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            """
            INSERT INTO payment_transactions (
                id,
                user_id,
                plan_id,
                provider,
                provider_order_id,
                provider_payment_id,
                amount_minor,
                currency,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payment_id,
                user_id,
                plan_id,
                provider,
                provider_order_id,
                provider_payment_id,
                amount_minor,
                "INR",
                status,
                now,
                now,
            ),
        )
        conn.commit()

    return payment_id


def _razorpay_configured() -> bool:
    return bool(
        os.getenv("RAZORPAY_KEY_ID")
        and os.getenv("RAZORPAY_KEY_SECRET")
    )


def _razorpay_live_enabled() -> bool:
    return (
        _razorpay_configured()
        and os.getenv("N1MOX_RAZORPAY_LIVE", "false").lower()
        == "true"
    )


def _create_razorpay_order(
    *,
    amount_minor: int,
    plan_id: str,
    user_id: str,
) -> dict[str, Any]:
    if not _razorpay_configured():
        raise HTTPException(
            status_code=503,
            detail="Razorpay is not configured. Add merchant credentials in the server environment.",
        )

    try:
        import requests
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Payment dependency 'requests' is unavailable.",
        ) from exc

    payload = {
        "amount": amount_minor,
        "currency": "INR",
        "receipt": f"nimox_{plan_id}_{uuid.uuid4().hex[:12]}",
        "notes": {
            "user_id": user_id,
            "plan_id": plan_id,
            "product": "N1MOX30",
        },
    }

    try:
        response = requests.post(
            "https://api.razorpay.com/v1/orders",
            auth=(
                os.environ["RAZORPAY_KEY_ID"],
                os.environ["RAZORPAY_KEY_SECRET"],
            ),
            json=payload,
            timeout=20,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to contact Razorpay.",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="Razorpay rejected the order request.",
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Razorpay returned an invalid response.",
        ) from exc

    return data


def verify_razorpay_signature(
    *,
    order_id: str,
    payment_id: str,
    signature: str,
    secret: str,
) -> bool:
    message = f"{order_id}|{payment_id}".encode("utf-8")

    expected = hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@router.get("/plans")
def plans() -> dict[str, Any]:
    normalized = []
    for plan in PLANS.values():
        normalized.append({
            **plan,
            "monthly_videos": plan["videos"],
            "monthly_clips": plan["clips"],
            "monthly_messages": plan["messages"],
            "monthly_email": plan["email"],
            "monthly_outlook": plan["outlook"],
        })
    return {
        "currency": "INR",
        "provider": PAYMENT_PROVIDER,
        "plans": normalized,
    }


@router.get("/providers")
def providers() -> dict[str, Any]:
    return {
        "active": PAYMENT_PROVIDER,
        "razorpay": {
            "available": True,
            "configured": _razorpay_configured(),
            "live_enabled": _razorpay_live_enabled(),
        },
        "stripe": {
            "available": False,
            "configured": bool(os.getenv("STRIPE_SECRET_KEY")),
            "live_enabled": False,
        },
    }


@router.get("/overview")
def overview() -> dict[str, Any]:
    _payment_table()

    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            """
            SELECT
                status,
                COUNT(*)
            FROM payment_transactions
            GROUP BY status
            """
        ).fetchall()

    return {
        "provider": PAYMENT_PROVIDER,
        "test_mode": not _razorpay_live_enabled(),
        "transactions": {
            status: count
            for status, count in rows
        },
    }


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(payload: CheckoutRequest) -> CheckoutResponse:
    plan = PLANS.get(payload.plan_id.lower())

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Unknown billing plan.",
        )

    amount_minor = plan["amount_inr"] * 100

    # Never silently create a real charge.
    if not _razorpay_live_enabled():
        order_id = f"order_test_{uuid.uuid4().hex}"

        _record_payment(
            user_id=payload.user_id,
            plan_id=plan["id"],
            provider="razorpay",
            provider_order_id=order_id,
            amount_minor=amount_minor,
            status="test_created",
        )

        return CheckoutResponse(
            provider="razorpay",
            order_id=order_id,
            plan_id=plan["id"],
            amount_inr=plan["amount_inr"],
            amount_minor=amount_minor,
            currency="INR",
            status="test_created",
            test_mode=True,
        )

    order = _create_razorpay_order(
        amount_minor=amount_minor,
        plan_id=plan["id"],
        user_id=payload.user_id,
    )

    order_id = str(order.get("id", ""))

    if not order_id:
        raise HTTPException(
            status_code=502,
            detail="Razorpay order ID was missing.",
        )

    _record_payment(
        user_id=payload.user_id,
        plan_id=plan["id"],
        provider="razorpay",
        provider_order_id=order_id,
        amount_minor=amount_minor,
        status="created",
    )

    return CheckoutResponse(
        provider="razorpay",
        order_id=order_id,
        plan_id=plan["id"],
        amount_inr=plan["amount_inr"],
        amount_minor=amount_minor,
        currency="INR",
        status="created",
        test_mode=False,
    )


@router.post("/verify")
async def verify_payment(
    request: Request,
) -> dict[str, Any]:
    body = await request.json()

    order_id = str(body.get("razorpay_order_id", ""))
    payment_id = str(body.get("razorpay_payment_id", ""))
    signature = str(body.get("razorpay_signature", ""))

    if not order_id or not payment_id or not signature:
        raise HTTPException(
            status_code=400,
            detail="Incomplete Razorpay verification payload.",
        )

    secret = os.getenv("RAZORPAY_KEY_SECRET", "")

    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Razorpay verification secret is not configured.",
        )

    if not verify_razorpay_signature(
        order_id=order_id,
        payment_id=payment_id,
        signature=signature,
        secret=secret,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay payment signature.",
        )

    _payment_table()

    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            """
            UPDATE payment_transactions
            SET
                provider_payment_id = ?,
                status = 'paid',
                updated_at = ?
            WHERE provider_order_id = ?
            """,
            (
                payment_id,
                time.time(),
                order_id,
            ),
        )
        conn.commit()

    return {
        "verified": True,
        "status": "paid",
        "provider": "razorpay",
        "order_id": order_id,
        "payment_id": payment_id,
    }


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
) -> dict[str, Any]:
    raw = await request.body()

    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Razorpay webhook secret is not configured.",
        )

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature.",
        )

    expected = hmac.new(
        secret.encode("utf-8"),
        raw,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected,
        x_razorpay_signature,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature.",
        )

    import json

    try:
        event = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook JSON.",
        ) from exc

    event_name = event.get("event", "unknown")

    entity = (
        event.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    order_id = entity.get("order_id")
    payment_id = entity.get("id")

    if order_id:
        _payment_table()

        status = (
            "paid"
            if event_name == "payment.captured"
            else event_name.replace(".", "_")
        )

        with sqlite3.connect(_db_path()) as conn:
            conn.execute(
                """
                UPDATE payment_transactions
                SET
                    provider_payment_id = COALESCE(?, provider_payment_id),
                    status = ?,
                    updated_at = ?
                WHERE provider_order_id = ?
                """,
                (
                    payment_id,
                    status,
                    time.time(),
                    order_id,
                ),
            )
            conn.commit()

    return {
        "received": True,
        "event": event_name,
        "order_id": order_id,
    }
