from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.project import ProjectResponse
from app.schemas.project_activity import (
    ProjectActivityResponse,
)


class ProjectWorkflowStatusCount(BaseModel):
    status: str
    count: int


class ProjectWorkflowSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    project_id: str | None

    command: str
    platform: str
    topic: str

    status: str
    current_stage: str | None
    progress: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ProjectDashboardStatistics(BaseModel):
    total_workflows: int

    completed_workflows: int
    running_workflows: int
    pending_workflows: int
    failed_workflows: int
    cancelled_workflows: int

    overall_progress: int


class ProjectDashboardResponse(BaseModel):
    project: ProjectResponse

    statistics: ProjectDashboardStatistics

    workflow_statuses: list[
        ProjectWorkflowStatusCount
    ]

    recent_workflows: list[
        ProjectWorkflowSummary
    ]

    active_workflows: list[
        ProjectWorkflowSummary
    ]

    completed_workflows: list[
        ProjectWorkflowSummary
    ]

    recent_activities: list[
        ProjectActivityResponse
    ]