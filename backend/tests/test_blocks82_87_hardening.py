import os
import uuid
from pathlib import Path


def test_production_config_boundary(monkeypatch):
    monkeypatch.setenv("N1MOX_ENV", "production")
    monkeypatch.setenv("N1MOX_TOKEN_ENCRYPTION_KEY", "x" * 40)
    monkeypatch.setenv("N1MOX_ALLOW_REAL_PUBLISH", "true")
    monkeypatch.setenv("YOUTUBE_CLIENT_ID", "client")
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRET", "secret")

    from app.core.production_config import get_production_config

    config = get_production_config()

    assert config.environment == "production"
    assert config.token_security_ready
    assert config.youtube_configured
    assert config.publishing_ready


def test_secure_token_roundtrip(monkeypatch):
    monkeypatch.setenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        "x" * 40,
    )

    from app.services.creator_accounts.secure_token_store import (
        save_secure_token,
        load_secure_token,
    )

    account = "test-" + uuid.uuid4().hex

    save_secure_token(
        999999,
        account,
        "access-token",
        "refresh-token",
    )

    result = load_secure_token(
        999999,
        account,
    )

    assert result["access_token"] == "access-token"
    assert result["refresh_token"] == "refresh-token"


def test_durable_queue():
    from app.services.publishing.durable_queue import (
        enqueue,
        load,
        mark_attempt,
    )

    job_id = "hardening-" + uuid.uuid4().hex

    item = enqueue(
        job_id,
        999999,
        "account",
        {"title": "N1MOX30"},
    )

    assert item["status"] == "queued"

    updated = mark_attempt(job_id)

    assert updated["attempts"] == 1
    assert load(job_id)["attempts"] == 1


def test_analytics_history():
    from app.services.analytics.history import (
        save_snapshot,
        calculate_trends,
    )

    user_id = 999998

    save_snapshot(
        user_id,
        {"views": 100, "engagement": 10},
    )

    save_snapshot(
        user_id,
        {"views": 150, "engagement": 15},
    )

    result = calculate_trends(user_id)

    assert result["status"] == "ready"
    assert result["trends"]["views"]["delta"] == 50


def test_creator_os_has_13_stages():
    from app.services.creator_os.pipeline import CREATOR_OS_STAGES

    assert len(CREATOR_OS_STAGES) == 13
    assert CREATOR_OS_STAGES[0] == "research"
    assert CREATOR_OS_STAGES[1] == "strategy"
    assert CREATOR_OS_STAGES[-1] == "publishing"