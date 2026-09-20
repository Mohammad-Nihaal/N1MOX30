import os
import uuid


def test_real_oauth_configuration_boundary(monkeypatch):
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_ID",
        "client",
    )
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_SECRET",
        "secret",
    )
    monkeypatch.setenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        "x" * 40,
    )

    from app.services.creator_accounts.youtube_real_oauth import (
        configured,
        authorization_url,
    )

    assert configured()

    result = authorization_url(
        900001,
        "yt-" + uuid.uuid4().hex,
    )

    assert result["status"] == "ready"
    assert "accounts.google.com" in result[
        "authorization_url"
    ]


def test_oauth_state_roundtrip(monkeypatch):
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_ID",
        "client",
    )
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_SECRET",
        "secret",
    )
    monkeypatch.setenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        "x" * 40,
    )

    from app.services.creator_accounts.youtube_real_oauth import (
        create_oauth_state,
        consume_oauth_state,
    )

    account = "yt-" + uuid.uuid4().hex

    state = create_oauth_state(
        900002,
        account,
    )

    result = consume_oauth_state(
        state
    )

    assert result["user_id"] == 900002
    assert result["account_id"] == account

    assert consume_oauth_state(state) is None


def test_real_publish_requires_authorization(monkeypatch):
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_ID",
        "client",
    )
    monkeypatch.setenv(
        "YOUTUBE_CLIENT_SECRET",
        "secret",
    )
    monkeypatch.setenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        "x" * 40,
    )

    from app.services.publishing.real_youtube_publish import (
        prepare_real_publish,
    )

    result = prepare_real_publish(
        900003,
        "missing-account-" + uuid.uuid4().hex,
        "missing.mp4",
        "N1MOX30",
    )

    assert result["status"] == "asset_missing"


def test_queue_execution_boundary():
    from app.services.publishing.durable_queue import (
        enqueue,
    )
    from app.services.publishing.queue_executor import (
        execute_queue_item,
    )

    job = "yt-" + uuid.uuid4().hex

    enqueue(
        job,
        900004,
        "account",
        {
            "video_path": "missing.mp4",
            "title": "N1MOX30",
        },
    )

    result = execute_queue_item(job)

    assert result["status"] == "asset_missing"


def test_13_stage_sequence():
    from app.services.creator_os.pipeline import (
        CREATOR_OS_STAGES,
    )

    expected = [
        "research",
        "strategy",
        "hooks",
        "script",
        "voice",
        "visuals",
        "video",
        "captions",
        "thumbnail",
        "metadata",
        "quality_check",
        "scheduling",
        "publishing",
    ]

    assert CREATOR_OS_STAGES == expected