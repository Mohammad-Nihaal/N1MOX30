from __future__ import annotations

from typing import Any

from app.services.creator_accounts.manager import list_accounts
from app.services.creator_accounts.token_store import load_token
from app.services.publishing.youtube_live import (
    get_channel,
    get_recent_videos,
    get_video_analytics,
)
from app.services.growth.intelligence import (
    build_growth_report,
)


def _authorized_account(user_id: int):
    accounts=list_accounts(user_id).get("accounts", [])

    for account in accounts:
        account_id=account.get("account_id")

        if not account_id:
            continue

        token=load_token(account_id)

        if token and token.get("access_token"):
            return account, token

    return None, None


def build_creator_dashboard(
    user_id: int,
) -> dict[str, Any]:

    account, token=_authorized_account(user_id)

    if not account or not token:
        return {
            "status":"authorization_required",
            "user_id":user_id,
            "channel":None,
            "videos":[],
            "analytics":[],
            "growth":build_growth_report({}),
            "publishing":{
                "queued":0,
                "published":0,
                "failed":0,
            },
        }

    access_token=token["access_token"]

    channel_result=get_channel(access_token)

    if channel_result.get("status")!="connected":
        return {
            "status":channel_result.get(
                "status",
                "failed",
            ),
            "user_id":user_id,
            "account":account,
            "channel":None,
            "videos":[],
            "analytics":[],
            "growth":build_growth_report({}),
            "publishing":{
                "queued":0,
                "published":0,
                "failed":0,
            },
        }

    videos_result=get_recent_videos(
        access_token,
        max_results=10,
    )

    videos=videos_result.get("videos",[])

    ids=[
        v.get("video_id")
        for v in videos
        if v.get("video_id")
    ]

    analytics_result=get_video_analytics(
        access_token,
        ids,
    )

    analytics=analytics_result.get(
        "videos",
        [],
    )

    total_views=sum(
        int(v.get("views",0))
        for v in analytics
    )

    total_likes=sum(
        int(v.get("likes",0))
        for v in analytics
    )

    total_comments=sum(
        int(v.get("comments",0))
        for v in analytics
    )

    total_engagement=(
        ((total_likes+total_comments)/total_views)*100
        if total_views
        else 0
    )

    growth_metrics={
        "views_growth":0,
        "engagement_growth":0,
        "subscriber_growth":0,
        "consistency_score":min(
            len(videos)*10,
            100,
        ),
        "engagement_rate":total_engagement,
        "subscriber_conversion_rate":0,
        "views":total_views,
    }

    return {
        "status":"ready",
        "user_id":user_id,
        "account":account,
        "channel":channel_result.get("channel"),
        "videos":videos,
        "analytics":analytics,
        "summary":{
            "total_views":total_views,
            "total_likes":total_likes,
            "total_comments":total_comments,
            "videos_analyzed":len(analytics),
            "engagement_rate":round(
                total_engagement,
                4,
            ),
        },
        "growth":build_growth_report(
            growth_metrics
        ),
        "publishing":{
            "queued":0,
            "published":0,
            "failed":0,
        },
    }