import base64
import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOKEN_ROOT = ROOT / "storage" / "secure_tokens"
TOKEN_ROOT.mkdir(parents=True, exist_ok=True)


def _key() -> bytes:
    value = os.getenv("N1MOX_TOKEN_ENCRYPTION_KEY")

    if not value:
        raise RuntimeError(
            "N1MOX_TOKEN_ENCRYPTION_KEY is required for secure token storage"
        )

    if len(value) < 32:
        raise RuntimeError(
            "N1MOX_TOKEN_ENCRYPTION_KEY must contain at least 32 characters"
        )

    return hashlib.sha256(value.encode("utf-8")).digest()


def _crypt(value: str) -> str:
    key = _key()
    raw = value.encode("utf-8")
    output = bytes(
        byte ^ key[index % len(key)]
        for index, byte in enumerate(raw)
    )
    return base64.urlsafe_b64encode(output).decode("ascii")


def _path(user_id: int, account_id: str) -> Path:
    safe_user = str(user_id)
    safe_account = hashlib.sha256(
        str(account_id).encode("utf-8")
    ).hexdigest()

    user_dir = TOKEN_ROOT / safe_user
    user_dir.mkdir(parents=True, exist_ok=True)

    return user_dir / f"{safe_account}.token"


def save_secure_token(
    user_id: int,
    account_id: str,
    access_token: str,
    refresh_token: str | None = None,
):
    payload = access_token

    if refresh_token:
        payload += "\n" + refresh_token

    _path(user_id, account_id).write_text(
        _crypt(payload),
        encoding="utf-8",
    )

    return {
        "status": "stored",
        "user_id": user_id,
        "account_id": account_id,
    }


def load_secure_token(
    user_id: int,
    account_id: str,
):
    path = _path(user_id, account_id)

    if not path.exists():
        return None

    encoded = path.read_text(
        encoding="utf-8"
    )

    key = _key()
    raw = base64.urlsafe_b64decode(
        encoded.encode("ascii")
    )

    decoded = bytes(
        byte ^ key[index % len(key)]
        for index, byte in enumerate(raw)
    ).decode("utf-8")

    parts = decoded.split("\n", 1)

    return {
        "access_token": parts[0],
        "refresh_token": parts[1] if len(parts) > 1 else None,
    }