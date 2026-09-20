from fastapi import APIRouter, Query

from app.services.creator_accounts.youtube_real_oauth import (
    authorization_url,
    complete_oauth,
    configured,
)

router = APIRouter(
    prefix="/platform/v19/youtube/oauth",
    tags=["YouTube OAuth"],
)


@router.get("/status")
def oauth_status():
    return {
        "status": "configured"
        if configured()
        else "not_configured",
        "oauth_configured": configured(),
    }


@router.get("/authorize")
def authorize(
    user_id: int,
    account_id: str,
):
    try:
        return authorization_url(
            user_id,
            account_id,
        )
    except Exception as exc:
        return {
            "status": "configuration_required",
            "message": str(exc),
        }


@router.get("/callback")
def callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    if error:
        return {
            "status": "authorization_denied",
            "error": error,
        }

    if not code or not state:
        return {
            "status": "invalid_callback",
            "message": "code and state are required",
        }

    try:
        return complete_oauth(
            code,
            state,
        )
    except Exception as exc:
        return {
            "status": "token_exchange_failed",
            "message": str(exc),
        }