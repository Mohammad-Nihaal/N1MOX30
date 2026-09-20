from __future__ import annotations

from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.analytics import AnalyticsSnapshot
from app.models.connected_account import ConnectedAccount
from app.models.user import User
from app.services.analytics_service import create_youtube_snapshot


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _account(current_user: User, db: Session, platform: str) -> ConnectedAccount:
    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.platform == platform,
            ConnectedAccount.is_active.is_(True),
            ConnectedAccount.is_authorized.is_(True),
        )
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail=f"No authorized {platform} account found.")
    return account


@router.post("/youtube/snapshot")
def create_youtube_analytics_snapshot(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = _account(current_user, db, "youtube")
    try:
        snapshot = create_youtube_snapshot(account, db)
        return {
            "status": "snapshot_created",
            "snapshot_id": snapshot.id,
            "platform": snapshot.platform,
            "views": snapshot.views,
            "followers": snapshot.followers,
            "likes": snapshot.likes,
            "comments": snapshot.comments,
            "recorded_at": snapshot.recorded_at,
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/youtube/history")
def get_youtube_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = _account(current_user, db, "youtube")
    snapshots = (
        db.query(AnalyticsSnapshot)
        .filter(AnalyticsSnapshot.connected_account_id == account.id, AnalyticsSnapshot.platform == "youtube", AnalyticsSnapshot.content_id.is_(None))
        .order_by(AnalyticsSnapshot.recorded_at.asc())
        .all()
    )
    return [_serialize(s) for s in snapshots]


def _serialize(snapshot: AnalyticsSnapshot) -> dict:
    return {
        "id": snapshot.id,
        "views": snapshot.views,
        "followers": snapshot.followers,
        "likes": snapshot.likes,
        "comments": snapshot.comments,
        "recorded_at": snapshot.recorded_at,
    }


def _fetch_platform_metrics(platform: str, account: ConnectedAccount) -> dict:
    token = account.access_token
    if not token:
        raise ValueError("Connected account access token is missing.")

    if platform == "x":
        response = httpx.get(
            "https://api.x.com/2/users/me",
            params={"user.fields": "public_metrics,username,name"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        user = response.json().get("data", {})
        metrics = user.get("public_metrics") or {}
        return {
            "views": 0,
            "followers": int(metrics.get("followers_count") or 0),
            "likes": int(metrics.get("like_count") or 0),
            "comments": 0,
            "raw": user,
        }

    if platform == "tiktok":
        response = httpx.get(
            "https://open.tiktokapis.com/v2/user/info/",
            params={"fields": "open_id,display_name,follower_count,following_count,likes_count,video_count"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        user = response.json().get("data", {}).get("user", {})
        return {
            "views": 0,
            "followers": int(user.get("follower_count") or 0),
            "likes": int(user.get("likes_count") or 0),
            "comments": 0,
            "raw": user,
        }

    if platform == "instagram":
        version = settings.instagram_graph_version
        response = httpx.get(
            f"https://graph.facebook.com/{version}/{account.platform_account_id}",
            params={"fields": "username,name,followers_count,media_count"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        user = response.json()
        return {
            "views": 0,
            "followers": int(user.get("followers_count") or 0),
            "likes": 0,
            "comments": 0,
            "raw": user,
        }

    raise ValueError(f"Unsupported analytics platform: {platform}")


@router.post("/{platform}/snapshot")
def create_platform_snapshot(platform: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    platform = platform.lower().strip()
    if platform == "youtube":
        return create_youtube_analytics_snapshot(current_user, db)
    if platform not in {"instagram", "tiktok", "x"}:
        raise HTTPException(status_code=400, detail="Supported platforms: youtube, instagram, tiktok, x.")
    account = _account(current_user, db, platform)
    try:
        metrics = _fetch_platform_metrics(platform, account)
        snapshot = AnalyticsSnapshot(
            connected_account_id=account.id,
            platform=platform,
            views=metrics["views"],
            followers=metrics["followers"],
            likes=metrics["likes"],
            comments=metrics["comments"],
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return {**_serialize(snapshot), "raw": metrics.get("raw")}
    except (ValueError, httpx.HTTPError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/overview")
def analytics_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = (
        db.query(ConnectedAccount)
        .filter(ConnectedAccount.user_id == current_user.id, ConnectedAccount.is_active.is_(True))
        .all()
    )
    overview = []
    for account in accounts:
        latest = (
            db.query(AnalyticsSnapshot)
            .filter(AnalyticsSnapshot.connected_account_id == account.id)
            .order_by(AnalyticsSnapshot.recorded_at.desc())
            .first()
        )
        overview.append({
            "platform": account.platform,
            "account_id": account.id,
            "account_name": account.account_name,
            "authorized": account.is_authorized,
            "latest": _serialize(latest) if latest else None,
        })
    return {"generated_at": datetime.utcnow(), "platforms": overview}
