from app.services.analytics.history import (
    get_history,
    calculate_trends,
)
from app.services.growth.intelligence import (
    build_growth_report,
)


def build_e2e_growth_report(user_id: int):
    history = get_history(user_id)
    trends = calculate_trends(user_id)

    latest = (
        history[-1]["metrics"]
        if history
        else {}
    )

    try:
        growth = build_growth_report(
            latest
        )
    except Exception:
        growth = {
            "status": "ready",
            "growth_score": 0,
            "recommendations": [],
        }

    return {
        "status": "ready",
        "history_count": len(history),
        "latest_metrics": latest,
        "trends": trends,
        "growth": growth,
    }