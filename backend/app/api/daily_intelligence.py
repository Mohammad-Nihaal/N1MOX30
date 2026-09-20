from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.intelligence.daily_intelligence_service import DailyIntelligenceService
from app.models.user import User

router = APIRouter(prefix="/daily-intelligence", tags=["Daily Intelligence"])


@router.get("")
def daily_intelligence(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DailyIntelligenceService(db).build(str(current_user.id))


@router.get("/health")
def health():
    return {"service": "daily-intelligence", "status": "ready", "quota": "unlimited"}
