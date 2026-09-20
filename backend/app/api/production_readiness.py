from fastapi import APIRouter

from app.core.production_config import get_production_config


router = APIRouter(
    prefix="/platform/v18/readiness",
    tags=["Production Readiness"],
)


@router.get("")
def readiness():
    config = get_production_config()

    return {
        "status": "ready",
        "environment": config.environment,
        "debug": config.debug,
        "youtube_configured": config.youtube_configured,
        "token_security_ready": config.token_security_ready,
        "real_publishing_enabled": config.allow_real_publish,
        "publishing_ready": config.publishing_ready,
    }