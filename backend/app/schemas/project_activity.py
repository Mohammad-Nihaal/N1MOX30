from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectActivityResponse(BaseModel):
    """
    Response schema for one project activity.
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