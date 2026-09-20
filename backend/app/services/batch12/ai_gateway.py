
from dataclasses import dataclass
from typing import Any
from sqlalchemy.orm import Session

from app.services.batch11.provider_router import choose_provider


@dataclass
class AIGatewayDecision:
    allowed: bool
    provider: str
    reason: str
    estimated_units: int = 1


def authorize_ai_call(
    db: Session,
    user_id: int,
    requested_provider: str | None = None,
    estimated_units: int = 1,
) -> AIGatewayDecision:
    decision = choose_provider(
        db,
        user_id,
        requested=requested_provider,
    )

    provider = getattr(decision, "provider", None) or "demo"

    # Batch 11 quota service
    try:
        from app.services.platform_service import consume_ai_units
        result = consume_ai_units(
            db=db,
            user_id=user_id,
            units=max(1, estimated_units),
            provider=provider,
        )

        if result is False:
            return AIGatewayDecision(
                False, provider, "AI usage quota exceeded", estimated_units
            )
    except TypeError:
        try:
            result = consume_ai_units(
                db, user_id, max(1, estimated_units), provider
            )
            if result is False:
                return AIGatewayDecision(
                    False, provider, "AI usage quota exceeded", estimated_units
                )
        except Exception:
            pass
    except Exception:
        # Keep provider routing available if quota accounting is unavailable.
        pass

    return AIGatewayDecision(
        True,
        provider,
        "AI request authorized",
        max(1, estimated_units),
    )


def gateway_status() -> dict[str, Any]:
    return {
        "service": "N1MOX30 AI Gateway",
        "version": "batch12",
        "status": "ready",
        "provider_routing": True,
        "quota_layer": True,
    }


def audit_ai_generation(
    db,
    user_id,
    provider,
    units,
    content_type="unknown",
    status="authorized",
):
    """Create a lightweight AI generation audit record."""
    try:
        from app.models.ai_generation import AIGeneration

        record = AIGeneration(
            user_id=str(user_id),
            platform="N1MOX30",
            topic="Gateway authorization",
            content_type=content_type,
            tone="system",
            provider=provider,
            generation_status=status,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "recorded": True,
            "generation_id": record.id,
            "provider": provider,
            "units": units,
        }
    except Exception as exc:
        db.rollback()
        return {
            "recorded": False,
            "provider": provider,
            "units": units,
            "error": str(exc),
        }


def record_provider_usage(
    db,
    user_id,
    provider,
    units,
    operation="generation",
):
    """Record provider usage in the Batch 11 usage ledger."""
    try:
        from app.models.platform import AIUsageLedger

        row = AIUsageLedger(
            user_id=str(user_id),
            provider=provider,
            units=max(1, int(units)),
            operation=operation,
        )

        db.add(row)
        db.commit()

        return {
            "recorded": True,
            "provider": provider,
            "units": int(units),
            "operation": operation,
        }

    except Exception as exc:
        db.rollback()
        return {
            "recorded": False,
            "provider": provider,
            "units": int(units),
            "operation": operation,
            "error": str(exc),
        }
