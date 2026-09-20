from __future__ import annotations

import hashlib
import json
import os
import secrets
import urllib.parse
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OAUTH_STORAGE = (
    PROJECT_ROOT
    / "storage"
    / "oauth"
)

OAUTH_STORAGE.mkdir(
    parents=True,
    exist_ok=True,
)


YOUTUBE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)

YOUTUBE_TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

YOUTUBE_SCOPE = (
    "https://www.googleapis.com/auth/youtube.upload"
)


def oauth_config() -> dict:
    return {
        "client_id": os.getenv(
            "N1MOX_YOUTUBE_CLIENT_ID"
        ),
        "client_secret": os.getenv(
            "N1MOX_YOUTUBE_CLIENT_SECRET"
        ),
        "redirect_uri": os.getenv(
            "N1MOX_YOUTUBE_REDIRECT_URI",
            "http://127.0.0.1:8000/platform/v11/accounts/youtube/callback",
        ),
    }


def _state_path(state: str) -> Path:
    return OAUTH_STORAGE / (
        f"{hashlib.sha256(state.encode('utf-8')).hexdigest()}.json"
    )


def _state_path(state: str) -> Path:
    digest = hashlib.sha256(state.encode("utf-8")).hexdigest()
    return OAUTH_STORAGE / f"{digest}.json"


def create_oauth_state(user_id: int, account_id: str) -> str:
    state = secrets.token_urlsafe(32)
    payload = {
        "state": state,
        "user_id": user_id,
        "account_id": account_id,
    }

    _state_path(state).write_text(
        json.dumps(payload),
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
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    finally:
        path.unlink(missing_ok=True)

    if data.get("state") != state:
        return None

    return data

def build_authorization_url(
    user_id: int,
    account_id: str,
) -> dict:
    config = oauth_config()

    state = create_oauth_state(
        user_id=user_id,
        account_id=account_id,
    )

    if not config["client_id"]:
        return {
            "status": "configuration_required",
            "state": state,
            "message": (
                "Set N1MOX_YOUTUBE_CLIENT_ID and "
                "N1MOX_YOUTUBE_CLIENT_SECRET before OAuth."
            ),
        }

    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": YOUTUBE_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    return {
        "status": "ready",
        "authorization_url": (
            YOUTUBE_AUTH_URL
            + "?"
            + urllib.parse.urlencode(params)
        ),
        "state": state,
    }


def consume_oauth_state(
    state: str,
) -> dict | None:

    if not state:
        return None

    path = _state_path(state)

    if not path.exists():
        return None

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    finally:
        path.unlink(
            missing_ok=True
        )

    # Prevent a stored-state mixup.
    if data.get("state") != state:
        return None

    return data

def exchange_code(
    code: str,
) -> dict:
    config = oauth_config()

    if not config["client_id"] or not config["client_secret"]:
        return {
            "status": "configuration_required",
            "message": "YouTube OAuth credentials are not configured.",
        }

    payload = urllib.parse.urlencode({
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config["redirect_uri"],
    }).encode()

    request = urllib.request.Request(
        YOUTUBE_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        return {
            "status": "completed",
            "token": data,
        }

    except Exception as exc:

        return {
            "status": "failed",
            "error": str(exc),
        }