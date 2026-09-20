from fastapi import APIRouter, Query

from app.services.youtube.channel_sync import (
    get_channel,
    sync_channel,
    get_channel_videos,
)

from app.services.publishing.tracking import (
    get_publish_result,
    list_publish_results,
)

from app.services.analytics.youtube_analytics import (
    build_channel_analytics,
    build_video_analytics,
)


router = APIRouter(
    prefix="/platform/v12/youtube",
    tags=["YouTube Analytics"],
)


@router.get("/channel/{account_id}")
def channel(account_id: str):
    return get_channel(account_id)


@router.post("/channel/{account_id}/sync")
def channel_sync(
    account_id: str,
    access_token: str | None = Query(default=None),
):
    return sync_channel(
        account_id,
        access_token=access_token,
    )


@router.get("/channel/{account_id}/videos")
def channel_videos(account_id: str):
    return get_channel_videos(account_id)


@router.get("/publishing/{job_id}")
def publishing_result(job_id: str):
    return get_publish_result(job_id)


@router.get("/publishing")
def publishing_results(
    account_id: str | None = Query(default=None),
):
    return list_publish_results(account_id)


@router.get("/analytics/{account_id}")
def analytics(account_id: str):
    channel_result = get_channel(account_id)

    if channel_result.get("status") != "available":
        return channel_result

    channel_data = channel_result["channel"]

    videos_result = get_channel_videos(account_id)

    videos = videos_result.get("videos", [])

    return {
        "status": "available",
        "channel": build_channel_analytics(channel_data),
        "videos": [
            build_video_analytics(video)
            for video in videos
        ],
    }