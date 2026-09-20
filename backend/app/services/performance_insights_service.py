from __future__ import annotations


def safe_int(value) -> int:
    """
    Safely convert a value to an integer.
    """

    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def safe_float(value) -> float:
    """
    Safely convert a value to a float.
    """

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def calculate_performance_score(
    video: dict,
    average_views: float,
    average_engagement_rate: float,
) -> float:
    """
    Calculate a simple performance score from
    views and engagement.

    Score range is approximately 0 to 100.
    """

    views = safe_int(
        video.get("views")
    )

    engagement_rate = safe_float(
        video.get("engagement_rate")
    )

    view_score = 0.0
    engagement_score = 0.0

    if average_views > 0:
        view_score = min(
            (views / average_views) * 50,
            50,
        )

    if average_engagement_rate > 0:
        engagement_score = min(
            (
                engagement_rate
                / average_engagement_rate
            )
            * 50,
            50,
        )
    elif engagement_rate > 0:
        engagement_score = min(
            engagement_rate * 10,
            50,
        )

    return round(
        view_score + engagement_score,
        2,
    )


def get_performance_label(
    score: float,
) -> str:
    """
    Convert a performance score into a readable label.
    """

    if score >= 80:
        return "excellent"

    if score >= 60:
        return "strong"

    if score >= 40:
        return "average"

    if score >= 20:
        return "below_average"

    return "low"


def get_engagement_label(
    engagement_rate: float,
) -> str:
    """
    Convert engagement rate into a readable label.
    """

    if engagement_rate >= 8:
        return "very_high"

    if engagement_rate >= 5:
        return "high"

    if engagement_rate >= 2:
        return "moderate"

    if engagement_rate > 0:
        return "low"

    return "unknown"


def normalize_video(
    video: dict,
) -> dict:
    """
    Normalize YouTube video data so downstream
    services always receive predictable fields.
    """

    views = safe_int(
        video.get("views")
    )

    likes = safe_int(
        video.get("likes")
    )

    comments = safe_int(
        video.get("comments")
    )

    engagement_rate = safe_float(
        video.get("engagement_rate")
    )

    if engagement_rate == 0 and views > 0:
        engagement_rate = round(
            (
                (likes + comments)
                / views
            )
            * 100,
            2,
        )

    return {
        "video_id": video.get(
            "video_id",
            "",
        ),
        "title": video.get(
            "title",
            "Untitled Video",
        ),
        "published_at": video.get(
            "published_at",
        ),
        "thumbnail_url": video.get(
            "thumbnail_url",
        ),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_rate": engagement_rate,
    }


def build_content_patterns(
    videos: list[dict],
    average_views: float,
) -> dict:
    """
    Detect simple performance patterns from
    the available video data.
    """

    above_average = [
        video
        for video in videos
        if safe_int(video.get("views"))
        >= average_views
    ]

    below_average = [
        video
        for video in videos
        if safe_int(video.get("views"))
        < average_views
    ]

    high_engagement = [
        video
        for video in videos
        if safe_float(
            video.get("engagement_rate")
        )
        >= 5
    ]

    titles = [
        video.get("title", "")
        for video in above_average
        if video.get("title")
    ]

    return {
        "videos_above_average": len(
            above_average
        ),
        "videos_below_average": len(
            below_average
        ),
        "high_engagement_videos": len(
            high_engagement
        ),
        "strongest_titles": titles[:5],
    }


def build_recommendations(
    videos: list[dict],
    best_video: dict | None,
    lowest_video: dict | None,
    average_views: float,
    average_engagement_rate: float,
) -> list[str]:
    """
    Generate actionable creator recommendations.
    """

    recommendations: list[str] = []

    if best_video:
        best_title = best_video.get(
            "title",
            "your top-performing video",
        )

        recommendations.append(
            f'Analyze "{best_title}" and reuse '
            "its strongest topic, hook, format, "
            "or storytelling style."
        )

    if average_engagement_rate < 2:
        recommendations.append(
            "Engagement is currently low. Add stronger "
            "calls to action and encourage viewers to "
            "comment and interact."
        )

    elif average_engagement_rate < 5:
        recommendations.append(
            "Engagement is moderate. Test stronger "
            "questions, calls to action, and audience "
            "interaction prompts."
        )

    else:
        recommendations.append(
            "Engagement is strong. Continue creating "
            "content that encourages meaningful "
            "audience interaction."
        )

    if lowest_video:
        lowest_title = lowest_video.get(
            "title",
            "your lowest-performing video",
        )

        recommendations.append(
            f'Review "{lowest_title}" and compare its '
            "topic, title, and format with your "
            "best-performing videos."
        )

    above_average_count = len(
        [
            video
            for video in videos
            if safe_int(video.get("views"))
            >= average_views
        ]
    )

    if above_average_count <= len(videos) / 2:
        recommendations.append(
            "Test new content ideas and improve hooks "
            "because fewer than half of the analyzed "
            "videos are performing above average."
        )
    else:
        recommendations.append(
            "Several videos are performing above "
            "average. Identify their common content "
            "patterns and repeat them strategically."
        )

    recommendations.append(
        "Track video performance regularly so "
        "N1MOX30 can identify stronger long-term "
        "content trends."
    )

    return recommendations


def generate_creator_summary(
    total_videos: int,
    total_views: int,
    average_views: float,
    average_engagement_rate: float,
    best_video: dict | None,
) -> str:
    """
    Generate a concise creator intelligence summary.
    """

    if total_videos == 0:
        return (
            "No video performance data is currently "
            "available."
        )

    best_title = (
        best_video.get(
            "title",
            "the top-performing video",
        )
        if best_video
        else "the top-performing video"
    )

    return (
        f"Across {total_videos} analyzed videos, "
        f"the channel generated {total_views:,} "
        f"total views with an average of "
        f"{average_views:,.2f} views per video. "
        f"The average engagement rate is "
        f"{average_engagement_rate:.2f}%. "
        f'The strongest current video is '
        f'"{best_title}".'
    )


def generate_performance_insights(
    videos: list[dict],
) -> dict:
    """
    Generate comprehensive YouTube video
    performance intelligence.

    Includes:
    - Summary metrics
    - Ranked videos
    - Performance scores
    - Best and lowest performers
    - Engagement analysis
    - Content patterns
    - Creator recommendations
    """

    if not videos:
        return {
            "status": "no_data",
            "summary": {
                "total_videos": 0,
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "average_views": 0.0,
                "average_likes": 0.0,
                "average_comments": 0.0,
                "average_engagement_rate": 0.0,
            },
            "creator_summary": (
                "No YouTube videos are currently "
                "available for performance analysis."
            ),
            "best_video": None,
            "lowest_video": None,
            "ranked_videos": [],
            "content_patterns": {
                "videos_above_average": 0,
                "videos_below_average": 0,
                "high_engagement_videos": 0,
                "strongest_titles": [],
            },
            "recommendations": [
                "Upload or fetch YouTube videos before "
                "generating performance intelligence."
            ],
        }

    normalized_videos = [
        normalize_video(video)
        for video in videos
    ]

    total_videos = len(
        normalized_videos
    )

    total_views = sum(
        video["views"]
        for video in normalized_videos
    )

    total_likes = sum(
        video["likes"]
        for video in normalized_videos
    )

    total_comments = sum(
        video["comments"]
        for video in normalized_videos
    )

    average_views = round(
        total_views / total_videos,
        2,
    )

    average_likes = round(
        total_likes / total_videos,
        2,
    )

    average_comments = round(
        total_comments / total_videos,
        2,
    )

    average_engagement_rate = round(
        sum(
            video["engagement_rate"]
            for video in normalized_videos
        )
        / total_videos,
        2,
    )

    ranked_videos = []

    for video in normalized_videos:

        performance_score = (
            calculate_performance_score(
                video,
                average_views,
                average_engagement_rate,
            )
        )

        ranked_video = {
            **video,
            "performance_score": performance_score,
            "performance_label": (
                get_performance_label(
                    performance_score
                )
            ),
            "engagement_label": (
                get_engagement_label(
                    video["engagement_rate"]
                )
            ),
        }

        ranked_videos.append(
            ranked_video
        )

    ranked_videos.sort(
        key=lambda video: (
            video["performance_score"],
            video["views"],
        ),
        reverse=True,
    )

    for index, video in enumerate(
        ranked_videos,
        start=1,
    ):
        video["rank"] = index

    best_video = (
        ranked_videos[0]
        if ranked_videos
        else None
    )

    lowest_video = (
        min(
            ranked_videos,
            key=lambda video: (
                video["performance_score"],
                video["views"],
            ),
        )
        if ranked_videos
        else None
    )

    content_patterns = build_content_patterns(
        ranked_videos,
        average_views,
    )

    recommendations = build_recommendations(
        videos=ranked_videos,
        best_video=best_video,
        lowest_video=lowest_video,
        average_views=average_views,
        average_engagement_rate=(
            average_engagement_rate
        ),
    )

    creator_summary = generate_creator_summary(
        total_videos=total_videos,
        total_views=total_views,
        average_views=average_views,
        average_engagement_rate=(
            average_engagement_rate
        ),
        best_video=best_video,
    )

    return {
        "status": "success",
        "summary": {
            "total_videos": total_videos,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_views": average_views,
            "average_likes": average_likes,
            "average_comments": average_comments,
            "average_engagement_rate": (
                average_engagement_rate
            ),
        },
        "creator_summary": creator_summary,
        "best_video": best_video,
        "lowest_video": lowest_video,
        "ranked_videos": ranked_videos,
        "content_patterns": content_patterns,
        "recommendations": recommendations,
    }