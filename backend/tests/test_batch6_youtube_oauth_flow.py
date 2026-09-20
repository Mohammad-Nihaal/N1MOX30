import os
from unittest.mock import patch

from fastapi.testclient import TestClient


def test_oauth_routes_are_reachable():
    from app.main import app

    client = TestClient(app)

    for path in [
        "/oauth/youtube/login",
        "/oauth/youtube/connect",
    ]:
        response = client.get(path, follow_redirects=False)

        # OAuth endpoints may redirect to Google or return a configuration error.
        # They must not return 404/405.
        assert response.status_code not in (404, 405)


def test_youtube_callback_route_is_reachable():
    from app.main import app

    client = TestClient(app)

    response = client.get(
        "/oauth/youtube/callback",
        params={"code": "test-code"},
        follow_redirects=False,
    )

    assert response.status_code not in (404, 405)


def test_oauth_state_helpers_are_configuration_gated():
    from app.services.creator_accounts import youtube_real_oauth

    create = getattr(youtube_real_oauth, "create_oauth_state", None)
    consume = getattr(youtube_real_oauth, "consume_oauth_state", None)

    assert callable(create)
    assert callable(consume)

    # OAuth state creation must refuse to operate when OAuth
    # configuration is absent. This prevents unauthenticated
    # state generation in an unconfigured environment.
    try:
        create(900006, "batch6-account")
    except RuntimeError as exc:
        assert "OAuth is not configured" in str(exc)
    else:
        # If the environment is configured, verify that a state
        # can actually be generated.
        state = create(900006, "batch6-account")
        assert state

        consumed = consume(state)
        assert consumed is not None


def test_google_oauth_configuration_present():
    client_id = os.getenv("GOOGLE_CLIENT_ID") or os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET") or os.getenv("YOUTUBE_CLIENT_SECRET")
    redirect_uri = (
        os.getenv("GOOGLE_REDIRECT_URI")
        or os.getenv("YOUTUBE_REDIRECT_URI")
    )

    # Configuration may be intentionally hidden in CI/test environments.
    # Verify the settings keys are available through the application's settings object.
    from app.core.config import settings

    configured_id = (
        getattr(settings, "google_client_id", None)
        or getattr(settings, "youtube_client_id", None)
        or client_id
    )

    configured_secret = (
        getattr(settings, "google_client_secret", None)
        or getattr(settings, "youtube_client_secret", None)
        or client_secret
    )

    configured_redirect = (
        getattr(settings, "google_redirect_uri", None)
        or getattr(settings, "youtube_redirect_uri", None)
        or redirect_uri
    )

    assert configured_id
    assert configured_secret
    assert configured_redirect
    assert "youtube/callback" in configured_redirect


def test_real_publish_remains_disabled():
    from app.services.publishing.real_youtube_publish import youtube_upload_ready

    with patch.dict(
        os.environ,
        {"N1MOX_ALLOW_REAL_PUBLISH": "false"},
        clear=False,
    ):
        result = youtube_upload_ready()

    assert result["ready"] is False

