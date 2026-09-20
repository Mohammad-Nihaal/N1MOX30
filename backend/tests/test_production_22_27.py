from pathlib import Path

from app.services.production.engine import (
    PRODUCTION_STAGES,
    create_job,
    execute_production,
    production_progress,
)


def test_production_job_creation():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    assert job["status"] == "created"
    assert len(PRODUCTION_STAGES) == 7
    assert job["completed_stages"] == []


def test_voice_visual_caption_pipeline():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    job["results"]["script"] = {
        "status": "completed",
        "content": (
            "AI is changing creator workflows. "
            "N1MOX30 connects the entire process."
        ),
    }

    from app.services.production.engine import (
        generate_voice,
        generate_visuals,
        generate_captions,
    )

    voice = generate_voice(job)
    visuals = generate_visuals(job)
    captions = generate_captions(job)

    assert voice["status"] in (
        "completed",
        "text_fallback",
    )

    assert visuals["status"] == "completed"
    assert len(visuals["assets"]) >= 3

    assert captions["status"] == "completed"
    assert Path(captions["subtitle"]).exists()


def test_full_production_pipeline():
    job = create_job(
        user_id=1,
        topic="AI creator automation",
    )

    result = execute_production(job)

    assert result["status"] == "completed"

    assert result["completed_stages"] == [
        "research",
        "hooks",
        "script",
        "voice",
        "visuals",
        "video",
        "captions",
    ]

    assert "voice" in result["results"]
    assert "visuals" in result["results"]
    assert "video" in result["results"]
    assert "captions" in result["results"]

    progress = production_progress(result)

    assert progress["completed_count"] == 7
    assert progress["progress_percent"] == 100.0
