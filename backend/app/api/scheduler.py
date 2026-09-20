from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.scheduler_service import collect_youtube_analytics


router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"],
)


@router.post("/run-youtube-analytics")
def run_youtube_analytics_now(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger the YouTube analytics collection job."""

    # Close the request DB session because the scheduler job
    # creates and manages its own database session.
    collect_youtube_analytics()

    return {
        "status": "completed",
        "message": (
            "YouTube analytics collection job was triggered successfully."
        ),
    }