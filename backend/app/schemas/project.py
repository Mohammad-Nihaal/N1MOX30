from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    platform: str = Field(
        default="youtube",
        min_length=2,
        max_length=50,
    )

    priority: str = Field(
        default="medium",
        min_length=2,
        max_length=50,
    )


class ProjectUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    platform: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    status: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    priority: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    user_id: str

    title: str
    description: str | None

    platform: str
    status: str
    priority: str

    progress: int

    workflow_count: int
    completed_workflow_count: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ProjectWorkflowSummary(BaseModel):
    """
    Lightweight workflow information used
    inside the project dashboard.
    """

    id: str

    command: str
    platform: str
    topic: str

    status: str
    current_stage: str | None
    progress: int

    error_message: str | None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ProjectWorkflowStatistics(BaseModel):
    """
    Aggregated workflow statistics
    for one project.
    """

    total: int

    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int


class ProjectDashboardResponse(BaseModel):
    """
    Complete project dashboard.

    Contains project information,
    workflow statistics, active workflow,
    and recent workflows.
    """

    project: ProjectResponse

    workflow_statistics: ProjectWorkflowStatistics

    active_workflow: ProjectWorkflowSummary | None

    recent_workflows: list[
        ProjectWorkflowSummary
    ]


class ProjectWorkflowAttachRequest(BaseModel):
    """
    Attach an existing workflow to a project.
    """

    workflow_id: str = Field(
        min_length=1,
        max_length=36,
    )


class ProjectLifecycleResponse(BaseModel):
    """
    Result returned after a project lifecycle action.
    """

    project: ProjectResponse

    action: str