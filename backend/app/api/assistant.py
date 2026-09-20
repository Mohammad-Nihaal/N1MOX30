from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.assistant_conversation import (
    AssistantConversation,
)
from app.models.user import User
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantConversationHistoryResponse,
    AssistantConversationResponse,
)
from app.services.assistant_service import (
    generate_assistant_response,
)


router = APIRouter(
    prefix="/assistant",
    tags=["Personal Creator AI Assistant"],
)


# =================================================
# CHAT WITH N1MOX30
# =================================================


@router.post(
    "/chat",
    response_model=AssistantChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def chat_with_assistant(
    request: AssistantChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Send a message to the N1MOX30 Personal
    Creator AI Assistant.
    """

    try:

        assistant_result = (
            generate_assistant_response(
                db=db,
                user_id=current_user.id,
                message=request.message,
            )
        )

        conversation = AssistantConversation(
            user_id=current_user.id,
            role="user",
            message=request.message,
            response=assistant_result.get(
                "response"
            ),
            conversation_type=(
                request.conversation_type
            ),
            action_type=assistant_result.get(
                "action_type"
            ),
            action_status=assistant_result.get(
                "action_status"
            ),
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return {
            "conversation_id": conversation.id,
            "message": conversation.message,
            "response": (
                conversation.response or ""
            ),
            "provider": (
                assistant_result.get("provider")
                or "unknown"
            ),
            "conversation_type": (
                conversation.conversation_type
            ),
            "action_type": (
                conversation.action_type
            ),
            "action_status": (
                conversation.action_status
            ),
            "created_at": conversation.created_at,
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "N1MOX30 Assistant failed to "
                f"process the message: {str(error)}"
            ),
        )


# =================================================
# CONVERSATION HISTORY
# =================================================


@router.get(
    "/history",
    response_model=(
        AssistantConversationHistoryResponse
    ),
)
def get_assistant_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get Personal Creator AI Assistant
    conversation history.
    """

    if limit < 1:

        limit = 1

    if limit > 100:

        limit = 100

    if offset < 0:

        offset = 0

    query = (
        db.query(AssistantConversation)
        .filter(
            AssistantConversation.user_id
            == current_user.id
        )
    )

    total = query.count()

    conversations = (
        query.order_by(
            AssistantConversation.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "conversations": conversations,
    }


# =================================================
# SINGLE CONVERSATION
# =================================================


@router.get(
    "/history/{conversation_id}",
    response_model=AssistantConversationResponse,
)
def get_assistant_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get one assistant conversation.
    """

    conversation = (
        db.query(AssistantConversation)
        .filter(
            AssistantConversation.id
            == conversation_id,
            AssistantConversation.user_id
            == current_user.id,
        )
        .first()
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return conversation


# =================================================
# DELETE CONVERSATION
# =================================================


@router.delete(
    "/history/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assistant_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Delete one assistant conversation.
    """

    conversation = (
        db.query(AssistantConversation)
        .filter(
            AssistantConversation.id
            == conversation_id,
            AssistantConversation.user_id
            == current_user.id,
        )
        .first()
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    db.delete(conversation)
    db.commit()

    return None