from datetime import datetime

from pydantic import BaseModel, Field


# =================================================
# ASSISTANT MESSAGE REQUEST
# =================================================


class PersonalAssistantMessageRequest(BaseModel):
    """
    Request for a message sent to the
    N1MOX30 Personal AI Assistant.
    """

    message: str = Field(
        min_length=1,
        max_length=5000,
    )


# =================================================
# ASSISTANT RESPONSE
# =================================================


class PersonalAssistantMessageResponse(BaseModel):
    """
    Response returned by the
    N1MOX30 Personal AI Assistant.
    """

    message: str

    provider: str

    personalized: bool

    generated_at: datetime


# =================================================
# PERSONAL CONTEXT RESPONSE
# =================================================


class PersonalContextResponse(BaseModel):
    """
    Summary of the personal context currently
    available to the N1MOX30 AI Assistant.
    """

    creator_profile: dict | None

    memories: list[dict]

    connected_accounts: list[dict]

    analytics: list[dict]