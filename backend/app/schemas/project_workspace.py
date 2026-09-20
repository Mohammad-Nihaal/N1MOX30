from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.automation import AutomationWorkflowResponse
from app.schemas.project import ProjectResponse


class ProjectActivityResponse(BaseModel):
    """
    Response model for a project activity.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    project_id: str
    user_id: str

    activity_type: str
    title: str
    description: str | None

    workflow_id: str | None

    created_at: datetime


class ProjectWorkspaceSummary(BaseModel):
    """
    High-level project workspace statistics.
    """

    project_id: str

    total_workflows: int
    completed_workflows: int
    running_workflows: int
    failed_workflows: int
    pending_workflows: int

    progress: int


class ProjectWorkspaceResponse(BaseModel):
    """
    Complete project workspace response.

    Combines:
    - project information
    - workflow statistics
    - project workflows
    - recent project activity
    """

    project: ProjectResponse

    summary: ProjectWorkspaceSummary

    workflows: list[
        AutomationWorkflowResponse
    ]

    activities: list[
        ProjectActivityResponse
    ]


class ProjectActivityCreate(BaseModel):
    """
    Internal/API request model for creating
    a project activity.
    """

    activity_type: str = Field(
        min_length=2,
        max_length=100,
    )

    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    workflow_id: str | None = None