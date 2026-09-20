import os
from pathlib import Path
from unittest.mock import patch


def test_real_publish_is_blocked_by_default():
    from app.services.publishing.real_youtube_publish import (
        publish_video,
    )

    previous = os.environ.get("N1MOX_ALLOW_REAL_PUBLISH")

    os.environ["N1MOX_ALLOW_REAL_PUBLISH"] = "false"

    try:
        with __import__("tempfile").TemporaryDirectory() as tmp:
            video = Path(tmp) / "queue-test.mp4"
            video.write_bytes(b"N1MOX30-QUEUE-TEST")

            result = publish_video(
                account_id=1,
                video_path=video,
                title="N1MOX30 Queue Test",
                description="Local queue integration test",
                tags=["nimox30"],
                privacy_status="private",
            )

            assert result["status"] == "blocked"
            assert result["reason"] == "real_publish_not_ready"

    finally:
        if previous is None:
            os.environ.pop("N1MOX_ALLOW_REAL_PUBLISH", None)
        else:
            os.environ["N1MOX_ALLOW_REAL_PUBLISH"] = previous


def test_publish_metadata_contract():
    from app.services.publishing.real_youtube_publish import (
        _metadata,
    )

    data = _metadata(
        title="Queue Test",
        description="Testing queue metadata",
        tags=["nimox30", "creator"],
        privacy_status="private",
    )

    assert data["snippet"]["title"] == "Queue Test"
    assert data["status"]["privacyStatus"] == "private"
    assert data["status"]["selfDeclaredMadeForKids"] is False


def test_resumable_upload_session_and_completion():
    from app.services.publishing import real_youtube_publish as publisher

    class FakeResponse:
        def __init__(self, status_code, headers=None, payload=None):
            self.status_code = status_code
            self.headers = headers or {}
            self._payload = payload or {}

        @property
        def text(self):
            return str(self._payload)

        def json(self):
            return self._payload

    responses = [
        FakeResponse(
            200,
            headers={
                "Location": "https://upload.youtube.test/session/123"
            },
        ),
        FakeResponse(
            200,
            payload={
                "id": "N1MOX30_TEST_VIDEO"
            },
        ),
    ]

    def fake_post(*args, **kwargs):
        return responses.pop(0)

    def fake_put(*args, **kwargs):
        return responses.pop(0)

    with __import__("tempfile").TemporaryDirectory() as tmp:

        video = Path(tmp) / "test.mp4"

        video.write_bytes(
            b"N1MOX30-FAKE-VIDEO-DATA"
        )

        with patch.object(
            publisher.requests,
            "post",
            side_effect=fake_post,
        ), patch.object(
            publisher.requests,
            "put",
            side_effect=fake_put,
        ), patch.object(
            publisher,
            "_token_for_account",
            return_value="TEST_ACCESS_TOKEN",
        ), patch.object(
            publisher,
            "youtube_upload_ready",
            return_value={
                "configured": True,
                "token_security_ready": True,
                "publishing_enabled": True,
                "ready": True,
            },
        ):

            result = publisher.publish_video(
                account_id=1,
                video_path=video,
                title="N1MOX30 Test Upload",
                description="Mock upload",
                tags=["nimox30"],
                privacy_status="private",
            )

        assert result["status"] == "published"
        assert result["video_id"] == "N1MOX30_TEST_VIDEO"
        assert result["privacy_status"] == "private"


def test_upload_failure_is_returned_safely():
    from app.services.publishing import real_youtube_publish as publisher

    class FakeResponse:
        status_code = 403
        headers = {}

        @property
        def text(self):
            return "Forbidden"

    with __import__("tempfile").TemporaryDirectory() as tmp:

        video = Path(tmp) / "test.mp4"
        video.write_bytes(b"N1MOX30-TEST")

        with patch.object(
            publisher.requests,
            "post",
            return_value=FakeResponse(),
        ), patch.object(
            publisher,
            "_token_for_account",
            return_value="TEST_ACCESS_TOKEN",
        ), patch.object(
            publisher,
            "youtube_upload_ready",
            return_value={
                "configured": True,
                "token_security_ready": True,
                "publishing_enabled": True,
                "ready": True,
            },
        ):

            result = publisher.publish_video(
                account_id=1,
                video_path=video,
                title="Failure Test",
                privacy_status="private",
            )

        assert result["status"] == "failed"
        assert result["reason"] == "upload_session_creation_failed"