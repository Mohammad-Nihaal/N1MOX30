def calculate_growth_score(
    videos: list[dict],
) -> dict:
    """Calculate a simple creator growth score from 0 to 100."""

    if not videos:
        return {
            "growth_score": 0,
            "score_level": "No Data",
            "metrics": {
                "average_views": 0,
                "average_engagement_rate": 0.0,
                "videos_analyzed": 0,
                "consistency_score": 0.0,
            },
        }

    total_videos = len(videos)

    total_views = sum(
        int(video.get("views", 0))
        for video in videos
    )

    average_views = total_views / total_videos

    average_engagement_rate = (
        sum(
            float(video.get("engagement_rate", 0))
            for video in videos
        )
        / total_videos
    )

    view_score = min(
        average_views / 1000 * 40,
        40,
    )

    engagement_score = min(
        average_engagement_rate / 10 * 30,
        30,
    )

    volume_score = min(
        total_videos / 10 * 15,
        15,
    )

    view_values = [
        int(video.get("views", 0))
        for video in videos
    ]

    if average_views > 0:
        lowest_views = min(view_values)

        consistency_ratio = (
            lowest_views / average_views
        )

        consistency_score = min(
            consistency_ratio * 15,
            15,
        )
    else:
        consistency_score = 0.0

    growth_score = round(
        view_score
        + engagement_score
        + volume_score
        + consistency_score
    )

    growth_score = max(
        0,
        min(growth_score, 100),
    )

    if growth_score >= 80:
        score_level = "Excellent"
    elif growth_score >= 60:
        score_level = "Strong"
    elif growth_score >= 40:
        score_level = "Growing"
    elif growth_score >= 20:
        score_level = "Developing"
    else:
        score_level = "Early Stage"

    return {
        "growth_score": growth_score,
        "score_level": score_level,
        "metrics": {
            "average_views": round(
                average_views,
                2,
            ),
            "average_engagement_rate": round(
                average_engagement_rate,
                2,
            ),
            "videos_analyzed": total_videos,
            "consistency_score": round(
                consistency_score,
                2,
            ),
        },
    }