from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.content import Content
from app.models.schedule import ContentSchedule
from app.models.user import User
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)


router = APIRouter(
    prefix="/schedules",
    tags=["Content Scheduling"],
)


def get_user_schedule(
    schedule_id: str,
    current_user: User,
    db: Session,
) -> ContentSchedule:
    schedule = (
        db.query(ContentSchedule)
        .join(Content, Content.id == ContentSchedule.content_id)
        .filter(
            ContentSchedule.id == schedule_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found.",
        )

    return schedule


@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if schedule_data.scheduled_for <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scheduled_for must be in the future.",
        )

    content = (
        db.query(Content)
        .filter(
            Content.id == schedule_data.content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found.",
        )

    if schedule_data.connected_account_id:
        connected_account = (
            db.query(ConnectedAccount)
            .filter(
                ConnectedAccount.id == schedule_data.connected_account_id,
                ConnectedAccount.user_id == current_user.id,
            )
            .first()
        )

        if not connected_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connected account not found.",
            )

        if connected_account.platform != content.platform:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connected account platform must match content platform.",
            )

    existing_schedule = (
        db.query(ContentSchedule)
        .filter(
            ContentSchedule.content_id == content.id,
            ContentSchedule.status.in_(["pending", "processing"]),
        )
        .first()
    )

    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This content already has an active schedule.",
        )

    schedule = ContentSchedule(
        content_id=content.id,
        connected_account_id=schedule_data.connected_account_id,
        scheduled_for=schedule_data.scheduled_for,
        status="pending",
    )

    content.status = "scheduled"

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.get(
    "/",
    response_model=list[ScheduleResponse],
)
def get_my_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedules = (
        db.query(ContentSchedule)
        .join(Content, Content.id == ContentSchedule.content_id)
        .filter(Content.user_id == current_user.id)
        .order_by(ContentSchedule.scheduled_for.asc())
        .all()
    )

    return schedules


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_schedule(schedule_id, current_user, db)


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedule = get_user_schedule(schedule_id, current_user, db)

    if schedule.status in ["published", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Published or cancelled schedules cannot be updated.",
        )

    update_data = schedule_data.model_dump(exclude_unset=True)

    if "scheduled_for" in update_data:
        if update_data["scheduled_for"] <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="scheduled_for must be in the future.",
            )

    if "connected_account_id" in update_data:
        account_id = update_data["connected_account_id"]

        if account_id:
            connected_account = (
                db.query(ConnectedAccount)
                .filter(
                    ConnectedAccount.id == account_id,
                    ConnectedAccount.user_id == current_user.id,
                )
                .first()
            )

            if not connected_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Connected account not found.",
                )

            content = (
                db.query(Content)
                .filter(Content.id == schedule.content_id)
                .first()
            )

            if (
                content
                and connected_account.platform != content.platform
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Connected account platform must match content platform.",
                )

    for field, value in update_data.items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return schedule


@router.post(
    "/{schedule_id}/cancel",
    response_model=ScheduleResponse,
)
def cancel_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedule = get_user_schedule(schedule_id, current_user, db)

    if schedule.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Published schedules cannot be cancelled.",
        )

    if schedule.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule is already cancelled.",
        )

    schedule.status = "cancelled"

    content = (
        db.query(Content)
        .filter(
            Content.id == schedule.content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if content:
        content.status = "draft"

    db.commit()
    db.refresh(schedule)

    return schedule 