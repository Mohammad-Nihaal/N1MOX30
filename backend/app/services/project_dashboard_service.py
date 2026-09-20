from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.automation_workflow import (
    AutomationWorkflow,
)
from app.models.project import Project
from app.schemas.project_dashboard import (
    ProjectDashboardResponse,
    ProjectDashboardStatistics,
    ProjectWorkflowStatusCount,
    ProjectWorkflowSummary,
)
from app.services.project_activity_service import (
    ProjectActivityService,
)


class ProjectDashboardService:
    """
    Central service for generating complete
    project dashboard information.

    Responsibilities:
    - retrieve project dashboard data
    - calculate workflow statistics
    - calculate project progress
    - group workflows by status
    - retrieve recent workflows
    - retrieve active workflows
    - retrieve completed workflows
    - retrieve recent project activities
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

        self.activity_service = ProjectActivityService(
            db=db,
        )

    def get_project_dashboard(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectDashboardResponse:
        """
        Generate complete dashboard information
        for one project.
        """

        project = (
            self.db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id,
            )
            .first()
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        workflows = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.project_id
                == project.id,
                AutomationWorkflow.user_id
                == user_id,
            )
            .order_by(
                AutomationWorkflow.updated_at.desc()
            )
            .all()
        )

        total_workflows = len(
            workflows
        )

        completed_workflows_count = len(
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

        pending_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status in [
                    "pending",
                    "created",
                ]
            ]
        )

        failed_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "failed"
            ]
        )

        cancelled_workflows = len(
            [
                workflow
                for workflow in workflows
                if workflow.status == "cancelled"
            ]
        )

        workflow_statuses = self._build_status_counts(
            workflows=workflows,
        )

        recent_workflows = [
            self._serialize_workflow(
                workflow
            )
            for workflow in workflows[:10]
        ]

        active_workflows = [
            self._serialize_workflow(
                workflow
            )
            for workflow in workflows
            if workflow.status in [
                "running",
                "pending",
                "created",
            ]
        ]

        completed_workflow_items = [
            self._serialize_workflow(
                workflow
            )
            for workflow in workflows
            if workflow.status == "completed"
        ]

        recent_activities = (
            self.activity_service.get_project_activities(
                project_id=project.id,
                user_id=user_id,
                limit=20,
            )
        )

        statistics = ProjectDashboardStatistics(
            total_workflows=total_workflows,
            completed_workflows=completed_workflows_count,
            running_workflows=running_workflows,
            pending_workflows=pending_workflows,
            failed_workflows=failed_workflows,
            cancelled_workflows=cancelled_workflows,
            overall_progress=project.progress,
        )

        return ProjectDashboardResponse(
            project=project,
            statistics=statistics,
            workflow_statuses=workflow_statuses,
            recent_workflows=recent_workflows,
            active_workflows=active_workflows,
            completed_workflows=completed_workflow_items,
            recent_activities=recent_activities,
        )

    def _build_status_counts(
        self,
        workflows: list[AutomationWorkflow],
    ) -> list[ProjectWorkflowStatusCount]:
        """
        Build workflow counts grouped by status.
        """

        status_counts: dict[
            str,
            int,
        ] = {}

        for workflow in workflows:

            status = workflow.status

            if status not in status_counts:
                status_counts[status] = 0

            status_counts[status] += 1

        return [
            ProjectWorkflowStatusCount(
                status=status,
                count=count,
            )
            for status, count
            in sorted(
                status_counts.items()
            )
        ]

    def _serialize_workflow(
        self,
        workflow: AutomationWorkflow,
    ) -> ProjectWorkflowSummary:
        """
        Convert a workflow database model into
        dashboard workflow response data.
        """

        current_stage = None

        if workflow.current_stage is not None:

            current_stage = str(
                workflow.current_stage
            )

        return ProjectWorkflowSummary(
            id=workflow.id,
            project_id=workflow.project_id,
            command=workflow.command,
            platform=workflow.platform,
            topic=workflow.topic,
            status=workflow.status,
            current_stage=current_stage,
            progress=workflow.progress,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            completed_at=workflow.completed_at,
        )