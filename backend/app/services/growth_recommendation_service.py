def generate_growth_recommendations(
    ranked_videos: list[dict],
    growth_score_result: dict,
) -> dict:
    """Generate actionable YouTube growth recommendations."""

    if not ranked_videos:
        return {
            "recommendations": [
                {
                    "priority": "high",
                    "category": "content",
                    "recommendation": (
                        "Publish more videos so performance data "
                        "can be analyzed."
                    ),
                }
            ]
        }

    recommendations = []

    total_views = sum(
        video.get("views", 0)
        for video in ranked_videos
    )

    total_likes = sum(
        video.get("likes", 0)
        for video in ranked_videos
    )

    total_comments = sum(
        video.get("comments", 0)
        for video in ranked_videos
    )

    video_count = len(ranked_videos)

    average_views = (
        total_views / video_count
        if video_count
        else 0
    )

    engagement_rate = 0.0

    if total_views > 0:
        engagement_rate = (
            (total_likes + total_comments)
            / total_views
        ) * 100

    best_video = ranked_videos[0]

    recommendations.append(
        {
            "priority": "high",
            "category": "content_strategy",
            "recommendation": (
                f"Analyze and create more content similar to "
                f"'{best_video.get('title', 'your best-performing video')}'."
            ),
        }
    )

    if average_views < 100:
        recommendations.append(
            {
                "priority": "high",
                "category": "discoverability",
                "recommendation": (
                    "Improve video titles, thumbnails, keywords, "
                    "and topic selection to increase discoverability."
                ),
            }
        )
    else:
        recommendations.append(
            {
                "priority": "medium",
                "category": "discoverability",
                "recommendation": (
                    "Continue testing stronger titles and thumbnails "
                    "to improve click-through potential."
                ),
            }
        )

    if engagement_rate < 2:
        recommendations.append(
            {
                "priority": "high",
                "category": "engagement",
                "recommendation": (
                    "Encourage viewers to like, comment, and share "
                    "your videos using clear calls to action."
                ),
            }
        )
    else:
        recommendations.append(
            {
                "priority": "medium",
                "category": "engagement",
                "recommendation": (
                    "Your engagement is healthy. Continue asking "
                    "questions and responding to audience comments."
                ),
            }
        )

    score = growth_score_result.get(
        "growth_score",
        0,
    )

    if score < 40:
        recommendations.append(
            {
                "priority": "high",
                "category": "growth",
                "recommendation": (
                    "Focus on consistent publishing and improving "
                    "video performance before expanding to new formats."
                ),
            }
        )
    elif score < 70:
        recommendations.append(
            {
                "priority": "medium",
                "category": "growth",
                "recommendation": (
                    "Your channel has growth potential. Experiment "
                    "with successful topics and content formats."
                ),
            }
        )
    else:
        recommendations.append(
            {
                "priority": "medium",
                "category": "growth",
                "recommendation": (
                    "Your growth indicators are strong. Scale successful "
                    "content while maintaining audience engagement."
                ),
            }
        )

    return {
        "growth_score": score,
        "average_views": round(
            average_views,
            2,
        ),
        "engagement_rate": round(
            engagement_rate,
            2,
        ),
        "best_video": {
            "video_id": best_video.get("video_id"),
            "title": best_video.get("title"),
            "views": best_video.get("views", 0),
        },
        "recommendations": recommendations,
    }