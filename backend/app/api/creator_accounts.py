from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.creator_accounts.manager import (
    create_connection,
    list_accounts,
    remove_account,
)

from app.services.creator_accounts.youtube_oauth import (
    build_authorization_url,
    consume_oauth_state,
    exchange_code,
)

from app.services.creator_accounts.token_store import (
    save_token,
)

from app.services.publishing.queue import (
    enqueue_publish,
)


router = APIRouter(
    prefix="/platform/v11/accounts",
    tags=["creator-accounts"],
)


class AccountRequest(BaseModel):
    user_id: int = Field(default=1, ge=1)
    provider: str = "youtube"


class PublishRequest(BaseModel):
    user_id: int = Field(default=1, ge=1)
    account_id: str
    video_path: str
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = "private"


@router.get("")
def accounts(user_id: int = Query(default=1, ge=1)):
    return list_accounts(user_id)


@router.post("/connect")
def connect(payload: AccountRequest):
    return create_connection(
        user_id=payload.user_id,
        provider=payload.provider,
    )


@router.delete("/{account_id}")
def disconnect(
    account_id: str,
    user_id: int = Query(default=1, ge=1),
):
    return remove_account(
        user_id=user_id,
        account_id=account_id,
    )


@router.get("/youtube/authorize")
def youtube_authorize(
    user_id: int = Query(default=1, ge=1),
    account_id: str = Query(...),
):
    return build_authorization_url(
        user_id=user_id,
        account_id=account_id,
    )


@router.get("/youtube/callback")
def youtube_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):

    if error:
        return {
            "status": "oauth_denied",
            "error": error,
        }

    if not code or not state:
        return {
            "status": "invalid_callback",
        }

    state_data = consume_oauth_state(state)

    if not state_data:
        return {
            "status": "invalid_state",
        }

    token_result = exchange_code(code)

    if token_result.get("status") != "completed":
        return token_result

    token = token_result["token"]

    save_token(
        state_data["account_id"],
        token,
    )

    return {
        "status": "connected",
        "account_id": state_data["account_id"],
        "message": (
            "YouTube OAuth completed. "
            "Channel metadata can now be synchronized."
        ),
    }


@router.post("/publish")
def queue_publish(payload: PublishRequest):

    metadata = {
        "snippet": {
            "title": payload.title,
            "description": payload.description,
            "tags": payload.tags,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": payload.privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    return enqueue_publish(
        user_id=payload.user_id,
        account_id=payload.account_id,
        video_path=payload.video_path,
        metadata=metadata,
    )