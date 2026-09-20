from pathlib import Path
from unittest.mock import patch

from app.services.creator_accounts import youtube_real_oauth
from app.services.publishing.real_youtube_publish import (
    prepare_real_publish,
    publish_video,
    youtube_upload_ready,
)


def test_youtube_oauth_router_has_required_routes():
    from app.api.oauth import router

    routes = {r.path for r in router.routes if hasattr(r, "path")}

    assert "/oauth/youtube/login" in routes
    assert "/oauth/youtube/connect" in routes
    assert "/oauth/youtube/callback" in routes


def test_oauth_state_storage_functions_exist():
    assert hasattr(youtube_real_oauth, "create_oauth_state")
    assert hasattr(youtube_real_oauth, "consume_oauth_state")


def test_missing_token_is_authorization_required(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value=None,
    ):
        result = prepare_real_publish(
            user_id="test-user",
            account_id="test-account",
            video_path=str(video),
            title="N1MOX30 Batch 5 Test",
        )

    assert result["status"] == "authorization_required"


def test_real_publish_stays_disabled():
    with patch.dict(
        "os.environ",
        {"N1MOX_ALLOW_REAL_PUBLISH": "false"},
        clear=False,
    ):
        result = youtube_upload_ready()

    assert result["ready"] is False


def test_publish_never_starts_without_authorization(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value=None,
    ):
        result = publish_video(
            account_id="test-account",
            video_path=str(video),
            title="N1MOX30 Batch 5 Safety Test",
        )

    assert result["status"] in {
        "authorization_required",
        "blocked",
    }
