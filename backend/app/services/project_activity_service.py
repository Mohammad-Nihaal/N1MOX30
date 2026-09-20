from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.project_activity import ProjectActivity


class ProjectActivityService:
    """
    Central service layer for N1MOX30 project activities.

    Responsibilities:
    - create project activity records
    - retrieve project activity timelines
    - retrieve workflow-related activities
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_activity(
        self,
        project_id: str,
        user_id: str,
        activity_type: str,
        title: str,
        description: str | None = None,
        workflow_id: str | None = None,
    ) -> ProjectActivity:
        """
        Create and persist a project activity.
        """

        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=description,
            workflow_id=workflow_id,
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        return activity

    def get_project_activities(
        self,
        project_id: str,
        user_id: str,
        limit: int = 100,
    ) -> list[ProjectActivity]:
        """
        Return activities belonging to one project.

        Activities are returned newest first.
        """

        return (
            self.db.query(ProjectActivity)
            .filter(
                ProjectActivity.project_id == project_id,
                ProjectActivity.user_id == user_id,
            )
            .order_by(
                ProjectActivity.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def get_workflow_activities(
        self,
        workflow_id: str,
        user_id: str,
        limit: int = 100,
    ) -> list[ProjectActivity]:
        """
        Return project activities related to one workflow.
        """

        return (
            self.db.query(ProjectActivity)
            .filter(
                ProjectActivity.workflow_id == workflow_id,
                ProjectActivity.user_id == user_id,
            )
            .order_by(
                ProjectActivity.created_at.desc(),
            )
            .limit(limit)
            .all()
        )