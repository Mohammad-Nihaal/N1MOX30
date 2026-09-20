from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.user import User

from app.services.content_strategy_service import (
    generate_content_strategy,
)
from app.services.growth_recommendation_service import (
    generate_growth_recommendations,
)
from app.services.growth_score_service import (
    calculate_growth_score,
)
from app.services.performance_insights_service import (
    generate_performance_insights,
)
from app.services.video_performance_service import (
    rank_youtube_videos,
)
from app.services.youtube_service import (
    get_recent_youtube_videos,
    get_youtube_channel_details,
    get_youtube_video_statistics,
    is_token_expired,
    refresh_youtube_access_token,
)


router = APIRouter(
    prefix="/youtube",
    tags=["YouTube Dashboard"],
)


def get_authorized_youtube_account(
    current_user: User,
    db: Session,
) -> ConnectedAccount:
    """Get the user's authorized YouTube account."""

    connected_account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id
            == current_user.id,
            ConnectedAccount.platform
            == "youtube",
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

    if not connected_account.access_token:
        raise HTTPException(
            status_code=400,
            detail=(
                "YouTube access token is missing."
            ),
        )

    return connected_account


def get_valid_youtube_access_token(
    connected_account: ConnectedAccount,
    db: Session,
) -> str:
    """
    Return a valid YouTube access token.

    If the stored token is expired or close to expiry,
    automatically refresh it and save the new token.
    """

    token_expired = is_token_expired(
        connected_account.token_expires_at
    )

    if not token_expired:
        return connected_account.access_token

    try:
        refreshed_token = (
            refresh_youtube_access_token(
                connected_account.refresh_token
            )
        )

        connected_account.access_token = (
            refreshed_token["access_token"]
        )

        connected_account.token_expires_at = (
            refreshed_token[
                "token_expires_at"
            ]
        )

        connected_account.is_active = True
        connected_account.is_authorized = True

        db.commit()

        db.refresh(connected_account)

        return connected_account.access_token

    except ValueError as error:

        connected_account.is_authorized = False

        db.commit()

        raise HTTPException(
            status_code=401,
            detail=(
                "Your YouTube session could not be "
                f"refreshed: {str(error)}"
            ),
        )


def get_youtube_videos_with_statistics(
    access_token: str,
    max_results: int = 10,
) -> tuple[dict, list[dict]]:
    """
    Get channel details and recent videos
    with their statistics.
    """

    channel = get_youtube_channel_details(
        access_token
    )

    uploads_playlist_id = channel.get(
        "uploads_playlist_id"
    )

    recent_videos = []

    if not uploads_playlist_id:
        return channel, recent_videos

    recent_videos = get_recent_youtube_videos(
        access_token=access_token,
        uploads_playlist_id=uploads_playlist_id,
        max_results=max_results,
    )

    video_ids = [
        video["video_id"]
        for video in recent_videos
        if video.get("video_id")
    ]

    if not video_ids:
        return channel, recent_videos

    statistics = (
        get_youtube_video_statistics(
            access_token=access_token,
            video_ids=video_ids,
        )
    )

    statistics_by_id = {
        video["video_id"]: video
        for video in statistics
    }

    for video in recent_videos:

        video_id = video.get("video_id")

        stats = statistics_by_id.get(
            video_id,
            {},
        )

        video["views"] = stats.get(
            "views",
            0,
        )

        video["likes"] = stats.get(
            "likes",
            0,
        )

        video["comments"] = stats.get(
            "comments",
            0,
        )

    return channel, recent_videos


@router.get("/dashboard")
def get_youtube_dashboard(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's YouTube dashboard."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, recent_videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel": channel,
            "recent_videos": recent_videos,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/performance")
def get_youtube_performance(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Rank recent YouTube videos by performance."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        ranked_videos = (
            rank_youtube_videos(videos)
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel_id": channel.get(
                "channel_id"
            ),
            "channel_name": channel.get(
                "channel_name"
            ),
            "total_videos_analyzed": len(
                ranked_videos
            ),
            "ranking_method": (
                "Videos are ranked primarily by "
                "views, with engagement rate used "
                "as a secondary factor."
            ),
            "videos": ranked_videos,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/insights")
def get_youtube_insights(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Generate performance insights."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        ranked_videos = (
            rank_youtube_videos(videos)
        )

        insights = (
            generate_performance_insights(
                ranked_videos
            )
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel_id": channel.get(
                "channel_id"
            ),
            "channel_name": channel.get(
                "channel_name"
            ),
            **insights,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/growth-score")
def get_youtube_growth_score(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Calculate the creator growth score."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        ranked_videos = (
            rank_youtube_videos(videos)
        )

        growth_result = (
            calculate_growth_score(
                ranked_videos
            )
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel_id": channel.get(
                "channel_id"
            ),
            "channel_name": channel.get(
                "channel_name"
            ),
            **growth_result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/recommendations")
def get_youtube_recommendations(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Generate actionable growth recommendations."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        ranked_videos = (
            rank_youtube_videos(videos)
        )

        growth_result = (
            calculate_growth_score(
                ranked_videos
            )
        )

        recommendations = (
            generate_growth_recommendations(
                ranked_videos=ranked_videos,
                growth_score_result=growth_result,
            )
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel_id": channel.get(
                "channel_id"
            ),
            "channel_name": channel.get(
                "channel_name"
            ),
            **recommendations,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/content-strategy")
def get_youtube_content_strategy(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Generate a personalized YouTube content strategy."""

    connected_account = (
        get_authorized_youtube_account(
            current_user,
            db,
        )
    )

    access_token = (
        get_valid_youtube_access_token(
            connected_account,
            db,
        )
    )

    try:
        channel, videos = (
            get_youtube_videos_with_statistics(
                access_token,
                max_results=10,
            )
        )

        ranked_videos = (
            rank_youtube_videos(videos)
        )

        growth_result = (
            calculate_growth_score(
                ranked_videos
            )
        )

        strategy = generate_content_strategy(
            ranked_videos=ranked_videos,
            growth_score_result=growth_result,
        )

        return {
            "platform": "youtube",
            "account_id": connected_account.id,
            "channel_id": channel.get(
                "channel_id"
            ),
            "channel_name": channel.get(
                "channel_name"
            ),
            **strategy,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )