from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Session, declarative_base

from app.api.dependencies import get_current_user
from app.core.database import engine, get_db
from app.models.user import User


BYOKBase = declarative_base()


router = APIRouter(
    prefix="/byok",
    tags=["BYOK"],
)


class BYOKCredential(BYOKBase):
    __tablename__ = "byok_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    provider = Column(String(64), nullable=False, index=True)
    encrypted_key = Column(Text, nullable=False)
    key_hint = Column(String(16), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider",
            name="uq_byok_user_provider",
        ),
    )


BYOKBase.metadata.create_all(bind=engine)


SUPPORTED_PROVIDERS = {
    "openai",
    "anthropic",
    "gemini",
    "groq",
    "openrouter",
    "xai",
    "elevenlabs",
}


class BYOKSaveRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=64)
    api_key: str = Field(min_length=8, max_length=4096)


class BYOKProviderResponse(BaseModel):
    provider: str
    configured: bool
    key_hint: Optional[str] = None


def _secret_material() -> bytes:
    secret = (
        os.getenv("N1MOX_BYOK_ENCRYPTION_KEY")
        or os.getenv("SECRET_KEY")
        or "N1MOX30-development-secret-change-before-production"
    )

    return hashlib.sha256(secret.encode("utf-8")).digest()


def _keystream(length: int) -> bytes:
    material = _secret_material()
    output = bytearray()

    counter = 0

    while len(output) < length:
        output.extend(
            hmac.new(
                material,
                counter.to_bytes(8, "big"),
                hashlib.sha256,
            ).digest()
        )
        counter += 1

    return bytes(output[:length])


def _encrypt(value: str) -> str:
    raw = value.encode("utf-8")
    stream = _keystream(len(raw))
    encrypted = bytes(a ^ b for a, b in zip(raw, stream))
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def _decrypt(value: str) -> str:
    encrypted = base64.urlsafe_b64decode(value.encode("ascii"))
    stream = _keystream(len(encrypted))
    raw = bytes(a ^ b for a, b in zip(encrypted, stream))
    return raw.decode("utf-8")


def _normalize_provider(provider: str) -> str:
    value = provider.strip().lower()

    aliases = {
        "google": "gemini",
        "google-gemini": "gemini",
        "google_gemini": "gemini",
        "open-router": "openrouter",
        "eleven-labs": "elevenlabs",
    }

    return aliases.get(value, value)


def _hint(api_key: str) -> str:
    if len(api_key) <= 8:
        return "••••••••"

    return f"{api_key[:4]}…{api_key[-4:]}"


@router.get(
    "/providers",
    response_model=list[BYOKProviderResponse],
)
def get_byok_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = str(current_user.id)

    configured = {
        row.provider: row
        for row in db.query(BYOKCredential)
        .filter(BYOKCredential.user_id == user_id)
        .all()
    }

    return [
        BYOKProviderResponse(
            provider=provider,
            configured=provider in configured,
            key_hint=(
                configured[provider].key_hint
                if provider in configured
                else None
            ),
        )
        for provider in sorted(SUPPORTED_PROVIDERS)
    ]


@router.put(
    "/credentials",
    response_model=BYOKProviderResponse,
)
def save_byok_credential(
    payload: BYOKSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = _normalize_provider(payload.provider)

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported BYOK provider: {provider}",
        )

    api_key = payload.api_key.strip()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key cannot be empty.",
        )

    user_id = str(current_user.id)

    credential = (
        db.query(BYOKCredential)
        .filter(
            BYOKCredential.user_id == user_id,
            BYOKCredential.provider == provider,
        )
        .first()
    )

    if credential is None:
        credential = BYOKCredential(
            user_id=user_id,
            provider=provider,
        )
        db.add(credential)

    credential.encrypted_key = _encrypt(api_key)
    credential.key_hint = _hint(api_key)

    db.commit()
    db.refresh(credential)

    return BYOKProviderResponse(
        provider=provider,
        configured=True,
        key_hint=credential.key_hint,
    )


@router.delete(
    "/credentials/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_byok_credential(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = _normalize_provider(provider)

    credential = (
        db.query(BYOKCredential)
        .filter(
            BYOKCredential.user_id == str(current_user.id),
            BYOKCredential.provider == provider,
        )
        .first()
    )

    if credential:
        db.delete(credential)
        db.commit()

    return None


def get_user_byok_key(
    db: Session,
    user_id: str,
    provider: str,
) -> Optional[str]:
    provider = _normalize_provider(provider)

    credential = (
        db.query(BYOKCredential)
        .filter(
            BYOKCredential.user_id == str(user_id),
            BYOKCredential.provider == provider,
        )
        .first()
    )

    if credential is None:
        return None

    return _decrypt(credential.encrypted_key)

