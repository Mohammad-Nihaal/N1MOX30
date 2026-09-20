from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.content import Content
from app.models.schedule import ContentSchedule
from app.models.user import User


router = APIRouter(prefix="/workspace", tags=["Creator Workspace"])


@router.get("/daily")
def daily_workspace(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    drafts = db.query(Content).filter(Content.user_id == current_user.id, Content.status == "draft").count()
    scheduled = (
        db.query(ContentSchedule)
        .join(Content, Content.id == ContentSchedule.content_id)
        .filter(Content.user_id == current_user.id, ContentSchedule.status == "pending")
        .count()
    )
    recent = (
        db.query(Content)
        .filter(Content.user_id == current_user.id, Content.created_at >= now - timedelta(days=7))
        .count()
    )
    tasks = [
        {"id": "review-drafts", "title": "Review draft content", "count": drafts, "status": "open" if drafts else "clear"},
        {"id": "scheduled", "title": "Check scheduled posts", "count": scheduled, "status": "open" if scheduled else "clear"},
        {"id": "weekly-output", "title": "Publish this week's target", "count": recent, "status": "on_track" if recent >= 3 else "open"},
    ]
    return {
        "date": now.date().isoformat(),
        "tasks": tasks,
        "goals": {
            "weekly_content_target": 3,
            "weekly_content_completed": recent,
            "completion_percent": min(100, round(recent / 3 * 100)),
        },
        "streak_days": min(30, recent),
    }
