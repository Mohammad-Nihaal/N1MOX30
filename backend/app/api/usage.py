from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.usage_service import get_usage


router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get("/")
def usage_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_usage(db, current_user.id)
