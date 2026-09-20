from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.user import User
from app.publishing.publishing_service import PublishingService


router = APIRouter(prefix="/multi-publishing", tags=["Multi-Platform Publishing"])


class MultiPublishRequest(BaseModel):
    platforms: list[str] = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("/preview")
def preview(payload: MultiPublishRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PublishingService(db)
    results = []
    for platform in dict.fromkeys(p.lower().strip() for p in payload.platforms):
        if platform not in {"youtube", "instagram", "tiktok", "x"}:
            continue
        try:
            result = service.preview(
                user_id=current_user.id,
                platform=platform,
                video_path=str(payload.payload.get("video_path", "")),
                title=str(payload.payload.get("title", "")),
                description=str(payload.payload.get("description", "")),
                tags=payload.payload.get("tags") or [],
                privacy_status=str(payload.payload.get("privacy_status", "private")),
                account_id=payload.payload.get("account_id_by_platform", {}).get(platform),
                media_url=payload.payload.get("media_url"),
                media_type=str(payload.payload.get("media_type", "video")),
                platform_options=payload.payload.get("platform_options_by_platform", {}).get(platform, {}),
            )
            results.append(result)
        except ValueError as error:
            results.append({"platform": platform, "ready": False, "error": str(error)})
    return {"status": "ready", "results": results}


@router.post("/publish")
def publish(payload: MultiPublishRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PublishingService(db)
    results = []
    for platform in dict.fromkeys(p.lower().strip() for p in payload.platforms):
        if platform not in {"youtube", "instagram", "tiktok", "x"}:
            continue
        try:
            result = service.publish(
                user_id=current_user.id,
                platform=platform,
                video_path=str(payload.payload.get("video_path", "")),
                title=str(payload.payload.get("title", "")),
                description=str(payload.payload.get("description", "")),
                tags=payload.payload.get("tags") or [],
                privacy_status=str(payload.payload.get("privacy_status", "private")),
                account_id=payload.payload.get("account_id_by_platform", {}).get(platform),
                media_url=payload.payload.get("media_url"),
                media_type=str(payload.payload.get("media_type", "video")),
                platform_options=payload.payload.get("platform_options_by_platform", {}).get(platform, {}),
            )
            results.append(result)
        except Exception as error:
            results.append({"platform": platform, "status": "failed", "error": str(error)})
    return {
        "status": "completed",
        "published": any(item.get("status") in {"published", "processing"} for item in results),
        "results": results,
    }


@router.post("/demo")
def demo_publish(payload: MultiPublishRequest, current_user: User = Depends(get_current_user)):
    platforms = [p.lower().strip() for p in payload.platforms if p.lower().strip()]
    return {
        "status": "simulated",
        "published": False,
        "message": "Preview-only demo. Use /publish with connected accounts for real publishing.",
        "results": [{"platform": p, "status": "simulated"} for p in platforms],
    }


@router.get("/health")
def health():
    return {
        "service": "multi-platform-publishing",
        "status": "ready",
        "supported": ["youtube", "instagram", "tiktok", "x"],
    }
