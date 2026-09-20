from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.models.batch11 import ProviderCredential


@dataclass
class ProviderDecision:
    provider: str
    source: str
    available: bool
    reason: str


SUPPORTED_PROVIDERS = (
    "openclaw",
    "openai",
    "gemini",
    "groq",
    "bedrock",
    "omniroute",
    "demo",
)


def _provider(row) -> str:
    return str(
        getattr(row, "provider", "")
        or getattr(row, "provider_name", "")
        or ""
    ).strip().lower()


def _active(row) -> bool:
    return bool(getattr(row, "is_active", True))


def available_user_providers(
    db: Session,
    user_id: str,
) -> list[str]:
    rows = (
        db.query(ProviderCredential)
        .filter(
            ProviderCredential.user_id == user_id,
        )
        .all()
    )

    result: list[str] = []

    for row in rows:
        provider = _provider(row)

        if provider and _active(row):
            if provider not in result:
                result.append(provider)

    return result


def choose_provider(
    db: Session,
    user_id: str,
    requested: Optional[str] = None,
    primary: Optional[str] = None,
    fallback: Optional[str] = None,
) -> ProviderDecision:
    available = available_user_providers(
        db,
        user_id,
    )

    candidates = []

    if requested:
        candidates.append(
            (requested.lower(), "user-request")
        )

    if primary:
        candidates.append(
            (primary.lower(), "user-primary")
        )

    if fallback:
        candidates.append(
            (fallback.lower(), "user-fallback")
        )

    candidates.extend(
        [
            ("openclaw", "platform"),
            ("omniroute", "platform"),
            ("groq", "platform"),
            ("openai", "platform"),
            ("gemini", "platform"),
            ("bedrock", "platform"),
            ("demo", "platform"),
        ]
    )

    seen: set[str] = set()

    for provider, source in candidates:
        if not provider or provider in seen:
            continue

        seen.add(provider)

        if provider not in SUPPORTED_PROVIDERS:
            continue

        if provider in available:
            return ProviderDecision(
                provider=provider,
                source="byok",
                available=True,
                reason="User provider credential is configured.",
            )

        if source == "platform":
            return ProviderDecision(
                provider=provider,
                source="platform",
                available=True,
                reason="Platform provider selected.",
            )

    return ProviderDecision(
        provider="demo",
        source="safe-fallback",
        available=True,
        reason="No configured provider was available.",
    )
