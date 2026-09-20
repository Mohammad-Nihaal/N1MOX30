from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.creator_accounts.manager import list_accounts
from app.services.creator_accounts.token_store import load_token
from app.services.publishing.live_publish import (
    publish_to_youtube,
)
from app.services.publishing.youtube_live import (
    get_channel,
    get_recent_videos,
    get_video_analytics,
)

router=APIRouter(
    prefix="/platform/v14/live",
    tags=["live-creator"],
)


class PublishRequest(BaseModel):
    user_id:int
    account_id:str
    video_path:str
    title:str
    description:str=""
    tags:list[str]=[]
    privacy_status:str="private"


@router.get("/accounts/{user_id}")
def accounts(user_id:int):
    return list_accounts(user_id)


@router.get("/youtube/{account_id}/channel")
def youtube_channel(account_id:str):

    token=load_token(account_id)

    if not token or not token.get("access_token"):
        return {
            "status":"authorization_required",
            "account_id":account_id,
        }

    return get_channel(
        token["access_token"]
    )


@router.get("/youtube/{account_id}/videos")
def youtube_videos(
    account_id:str,
    limit:int=10,
):

    token=load_token(account_id)

    if not token or not token.get("access_token"):
        return {
            "status":"authorization_required",
            "account_id":account_id,
        }

    return get_recent_videos(
        token["access_token"],
        max_results=max(1,min(limit,50)),
    )


@router.get("/youtube/{account_id}/analytics")
def youtube_analytics(
    account_id:str,
    limit:int=10,
):

    token=load_token(account_id)

    if not token or not token.get("access_token"):
        return {
            "status":"authorization_required",
            "account_id":account_id,
        }

    videos=get_recent_videos(
        token["access_token"],
        max_results=max(1,min(limit,50)),
    )

    if videos.get("status")!="ready":
        return videos

    ids=[
        video["video_id"]
        for video in videos.get("videos",[])
        if video.get("video_id")
    ]

    return get_video_analytics(
        token["access_token"],
        ids,
    )


@router.post("/youtube/publish")
def youtube_publish(payload:PublishRequest):

    return publish_to_youtube(
        user_id=payload.user_id,
        account_id=payload.account_id,
        video_path=payload.video_path,
        title=payload.title,
        description=payload.description,
        tags=payload.tags,
        privacy_status=payload.privacy_status,
    )