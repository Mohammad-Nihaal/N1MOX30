from urllib.parse import urlencode

from app.core.config import settings


YOUTUBE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)


YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]


def youtube_oauth_configured() -> bool:
    """
    Check whether Google OAuth credentials are configured.
    """

    return bool(
        settings.google_client_id.strip()
        and settings.google_client_secret.strip()
    )


def get_youtube_authorization_url(
    state: str,
) -> str:
    """
    Build the Google OAuth authorization URL.
    """

    if not youtube_oauth_configured():
        raise ValueError(
            "Google OAuth is not configured. "
            "Add GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET to .env."
        )

    redirect_uri = (
        settings.youtube_redirect_uri.strip()
    )

    params = {
        "client_id": (
            settings.google_client_id.strip()
        ),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(YOUTUBE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }

    return (
        f"{YOUTUBE_AUTH_URL}?"
        f"{urlencode(params)}"
    )