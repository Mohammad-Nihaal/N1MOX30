from pathlib import Path

from app.services.production.engine import (
    create_job,
    generate_thumbnail,
    generate_metadata,
    quality_check_production,
    schedule_production,
    publish_production,
    execute_extended_production,
)


def test_block_28_thumbnail():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    result = generate_thumbnail(job)

    assert result["status"] == "completed"
    assert result["stage"] == "thumbnail"


def test_block_29_metadata():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    job["results"]["script"] = {
        "status": "completed",
        "content": "AI is transforming creator workflows.",
    }

    result = generate_metadata(job)

    assert result["status"] == "completed"
    assert result["stage"] == "metadata"
    assert result["title"]
    assert result["description"]
    assert result["keywords"]
    assert result["hashtags"]


def test_block_30_qc():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    job["results"] = {
        stage: {
            "status": "completed"
        }
        for stage in [
            "research",
            "hooks",
            "script",
            "voice",
            "visuals",
            "video",
            "captions",
            "thumbnail",
            "metadata",
        ]
    }

    result = quality_check_production(job)

    assert result["status"] == "completed"
    assert result["passed"] is True
    assert result["score"] >= 90


def test_block_31_32_schedule_publish():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    job["results"] = {
        "metadata": {
            "title": "AI Creator Automation",
            "description": "N1MOX30 creator workflow",
        },
        "video": {
            "video": None,
        },
        "thumbnail": {
            "thumbnail": None,
        },
        "captions": {
            "subtitle": None,
        },
    }

    scheduled = schedule_production(job)

    assert scheduled["status"] == "scheduled"

    job["results"]["scheduling"] = scheduled

    published = publish_production(job)

    assert published["status"] == "ready_to_publish"
    assert published["published"] is False
    assert Path(published["package"]).exists()


def test_block_33_extended_pipeline():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    result = execute_extended_production(job)

    assert result["status"] == "completed"
    assert result["extended_pipeline"] is True

    expected = [
        "research",
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

    for stage in expected:
        assert stage in result["results"]

    assert len(result["completed_stages"]) == 12
