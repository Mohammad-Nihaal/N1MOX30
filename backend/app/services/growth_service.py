from app.models.analytics import AnalyticsSnapshot


def calculate_percentage_change(
    current_value: int,
    previous_value: int,
) -> float:
    """
    Calculate percentage change between two values.
    """

    if previous_value <= 0:
        return 0.0

    return round(
        (
            (current_value - previous_value)
            / previous_value
        )
        * 100,
        2,
    )


def determine_trend(
    change: int,
) -> str:
    """
    Determine whether a metric is growing,
    declining, or stable.
    """

    if change > 0:
        return "growing"

    if change < 0:
        return "declining"

    return "stable"


def determine_growth_status(
    view_change: int,
    subscriber_change: int,
) -> str:
    """
    Determine the overall channel growth status.
    """

    if (
        view_change > 0
        and subscriber_change > 0
    ):
        return "strong_growth"

    if (
        view_change > 0
        or subscriber_change > 0
    ):
        return "positive_growth"

    if (
        view_change < 0
        or subscriber_change < 0
    ):
        return "declining"

    return "stable"


def calculate_youtube_growth(
    snapshots: list[AnalyticsSnapshot],
) -> dict:
    """
    Calculate YouTube growth metrics using
    the latest two analytics snapshots.

    Snapshots must be ordered with the
    latest snapshot first.
    """

    if not snapshots:
        raise ValueError(
            "No analytics snapshots available."
        )

    latest = snapshots[0]

    previous = (
        snapshots[1]
        if len(snapshots) > 1
        else None
    )

    view_change = 0
    subscriber_change = 0

    view_growth_percent = 0.0
    subscriber_growth_percent = 0.0

    if previous:

        view_change = (
            latest.views
            - previous.views
        )

        subscriber_change = (
            latest.followers
            - previous.followers
        )

        view_growth_percent = (
            calculate_percentage_change(
                latest.views,
                previous.views,
            )
        )

        subscriber_growth_percent = (
            calculate_percentage_change(
                latest.followers,
                previous.followers,
            )
        )

    view_trend = determine_trend(
        view_change
    )

    subscriber_trend = determine_trend(
        subscriber_change
    )

    overall_status = determine_growth_status(
        view_change,
        subscriber_change,
    )

    return {
        "total_snapshots": len(snapshots),

        "latest": {
            "views": latest.views,
            "followers": latest.followers,
            "recorded_at": latest.recorded_at,
        },

        "previous": (
            {
                "views": previous.views,
                "followers": previous.followers,
                "recorded_at": previous.recorded_at,
            }
            if previous
            else None
        ),

        "growth": {
            "view_change": view_change,
            "view_growth_percent": (
                view_growth_percent
            ),
            "view_trend": view_trend,

            "subscriber_change": (
                subscriber_change
            ),
            "subscriber_growth_percent": (
                subscriber_growth_percent
            ),
            "subscriber_trend": (
                subscriber_trend
            ),

            "overall_status": overall_status,
        },
    }