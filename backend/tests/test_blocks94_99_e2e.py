import os
import uuid


def test_e2e_job_contains_13_stages():
    from app.services.creator_os.e2e import (
        build_e2e_job,
    )
    from app.services.creator_os.pipeline import (
        CREATOR_OS_STAGES,
    )

    job = build_e2e_job(
        910001,
        "N1MOX30 creator automation",
    )

    assert job["status"] == "created"
    assert len(CREATOR_OS_STAGES) == 13
    assert job["completed_stages"] == []


def test_publish_gate_blocks_unconfigured_real_publish(
    monkeypatch,
):
    monkeypatch.delenv(
        "N1MOX_ALLOW_REAL_PUBLISH",
        raising=False,
    )
    monkeypatch.delenv(
        "YOUTUBE_CLIENT_ID",
        raising=False,
    )
    monkeypatch.delenv(
        "YOUTUBE_CLIENT_SECRET",
        raising=False,
    )
    monkeypatch.delenv(
        "N1MOX_TOKEN_ENCRYPTION_KEY",
        raising=False,
    )

    from app.services.publishing.publish_gate import (
        authorize_real_publish,
    )

    result = authorize_real_publish()

    assert result["status"] == "authorization_required"
    assert not result["gate"]["allowed"]


def test_e2e_pipeline_execution():
    from app.services.creator_os.e2e import (
        run_creator_os_e2e,
    )
    from app.services.creator_os.pipeline import (
        CREATOR_OS_STAGES,
    )

    result = run_creator_os_e2e(
        910002,
        "AI creator automation",
    )

    assert result["status"] in {
        "completed",
        "failed",
    }

    assert result["e2e"]["total_stages"] == 13

    if result["status"] == "completed":
        assert result["completed_stages"] == CREATOR_OS_STAGES
        assert result["e2e"]["all_stages_complete"]


def test_publish_queue_requires_rendered_asset():
    from app.services.creator_os.e2e import (
        build_publish_queue,
    )

    result = build_publish_queue(
        {
            "job_id": "missing-" + uuid.uuid4().hex,
            "user_id": 910003,
            "topic": "test",
            "results": {
                "video": {},
                "metadata": {},
            },
        },
        "account",
    )

    assert result["status"] == "asset_missing"


def test_e2e_growth_report():
    from app.services.analytics.e2e_report import (
        build_e2e_growth_report,
    )

    result = build_e2e_growth_report(
        910004
    )

    assert result["status"] == "ready"
    assert "trends" in result
    assert "growth" in result


def test_expected_stage_order():
    from app.services.creator_os.pipeline import (
        CREATOR_OS_STAGES,
    )

    assert CREATOR_OS_STAGES == [
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