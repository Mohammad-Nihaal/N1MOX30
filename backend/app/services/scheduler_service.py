from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.services.analytics_service import (
    create_snapshots_for_all_youtube_accounts,
)


scheduler = BackgroundScheduler()


def collect_youtube_analytics() -> None:
    """Collect analytics snapshots for all connected YouTube accounts."""

    db = SessionLocal()

    try:
        result = create_snapshots_for_all_youtube_accounts(db)

        print(
            "YouTube analytics scheduler completed:",
            result,
        )

    except Exception as error:
        print(
            "YouTube analytics scheduler error:",
            str(error),
        )

    finally:
        db.close()


def start_scheduler() -> None:
    """Start background jobs."""

    if scheduler.running:
        return

    scheduler.add_job(
        collect_youtube_analytics,
        trigger="cron",
        hour=0,
        minute=0,
        id="youtube_daily_analytics",
        replace_existing=True,
    )

    scheduler.start()

    print("Analytics scheduler started.")