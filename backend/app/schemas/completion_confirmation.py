from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompletionConfirmationRequest(BaseModel):
    workflow_id: str
    force: bool = False


class CompletionCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class CompletionConfirmationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    status: str
    confirmed: bool
    score: float = Field(ge=0, le=1)
    checks: list[CompletionCheck]
    message: str
    created_at: datetime
    updated_at: datetime