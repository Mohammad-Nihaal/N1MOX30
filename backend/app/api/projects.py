from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectDashboardResponse,
    ProjectLifecycleResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# =================================================
# CREATE
# =================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Create a new creator project.
    """

    service = ProjectService(db)

    return service.create_project(
        user_id=current_user.id,
        project_data=project_data,
    )


# =================================================
# LIST
# =================================================

@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_my_projects(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Return all projects owned by the current user.
    """

    service = ProjectService(db)

    return service.get_projects(
        user_id=current_user.id,
    )


# =================================================
# DASHBOARD
# =================================================

@router.get(
    "/{project_id}/dashboard",
    response_model=ProjectDashboardResponse,
)
def get_project_dashboard(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Return the complete project dashboard.
    """

    service = ProjectService(db)

    try:

        return service.get_project_dashboard(
            project_id=project_id,
            user_id=current_user.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# =================================================
# PAUSE
# =================================================

@router.post(
    "/{project_id}/pause",
    response_model=ProjectLifecycleResponse,
)
def pause_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Pause a project.
    """

    service = ProjectService(db)

    try:

        project = service.pause_project(
            project_id=project_id,
            user_id=current_user.id,
        )

        return ProjectLifecycleResponse(
            project=project,
            action="paused",
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# =================================================
# RESUME
# =================================================

@router.post(
    "/{project_id}/resume",
    response_model=ProjectLifecycleResponse,
)
def resume_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Resume a paused project.
    """

    service = ProjectService(db)

    try:

        project = service.resume_project(
            project_id=project_id,
            user_id=current_user.id,
        )

        return ProjectLifecycleResponse(
            project=project,
            action="resumed",
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# =================================================
# ARCHIVE
# =================================================

@router.post(
    "/{project_id}/archive",
    response_model=ProjectLifecycleResponse,
)
def archive_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Archive a project without deleting its data.
    """

    service = ProjectService(db)

    try:

        project = service.archive_project(
            project_id=project_id,
            user_id=current_user.id,
        )

        return ProjectLifecycleResponse(
            project=project,
            action="archived",
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# =================================================
# WORKFLOWS
# =================================================

@router.get(
    "/{project_id}/workflows",
)
def get_project_workflows(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Return every workflow belonging to the project.
    """

    service = ProjectService(db)

    try:

        return service.get_project_workflows(
            project_id=project_id,
            user_id=current_user.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# =================================================
# GET ONE
# =================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Return one project.
    """

    service = ProjectService(db)

    project = service.get_project(
        project_id=project_id,
        user_id=current_user.id,
    )

    if project is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


# =================================================
# UPDATE
# =================================================

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Update project information.
    """

    service = ProjectService(db)

    try:

        return service.update_project(
            project_id=project_id,
            user_id=current_user.id,
            project_data=project_data,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


# =================================================
# SYNC
# =================================================

@router.post(
    "/{project_id}/sync",
    response_model=ProjectResponse,
)
def sync_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Synchronize project statistics with
    its current workflows.
    """

    service = ProjectService(db)

    try:

        return service.sync_project_statistics(
            project_id=project_id,
            user_id=current_user.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


# =================================================
# DELETE
# =================================================

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Delete an empty project.

    Projects containing workflows cannot be deleted.
    """

    service = ProjectService(db)

    try:

        service.delete_project(
            project_id=project_id,
            user_id=current_user.id,
        )

    except ValueError as error:

        message = str(error)

        if message == "Project not found.":

            response_status = (
                status.HTTP_404_NOT_FOUND
            )

        else:

            response_status = (
                status.HTTP_400_BAD_REQUEST
            )

        raise HTTPException(
            status_code=response_status,
            detail=message,
        ) from error