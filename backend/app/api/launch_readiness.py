from __future__ import annotations

import os

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/launch-readiness", tags=["Launch Readiness"])


def _secret_ready(name: str, minimum: int = 32) -> bool:
    value = os.getenv(name, "")
    return len(value) >= minimum and "change-me" not in value.lower() and "your-" not in value.lower()


@router.get("/check")
def check(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    checks = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False
    checks["production_secret"] = _secret_ready("SECRET_KEY")
    checks["encryption_key"] = _secret_ready("ENCRYPTION_KEY", 32) or _secret_ready("N1MOX_BYOK_ENCRYPTION_KEY", 32)
    checks["debug_disabled"] = os.getenv("DEBUG", "false").lower() != "true"
    checks["razorpay_configured"] = bool(os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"))
    checks["razorpay_live_enabled"] = os.getenv("N1MOX_RAZORPAY_LIVE", "false").lower() == "true"
    checks["google_oauth_configured"] = bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET") and (os.getenv("GOOGLE_REDIRECT_URI") or os.getenv("YOUTUBE_REDIRECT_URI")))
    checks["frontend_url_configured"] = bool(os.getenv("FRONTEND_URL"))
    checks["https_ready"] = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower() != "production" or os.getenv("FRONTEND_URL", "").startswith("https://")
    return {"status": "ready" if all(checks.values()) else "action_required", "checks": checks, "user": str(current_user.id)}
