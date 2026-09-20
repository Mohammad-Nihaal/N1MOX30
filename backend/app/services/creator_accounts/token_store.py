from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TOKEN_STORAGE = (
    PROJECT_ROOT
    / "storage"
    / "creator_tokens"
)

TOKEN_STORAGE.mkdir(
    parents=True,
    exist_ok=True,
)


def _key() -> bytes:
    raw = os.getenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        "development-only-change-this-key",
    )

    return hashlib.sha256(
        raw.encode()
    ).digest()


def _crypt(value: str) -> str:
    data = value.encode()
    key = _key()

    encrypted = bytes(
        byte ^ key[index % len(key)]
        for index, byte in enumerate(data)
    )

    return base64.urlsafe_b64encode(
        encrypted
    ).decode()


def _decrypt(value: str) -> str:
    encrypted = base64.urlsafe_b64decode(
        value.encode()
    )

    key = _key()

    decrypted = bytes(
        byte ^ key[index % len(key)]
        for index, byte in enumerate(encrypted)
    )

    return decrypted.decode()


def save_token(
    account_id: str,
    token: dict,
) -> str:

    payload = {
        "account_id": account_id,
        "token": _crypt(
            json.dumps(
                token,
                ensure_ascii=False,
            )
        ),
    }

    path = TOKEN_STORAGE / f"{account_id}.json"

    path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return str(path)


def load_token(
    account_id: str,
) -> dict | None:

    path = TOKEN_STORAGE / f"{account_id}.json"

    if not path.exists():
        return None

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    return json.loads(
        _decrypt(payload["token"])
    )


def delete_token(
    account_id: str,
) -> bool:

    path = TOKEN_STORAGE / f"{account_id}.json"

    if not path.exists():
        return False

    path.unlink()

    return True