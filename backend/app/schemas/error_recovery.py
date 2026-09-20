from typing import Any

from pydantic import BaseModel


class RecoveryResponse(BaseModel):
    workflow_id: str
    status: str
    workflow_status: str | None = None
    message: str | None = None
    recoveries: list[dict[str, Any]] = []


class StepRecoveryResponse(BaseModel):
    step_id: str
    stage: str
    status: str
    workflow_status: str | None = None
    message: str | None = None
    error: str | None = None
    result: Any = None


class RecoveryStatusResponse(BaseModel):
    workflow_id: str
    workflow_status: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    recovery_available: bool
    failures: list[dict[str, Any]]
