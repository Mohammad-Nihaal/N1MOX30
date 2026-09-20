from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

YOUTUBE_CHANNELS_URL = (
    "https://www.googleapis.com/youtube/v3/channels"
)

YOUTUBE_PLAYLIST_ITEMS_URL = (
    "https://www.googleapis.com/youtube/v3/playlistItems"
)

YOUTUBE_VIDEOS_URL = (
    "https://www.googleapis.com/youtube/v3/videos"
)


def youtube_oauth_configured() -> bool:
    """Check whether Google OAuth credentials are configured."""

    return bool(
        settings.google_client_id
        and settings.google_client_secret
    )


def get_token_expiration(
    expires_in: int | str | None,
) -> datetime | None:
    """Convert Google's expires_in value into a UTC datetime."""

    if not expires_in:
        return None

    return (
        datetime.now(timezone.utc)
        + timedelta(seconds=int(expires_in))
    )


def is_token_expired(
    token_expires_at: datetime | None,
    buffer_seconds: int = 120,
) -> bool:
    """
    Check whether a token has expired or will expire soon.

    A small buffer prevents API requests from failing when the token
    expires while a request is being processed.
    """

    if token_expires_at is None:
        return True

    now = datetime.now(timezone.utc)

    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(
            tzinfo=timezone.utc
        )

    expiration_with_buffer = (
        token_expires_at
        - timedelta(seconds=buffer_seconds)
    )

    return now >= expiration_with_buffer


def exchange_youtube_code(
    code: str,
) -> dict:
    """Exchange a Google OAuth authorization code for tokens."""

    if not youtube_oauth_configured():
        raise ValueError(
            "Google OAuth is not configured. "
            "Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env."
        )

    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.youtube_redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data=data,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact Google's authentication service."
        ) from error

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get(
                "error_description",
                error_data.get(
                    "error",
                    "Unknown Google authentication error.",
                ),
            )
        except ValueError:
            error_message = (
                "Google token exchange failed."
            )

        raise ValueError(
            f"Google token exchange failed: {error_message}"
        )

    token_data = response.json()

    access_token = token_data.get(
        "access_token"
    )

    if not access_token:
        raise ValueError(
            "Google did not return an access token."
        )

    return {
        "access_token": access_token,
        "refresh_token": token_data.get(
            "refresh_token"
        ),
        "token_expires_at": get_token_expiration(
            token_data.get("expires_in")
        ),
        "scope": token_data.get("scope"),
        "token_type": token_data.get(
            "token_type"
        ),
    }


def refresh_youtube_access_token(
    refresh_token: str,
) -> dict:
    """Use a Google refresh token to obtain a new access token."""

    if not youtube_oauth_configured():
        raise ValueError(
            "Google OAuth is not configured."
        )

    if not refresh_token:
        raise ValueError(
            "YouTube refresh token is missing. "
            "Please reconnect your YouTube account."
        )

    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    try:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data=data,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact Google's authentication service."
        ) from error

    if response.status_code != 200:
        try:
            error_data = response.json()

            error_message = error_data.get(
                "error_description",
                error_data.get(
                    "error",
                    "Unknown token refresh error.",
                ),
            )
        except ValueError:
            error_message = (
                "Failed to refresh YouTube access token."
            )

        raise ValueError(
            f"Failed to refresh YouTube access token: "
            f"{error_message}"
        )

    token_data = response.json()

    access_token = token_data.get(
        "access_token"
    )

    if not access_token:
        raise ValueError(
            "Google did not return a new access token."
        )

    return {
        "access_token": access_token,
        "token_expires_at": get_token_expiration(
            token_data.get("expires_in")
        ),
    }


def get_youtube_channel(
    access_token: str,
) -> dict:
    """Get the authenticated user's YouTube channel."""

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
    }

    params = {
        "part": "id,snippet",
        "mine": "true",
    }

    try:
        response = httpx.get(
            YOUTUBE_CHANNELS_URL,
            headers=headers,
            params=params,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact the YouTube API."
        ) from error

    if response.status_code != 200:
        raise ValueError(
            get_youtube_api_error(response)
        )

    data = response.json()

    items = data.get("items", [])

    if not items:
        raise ValueError(
            "No YouTube channel was found for this "
            "Google account."
        )

    channel = items[0]

    return {
        "channel_id": channel["id"],
        "channel_name": channel["snippet"]["title"],
    }


def get_youtube_channel_details(
    access_token: str,
) -> dict:
    """Get detailed statistics for the authenticated YouTube channel."""

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
    }

    params = {
        "part": (
            "snippet,statistics,contentDetails"
        ),
        "mine": "true",
    }

    try:
        response = httpx.get(
            YOUTUBE_CHANNELS_URL,
            headers=headers,
            params=params,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact the YouTube API."
        ) from error

    if response.status_code != 200:
        raise ValueError(
            get_youtube_api_error(response)
        )

    data = response.json()

    items = data.get("items", [])

    if not items:
        raise ValueError(
            "No YouTube channel was found."
        )

    channel = items[0]

    statistics = channel.get(
        "statistics",
        {},
    )

    snippet = channel.get(
        "snippet",
        {},
    )

    content_details = channel.get(
        "contentDetails",
        {},
    )

    uploads_playlist_id = (
        content_details
        .get("relatedPlaylists", {})
        .get("uploads")
    )

    return {
        "channel_id": channel.get("id"),
        "channel_name": snippet.get("title"),
        "description": snippet.get(
            "description"
        ),
        "thumbnail": (
            snippet
            .get("thumbnails", {})
            .get("high", {})
            .get("url")
        ),
        "subscriber_count": int(
            statistics.get(
                "subscriberCount",
                0,
            )
        ),
        "view_count": int(
            statistics.get(
                "viewCount",
                0,
            )
        ),
        "video_count": int(
            statistics.get(
                "videoCount",
                0,
            )
        ),
        "uploads_playlist_id": (
            uploads_playlist_id
        ),
    }


def get_recent_youtube_videos(
    access_token: str,
    uploads_playlist_id: str,
    max_results: int = 10,
) -> list[dict]:
    """Get recent videos from the channel uploads playlist."""

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
    }

    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": max_results,
    }

    try:
        response = httpx.get(
            YOUTUBE_PLAYLIST_ITEMS_URL,
            headers=headers,
            params=params,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact the YouTube API."
        ) from error

    if response.status_code != 200:
        raise ValueError(
            get_youtube_api_error(response)
        )

    data = response.json()

    videos = []

    for item in data.get("items", []):

        snippet = item.get(
            "snippet",
            {},
        )

        content_details = item.get(
            "contentDetails",
            {},
        )

        video_id = (
            content_details.get("videoId")
            or snippet
            .get("resourceId", {})
            .get("videoId")
        )

        videos.append(
            {
                "video_id": video_id,
                "title": snippet.get("title"),
                "description": snippet.get(
                    "description"
                ),
                "published_at": (
                    content_details.get(
                        "videoPublishedAt"
                    )
                    or snippet.get(
                        "publishedAt"
                    )
                ),
                "thumbnail": (
                    snippet
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                ),
            }
        )

    return videos


def get_youtube_video_statistics(
    access_token: str,
    video_ids: list[str],
) -> list[dict]:
    """Get statistics for multiple YouTube videos."""

    if not video_ids:
        return []

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
    }

    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
    }

    try:
        response = httpx.get(
            YOUTUBE_VIDEOS_URL,
            headers=headers,
            params=params,
            timeout=30.0,
        )
    except httpx.RequestError as error:
        raise ValueError(
            "Unable to contact the YouTube API."
        ) from error

    if response.status_code != 200:
        raise ValueError(
            get_youtube_api_error(response)
        )

    data = response.json()

    videos = []

    for item in data.get("items", []):

        snippet = item.get(
            "snippet",
            {},
        )

        statistics = item.get(
            "statistics",
            {},
        )

        videos.append(
            {
                "video_id": item.get("id"),
                "title": snippet.get("title"),
                "published_at": snippet.get(
                    "publishedAt"
                ),
                "thumbnail": (
                    snippet
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                ),
                "views": int(
                    statistics.get(
                        "viewCount",
                        0,
                    )
                ),
                "likes": int(
                    statistics.get(
                        "likeCount",
                        0,
                    )
                ),
                "comments": int(
                    statistics.get(
                        "commentCount",
                        0,
                    )
                ),
            }
        )

    return videos


def get_youtube_api_error(
    response: httpx.Response,
) -> str:
    """Convert a YouTube API error into a useful message."""

    try:
        error_data = response.json()

        error = error_data.get(
            "error",
            {},
        )

        message = error.get("message")

        if message:
            return (
                f"YouTube API error: {message}"
            )

    except ValueError:
        pass

    if response.status_code == 401:
        return (
            "YouTube authorization failed. "
            "Please reconnect your YouTube account."
        )

    if response.status_code == 403:
        return (
            "YouTube access was denied. Check OAuth "
            "permissions or YouTube API quota."
        )

    return (
        "Failed to retrieve data from the "
        "YouTube API."
    )