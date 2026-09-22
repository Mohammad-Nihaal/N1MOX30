import hashlib
import hmac
import json
import os

from fastapi.testclient import TestClient

from app.main import app
from app.api.billing import verify_razorpay_signature


def test_billing_routes_are_registered():
    routes = {
        getattr(route, "path", "")
        for route in app.routes
    }

    assert "/billing/plans" in routes
    assert "/billing/providers" in routes
    assert "/billing/overview" in routes
    assert "/billing/checkout" in routes
    assert "/billing/verify" in routes
    assert "/billing/webhook" in routes


def test_billing_plans():
    client = TestClient(app)

    response = client.get("/billing/plans")

    assert response.status_code == 200

    body = response.json()

    assert body["currency"] == "INR"
    assert len(body["plans"]) == 3

    ids = {plan["id"] for plan in body["plans"]}

    assert ids == {"creator", "pro", "studio"}


def test_checkout_is_safe_in_test_mode(monkeypatch):
    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
    monkeypatch.setenv("N1MOX_RAZORPAY_LIVE", "false")

    client = TestClient(app)

    response = client.post(
        "/billing/checkout",
        json={
            "plan_id": "creator",
            "user_id": "payment-test-user",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["provider"] == "razorpay"
    assert body["test_mode"] is True
    assert body["status"] == "test_created"
    assert body["amount_minor"] == body["amount_inr"] * 100


def test_invalid_plan_is_rejected():
    client = TestClient(app)

    response = client.post(
        "/billing/checkout",
        json={
            "plan_id": "does-not-exist",
            "user_id": "payment-test-user",
        },
    )

    assert response.status_code == 404


def test_razorpay_signature_verification():
    secret = "test_webhook_secret"
    order_id = "order_test_123"
    payment_id = "pay_test_123"

    message = f"{order_id}|{payment_id}".encode()

    signature = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    assert verify_razorpay_signature(
        order_id=order_id,
        payment_id=payment_id,
        signature=signature,
        secret=secret,
    )

    assert not verify_razorpay_signature(
        order_id=order_id,
        payment_id=payment_id,
        signature="invalid",
        secret=secret,
    )


def test_provider_status_is_safe(monkeypatch):
    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
    monkeypatch.setenv("N1MOX_RAZORPAY_LIVE", "false")

    client = TestClient(app)

    response = client.get("/billing/providers")

    assert response.status_code == 200

    body = response.json()

    assert body["razorpay"]["available"] is True
    assert body["razorpay"]["configured"] is False
    assert body["razorpay"]["live_enabled"] is False
