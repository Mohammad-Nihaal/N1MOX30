from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.notifications.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)
    notification_type: str = Field(default="info", max_length=50)


@router.get("")
def list_notifications(unread_only: bool = False, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = NotificationService(db).list(str(current_user.id), unread_only=unread_only)
    return [{"id": x.id, "title": x.title, "message": x.message, "type": x.notification_type, "is_read": x.is_read, "created_at": x.created_at.isoformat()} for x in items]


@router.post("", status_code=201)
def create_notification(payload: NotificationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).create(str(current_user.id), payload.title, payload.message, payload.notification_type)


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = NotificationService(db).mark_read(str(current_user.id), notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return item


@router.post("/read-all")
def mark_all_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"updated": NotificationService(db).mark_all_read(str(current_user.id))}


@router.get("/health")
def health():
    return {"service": "notifications", "status": "ready"}
