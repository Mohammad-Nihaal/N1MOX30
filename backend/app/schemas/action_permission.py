from typing import Any

from pydantic import BaseModel, Field


class ActionPermissionRequest(BaseModel):
    action: str = Field(min_length=1)


class ActionApprovalRequest(BaseModel):
    action: str = Field(min_length=1)


class ActionRejectionRequest(BaseModel):
    action: str = Field(min_length=1)
    reason: str | None = None


class ActionPermissionResponse(BaseModel):
    workflow_id: str
    action: str
    allowed: bool
    approval_required: bool
    status: str
    reason: str | None = None
    approved_at: str | None = None
    rejected_at: str | None = None
    requested_at: str | None = None


class WorkflowPermissionResponse(BaseModel):
    workflow_id: str
    workflow_status: str
    permissions: list[dict[str, Any]]
    approval_required: bool
