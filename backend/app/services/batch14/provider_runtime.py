import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass

@dataclass
class RuntimeResult:
    success: bool
    provider: str
    content: str = ""
    error: str | None = None
    fallback_used: bool = False

def _request_json(url, payload, headers=None, timeout=30):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(str(exc))

def _openai(prompt, key):
    data = _request_json(
        "https://api.openai.com/v1/chat/completions",
        {
            "model": os.getenv("N1MOX30_OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [{"role": "user", "content": prompt}],
        },
        {"Authorization": f"Bearer {key}"},
    )
    return data["choices"][0]["message"]["content"]

def _groq(prompt, key):
    data = _request_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {
            "model": os.getenv("N1MOX30_GROQ_MODEL", "llama-3.3-70b-versatile"),
            "messages": [{"role": "user", "content": prompt}],
        },
        {"Authorization": f"Bearer {key}"},
    )
    return data["choices"][0]["message"]["content"]

def _gemini(prompt, key):
    model = os.getenv("N1MOX30_GEMINI_MODEL", "gemini-2.0-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={key}"
    )
    data = _request_json(
        url,
        {"contents": [{"parts": [{"text": prompt}]}]},
    )
    return data["candidates"][0]["content"]["parts"][0]["text"]

def _omniroute(prompt, key):
    base = os.getenv("OMNIROUTE_BASE_URL", "").rstrip("/")
    if not base:
        raise RuntimeError("OMNIROUTE_BASE_URL is not configured")

    data = _request_json(
        f"{base}/v1/chat/completions",
        {
            "model": os.getenv("N1MOX30_OMNIROUTE_MODEL", "auto"),
            "messages": [{"role": "user", "content": prompt}],
        },
        {"Authorization": f"Bearer {key}"} if key else {},
    )
    return data["choices"][0]["message"]["content"]

def _openclaw(prompt, key):
    base = os.getenv("OPENCLAW_BASE_URL", "").rstrip("/")
    if not base:
        raise RuntimeError("OPENCLAW_BASE_URL is not configured")

    data = _request_json(
        f"{base}/v1/chat/completions",
        {
            "model": os.getenv("N1MOX30_OPENCLAW_MODEL", "auto"),
            "messages": [{"role": "user", "content": prompt}],
        },
        {"Authorization": f"Bearer {key}"} if key else {},
    )
    return data["choices"][0]["message"]["content"]

def execute_real_provider(provider, prompt, key=None):
    provider = (provider or "").lower()

    if provider == "openai":
        return _openai(prompt, key)
    if provider == "groq":
        return _groq(prompt, key)
    if provider == "gemini":
        return _gemini(prompt, key)
    if provider == "omniroute":
        return _omniroute(prompt, key)
    if provider == "openclaw":
        return _openclaw(prompt, key)

    raise RuntimeError(f"No runtime adapter for provider: {provider}")

def execute_runtime(provider, prompt, key=None):
    if provider == "demo":
        return RuntimeResult(
            True,
            "demo",
            f"N1MOX30 demo response: {prompt}",
        )

    if not key and provider not in ("openclaw", "omniroute"):
        return RuntimeResult(
            False,
            provider,
            error="Provider credential unavailable",
        )

    try:
        content = execute_real_provider(provider, prompt, key)
        return RuntimeResult(True, provider, content)
    except Exception as exc:
        return RuntimeResult(
            False,
            provider,
            error=str(exc)[:500],
        )

def execute_runtime_with_fallback(
    db,
    user_id,
    prompt,
    requested=None,
):
    from app.services.batch11.provider_router import choose_provider
    from app.services.batch13.provider_execution import _credential_value

    decision = choose_provider(
        db,
        user_id,
        requested=requested,
    )

    candidates = []

    if decision.provider:
        candidates.append(decision.provider)

    for provider in (
        "openclaw",
        "omniroute",
        "groq",
        "openai",
        "gemini",
        "bedrock",
        "demo",
    ):
        if provider not in candidates:
            candidates.append(provider)

    errors = []

    for index, provider in enumerate(candidates):
        key = _credential_value(db, user_id, provider)

        if not key:
            env_map = {
                "openai": "OPENAI_API_KEY",
                "groq": "GROQ_API_KEY",
                "gemini": "GEMINI_API_KEY",
                "omniroute": "OMNIROUTE_API_KEY",
                "openclaw": "OPENCLAW_API_KEY",
            }
            env_name = env_map.get(provider)
            if env_name:
                key = os.getenv(env_name)

        result = execute_runtime(provider, prompt, key)

        if result.success:
            result.fallback_used = index > 0
            return result

        if result.error:
            errors.append(f"{provider}: {result.error}")

    return RuntimeResult(
        False,
        "none",
        error=" | ".join(errors)[:2000],
    )

