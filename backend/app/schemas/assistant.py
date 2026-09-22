from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =================================================
# ASSISTANT CHAT REQUEST
# =================================================


class AssistantChatRequest(BaseModel):
    """
    Request sent by the creator to the
    N1MOX30 Personal Creator AI Assistant.
    """

    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    conversation_type: str = Field(
        default="chat",
        max_length=100,
    )


# =================================================
# ASSISTANT CHAT RESPONSE
# =================================================


class AssistantChatResponse(BaseModel):
    """
    Response returned by the N1MOX30
    Personal Creator AI Assistant.
    """

    conversation_id: str

    message: str

    response: str

    provider: str

    conversation_type: str

    action_type: str | None = None

    action_status: str | None = None

    created_at: datetime


# =================================================
# ASSISTANT CONVERSATION ITEM
# =================================================


class AssistantConversationResponse(BaseModel):
    """
    Single conversation record.
    """

    id: str

    role: str

    message: str

    response: str | None = None

    conversation_type: str

    action_type: str | None = None

    action_status: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =================================================
# ASSISTANT CONVERSATION HISTORY
# =================================================


class AssistantConversationHistoryResponse(BaseModel):
    """
    Paginated assistant conversation history.
    """

    total: int

    limit: int

    offset: int

    conversations: list[
        AssistantConversationResponse
    ]
