from app.services.creator_os.pipeline import (
    CREATOR_OS_STAGES,
    create_creator_os_job,
    complete_stage,
    progress,
)

from app.services.analytics.creator_analytics import (
    normalize_metrics,
    analyze_content,
)

from app.services.growth.intelligence import (
    calculate_growth_score,
    generate_recommendations,
    build_growth_report,
)


def test_true_13_stage_creator_os():
    assert len(CREATOR_OS_STAGES) == 13
    assert CREATOR_OS_STAGES[0] == "research"
    assert CREATOR_OS_STAGES[1] == "strategy"
    assert CREATOR_OS_STAGES[-1] == "publishing"


def test_creator_os_progress():
    job = create_creator_os_job(
        user_id=1,
        topic="AI creator automation",
    )

    assert job["status"] == "created"

    complete_stage(
        job,
        "research",
        {"status": "completed"},
    )

    result = progress(job)

    assert result["total_stages"] == 13
    assert result["completed_count"] == 1
    assert result["progress_percent"] > 0
    assert "strategy" in result["remaining_stages"]


def test_creator_os_completion():
    job = create_creator_os_job(
        user_id=2,
        topic="N1MOX30",
    )

    for stage in CREATOR_OS_STAGES:
        complete_stage(
            job,
            stage,
            {"status": "completed"},
        )

    result = progress(job)

    assert job["status"] == "completed"
    assert result["completed_count"] == 13
    assert result["progress_percent"] == 100.0


def test_analytics_normalization():
    result = normalize_metrics(
        views=10000,
        likes=500,
        comments=100,
        shares=50,
        subscribers_gained=120,
        watch_time_seconds=3600,
    )

    assert result["views"] == 10000
    assert result["engagement_rate"] == 6.5
    assert result["subscriber_conversion_rate"] == 1.2


def test_content_analysis():
    result = analyze_content(
        "N1MOX30 Creator OS",
        {
            "views": 10000,
            "likes": 500,
            "comments": 100,
            "shares": 50,
            "subscribers_gained": 120,
            "watch_time_seconds": 3600,
        },
    )

    assert result["status"] == "analyzed"
    assert 0 <= result["performance_score"] <= 100


def test_growth_intelligence():
    score = calculate_growth_score(
        views_growth=80,
        engagement_growth=70,
        subscriber_growth=60,
        consistency_score=90,
    )

    assert 0 <= score <= 100

    recommendations = generate_recommendations(
        {
            "engagement_rate": 1,
            "subscriber_conversion_rate": 0.5,
            "views": 1000,
        }
    )

    assert len(recommendations) >= 1


def test_growth_report():
    report = build_growth_report(
        {
            "views_growth": 70,
            "engagement_growth": 60,
            "subscriber_growth": 50,
            "consistency_score": 80,
            "engagement_rate": 2,
            "subscriber_conversion_rate": 0.5,
            "views": 1000,
        }
    )

    assert report["status"] == "ready"
    assert 0 <= report["growth_score"] <= 100
    assert isinstance(report["recommendations"], list)