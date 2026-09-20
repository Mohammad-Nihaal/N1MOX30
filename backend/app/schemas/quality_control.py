from typing import Any

from pydantic import BaseModel


class QualityControlResponse(BaseModel):
    workflow_id: str
    status: str
    score: float
    passed_checks: int
    total_checks: int
    failed_checks: list[str]
    checks: list[dict[str, Any]]


class StepQualityControlResponse(BaseModel):
    step_id: str
    stage: str
    score: float
    status: str
    checks: list[dict[str, Any]]
