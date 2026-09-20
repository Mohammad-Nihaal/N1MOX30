import requests
from unittest.mock import patch


def test_retryable_statuses_are_defined():
    from app.services.publishing import real_youtube_publish

    source = open(
        real_youtube_publish.__file__,
        "r",
        encoding="utf-8",
    ).read()

    # Real uploader must explicitly account for transient YouTube failures.
    for status in ["429", "500", "502", "503", "504"]:
        assert status in source


def test_publisher_contains_retry_backoff_logic():
    from app.services.publishing import real_youtube_publish

    source = open(
        real_youtube_publish.__file__,
        "r",
        encoding="utf-8",
    ).read()

    assert "retry" in source.lower()
    assert "time.sleep" in source or "sleep(" in source
    assert "sleep" in source.lower()


def test_retryable_upload_failure_does_not_fake_success(tmp_path):
    from app.services.publishing.real_youtube_publish import publish_video

    video = tmp_path / "batch9.mp4"
    video.write_bytes(b"batch9-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value="batch9-token",
    ), patch(
        "app.services.publishing.real_youtube_publish.youtube_upload_ready",
        return_value={"ready": True},
    ), patch(
        "app.services.publishing.real_youtube_publish.requests.post",
        side_effect=requests.RequestException("temporary network failure"),
    ):
        result = publish_video(
            account_id="batch9-account",
            video_path=str(video),
            title="N1MOX30 Batch 9",
        )

    assert result.get("status") != "published"


def test_missing_authorization_never_retries_upload(tmp_path):
    from app.services.publishing.real_youtube_publish import publish_video

    video = tmp_path / "batch9-auth.mp4"
    video.write_bytes(b"batch9-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value=None,
    ), patch(
        "app.services.publishing.real_youtube_publish.requests.post",
    ) as post:
        result = publish_video(
            account_id="batch9-account",
            video_path=str(video),
            title="N1MOX30 Batch 9",
        )

    assert result.get("status") in {
        "authorization_required",
        "blocked",
    }
    post.assert_not_called()


def test_disabled_publish_gate_prevents_network_upload(tmp_path):
    from app.services.publishing.real_youtube_publish import publish_video

    video = tmp_path / "batch9-gate.mp4"
    video.write_bytes(b"batch9-video")

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value="batch9-token",
    ), patch(
        "app.services.publishing.real_youtube_publish.youtube_upload_ready",
        return_value={"ready": False, "message": "disabled"},
    ), patch(
        "app.services.publishing.real_youtube_publish.requests.post",
    ) as post:
        result = publish_video(
            account_id="batch9-account",
            video_path=str(video),
            title="N1MOX30 Batch 9",
        )

    assert result.get("status") == "blocked"
    post.assert_not_called()


