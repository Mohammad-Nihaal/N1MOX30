from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.user import User
from app.services.analytics_service import (
    refresh_account_token_if_needed,
)
from app.services.performance_insights_service import (
    generate_performance_insights,
)
from app.services.youtube_service import (
    get_recent_youtube_videos,
    get_youtube_channel_details,
    get_youtube_video_statistics,
)


router = APIRouter(
    prefix="/performance",
    tags=["Video Performance Intelligence"],
)


def get_authorized_youtube_account(
    current_user: User,
    db: Session,
) -> ConnectedAccount:
    """
    Get the current user's active and authorized
    YouTube account.
    """

    connected_account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.platform == "youtube",
            ConnectedAccount.is_active.is_(True),
            ConnectedAccount.is_authorized.is_(True),
        )
        .first()
    )

    if not connected_account:
        raise HTTPException(
            status_code=404,
            detail=(
                "No authorized YouTube account found."
            ),
        )

    return connected_account


@router.get("/youtube")
def get_youtube_video_performance(
    max_results: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze recent YouTube videos and return
    content performance intelligence.
    """

    if max_results < 1 or max_results > 50:
        raise HTTPException(
            status_code=400,
            detail=(
                "max_results must be between 1 and 50."
            ),
        )

    connected_account = get_authorized_youtube_account(
        current_user,
        db,
    )

    try:
        # Refresh the OAuth token when needed.
        connected_account = (
            refresh_account_token_if_needed(
                connected_account,
                db,
            )
        )

        if not connected_account.access_token:
            raise ValueError(
                "YouTube access token is missing."
            )

        # Get channel details including the uploads playlist.
        channel = get_youtube_channel_details(
            connected_account.access_token
        )

        uploads_playlist_id = channel.get(
            "uploads_playlist_id"
        )

        if not uploads_playlist_id:
            raise ValueError(
                "Could not find the YouTube uploads "
                "playlist for this channel."
            )

        # Get recent uploaded videos.
        recent_videos = get_recent_youtube_videos(
            access_token=connected_account.access_token,
            uploads_playlist_id=uploads_playlist_id,
            max_results=max_results,
        )

        # Remove playlist items without a valid video ID.
        recent_videos = [
            video
            for video in recent_videos
            if video.get("video_id")
        ]

        if not recent_videos:
            return {
                "status": "success",
                "channel": {
                    "channel_id": channel.get(
                        "channel_id"
                    ),
                    "channel_name": channel.get(
                        "channel_name"
                    ),
                    "subscribers": channel.get(
                        "subscriber_count",
                        0,
                    ),
                    "total_views": channel.get(
                        "view_count",
                        0,
                    ),
                    "total_videos": channel.get(
                        "video_count",
                        0,
                    ),
                },
                "total_videos_analyzed": 0,
                "videos": [],
                "best_performing_video": None,
                "worst_performing_video": None,
                "performance_insights": [
                    "No recent videos were found to analyze."
                ],
                "recommendations": [
                    "Publish videos and return later to "
                    "analyze content performance."
                ],
            }

        video_ids = [
            video["video_id"]
            for video in recent_videos
        ]

        # Get statistics for the recent videos.
        video_statistics = (
            get_youtube_video_statistics(
                access_token=connected_account.access_token,
                video_ids=video_ids,
            )
        )

        # Build a lookup dictionary.
        statistics_by_id = {
            video["video_id"]: video
            for video in video_statistics
            if video.get("video_id")
        }

        analyzed_videos = []

        for recent_video in recent_videos:

            video_id = recent_video[
                "video_id"
            ]

            statistics = statistics_by_id.get(
                video_id,
                {},
            )

            views = int(
                statistics.get("views", 0)
            )

            likes = int(
                statistics.get("likes", 0)
            )

            comments = int(
                statistics.get("comments", 0)
            )

            engagement_count = (
                likes + comments
            )

            engagement_rate = 0.0

            if views > 0:
                engagement_rate = round(
                    (
                        engagement_count
                        / views
                    )
                    * 100,
                    2,
                )

            analyzed_videos.append(
                {
                    "video_id": video_id,
                    "title": (
                        statistics.get("title")
                        or recent_video.get("title")
                        or "Untitled Video"
                    ),
                    "published_at": (
                        statistics.get("published_at")
                        or recent_video.get(
                            "published_at"
                        )
                    ),
                    "thumbnail": (
                        statistics.get("thumbnail")
                        or recent_video.get(
                            "thumbnail"
                        )
                    ),
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "engagement_count": (
                        engagement_count
                    ),
                    "engagement_rate": (
                        engagement_rate
                    ),
                }
            )

        # Rank videos by views.
        videos_by_views = sorted(
            analyzed_videos,
            key=lambda video: video["views"],
            reverse=True,
        )

        for index, video in enumerate(
            videos_by_views,
            start=1,
        ):
            video["performance_rank"] = index

        # Best and worst by views.
        best_video = (
            videos_by_views[0]
            if videos_by_views
            else None
        )

        worst_video = (
            videos_by_views[-1]
            if videos_by_views
            else None
        )

        # Generate intelligence from actual metrics.
        intelligence = generate_performance_insights(
            videos_by_views
        )

        return {
            "status": "success",
            "channel": {
                "channel_id": channel.get(
                    "channel_id"
                ),
                "channel_name": channel.get(
                    "channel_name"
                ),
                "subscribers": channel.get(
                    "subscriber_count",
                    0,
                ),
                "total_views": channel.get(
                    "view_count",
                    0,
                ),
                "total_videos": channel.get(
                    "video_count",
                    0,
                ),
            },
            "total_videos_analyzed": len(
                videos_by_views
            ),
            "videos": videos_by_views,
            "best_performing_video": best_video,
            "worst_performing_video": worst_video,
            "performance_summary": intelligence.get(
                "creator_summary"
            ),
            "performance_insights": intelligence.get(
                "insights",
                intelligence.get("content_patterns", {}),
            ),
            "recommendations": (
                intelligence.get(
                    "recommendations",
                    [],
                )
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to analyze YouTube video "
                f"performance: {str(error)}"
            ),
        )