from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User

from app.schemas.personal_ai_assistant import (
    PersonalAssistantMessageRequest,
    PersonalAssistantMessageResponse,
    PersonalContextResponse,
)

from app.services.personal_ai_assistant_service import (
    build_assistant_instructions,
    build_personal_ai_context,
)


# =================================================
# ROUTER
# =================================================


router = APIRouter(
    prefix="/personal-ai",
    tags=["Personal AI Assistant"],
)


# =================================================
# GET PERSONAL CONTEXT
# =================================================


@router.get(
    "/context",
    response_model=PersonalContextResponse,
)
def get_personal_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current personalized context used by
    the N1MOX30 Personal AI Assistant.
    """

    personal_context = build_personal_ai_context(
        db=db,
        user_id=current_user.id,
    )

    return personal_context


# =================================================
# PERSONAL AI MESSAGE
# =================================================


@router.post(
    "/message",
    response_model=PersonalAssistantMessageResponse,
)
def send_personal_ai_message(
    message_data: PersonalAssistantMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a personalized message to N1MOX30.

    The assistant receives:
    - Creator Profile
    - Long-Term Memory
    - Connected Accounts
    - Latest Analytics
    """

    personal_context = build_personal_ai_context(
        db=db,
        user_id=current_user.id,
    )

    instructions = build_assistant_instructions(
        personal_context=personal_context,
    )

    user_message = message_data.message.strip()

    # =================================================
    # TEMPORARY DETERMINISTIC RESPONSE
    # =================================================
    #
    # This provides a working Personal AI API now.
    #
    # In the next step, we will connect this endpoint
    # directly to the existing N1MOX30 AI provider
    # system so the assistant generates real AI responses.
    # =================================================

    response_message = (
        "I am N1MOX30, your personal creator AI assistant.\n\n"
        f"You asked: {user_message}\n\n"
        "I have loaded your personal creator context including "
        "your profile, long-term memory, connected accounts, "
        "and available analytics.\n\n"
        "Personal AI provider integration is the next step."
    )

    return {
        "message": response_message,
        "provider": "personal_context_fallback",
        "personalized": True,
        "generated_at": datetime.utcnow(),
    }