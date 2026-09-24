from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.billing.plans import PLANS
from app.models.base import Base
from app.models.batch11 import Plan as BillingPlan, Subscription
from app.models.user import User
from app.models.usage import UsageLedger
from app.services.usage_service import get_usage, reserve_usage
from app.services.video.video_service import VideoService


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def seed_user_and_plan(db, code="creator"):
    user = User(id="u1", email="u1@example.com", full_name="Test", password_hash="x")
    db.add(user)
    plan = PLANS[code]
    db_plan = BillingPlan(
        id=f"plan-{code}",
        code=code,
        name=plan.name,
        description=plan.description,
        price_minor=0,
        currency="INR",
        monthly_ai_units=0,
        monthly_video_units=plan.monthly_videos,
        monthly_storage_mb=1024,
        max_connected_accounts=10,
        entitlements={},
    )
    db.add(db_plan)
    now = datetime.utcnow()
    db.add(Subscription(
        user_id=user.id,
        plan_id=db_plan.id,
        status="active",
        current_period_start=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        current_period_end=now.replace(day=28, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=4),
    ))
    db.commit()


@pytest.mark.parametrize(
    "code,youtube,clips,messages",
    [("creator", 27, 12, 999), ("pro", 72, 39, 1999), ("studio", 111, 100, 4499)],
)
def test_plan_entitlements(code, youtube, clips, messages):
    plan = PLANS[code]
    assert plan.monthly_videos == youtube
    assert plan.monthly_clips == clips
    assert plan.monthly_messages == messages
    assert plan.monthly_email == messages
    assert plan.monthly_outlook == messages
    assert plan.monthly_instagram == {"creator": 60, "pro": 180, "studio": 360}[code]
    assert plan.monthly_x == plan.monthly_instagram
    assert plan.monthly_tiktok == plan.monthly_instagram
    assert plan.youtube_min_minutes == 15
    assert plan.youtube_target_minutes == 25


def test_creator_hard_blocks_after_limit(db):
    seed_user_and_plan(db, "creator")
    reserve_usage(db, "u1", "messages", 999)
    usage = get_usage(db, "u1")
    assert usage["metrics"]["messages"]["remaining"] == 0
    with pytest.raises(Exception) as exc:
        reserve_usage(db, "u1", "messages", 1)
    assert getattr(exc.value, "status_code", None) == 429


def test_studio_has_111_youtube_videos(db):
    seed_user_and_plan(db, "studio")
    for _ in range(111):
        reserve_usage(db, "u1", "youtube", 1)
    assert get_usage(db, "u1")["metrics"]["youtube"]["remaining"] == 0
    with pytest.raises(Exception):
        reserve_usage(db, "u1", "youtube", 1)


def test_youtube_duration_is_15_minutes_minimum_and_25_minutes_target():
    service = VideoService()
    assert service._validate_and_normalize_duration("youtube", 900) == 900
    assert service._validate_and_normalize_duration("youtube", 1500) == 1500
    assert service._validate_and_normalize_duration("youtube", 1800) == 1800
    with pytest.raises(ValueError):
        service._validate_and_normalize_duration("youtube", 899)
