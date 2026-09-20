from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project_workspace import (
    ProjectActivityCreate,
    ProjectActivityResponse,
    ProjectWorkspaceResponse,
    ProjectWorkspaceSummary,
)
from app.services.project_workspace_service import (
    ProjectWorkspaceService,
)


router = APIRouter(
    prefix="/projects",
    tags=["Project Workspace"],
)


# --------------------------------------------------
# Complete project workspace
# --------------------------------------------------

@router.get(
    "/{project_id}/workspace",
    response_model=ProjectWorkspaceResponse,
)
def get_project_workspace(
    project_id: str,
    activity_limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the complete project workspace.

    Includes:
    - project information
    - workflow summary
    - project workflows
    - project activity timeline
    """

    service = ProjectWorkspaceService(db)

    try:
        workspace = service.get_workspace(
            project_id=project_id,
            user_id=current_user.id,
            activity_limit=activity_limit,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return workspace


# --------------------------------------------------
# Workspace summary
# --------------------------------------------------

@router.get(
    "/{project_id}/workspace/summary",
    response_model=ProjectWorkspaceSummary,
)
def get_project_workspace_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return workflow statistics for a project.
    """

    service = ProjectWorkspaceService(db)

    project = service.get_project(
        project_id=project_id,
        user_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    summary = service.get_workspace_summary(
        project_id=project_id,
        user_id=current_user.id,
    )

    return {
        "project_id": project.id,
        **summary,
    }


# --------------------------------------------------
# Project activities
# --------------------------------------------------

@router.get(
    "/{project_id}/activities",
    response_model=list[ProjectActivityResponse],
)
def get_project_activities(
    project_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the project activity timeline.
    """

    service = ProjectWorkspaceService(db)

    project = service.get_project(
        project_id=project_id,
        user_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return service.get_project_activities(
        project_id=project_id,
        user_id=current_user.id,
        limit=limit,
    )


# --------------------------------------------------
# Create project activity
# --------------------------------------------------

@router.post(
    "/{project_id}/activities",
    response_model=ProjectActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_activity(
    project_id: str,
    activity_data: ProjectActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a project activity.

    This endpoint is also useful for future frontend
    and external automation integrations.
    """

    service = ProjectWorkspaceService(db)

    try:
        return service.create_activity(
            project_id=project_id,
            user_id=current_user.id,
            activity_type=activity_data.activity_type,
            title=activity_data.title,
            description=activity_data.description,
            workflow_id=activity_data.workflow_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error