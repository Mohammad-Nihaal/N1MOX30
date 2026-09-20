from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.automation_workflow import AutomationWorkflow
from app.models.project import Project
from app.models.project_activity import ProjectActivity


class ProjectWorkspaceService:
    """
    Central service for the N1MOX30 Project Workspace.

    Responsibilities:
    - retrieve project workspace data
    - calculate workflow statistics
    - retrieve project workflows
    - manage project activities
    - build project timeline information
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # --------------------------------------------------
    # Project retrieval
    # --------------------------------------------------

    def get_project(
        self,
        project_id: str,
        user_id: str,
    ) -> Project | None:
        """
        Return one project belonging to the user.
        """

        return (
            self.db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id,
            )
            .first()
        )

    # --------------------------------------------------
    # Workflow retrieval
    # --------------------------------------------------

    def get_project_workflows(
        self,
        project_id: str,
        user_id: str,
    ) -> list[AutomationWorkflow]:
        """
        Return all workflows belonging to a project.
        """

        return (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.project_id
                == project_id,
                AutomationWorkflow.user_id
                == user_id,
            )
            .order_by(
                AutomationWorkflow.created_at.desc(),
            )
            .all()
        )

    # --------------------------------------------------
    # Activity retrieval
    # --------------------------------------------------

    def get_project_activities(
        self,
        project_id: str,
        user_id: str,
        limit: int = 50,
    ) -> list[ProjectActivity]:
        """
        Return recent project activities.
        """

        return (
            self.db.query(ProjectActivity)
            .filter(
                ProjectActivity.project_id
                == project_id,
                ProjectActivity.user_id
                == user_id,
            )
            .order_by(
                ProjectActivity.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    # --------------------------------------------------
    # Activity creation
    # --------------------------------------------------

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
        Create a persistent project activity.

        The project ownership is verified before
        the activity is created.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

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

    # --------------------------------------------------
    # Summary calculation
    # --------------------------------------------------

    def get_workspace_summary(
        self,
        project_id: str,
        user_id: str,
    ) -> dict[str, int]:
        """
        Calculate workflow statistics for a project.
        """

        workflows = self.get_project_workflows(
            project_id=project_id,
            user_id=user_id,
        )

        total_workflows = len(workflows)

        completed_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "completed"
            ]
        )

        running_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "running"
            ]
        )

        failed_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "failed"
            ]
        )

        pending_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "pending"
            ]
        )

        if total_workflows == 0:
            progress = 0

        else:
            total_progress = sum(
                workflow.progress
                for workflow in workflows
            )

            progress = int(
                total_progress / total_workflows
            )

        return {
            "total_workflows": total_workflows,
            "completed_workflows": (
                completed_workflows
            ),
            "running_workflows": (
                running_workflows
            ),
            "failed_workflows": failed_workflows,
            "pending_workflows": (
                pending_workflows
            ),
            "progress": progress,
        }

    # --------------------------------------------------
    # Complete workspace
    # --------------------------------------------------

    def get_workspace(
        self,
        project_id: str,
        user_id: str,
        activity_limit: int = 50,
    ) -> dict:
        """
        Build the complete project workspace.

        Returns:
        - project
        - summary
        - workflows
        - activities
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        summary = self.get_workspace_summary(
            project_id=project_id,
            user_id=user_id,
        )

        workflows = self.get_project_workflows(
            project_id=project_id,
            user_id=user_id,
        )

        activities = self.get_project_activities(
            project_id=project_id,
            user_id=user_id,
            limit=activity_limit,
        )

        return {
            "project": project,
            "summary": {
                "project_id": project.id,
                **summary,
            },
            "workflows": workflows,
            "activities": activities,
        }