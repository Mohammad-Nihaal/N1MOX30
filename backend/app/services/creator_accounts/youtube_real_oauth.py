import hashlib
import json
import os
import secrets
import urllib.parse
import urllib.request
from pathlib import Path

from app.services.creator_accounts.secure_token_store import (
    save_secure_token,
)

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"

ROOT = Path(__file__).resolve().parents[3]
OAUTH_ROOT = ROOT / "storage" / "youtube_oauth"
OAUTH_ROOT.mkdir(parents=True, exist_ok=True)

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _config():
    return {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uri": os.getenv(
            "YOUTUBE_REDIRECT_URI",
            "http://127.0.0.1:8000/oauth/youtube/callback",
        ),
    }


def configured():
    config = _config()
    return bool(
        config["client_id"]
        and config["client_secret"]
        and config["redirect_uri"]
    )


def _state_path(state: str):
    digest = hashlib.sha256(
        state.encode("utf-8")
    ).hexdigest()

    return OAUTH_ROOT / f"{digest}.json"


def create_oauth_state(
    user_id: int,
    account_id: str,
):
    if not configured():
        raise RuntimeError(
            "YouTube OAuth is not configured"
        )

    state = secrets.token_urlsafe(32)

    _state_path(state).write_text(
        json.dumps(
            {
                "state": state,
                "user_id": user_id,
                "account_id": account_id,
            }
        ),
        encoding="utf-8",
    )

    return state


def consume_oauth_state(state: str):
    if not state:
        return None

    path = _state_path(state)

    if not path.exists():
        return None

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    finally:
        path.unlink(missing_ok=True)

    if payload.get("state") != state:
        return None

    return payload


def authorization_url(
    user_id: int,
    account_id: str,
):
    config = _config()
    state = create_oauth_state(
        user_id,
        account_id,
    )

    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    return {
        "status": "ready",
        "authorization_url": (
            GOOGLE_AUTH
            + "?"
            + urllib.parse.urlencode(params)
        ),
        "state": state,
    }


def exchange_code(code: str):
    config = _config()

    if not configured():
        raise RuntimeError(
            "YouTube OAuth is not configured"
        )

    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        GOOGLE_TOKEN,
        data=payload,
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def complete_oauth(
    code: str,
    state: str,
):
    state_data = consume_oauth_state(state)

    if not state_data:
        return {
            "status": "invalid_state"
        }

    tokens = exchange_code(code)

    access_token = tokens.get(
        "access_token"
    )

    if not access_token:
        return {
            "status": "token_exchange_failed",
            "details": tokens,
        }

    stored = save_secure_token(
        state_data["user_id"],
        state_data["account_id"],
        access_token,
        tokens.get("refresh_token"),
    )

    return {
        "status": "connected",
        "user_id": state_data["user_id"],
        "account_id": state_data["account_id"],
        "token_type": tokens.get(
            "token_type",
            "Bearer",
        ),
        "expires_in": tokens.get(
            "expires_in"
        ),
        "storage": stored,
    }