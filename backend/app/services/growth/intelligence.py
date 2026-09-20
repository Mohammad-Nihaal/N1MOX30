from __future__ import annotations

from typing import Any


def calculate_growth_score(
    views_growth: float = 0,
    engagement_growth: float = 0,
    subscriber_growth: float = 0,
    consistency_score: float = 0,
) -> float:

    score = (
        float(views_growth) * 0.30
        + float(engagement_growth) * 0.25
        + float(subscriber_growth) * 0.25
        + float(consistency_score) * 0.20
    )

    return round(max(0, min(score, 100)), 2)


def generate_recommendations(
    metrics: dict[str, Any],
) -> list[dict[str, str]]:

    recommendations = []

    if float(metrics.get("engagement_rate", 0)) < 3:
        recommendations.append({
            "type": "engagement",
            "priority": "high",
            "recommendation": (
                "Strengthen the opening hook and add a clear "
                "viewer interaction prompt."
            ),
        })

    if float(metrics.get("subscriber_conversion_rate", 0)) < 1:
        recommendations.append({
            "type": "conversion",
            "priority": "medium",
            "recommendation": (
                "Add a stronger reason for viewers to subscribe "
                "after delivering the main value."
            ),
        })

    if int(metrics.get("views", 0)) > 0 and not recommendations:
        recommendations.append({
            "type": "optimization",
            "priority": "low",
            "recommendation": (
                "Continue the current content pattern and "
                "test variations of titles and thumbnails."
            ),
        })

    return recommendations


def build_growth_report(
    metrics: dict[str, Any],
) -> dict[str, Any]:

    score = calculate_growth_score(
        views_growth=metrics.get("views_growth", 0),
        engagement_growth=metrics.get(
            "engagement_growth", 0
        ),
        subscriber_growth=metrics.get(
            "subscriber_growth", 0
        ),
        consistency_score=metrics.get(
            "consistency_score", 0
        ),
    )

    return {
        "growth_score": score,
        "recommendations": generate_recommendations(
            metrics
        ),
        "status": "ready",
    }