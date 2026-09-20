from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.automation_workflow import AutomationWorkflow
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectDashboardResponse,
    ProjectUpdate,
    ProjectWorkflowStatistics,
    ProjectWorkflowSummary,
)
from app.services.project_activity_service import (
    ProjectActivityService,
)


class ProjectService:
    """
    Central project management service for N1MOX30.

    Responsibilities:

    - create projects
    - retrieve projects
    - update projects
    - delete projects
    - manage project lifecycle
    - attach workflows
    - detach workflows
    - synchronize workflow statistics
    - calculate project progress
    - generate project dashboards
    - identify active workflows
    - record project activity

    Projects are user-scoped.
    """

    ACTIVE_STATUSES = {
        "active",
        "running",
    }

    VALID_STATUSES = {
        "active",
        "paused",
        "completed",
        "archived",
    }

    WORKFLOW_COMPLETED = "completed"
    WORKFLOW_RUNNING = "running"
    WORKFLOW_FAILED = "failed"
    WORKFLOW_CANCELLED = "cancelled"
    WORKFLOW_PENDING = "pending"

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

        self.activity_service = ProjectActivityService(
            db=db,
        )

    # =================================================
    # CREATE
    # =================================================

    def create_project(
        self,
        user_id: str,
        project_data: ProjectCreate,
    ) -> Project:
        """
        Create a new project.
        """

        project = Project(
            user_id=user_id,
            title=project_data.title.strip(),
            description=project_data.description,
            platform=project_data.platform.strip().lower(),
            priority=project_data.priority.strip().lower(),
            status="active",
            progress=0,
            workflow_count=0,
            completed_workflow_count=0,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="project_created",
            title="Project created",
            description=(
                f"Project '{project.title}' "
                "was created."
            ),
        )

        return project

    # =================================================
    # READ
    # =================================================

    def get_projects(
        self,
        user_id: str,
    ) -> list[Project]:
        """
        Return all projects belonging to the user.
        """

        return (
            self.db.query(Project)
            .filter(
                Project.user_id == user_id,
            )
            .order_by(
                Project.updated_at.desc(),
            )
            .all()
        )

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

    # =================================================
    # UPDATE
    # =================================================

    def update_project(
        self,
        project_id: str,
        user_id: str,
        project_data: ProjectUpdate,
    ) -> Project:
        """
        Update project information.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        update_data = project_data.model_dump(
            exclude_unset=True,
        )

        previous_status = project.status

        for field, value in update_data.items():

            if isinstance(value, str):
                value = value.strip()

                if field in {
                    "platform",
                    "priority",
                    "status",
                }:
                    value = value.lower()

            setattr(
                project,
                field,
                value,
            )

        if project.status not in self.VALID_STATUSES:
            raise ValueError(
                "Invalid project status. "
                "Use active, paused, completed, "
                "or archived."
            )

        if project.status == "completed":

            if project.completed_at is None:
                project.completed_at = datetime.utcnow()

            project.progress = 100

        else:

            if previous_status == "completed":
                project.completed_at = None

        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        if (
            previous_status != "completed"
            and project.status == "completed"
        ):
            self.activity_service.create_activity(
                project_id=project.id,
                user_id=user_id,
                activity_type="project_completed",
                title="Project completed",
                description=(
                    f"Project '{project.title}' "
                    "was marked as completed."
                ),
            )

        elif (
            previous_status == "completed"
            and project.status != "completed"
        ):
            self.activity_service.create_activity(
                project_id=project.id,
                user_id=user_id,
                activity_type="project_reactivated",
                title="Project reactivated",
                description=(
                    f"Project '{project.title}' "
                    "was reactivated."
                ),
            )

        elif update_data:

            updated_fields = ", ".join(
                update_data.keys()
            )

            self.activity_service.create_activity(
                project_id=project.id,
                user_id=user_id,
                activity_type="project_updated",
                title="Project updated",
                description=(
                    "Updated project fields: "
                    f"{updated_fields}."
                ),
            )

        return project

    # =================================================
    # LIFECYCLE
    # =================================================

    def pause_project(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        """
        Pause a project.

        Existing workflows are preserved.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        if project.status == "archived":
            raise ValueError(
                "Archived projects cannot be paused."
            )

        project.status = "paused"
        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="project_paused",
            title="Project paused",
            description=(
                f"Project '{project.title}' "
                "was paused."
            ),
        )

        return project

    def resume_project(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        """
        Resume a paused project.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        if project.status == "archived":
            raise ValueError(
                "Archived projects cannot be resumed."
            )

        project.status = "active"
        project.completed_at = None
        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="project_resumed",
            title="Project resumed",
            description=(
                f"Project '{project.title}' "
                "was resumed."
            ),
        )

        return project

    def archive_project(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        """
        Archive a project.

        Archiving does not delete workflows.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        project.status = "archived"
        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="project_archived",
            title="Project archived",
            description=(
                f"Project '{project.title}' "
                "was archived."
            ),
        )

        return project

    # =================================================
    # WORKFLOW ASSOCIATION
    # =================================================

    def attach_workflow(
        self,
        project_id: str,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow:
        """
        Attach an existing workflow to a project.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        workflow = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.user_id == user_id,
            )
            .first()
        )

        if workflow is None:
            raise ValueError(
                "Workflow not found."
            )

        workflow.project_id = project.id

        self.db.commit()
        self.db.refresh(workflow)

        self.sync_project_statistics(
            project_id=project.id,
            user_id=user_id,
        )

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="workflow_attached",
            title="Workflow attached",
            description=(
                f"Workflow '{workflow.id}' "
                f"was attached to project "
                f"'{project.title}'."
            ),
            workflow_id=workflow.id,
        )

        return workflow

    def detach_workflow(
        self,
        project_id: str,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow:
        """
        Remove a workflow from a project.

        The workflow itself is not deleted.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        workflow = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.project_id == project.id,
                AutomationWorkflow.user_id == user_id,
            )
            .first()
        )

        if workflow is None:
            raise ValueError(
                "Workflow is not attached to this project."
            )

        workflow.project_id = None

        self.db.commit()
        self.db.refresh(workflow)

        self.sync_project_statistics(
            project_id=project.id,
            user_id=user_id,
        )

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="workflow_detached",
            title="Workflow detached",
            description=(
                f"Workflow '{workflow.id}' "
                "was detached from the project."
            ),
            workflow_id=workflow.id,
        )

        return workflow

    def get_project_workflows(
        self,
        project_id: str,
        user_id: str,
    ) -> list[AutomationWorkflow]:
        """
        Return every workflow belonging to a project.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        return (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.project_id == project.id,
                AutomationWorkflow.user_id == user_id,
            )
            .order_by(
                AutomationWorkflow.created_at.desc(),
            )
            .all()
        )

    # =================================================
    # STATISTICS
    # =================================================

    def sync_project_statistics(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        """
        Recalculate workflow count,
        completion count and project progress.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        workflows = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.project_id == project.id,
                AutomationWorkflow.user_id == user_id,
            )
            .all()
        )

        previous_progress = project.progress
        previous_status = project.status

        project.workflow_count = len(
            workflows
        )

        project.completed_workflow_count = sum(
            1
            for workflow in workflows
            if workflow.status
            == self.WORKFLOW_COMPLETED
        )

        if not workflows:

            project.progress = 0

        else:

            progress_values = [
                max(
                    0,
                    min(
                        100,
                        int(
                            getattr(
                                workflow,
                                "progress",
                                0,
                            )
                            or 0
                        ),
                    ),
                )
                for workflow in workflows
            ]

            project.progress = int(
                sum(progress_values)
                / len(progress_values)
            )

        if (
            workflows
            and project.completed_workflow_count
            == project.workflow_count
        ):
            project.progress = 100

            if project.status != "archived":
                project.status = "completed"

                if project.completed_at is None:
                    project.completed_at = datetime.utcnow()

        elif project.status == "completed":

            project.status = "active"
            project.completed_at = None

        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        if (
            previous_status != "completed"
            and project.status == "completed"
        ):
            self.activity_service.create_activity(
                project_id=project.id,
                user_id=user_id,
                activity_type="project_completed",
                title="Project completed",
                description=(
                    "All workflows in this project "
                    "were completed."
                ),
            )

        elif previous_progress != project.progress:

            self.activity_service.create_activity(
                project_id=project.id,
                user_id=user_id,
                activity_type="project_progress_updated",
                title="Project progress updated",
                description=(
                    f"Project progress changed from "
                    f"{previous_progress}% to "
                    f"{project.progress}%."
                ),
            )

        return project

    # =================================================
    # DASHBOARD
    # =================================================

    def get_project_dashboard(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectDashboardResponse:
        """
        Build the complete project dashboard.
        """

        project = self.sync_project_statistics(
            project_id=project_id,
            user_id=user_id,
        )

        workflows = self.get_project_workflows(
            project_id=project.id,
            user_id=user_id,
        )

        statistics = {
            "total": len(workflows),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for workflow in workflows:

            workflow_status = (
                workflow.status or "pending"
            ).lower()

            if workflow_status in statistics:
                statistics[workflow_status] += 1

        active_workflow = None

        for workflow in workflows:

            if workflow.status in {
                "running",
                "pending",
            }:

                active_workflow = (
                    self.workflow_to_summary(
                        workflow
                    )
                )

                if workflow.status == "running":
                    break

        recent_workflows = [
            self.workflow_to_summary(
                workflow
            )
            for workflow in workflows[:10]
        ]

        return ProjectDashboardResponse(
            project=project,
            workflow_statistics=(
                ProjectWorkflowStatistics(
                    **statistics
                )
            ),
            active_workflow=active_workflow,
            recent_workflows=recent_workflows,
        )

    # =================================================
    # WORKFLOW SUMMARY
    # =================================================

    @staticmethod
    def workflow_to_summary(
        workflow: AutomationWorkflow,
    ) -> ProjectWorkflowSummary:
        """
        Convert a workflow model into
        a dashboard-safe summary.
        """

        return ProjectWorkflowSummary(
            id=workflow.id,
            command=getattr(
                workflow,
                "command",
                "",
            )
            or "",
            platform=getattr(
                workflow,
                "platform",
                "",
            )
            or "",
            topic=getattr(
                workflow,
                "topic",
                "",
            )
            or "",
            status=getattr(
                workflow,
                "status",
                "pending",
            )
            or "pending",
            current_stage=getattr(
                workflow,
                "current_stage",
                None,
            ),
            progress=int(
                getattr(
                    workflow,
                    "progress",
                    0,
                )
                or 0
            ),
            error_message=getattr(
                workflow,
                "error_message",
                None,
            ),
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            completed_at=getattr(
                workflow,
                "completed_at",
                None,
            ),
        )

    # =================================================
    # DELETE
    # =================================================

    def delete_project(
        self,
        project_id: str,
        user_id: str,
    ) -> None:
        """
        Delete an empty project.

        Workflows are never automatically deleted.
        """

        project = self.get_project(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        workflow_count = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.project_id
                == project.id,
                AutomationWorkflow.user_id
                == user_id,
            )
            .count()
        )

        if workflow_count > 0:
            raise ValueError(
                "Cannot delete a project that "
                "contains workflows. "
                "Detach the workflows first."
            )

        project_title = project.title

        self.db.delete(project)
        self.db.commit()

        self.activity_service.create_activity(
            project_id=project.id,
            user_id=user_id,
            activity_type="project_deleted",
            title="Project deleted",
            description=(
                f"Project '{project_title}' "
                "was deleted."
            ),
        )