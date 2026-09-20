from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.automation_workflow import AutomationWorkflow
from app.models.content import Content
from app.models.notification import Notification
from app.models.schedule import ContentSchedule
from app.models.project_activity import ProjectActivity


class DailyIntelligenceService:
    """Build a compact daily operating brief from persistent N1MOX data."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def build(self, user_id: str) -> dict[str, Any]:
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        workflows = self.db.query(AutomationWorkflow).filter(AutomationWorkflow.user_id == user_id).all()
        content = self.db.query(Content).filter(Content.user_id == user_id).all()
        schedules = (
            self.db.query(ContentSchedule)
            .join(Content, Content.id == ContentSchedule.content_id)
            .filter(Content.user_id == user_id)
            .order_by(ContentSchedule.scheduled_for.asc())
            .all()
        )
        unread = self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).count()
        activities = (
            self.db.query(ProjectActivity)
            .filter(ProjectActivity.user_id == user_id, ProjectActivity.created_at >= week_ago)
            .order_by(ProjectActivity.created_at.desc())
            .limit(25)
            .all()
        )

        def status_of(item: Any) -> str:
            return str(item.status).split(".")[-1].lower()

        active = [w for w in workflows if status_of(w) in {"pending", "running", "paused"}]
        failed = [w for w in workflows if status_of(w) == "failed"]
        completed_today = [w for w in workflows if status_of(w) == "completed" and getattr(w, "updated_at", now) >= day_ago]
        upcoming = [s for s in schedules if s.scheduled_for >= now and status_of(s) in {"pending", "processing"}][:10]

        actions: list[dict[str, Any]] = []
        if failed:
            actions.append({"priority": "high", "type": "recovery", "message": f"Review {len(failed)} failed workflow(s)."})
        if upcoming:
            actions.append({"priority": "medium", "type": "publishing", "message": f"{len(upcoming)} publishing item(s) are queued."})
        if not active:
            actions.append({"priority": "medium", "type": "creation", "message": "No active workflow is running; create the next content piece."})
        if unread:
            actions.append({"priority": "low", "type": "notifications", "message": f"You have {unread} unread notification(s)."})

        return {
            "generated_at": now.isoformat() + "Z",
            "summary": {
                "active_workflows": len(active),
                "failed_workflows": len(failed),
                "completed_today": len(completed_today),
                "content_items": len(content),
                "upcoming_schedules": len(upcoming),
                "unread_notifications": unread,
                "activities_last_7_days": len(activities),
            },
            "next_actions": actions,
            "upcoming": [
                {"id": s.id, "content_id": s.content_id, "scheduled_for": s.scheduled_for.isoformat(), "status": status_of(s)}
                for s in upcoming
            ],
            "recent_activity": [
                {"id": a.id, "type": a.activity_type, "title": a.title, "description": a.description, "created_at": a.created_at.isoformat()}
                for a in activities[:10]
            ],
        }
