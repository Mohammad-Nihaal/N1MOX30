from unittest.mock import patch


def test_youtube_oauth_module_exposes_account_flow():
    from app.services.creator_accounts import youtube_real_oauth

    source = open(
        youtube_real_oauth.__file__,
        "r",
        encoding="utf-8",
    ).read()

    assert "create_oauth_state" in source
    assert "consume_oauth_state" in source
    assert "youtube" in source.lower()


def test_secure_token_store_module_available():
    from app.services.creator_accounts import secure_token_store

    assert secure_token_store is not None


def test_publisher_resolves_account_token():
    from app.services.publishing import real_youtube_publish

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value="batch7-token",
    ):
        token = real_youtube_publish._token_for_account(
            "batch7-account"
        )

    assert token == "batch7-token"


def test_missing_account_token_blocks_authorized_publish(tmp_path):
    from app.services.publishing.real_youtube_publish import (
        prepare_real_publish,
    )

    video = tmp_path / "batch7.mp4"
    video.write_bytes(b"batch7-test-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value=None,
    ):
        result = prepare_real_publish(
            user_id="batch7-user",
            account_id="batch7-account",
            video_path=str(video),
            title="N1MOX30 Batch 7",
        )

    assert result["status"] == "authorization_required"


def test_authorized_account_still_respects_publish_gate(tmp_path):
    from app.services.publishing.real_youtube_publish import (
        prepare_real_publish,
    )

    video = tmp_path / "batch7-authorized.mp4"
    video.write_bytes(b"batch7-authorized-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value="batch7-token",
    ):
        result = prepare_real_publish(
            user_id="batch7-user",
            account_id="batch7-account",
            video_path=str(video),
            title="N1MOX30 Batch 7",
        )

    assert result["status"] == "blocked"
