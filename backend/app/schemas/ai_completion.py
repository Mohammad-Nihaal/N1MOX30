from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AICompletionCreate(BaseModel):
    """
    Create a confirmation record for an AI-generated result.
    """

    generation_id: str | None = None

    workflow_id: str | None = None

    project_id: str | None = None

    content_type: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    content: str = Field(
        min_length=1,
    )


class AICompletionApprove(BaseModel):
    """
    Approve an AI completion.
    """

    pass


class AICompletionReject(BaseModel):
    """
    Reject an AI completion.
    """

    rejection_reason: str | None = Field(
        default=None,
        max_length=5000,
    )


class AICompletionResponse(BaseModel):
    """
    Response schema for AI completion records.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    generation_id: str | None
    workflow_id: str | None
    project_id: str | None

    content_type: str

    title: str
    content: str

    status: str

    rejection_reason: str | None

    approved_at: datetime | None
    rejected_at: datetime | None

    created_at: datetime
    updated_at: datetime