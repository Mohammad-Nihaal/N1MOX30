from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.automation_workflow import (
    AutomationWorkflow,
)
from app.models.project import Project
from app.models.user import User
from app.schemas.project_dashboard import (
    ProjectWorkflowSummary,
)


router = APIRouter(
    prefix="/project-workflows",
    tags=["Project Workflows"],
)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectWorkflowSummary],
)
def get_project_workflows(
    project_id: str,
    status: str | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return workflows belonging to a project.

    Optionally filter workflows by status.
    """

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    query = (
        db.query(AutomationWorkflow)
        .filter(
            AutomationWorkflow.project_id == project.id,
            AutomationWorkflow.user_id == current_user.id,
        )
    )

    if status is not None:
        query = query.filter(
            AutomationWorkflow.status == status,
        )

    workflows = (
        query
        .order_by(
            AutomationWorkflow.created_at.desc(),
        )
        .limit(limit)
        .all()
    )

    return workflows