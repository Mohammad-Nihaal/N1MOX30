from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.launch_workspace import CommunicationMessage
from app.models.user import User
from app.services.usage_service import reserve_usage

router = APIRouter(prefix="/communications", tags=["Communications"])


class DraftRequest(BaseModel):
    provider: str = Field(pattern="^(instagram|x|tiktok|gmail|outlook)$")
    recipient: str = ""
    sender: str = ""
    subject: str = ""
    body: str = Field(min_length=1, max_length=20000)
    category: str = "general"
    auto_reply_enabled: bool = False


@router.get("/messages")
def list_messages(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(CommunicationMessage)
            .filter(CommunicationMessage.user_id == current_user.id)
            .order_by(CommunicationMessage.created_at.desc())
            .limit(100).all())
    return [{
        "id": row.id, "provider": row.provider, "direction": row.direction,
        "category": row.category, "sender": row.sender, "recipient": row.recipient,
        "subject": row.subject, "body": row.body, "status": row.status,
        "auto_reply_enabled": row.auto_reply_enabled,
        "created_at": row.created_at.isoformat(),
    } for row in rows]


@router.post("/draft", status_code=status.HTTP_201_CREATED)
def create_draft(payload: DraftRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    metric = "messages" if payload.provider in {"instagram", "x", "tiktok"} else ("email" if payload.provider == "gmail" else "outlook")
    reserve_usage(db, current_user.id, metric)
    row = CommunicationMessage(user_id=current_user.id, provider=payload.provider, direction="outbound",
                               category=payload.category, sender=payload.sender, recipient=payload.recipient,
                               subject=payload.subject, body=payload.body, status="draft",
                               auto_reply_enabled=payload.auto_reply_enabled)
    db.add(row)
    db.commit(); db.refresh(row)
    return {"id": row.id, "status": row.status, "provider": row.provider, "message": "Draft saved. Review before sending."}


@router.post("/{message_id}/send")
def send_message(message_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = (db.query(CommunicationMessage)
           .filter(CommunicationMessage.id == message_id, CommunicationMessage.user_id == current_user.id)
           .first())
    if not row:
        raise HTTPException(404, "Message draft not found.")
    if row.status == "sent":
        return {"id": row.id, "status": "sent"}
    raise HTTPException(501, "The connected provider must be authorized and configured before external sending is enabled. Draft remains saved and unsent.")
