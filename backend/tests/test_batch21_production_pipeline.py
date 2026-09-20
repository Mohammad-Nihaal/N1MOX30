from app.services.batch21.production_pipeline import (
    create_production_job,
    production_progress,
    run_production_job,
)


def test_batch21_job_creation():
    job = create_production_job(
        user_id=1,
        topic="AI creator automation",
    )

    assert job["status"] == "created"
    assert len(job["stages"]) == 11
    assert job["completed_stages"] == []


def test_batch21_progress():
    job = create_production_job(
        user_id=1,
        topic="AI creator automation",
        stages=["research", "hooks", "script"],
    )

    job["completed_stages"] = ["research"]

    progress = production_progress(job)

    assert progress["total_stages"] == 3
    assert progress["completed_count"] == 1
    assert progress["progress_percent"] == 33.33


def test_batch21_execution():
    job = create_production_job(
        user_id=1,
        topic="AI creator automation",
        stages=["research", "hooks", "script"],
    )

    result = run_production_job(job)

    assert result["status"] == "completed"
    assert result["completed_stages"] == [
        "research",
        "hooks",
        "script",
    ]

    assert set(result["results"]) == {
        "research",
        "hooks",
        "script",
    }
