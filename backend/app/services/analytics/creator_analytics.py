from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_metrics(
    views: int = 0,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    subscribers_gained: int = 0,
    watch_time_seconds: int = 0,
) -> dict[str, Any]:

    views = max(0, int(views))
    likes = max(0, int(likes))
    comments = max(0, int(comments))
    shares = max(0, int(shares))
    subscribers_gained = max(0, int(subscribers_gained))
    watch_time_seconds = max(0, int(watch_time_seconds))

    engagement_rate = (
        ((likes + comments + shares) / views) * 100
        if views else 0.0
    )

    subscriber_rate = (
        (subscribers_gained / views) * 100
        if views else 0.0
    )

    return {
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "subscribers_gained": subscribers_gained,
        "watch_time_seconds": watch_time_seconds,
        "engagement_rate": round(engagement_rate, 4),
        "subscriber_conversion_rate": round(subscriber_rate, 4),
        "updated_at": utc_now(),
    }


def score_content(metrics: dict[str, Any]) -> float:
    engagement = float(metrics.get("engagement_rate", 0))
    conversion = float(
        metrics.get("subscriber_conversion_rate", 0)
    )

    score = (
        min(engagement * 10, 60)
        + min(conversion * 10, 30)
        + min(
            float(metrics.get("watch_time_seconds", 0)) / 600,
            10,
        )
    )

    return round(min(score, 100), 2)


def analyze_content(
    title: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:

    normalized = normalize_metrics(
        views=metrics.get("views", 0),
        likes=metrics.get("likes", 0),
        comments=metrics.get("comments", 0),
        shares=metrics.get("shares", 0),
        subscribers_gained=metrics.get(
            "subscribers_gained", 0
        ),
        watch_time_seconds=metrics.get(
            "watch_time_seconds", 0
        ),
    )

    return {
        "title": title,
        "metrics": normalized,
        "performance_score": score_content(normalized),
        "status": "analyzed",
    }