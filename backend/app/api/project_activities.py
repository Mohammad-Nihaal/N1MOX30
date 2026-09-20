from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project_activity import (
    ProjectActivityResponse,
)
from app.services.project_activity_service import (
    ProjectActivityService,
)


router = APIRouter(
    prefix="/project-activities",
    tags=["Project Activities"],
)


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectActivityResponse],
)
def get_project_activities(
    project_id: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the activity timeline for one project.
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

    service = ProjectActivityService(db)

    return service.get_project_activities(
        project_id=project.id,
        user_id=current_user.id,
        limit=limit,
    )


@router.get(
    "/workflow/{workflow_id}",
    response_model=list[ProjectActivityResponse],
)
def get_workflow_activities(
    workflow_id: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return project activities related to one workflow.
    """

    service = ProjectActivityService(db)

    return service.get_workflow_activities(
        workflow_id=workflow_id,
        user_id=current_user.id,
        limit=limit,
    )