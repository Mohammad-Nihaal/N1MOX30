from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
) -> Notification:

    notification = Notification(
        user_id=user_id,
        title=title[:255],
        message=message,
        notification_type=notification_type[:50],
        is_read=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_read(
    db: Session,
    user_id: str,
    notification_id: str,
) -> bool:

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if notification is None:
        return False

    notification.is_read = True

    db.commit()

    return True
