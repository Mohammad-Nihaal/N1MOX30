def calculate_engagement_rate(
    views: int,
    likes: int,
    comments: int,
) -> float:
    """Calculate engagement percentage."""

    if views <= 0:
        return 0.0

    return round(
        ((likes + comments) / views) * 100,
        2,
    )


def rank_youtube_videos(
    videos: list[dict],
) -> list[dict]:
    """Rank YouTube videos by performance."""

    ranked_videos = []

    for video in videos:
        views = int(video.get("views", 0))
        likes = int(video.get("likes", 0))
        comments = int(video.get("comments", 0))

        engagement_rate = calculate_engagement_rate(
            views=views,
            likes=likes,
            comments=comments,
        )

        ranked_videos.append(
            {
                **video,
                "engagement_rate": engagement_rate,
            }
        )

    ranked_videos.sort(
        key=lambda video: (
            video["views"],
            video["engagement_rate"],
        ),
        reverse=True,
    )

    for index, video in enumerate(
        ranked_videos,
        start=1,
    ):
        video["rank"] = index

    return ranked_videos