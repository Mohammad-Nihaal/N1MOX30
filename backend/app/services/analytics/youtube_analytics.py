from datetime import datetime, timezone


def _safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def build_channel_analytics(channel):
    subscribers = _safe_int(channel.get("subscriber_count"))
    views = _safe_int(channel.get("view_count"))
    videos = _safe_int(channel.get("video_count"))

    avg_views_per_video = (
        round(views / videos, 2)
        if videos
        else 0
    )

    return {
        "channel_id": channel.get("channel_id"),
        "channel_title": channel.get("title"),
        "subscribers": subscribers,
        "views": views,
        "videos": videos,
        "average_views_per_video": avg_views_per_video,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
    }


def build_video_analytics(video):
    views = _safe_int(video.get("view_count"))
    likes = _safe_int(video.get("like_count"))
    comments = _safe_int(video.get("comment_count"))

    engagement_rate = (
        round(((likes + comments) / views) * 100, 4)
        if views
        else 0
    )

    return {
        "video_id": video.get("video_id"),
        "title": video.get("title"),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_rate": engagement_rate,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
    }