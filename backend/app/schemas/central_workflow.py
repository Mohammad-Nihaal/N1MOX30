from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CentralWorkflowCreate(BaseModel):
    """
    Request to create a centrally orchestrated workflow.
    """

    command: str = Field(
        min_length=1,
        max_length=10000,
    )

    platform: str = Field(
        default="youtube",
        min_length=1,
        max_length=100,
    )

    topic: str = Field(
        min_length=1,
        max_length=5000,
    )


class CentralWorkflowContextResponse(BaseModel):
    """
    Creator-aware context returned by the orchestration layer.
    """

    creator: dict[str, Any] = Field(
        default_factory=dict,
    )

    request: dict[str, Any] = Field(
        default_factory=dict,
    )


class CentralWorkflowResponse(BaseModel):
    """
    Central workflow response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    user_id: str
    command: str
    platform: str
    topic: str
    status: str
    current_stage: str | None = None
    progress: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CentralWorkflowDetailResponse(
    CentralWorkflowResponse
):
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    context: dict[str, Any] = Field(
        default_factory=dict,
    )

    policy: dict[str, Any] = Field(
        default_factory=dict,
    )


class CentralWorkflowActionResponse(BaseModel):
    message: str
    workflow: CentralWorkflowDetailResponse