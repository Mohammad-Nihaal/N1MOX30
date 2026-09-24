from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.launch_workspace import ClipJob
from app.models.user import User
from app.services.usage_service import reserve_usage

router = APIRouter(prefix="/clips", tags=["Clips"])


class ClipCreateRequest(BaseModel):
    source_path: str = Field(min_length=1, max_length=4000)
    title: str = Field(default="", max_length=500)
    formats: list[str] = Field(default_factory=lambda: ["9:16", "1:1", "16:9"])


@router.get("/pipeline")
def pipeline():
    return {"steps": ["transcription", "moment_detection", "hook_detection", "clip_selection", "reframing", "captions", "brand_styling", "audio_processing", "vertical_formatting", "qc", "ready_to_publish"]}


@router.get("/jobs")
def jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(ClipJob).filter(ClipJob.user_id == current_user.id).order_by(ClipJob.created_at.desc()).limit(100).all())
    return [{"id": r.id, "source_path": r.source_path, "title": r.title, "status": r.status, "formats": r.requested_formats, "pipeline": r.pipeline, "result": r.result, "created_at": r.created_at.isoformat()} for r in rows]


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_job(payload: ClipCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    formats = [f for f in dict.fromkeys(payload.formats) if f in {"9:16", "1:1", "16:9"}]
    if not formats:
        raise HTTPException(400, "At least one supported output format is required.")
    reserve_usage(db, current_user.id, "clips")
    row = ClipJob(user_id=current_user.id, source_path=payload.source_path, title=payload.title, requested_formats=formats)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "status": row.status, "formats": formats, "message": "Clip pipeline queued. Generate → Edit → Preview → Schedule → Publish."}
