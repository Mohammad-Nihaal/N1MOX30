from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AutomationWorkflowCreate(BaseModel):
    command: str = Field(
        min_length=2,
        max_length=5000,
    )

    platform: str = Field(
        min_length=2,
        max_length=50,
    )

    topic: str = Field(
        min_length=2,
        max_length=1000,
    )

    project_id: str | None = None


class AutomationWorkflowProjectUpdate(BaseModel):
    """
    Assign, move, or remove a workflow
    from a project.

    Set project_id to:
    - a project ID to assign or move
    - null to remove the workflow from its project
    """

    project_id: str | None = None


class AutomationStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    stage: str
    step_order: int
    status: str

    input_data: str | None
    output_data: str | None
    error_message: str | None

    attempts: int

    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AutomationWorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: str | None

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


class AutomationWorkflowDetailResponse(
    AutomationWorkflowResponse
):
    steps: list[AutomationStepResponse]


class AutomationWorkflowActionResponse(BaseModel):
    message: str
    workflow: AutomationWorkflowDetailResponse