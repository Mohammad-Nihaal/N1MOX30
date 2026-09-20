from __future__ import annotations

from sqlalchemy.orm import Session

from app.automation.engine import WorkflowEngine
from app.automation.handlers.captions_handler import (
    captions_stage_handler,
)
from app.automation.handlers.hooks_handler import (
    hooks_stage_handler,
)
from app.automation.handlers.metadata_handler import (
    metadata_stage_handler,
)
from app.automation.handlers.publishing_handler import (
    publishing_stage_handler,
)
from app.automation.handlers.quality_check_handler import (
    quality_check_stage_handler,
)
from app.automation.handlers.research_handler import (
    research_stage_handler,
)
from app.automation.handlers.scheduling_handler import (
    scheduling_stage_handler,
)
from app.automation.handlers.script_handler import (
    script_stage_handler,
)
from app.automation.handlers.strategy_handler import (
    strategy_stage_handler,
)
from app.automation.handlers.thumbnail_handler import (
    thumbnail_stage_handler,
)
from app.automation.handlers.video_handler import (
    video_stage_handler,
)
from app.automation.handlers.visuals_handler import (
    visuals_stage_handler,
)
from app.automation.handlers.voice_handler import (
    voice_stage_handler,
)
from app.automation.workflow_types import WorkflowStage
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.project import Project
from app.services.project_activity_service import (
    ProjectActivityService,
)
from app.services.project_service import ProjectService


class AutomationService:
    """
    Central service layer for the N1MOX30 automation system.

    Responsibilities:
    - connect API routes to WorkflowEngine
    - register all workflow stage handlers
    - create workflows
    - connect workflows to projects
    - retrieve workflows and steps
    - execute workflows
    - retry workflow stages
    - synchronize project progress
    - create project activity records
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

        self.engine = WorkflowEngine(
            db=db,
        )

        self.activity_service = ProjectActivityService(
            db=db,
        )

        self.project_service = ProjectService(
            db=db,
        )

        self.engine.register_handlers(
            {
                WorkflowStage.RESEARCH: research_stage_handler,
                WorkflowStage.STRATEGY: strategy_stage_handler,
                WorkflowStage.HOOKS: hooks_stage_handler,
                WorkflowStage.SCRIPT: script_stage_handler,
                WorkflowStage.VOICE: voice_stage_handler,
                WorkflowStage.VISUALS: visuals_stage_handler,
                WorkflowStage.VIDEO: video_stage_handler,
                WorkflowStage.CAPTIONS: captions_stage_handler,
                WorkflowStage.THUMBNAIL: thumbnail_stage_handler,
                WorkflowStage.METADATA: metadata_stage_handler,
                WorkflowStage.QUALITY_CHECK: quality_check_stage_handler,
                WorkflowStage.SCHEDULING: scheduling_stage_handler,
                WorkflowStage.PUBLISHING: publishing_stage_handler,
            }
        )

    def get_engine(
        self,
    ) -> WorkflowEngine:
        """Return the configured workflow engine."""

        return self.engine

    def create_workflow(
        self,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
        project_id: str | None = None,
    ) -> AutomationWorkflow:
        """
        Create a new automation workflow.

        If a project_id is provided, verify that the project belongs
        to the current user and connect the workflow to that project.
        """

        if project_id is not None:
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

        workflow = self.engine.create_workflow(
            user_id=user_id,
            command=command,
            platform=platform,
            topic=topic,
            project_id=project_id,
        )

        if project_id is not None:
            self.activity_service.create_activity(
                project_id=project_id,
                user_id=user_id,
                workflow_id=workflow.id,
                activity_type="workflow_created",
                title="Workflow created",
                description=(
                    f"Workflow for topic '{workflow.topic}' "
                    "was created."
                ),
            )

            self.sync_project(
                project_id=project_id,
                user_id=user_id,
            )

        return workflow

    def get_workflow(
        self,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow | None:
        """Return one workflow belonging to a user."""

        return self.engine.get_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
        )

    def get_workflow_steps(
        self,
        workflow_id: str,
    ) -> list[AutomationStep]:
        """Return workflow steps in execution order."""

        return self.engine.get_steps(
            workflow_id=workflow_id,
        )

    def run_workflow(
        self,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow:
        """
        Execute a workflow after verifying ownership.
        """

        workflow = self.engine.get_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
        )

        if workflow is None:
            raise ValueError(
                "Automation workflow not found."
            )

        if workflow.project_id is not None:
            self.activity_service.create_activity(
                project_id=workflow.project_id,
                user_id=user_id,
                workflow_id=workflow.id,
                activity_type="workflow_started",
                title="Workflow started",
                description=(
                    f"Workflow for topic '{workflow.topic}' "
                    "started execution."
                ),
            )

        workflow = self.engine.run_workflow(
            workflow_id=workflow.id,
        )

        if workflow.project_id is not None:
            if workflow.status == "completed":
                self.activity_service.create_activity(
                    project_id=workflow.project_id,
                    user_id=user_id,
                    workflow_id=workflow.id,
                    activity_type="workflow_completed",
                    title="Workflow completed",
                    description=(
                        f"Workflow for topic '{workflow.topic}' "
                        "completed successfully."
                    ),
                )

            elif workflow.status == "failed":
                self.activity_service.create_activity(
                    project_id=workflow.project_id,
                    user_id=user_id,
                    workflow_id=workflow.id,
                    activity_type="workflow_failed",
                    title="Workflow failed",
                    description=(
                        workflow.error_message
                        or (
                            f"Workflow for topic "
                            f"'{workflow.topic}' failed."
                        )
                    ),
                )

            self.sync_project(
                project_id=workflow.project_id,
                user_id=user_id,
            )

        return workflow

    def retry_step(
        self,
        workflow_id: str,
        user_id: str,
        stage: WorkflowStage,
    ) -> AutomationWorkflow:
        """
        Retry a workflow stage after verifying ownership.
        """

        workflow = self.engine.get_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
        )

        if workflow is None:
            raise ValueError(
                "Automation workflow not found."
            )

        if workflow.project_id is not None:
            self.activity_service.create_activity(
                project_id=workflow.project_id,
                user_id=user_id,
                workflow_id=workflow.id,
                activity_type="workflow_stage_retried",
                title="Workflow stage retried",
                description=(
                    f"Stage '{stage.value}' was retried for "
                    f"workflow topic '{workflow.topic}'."
                ),
            )

        workflow = self.engine.retry_step(
            workflow_id=workflow.id,
            stage=stage,
        )

        if workflow.project_id is not None:
            if workflow.status == "completed":
                self.activity_service.create_activity(
                    project_id=workflow.project_id,
                    user_id=user_id,
                    workflow_id=workflow.id,
                    activity_type="workflow_completed",
                    title="Workflow completed",
                    description=(
                        f"Workflow for topic '{workflow.topic}' "
                        "completed successfully after retry."
                    ),
                )

            elif workflow.status == "failed":
                self.activity_service.create_activity(
                    project_id=workflow.project_id,
                    user_id=user_id,
                    workflow_id=workflow.id,
                    activity_type="workflow_failed",
                    title="Workflow failed",
                    description=(
                        workflow.error_message
                        or "Workflow failed after retry."
                    ),
                )

            self.sync_project(
                project_id=workflow.project_id,
                user_id=user_id,
            )

        return workflow

    def sync_project(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        """
        Synchronize project workflow statistics and progress.
        """

        return self.project_service.sync_project_statistics(
            project_id=project_id,
            user_id=user_id,
        )