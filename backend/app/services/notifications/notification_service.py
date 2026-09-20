from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: str, unread_only: bool = False, limit: int = 100):
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        return query.order_by(Notification.created_at.desc()).limit(max(1, min(limit, 500))).all()

    def create(self, user_id: str, title: str, message: str, notification_type: str = "info"):
        item = Notification(user_id=user_id, title=title, message=message, notification_type=notification_type)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def mark_read(self, user_id: str, notification_id: str):
        item = self.db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if item is None:
            return None
        item.is_read = True
        self.db.commit()
        self.db.refresh(item)
        return item

    def mark_all_read(self, user_id: str) -> int:
        items = self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).all()
        for item in items:
            item.is_read = True
        self.db.commit()
        return len(items)
