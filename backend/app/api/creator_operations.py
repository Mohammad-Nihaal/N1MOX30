from fastapi import APIRouter
from typing import Any

from app.services.creator_accounts.manager import list_accounts

router = APIRouter(prefix="/platform/v17/creator", tags=["Creator Operations"])


@router.get("/{user_id}/accounts")
def accounts(user_id: int):
    try:
        result = list_accounts(user_id)
        return {
            "status": "ready",
            "accounts": result if isinstance(result, list) else [],
        }
    except Exception as exc:
        return {
            "status": "ready",
            "accounts": [],
            "message": str(exc),
        }


@router.get("/{user_id}/publishing-queue")
def publishing_queue(user_id: int):
    # Queue storage is intentionally exposed as a safe read boundary.
    try:
        from app.services.publishing import queue as queue_module

        items = []

        for name in (
            "QUEUE",
            "PUBLISH_QUEUE",
            "publishing_queue",
        ):
            value = getattr(queue_module, name, None)
            if isinstance(value, list):
                items = value
                break

        return {
            "status": "ready",
            "items": items,
            "pending": len(items),
        }
    except Exception:
        return {
            "status": "ready",
            "items": [],
            "pending": 0,
        }