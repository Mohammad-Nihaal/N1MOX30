from app.models.analytics import AnalyticsSnapshot
from app.services.ai_service import (
    generate_youtube_ai_insights,
)
from app.services.growth_service import (
    calculate_youtube_growth,
)


def generate_rule_based_insights(
    growth_data: dict,
) -> tuple[list[str], list[str]]:
    """
    Generate deterministic insights and recommendations
    from YouTube growth data.
    """

    insights: list[str] = []
    recommendations: list[str] = []

    total_snapshots = growth_data.get(
        "total_snapshots",
        0,
    )

    growth = growth_data.get(
        "growth",
        {},
    )

    latest = growth_data.get(
        "latest",
        {},
    )

    if total_snapshots < 2:

        insights.append(
            "This is your first analytics snapshot. "
            "More snapshots are needed to measure "
            "real channel growth over time."
        )

        insights.append(
            f"Your channel currently has "
            f"{latest.get('views', 0):,} total views."
        )

        insights.append(
            f"Your channel currently has "
            f"{latest.get('followers', 0):,} subscribers."
        )

        recommendations.append(
            "Create another analytics snapshot later "
            "to begin tracking channel growth."
        )

        recommendations.append(
            "Keep publishing consistently so future "
            "analytics comparisons become more useful."
        )

        recommendations.append(
            "Use AI content generation to test different "
            "topics, hooks, titles, and content styles."
        )

        return insights, recommendations

    view_change = growth.get(
        "view_change",
        0,
    )

    view_growth_percent = growth.get(
        "view_growth_percent",
        0.0,
    )

    view_trend = growth.get(
        "view_trend",
        "stable",
    )

    subscriber_change = growth.get(
        "subscriber_change",
        0,
    )

    subscriber_growth_percent = growth.get(
        "subscriber_growth_percent",
        0.0,
    )

    subscriber_trend = growth.get(
        "subscriber_trend",
        "stable",
    )

    overall_status = growth.get(
        "overall_status",
        "stable",
    )

    # =============================================
    # VIEW INSIGHTS
    # =============================================

    if view_trend == "growing":

        insights.append(
            f"Channel views increased by "
            f"{view_change:,} "
            f"({view_growth_percent}%)."
        )

        recommendations.append(
            "Analyze your recent content topics and "
            "formats to identify what may be driving "
            "view growth."
        )

    elif view_trend == "declining":

        insights.append(
            f"Channel views decreased by "
            f"{abs(view_change):,} "
            f"({abs(view_growth_percent)}%)."
        )

        recommendations.append(
            "Experiment with stronger hooks, clearer "
            "titles, thumbnails, and trending topics."
        )

    else:

        insights.append(
            "Channel views are currently stable."
        )

        recommendations.append(
            "Test new content formats or topics to "
            "create stronger view growth."
        )

    # =============================================
    # SUBSCRIBER INSIGHTS
    # =============================================

    if subscriber_trend == "growing":

        insights.append(
            f"Subscribers increased by "
            f"{subscriber_change:,} "
            f"({subscriber_growth_percent}%)."
        )

        recommendations.append(
            "Continue producing content similar to "
            "topics that may be attracting subscribers."
        )

    elif subscriber_trend == "declining":

        insights.append(
            f"Subscribers decreased by "
            f"{abs(subscriber_change):,} "
            f"({abs(subscriber_growth_percent)}%)."
        )

        recommendations.append(
            "Improve subscriber calls-to-action and "
            "focus on creating more repeat-viewer value."
        )

    else:

        insights.append(
            "Subscriber growth is currently stable."
        )

        recommendations.append(
            "Include a clear reason for viewers to "
            "subscribe and return for future content."
        )

    # =============================================
    # OVERALL CHANNEL STATUS
    # =============================================

    if overall_status == "strong_growth":

        insights.append(
            "Overall channel performance shows "
            "strong growth."
        )

    elif overall_status == "positive_growth":

        insights.append(
            "Overall channel performance shows "
            "positive growth."
        )

    elif overall_status == "declining":

        insights.append(
            "Overall channel performance needs "
            "attention because one or more key "
            "metrics are declining."
        )

    else:

        insights.append(
            "Overall channel performance is "
            "currently stable."
        )

    return insights, recommendations


def build_ai_analytics_data(
    growth_data: dict,
) -> dict:
    """
    Convert growth intelligence into the format
    required by the AI insights generator.
    """

    latest = growth_data.get(
        "latest",
        {},
    )

    previous = growth_data.get(
        "previous",
    )

    growth = growth_data.get(
        "growth",
        {},
    )

    previous_views = (
        previous.get("views", 0)
        if previous
        else latest.get("views", 0)
    )

    previous_followers = (
        previous.get("followers", 0)
        if previous
        else latest.get("followers", 0)
    )

    return {
        "platform": "youtube",

        "snapshot_count": growth_data.get(
            "total_snapshots",
            0,
        ),

        "views": {
            "first": previous_views,
            "latest": latest.get(
                "views",
                0,
            ),
            "change": growth.get(
                "view_change",
                0,
            ),
            "trend": growth.get(
                "view_trend",
                "stable",
            ),
        },

        "followers": {
            "first": previous_followers,
            "latest": latest.get(
                "followers",
                0,
            ),
            "change": growth.get(
                "subscriber_change",
                0,
            ),
            "trend": growth.get(
                "subscriber_trend",
                "stable",
            ),
        },
    }


def generate_youtube_insights(
    snapshots: list[AnalyticsSnapshot],
) -> dict:
    """
    Generate complete YouTube channel intelligence.

    Includes:
    - Analytics growth
    - Trend detection
    - Rule-based insights
    - Actionable recommendations
    - AI-powered analysis
    """

    if not snapshots:

        return {
            "status": "no_data",
            "message": (
                "No YouTube analytics snapshots found. "
                "Create an analytics snapshot first."
            ),
            "growth": None,
            "insights": [],
            "recommendations": [],
            "ai_insights": None,
        }

    # =============================================
    # ORDER SNAPSHOTS
    # =============================================

    ordered_snapshots = sorted(
        snapshots,
        key=lambda snapshot: snapshot.recorded_at,
        reverse=True,
    )

    # =============================================
    # CALCULATE GROWTH
    # =============================================

    growth_data = calculate_youtube_growth(
        ordered_snapshots
    )

    # =============================================
    # RULE-BASED INSIGHTS
    # =============================================

    insights, recommendations = (
        generate_rule_based_insights(
            growth_data
        )
    )

    # =============================================
    # AI ANALYTICS DATA
    # =============================================

    analytics_data = build_ai_analytics_data(
        growth_data
    )

    # =============================================
    # AI INSIGHTS
    # =============================================

    try:

        ai_insights = (
            generate_youtube_ai_insights(
                analytics_data
            )
        )

    except Exception as error:

        ai_insights = {
            "status": "unavailable",
            "message": str(error),
        }

    # =============================================
    # FINAL RESPONSE
    # =============================================

    return {
        "status": "success",

        "growth": growth_data,

        "insights": insights,

        "recommendations": recommendations,

        "ai_insights": ai_insights,
    }