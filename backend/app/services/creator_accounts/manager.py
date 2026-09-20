from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

ACCOUNT_STORAGE = (
    PROJECT_ROOT
    / "storage"
    / "creator_accounts"
)

ACCOUNT_STORAGE.mkdir(
    parents=True,
    exist_ok=True,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(user_id: int) -> Path:
    return ACCOUNT_STORAGE / f"user_{user_id}.json"


def _load(user_id: int) -> dict:
    path = _path(user_id)

    if not path.exists():
        return {
            "user_id": user_id,
            "accounts": [],
        }

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def _save(user_id: int, data: dict) -> str:
    path = _path(user_id)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return str(path)


def list_accounts(user_id: int) -> dict:
    data = _load(user_id)

    public_accounts = []

    for account in data.get("accounts", []):
        public_accounts.append({
            "account_id": account["account_id"],
            "provider": account["provider"],
            "channel_id": account.get("channel_id"),
            "channel_name": account.get("channel_name"),
            "status": account.get("status"),
            "created_at": account.get("created_at"),
            "updated_at": account.get("updated_at"),
        })

    return {
        "user_id": user_id,
        "accounts": public_accounts,
    }


def create_connection(
    user_id: int,
    provider: str = "youtube",
) -> dict:
    data = _load(user_id)

    account = {
        "account_id": f"acct_{uuid.uuid4().hex}",
        "provider": provider,
        "channel_id": None,
        "channel_name": None,
        "status": "pending",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "token": None,
    }

    data.setdefault("accounts", []).append(account)

    _save(user_id, data)

    return {
        "status": "created",
        "account": {
            key: value
            for key, value in account.items()
            if key != "token"
        },
    }


def update_account(
    user_id: int,
    account_id: str,
    **updates,
) -> dict:
    data = _load(user_id)

    for account in data.get("accounts", []):
        if account["account_id"] == account_id:

            account.update(updates)
            account["updated_at"] = utc_now()

            _save(user_id, data)

            return {
                "status": "updated",
                "account": {
                    key: value
                    for key, value in account.items()
                    if key != "token"
                },
            }

    return {
        "status": "not_found",
        "account_id": account_id,
    }


def remove_account(
    user_id: int,
    account_id: str,
) -> dict:
    data = _load(user_id)

    before = len(data.get("accounts", []))

    data["accounts"] = [
        account
        for account in data.get("accounts", [])
        if account["account_id"] != account_id
    ]

    removed = len(data["accounts"]) < before

    _save(user_id, data)

    return {
        "status": "removed" if removed else "not_found",
        "account_id": account_id,
    }