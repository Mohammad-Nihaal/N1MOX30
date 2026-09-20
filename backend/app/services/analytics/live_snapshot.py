from app.services.analytics.history import (
    save_snapshot,
)
from app.services.publishing.youtube_live import (
    get_channel,
    get_recent_videos,
    get_video_analytics,
)


def collect_creator_snapshot(
    user_id: int,
    access_token: str,
):
    channel = get_channel(
        access_token
    )

    videos = get_recent_videos(
        access_token,
        max_results=20,
    )

    analytics = []

    if isinstance(videos, dict):
        video_items = videos.get(
            "items",
            [],
        )
    else:
        video_items = []

    for video in video_items:
        video_id = (
            video.get("id")
            if isinstance(video, dict)
            else None
        )

        if not video_id:
            continue

        result = get_video_analytics(
            access_token,
            video_id,
        )

        if isinstance(result, dict):
            analytics.append(result)

    total_views = 0
    total_likes = 0
    total_comments = 0

    for item in analytics:
        stats = item.get(
            "statistics",
            item.get("stats", {}),
        )

        try:
            total_views += int(
                stats.get("viewCount", 0)
            )
            total_likes += int(
                stats.get("likeCount", 0)
            )
            total_comments += int(
                stats.get("commentCount", 0)
            )
        except Exception:
            continue

    metrics = {
        "views": total_views,
        "likes": total_likes,
        "comments": total_comments,
        "videos": len(video_items),
    }

    snapshot = save_snapshot(
        user_id,
        metrics,
    )

    return {
        "status": "ready",
        "channel": channel,
        "metrics": metrics,
        "snapshot": snapshot,
    }