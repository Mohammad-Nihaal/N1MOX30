import os
import uuid
from pathlib import Path
from unittest.mock import patch


def test_youtube_oauth_routes_registered():
    from app.main import app

    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/oauth/youtube/login" in routes
    assert "/oauth/youtube/connect" in routes
    assert "/oauth/youtube/callback" in routes


def test_token_resolver_accepts_existing_store():
    from app.services.publishing import real_youtube_publish as publisher

    with patch.object(
        publisher,
        "_token_for_account",
        return_value="TEST_ACCESS_TOKEN",
    ):
        token = publisher._token_for_account(900001)

    assert token == "TEST_ACCESS_TOKEN"


def test_missing_token_is_authorization_required():
    from app.services.publishing import real_youtube_publish as publisher

    previous = os.environ.get("N1MOX_ALLOW_REAL_PUBLISH")

    os.environ["N1MOX_ALLOW_REAL_PUBLISH"] = "true"

    try:
        with __import__("tempfile").TemporaryDirectory() as tmp:

            video = Path(tmp) / "oauth-test.mp4"
            video.write_bytes(b"N1MOX30-OAUTH-TEST")

            with patch.object(
                publisher,
                "_token_for_account",
                return_value=None,
            ):
                result = publisher.prepare_real_publish(
                    900001,
                    "missing-youtube-account",
                    video,
                    "N1MOX30 OAuth Test",
                )

            assert result["status"] == "authorization_required"

    finally:
        if previous is None:
            os.environ.pop("N1MOX_ALLOW_REAL_PUBLISH", None)
        else:
            os.environ["N1MOX_ALLOW_REAL_PUBLISH"] = previous


def test_queue_job_can_hold_youtube_publish_payload():
    from app.services.publishing.durable_queue import (
        enqueue,
        load,
    )

    job_id = "batch4-" + uuid.uuid4().hex

    enqueue(
        job_id,
        900001,
        "youtube-account",
        {
            "video_path": "test.mp4",
            "title": "N1MOX30 OAuth Queue Test",
            "description": "OAuth queue validation",
            "tags": ["nimox30"],
            "privacy_status": "private",
        },
    )

    item = load(job_id)

    assert item is not None
    assert item["user_id"] == 900001
    assert item["account_id"] == "youtube-account"
    assert item["payload"]["video_path"] == "test.mp4"
    assert item["payload"]["privacy_status"] == "private"