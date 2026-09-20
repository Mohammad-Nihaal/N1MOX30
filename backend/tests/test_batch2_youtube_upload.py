from pathlib import Path
import tempfile

from app.services.publishing.real_youtube_publish import (
    _metadata,
    _video_path,
    youtube_upload_ready,
)


def test_metadata_contract():
    data = _metadata(
        title="N1MOX30 Test",
        description="Launch validation",
        tags=["nimox30", "creator"],
        privacy_status="private",
    )

    assert data["snippet"]["title"] == "N1MOX30 Test"
    assert data["status"]["privacyStatus"] == "private"
    assert "snippet" in data
    assert "status" in data


def test_video_file_validation():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.mp4"
        path.write_bytes(b"fake-video")

        resolved = _video_path(path)

        assert resolved.exists()
        assert resolved.stat().st_size > 0


def test_publish_is_safe_by_default():
    readiness = youtube_upload_ready()

    assert "ready" in readiness
    assert "publishing_enabled" in readiness