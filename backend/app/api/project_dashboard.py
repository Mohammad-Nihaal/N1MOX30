from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project_dashboard import (
    ProjectDashboardResponse,
)
from app.services.project_dashboard_service import (
    ProjectDashboardService,
)


router = APIRouter(
    prefix="/project-dashboard",
    tags=["Project Dashboard"],
)


@router.get(
    "/{project_id}",
    response_model=ProjectDashboardResponse,
)
def get_project_dashboard(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return complete dashboard information
    for one project.
    """

    service = ProjectDashboardService(
        db=db,
    )

    try:
        return service.get_project_dashboard(
            project_id=project_id,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error