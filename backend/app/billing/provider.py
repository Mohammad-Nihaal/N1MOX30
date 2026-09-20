from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckoutRequest:
    user_id: str
    plan_id: str
    currency: str = "USD"
    country: str | None = None


class BillingProvider:
    """Provider-neutral billing boundary.

    Implement Stripe, Paddle/MoR, or another approved provider behind this
    interface. Never trust prices, plan ids, currency, or payment status
    from the browser as authoritative values.
    """

    def create_checkout(self, request: CheckoutRequest) -> dict[str, Any]:
        raise NotImplementedError

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict[str, Any]:
        raise NotImplementedError