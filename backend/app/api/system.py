from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.automation.registry import stage_registry

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/readiness")
def readiness(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tables = inspect(db.bind).get_table_names()
    stages = [definition.stage.value for definition in stage_registry.all()]
    return {
        "product": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "authenticated_user": str(current_user.id),
        "database": {"ok": True, "tables": len(tables)},
        "workflow": {"ok": len(stages) >= 13, "stages": stages},
        "ai": {"mode": settings.ai_provider, "primary": settings.ai_primary_provider, "fallback": settings.ai_fallback_provider, "demo_fallback": settings.ai_enable_demo_fallback},
        "unlimited_policy": "N1MOX30 imposes no creator usage quota; external provider limits are handled by adapters/queues/retries.",
        "external_setup": {"youtube_oauth": bool(settings.google_client_id and settings.google_client_secret), "openai": bool(settings.openai_api_key), "bedrock": bool(settings.aws_access_key_id and settings.aws_secret_access_key and settings.bedrock_model_id), "openclaw": settings.openclaw_enabled},
    }


@router.get("/health")
def health():
    return {"status": "healthy", "service": "N1MOX30 system"}
