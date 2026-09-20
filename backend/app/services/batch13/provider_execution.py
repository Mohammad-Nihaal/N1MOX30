from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class ProviderResult:
    success: bool
    provider: str
    content: str = ""
    error: Optional[str] = None

SUPPORTED = ("openclaw","omniroute","groq","openai","gemini","bedrock","demo")

def _env_key(provider: str):
    return {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "omniroute": "OMNIROUTE_API_KEY",
        "openclaw": "OPENCLAW_API_KEY",
    }.get(provider)

def _credential_value(db, user_id, provider):
    try:
        from app.models.platform import ProviderCredential
        rows = db.query(ProviderCredential).filter(
            ProviderCredential.user_id == user_id,
            ProviderCredential.provider == provider,
            ProviderCredential.is_active == True,
        ).all()

        for row in rows:
            for name in (
                "api_key", "credential", "secret", "key",
                "encrypted_api_key", "encrypted_key",
                "api_key_encrypted", "credential_encrypted",
                "secret_encrypted",
            ):
                if hasattr(row, name):
                    value = getattr(row, name, None)
                    if value:
                        return value
    except Exception:
        pass
    return None

def _demo(prompt):
    return ProviderResult(
        True,
        "demo",
        f"N1MOX30 demo generation: {prompt}"
    )

def execute_provider(provider, prompt, api_key=None):
    provider = (provider or "demo").lower()

    if provider == "demo":
        return _demo(prompt)

    if provider in ("openai","groq","gemini","omniroute","openclaw"):
        if not api_key:
            return ProviderResult(False, provider, error="Provider credential unavailable")

        # Existing provider adapters can be plugged in here without
        # changing the gateway contract.
        try:
            if provider == "groq":
                from app.services.groq_service import GroqService
                service = GroqService(api_key=api_key)
                result = service.generate(prompt)
                return ProviderResult(True, provider, str(result))
        except Exception:
            pass

        return ProviderResult(
            False,
            provider,
            error="Provider adapter unavailable"
        )

    if provider == "bedrock":
        return ProviderResult(
            False,
            provider,
            error="Bedrock execution adapter unavailable"
        )

    return ProviderResult(False, provider, error="Unsupported provider")

def execute_with_fallback(db, user_id, prompt, requested=None):
    from app.services.batch11.provider_router import choose_provider

    decision = choose_provider(
        db,
        user_id,
        requested=requested
    )

    candidates = []
    if decision.provider:
        candidates.append(decision.provider)

    for provider in SUPPORTED:
        if provider not in candidates:
            candidates.append(provider)

    errors = []

    for provider in candidates:
        key = _credential_value(db, user_id, provider)

        if not key:
            env_name = _env_key(provider)
            if env_name:
                key = os.getenv(env_name)

        result = execute_provider(provider, prompt, key)

        if result.success:
            return result

        if result.error:
            errors.append(f"{provider}: {result.error}")

    return ProviderResult(
        False,
        "none",
        error="; ".join(errors) or "No provider available"
    )

