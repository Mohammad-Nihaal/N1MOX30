from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.user import User

router = APIRouter(prefix="/social-hub", tags=["Social Hub"])

SUPPORTED = {"youtube", "instagram", "tiktok", "x"}
CAPABILITIES = {"connect": True, "content_preparation": True, "scheduling": True, "publishing": True, "analytics": True, "account_status": True}


@router.get("/overview")
def overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = (db.query(ConnectedAccount).filter(ConnectedAccount.user_id == current_user.id).all())
    by_platform = {}
    for account in accounts:
        platform = account.platform.lower()
        if platform in SUPPORTED:
            by_platform.setdefault(platform, []).append({"id": account.id, "name": account.account_name, "authorized": bool(account.is_authorized), "active": bool(account.is_active)})
    return {"platforms": sorted(SUPPORTED), "capabilities": CAPABILITIES, "accounts": by_platform, "api_note": "Only capabilities authorized by each provider should be enabled for production actions."}
