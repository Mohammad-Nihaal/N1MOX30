from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.integrations.instagram_oauth import get_instagram_authorization_url
from app.integrations.social_oauth import (
    create_x_pkce,
    instagram_exchange_code,
    tiktok_authorization_url,
    tiktok_exchange_code,
    x_authorization_url,
    x_exchange_code,
)
from app.integrations.youtube_oauth import get_youtube_authorization_url
from app.models.connected_account import ConnectedAccount
from app.models.oauth_state import OAuthState
from app.models.user import User
from app.services.youtube_service import exchange_youtube_code, get_youtube_channel


router = APIRouter(prefix="/oauth", tags=["OAuth Connections"])


def create_oauth_state(db: Session, user_id: str, platform: str, suffix: str = "") -> str:
    state_value = secrets.token_urlsafe(32) + suffix
    db.add(OAuthState(user_id=user_id, platform=platform, state=state_value))
    db.commit()
    return state_value


def validate_oauth_state(db: Session, state_value: str, platform: str) -> OAuthState:
    oauth_state = (
        db.query(OAuthState)
        .filter(OAuthState.state == state_value, OAuthState.platform == platform)
        .first()
    )
    if not oauth_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")
    if oauth_state.expires_at < datetime.utcnow():
        db.delete(oauth_state)
        db.commit()
        raise HTTPException(status_code=400, detail="OAuth state has expired. Please try connecting again.")
    return oauth_state


def _save_account(
    db: Session,
    *,
    user_id: str,
    platform: str,
    platform_account_id: str,
    account_name: str,
    access_token: str,
    refresh_token: str | None = None,
    expires_in: int | None = None,
):
    from datetime import timedelta
    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.platform == platform,
            ConnectedAccount.platform_account_id == platform_account_id,
        )
        .first()
    )
    expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in)) if expires_in else None
    if account:
        account.account_name = account_name
        account.access_token = access_token
        account.refresh_token = refresh_token or account.refresh_token
        account.token_expires_at = expires_at
        account.is_active = True
        account.is_authorized = True
    else:
        account = ConnectedAccount(
            user_id=user_id,
            platform=platform,
            platform_account_id=platform_account_id,
            account_name=account_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=expires_at,
            is_active=True,
            is_authorized=True,
        )
        db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/youtube/login")
def youtube_login(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return connect_youtube(current_user, db)


@router.get("/youtube/connect")
def connect_youtube(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    state = create_oauth_state(db, current_user.id, "youtube")
    try:
        return {"platform": "youtube", "authorization_url": get_youtube_authorization_url(state)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/youtube/callback")
def youtube_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return {"platform": "youtube", "status": "authorization_failed", "error": error}
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state.")
    oauth_state = validate_oauth_state(db, state, "youtube")
    try:
        tokens = exchange_youtube_code(code)
        access_token = tokens.get("access_token")
        if not access_token:
            raise ValueError("Google did not return an access token.")
        channel = get_youtube_channel(access_token)
        account = _save_account(
            db,
            user_id=oauth_state.user_id,
            platform="youtube",
            platform_account_id=channel["channel_id"],
            account_name=channel["channel_name"],
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens.get("expires_in"),
        )
        db.delete(oauth_state)
        db.commit()
        return {"platform": "youtube", "status": "connected", "account_id": account.id, "channel_id": account.platform_account_id, "channel_name": account.account_name}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/instagram/connect")
def connect_instagram(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    state = create_oauth_state(db, current_user.id, "instagram")
    try:
        return {"platform": "instagram", "authorization_url": get_instagram_authorization_url(state)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/instagram/callback")
def instagram_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return {"platform": "instagram", "status": "authorization_failed", "error": error}
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state.")
    oauth_state = validate_oauth_state(db, state, "instagram")
    try:
        token = instagram_exchange_code(code)
        account = _save_account(
            db,
            user_id=oauth_state.user_id,
            platform="instagram",
            platform_account_id=token["platform_account_id"],
            account_name=token["account_name"],
            access_token=token["access_token"],
            expires_in=token.get("expires_in"),
        )
        db.delete(oauth_state)
        db.commit()
        return {"platform": "instagram", "status": "connected", "account_id": account.id, "account_name": account.account_name}
    except (ValueError, Exception) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/x/connect")
def connect_x(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    verifier, challenge = create_x_pkce()
    # Keep the verifier after a delimiter inside the server-side state record.
    state = create_oauth_state(db, current_user.id, "x", suffix="." + verifier)
    try:
        return {"platform": "x", "authorization_url": x_authorization_url(state, challenge)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/x/callback")
def x_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return {"platform": "x", "status": "authorization_failed", "error": error}
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state.")
    oauth_state = validate_oauth_state(db, state, "x")
    verifier = state.rsplit(".", 1)[-1]
    try:
        token = x_exchange_code(code, verifier)
        account = _save_account(
            db,
            user_id=oauth_state.user_id,
            platform="x",
            platform_account_id=token["platform_account_id"],
            account_name=token["account_name"],
            access_token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            expires_in=token.get("expires_in"),
        )
        db.delete(oauth_state)
        db.commit()
        return {"platform": "x", "status": "connected", "account_id": account.id, "account_name": account.account_name}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/tiktok/connect")
def connect_tiktok(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    state = create_oauth_state(db, current_user.id, "tiktok")
    try:
        return {"platform": "tiktok", "authorization_url": tiktok_authorization_url(state)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/tiktok/callback")
def tiktok_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return {"platform": "tiktok", "status": "authorization_failed", "error": error}
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state.")
    oauth_state = validate_oauth_state(db, state, "tiktok")
    try:
        token = tiktok_exchange_code(code)
        account = _save_account(
            db,
            user_id=oauth_state.user_id,
            platform="tiktok",
            platform_account_id=token["platform_account_id"],
            account_name=token["account_name"],
            access_token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            expires_in=token.get("expires_in"),
        )
        db.delete(oauth_state)
        db.commit()
        return {"platform": "tiktok", "status": "connected", "account_id": account.id, "account_name": account.account_name}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
