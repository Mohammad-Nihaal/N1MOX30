from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.automation.engine import WorkflowEngine
from app.automation.workflow_types import WorkflowStage
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.orchestration.context.workflow_context import (
    WorkflowContextBuilder,
)
from app.orchestration.policies.workflow_policy import (
    WorkflowPolicy,
)
from app.services.automation_service import (
    AutomationService,
)


class CentralWorkflowEngine:
    """
    Central N1MOX30 workflow orchestration layer.

    This is the single high-level entry point that future
    N1MOX features should use for workflow execution.

    Responsibilities:

    - Build creator-aware context
    - Resolve workflow policy
    - Create workflows
    - Execute workflows
    - Retrieve workflow state
    - Retry failed stages
    - Expose persistent workflow progress
    - Keep low-level stage execution behind WorkflowEngine

    The existing WorkflowEngine remains the low-level
    execution mechanism. This class is the central coordinator
    above it.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

        self.automation_service = AutomationService(
            db=db,
        )

        self.engine: WorkflowEngine = (
            self.automation_service.get_engine()
        )

        self.context_builder = (
            WorkflowContextBuilder(
                db=db,
            )
        )

    # ------------------------------------------------------------------
    # Workflow creation
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
    ) -> AutomationWorkflow:
        """
        Create a workflow using the existing persistent
        automation engine.
        """

        workflow = (
            self.automation_service.create_workflow(
                user_id=user_id,
                command=command,
                platform=platform,
                topic=topic,
            )
        )

        return workflow

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def build_context(
        self,
        *,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
    ) -> dict[str, Any]:
        """
        Build complete creator-aware execution context.
        """

        return self.context_builder.build(
            user_id=user_id,
            command=command,
            platform=platform,
            topic=topic,
        )

    # ------------------------------------------------------------------
    # Policy
    # ------------------------------------------------------------------

    def resolve_policy(
        self,
        *,
        context: dict[str, Any],
    ) -> WorkflowPolicy:
        """
        Resolve workflow execution policy from creator
        preferences.
        """

        creator = context.get(
            "creator",
            {},
        )

        preferences = creator.get(
            "preferences",
            {},
        )

        return WorkflowPolicy.from_preferences(
            preferences,
        )

    # ------------------------------------------------------------------
    # Create + context
    # ------------------------------------------------------------------

    def prepare(
        self,
        *,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
    ) -> dict[str, Any]:
        """
        Prepare a workflow together with its creator-aware
        context and resolved policy.
        """

        context = self.build_context(
            user_id=user_id,
            command=command,
            platform=platform,
            topic=topic,
        )

        policy = self.resolve_policy(
            context=context,
        )

        workflow = self.create(
            user_id=user_id,
            command=command,
            platform=platform,
            topic=topic,
        )

        return {
            "workflow": workflow,
            "context": context,
            "policy": policy,
        }

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow:
        """
        Execute a workflow after ownership verification.
        """

        return self.automation_service.run_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
        )

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    def retry(
        self,
        *,
        workflow_id: str,
        user_id: str,
        stage: WorkflowStage,
    ) -> AutomationWorkflow:
        """
        Retry a workflow stage after ownership verification.
        """

        return self.automation_service.retry_step(
            workflow_id=workflow_id,
            user_id=user_id,
            stage=stage,
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow | None:
        return self.automation_service.get_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
        )

    def get_steps(
        self,
        *,
        workflow_id: str,
    ) -> list[AutomationStep]:
        return self.automation_service.get_workflow_steps(
            workflow_id=workflow_id,
        )

    # ------------------------------------------------------------------
    # Detailed state
    # ------------------------------------------------------------------

    def get_detail(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        """
        Return workflow state plus creator context and policy.
        """

        workflow = self.get(
            workflow_id=workflow_id,
            user_id=user_id,
        )

        if workflow is None:
            return None

        steps = self.get_steps(
            workflow_id=workflow.id,
        )

        context = self.build_context(
            user_id=user_id,
            command=workflow.command,
            platform=workflow.platform,
            topic=workflow.topic,
        )

        policy = self.resolve_policy(
            context=context,
        )

        return {
            "workflow": workflow,
            "steps": steps,
            "context": context,
            "policy": policy,
        }

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        """
        Return concise workflow execution status.
        """

        workflow = self.get(
            workflow_id=workflow_id,
            user_id=user_id,
        )

        if workflow is None:
            return None

        steps = self.get_steps(
            workflow_id=workflow.id,
        )

        completed = sum(
            1
            for step in steps
            if step.status == "completed"
        )

        failed = sum(
            1
            for step in steps
            if step.status == "failed"
        )

        running = sum(
            1
            for step in steps
            if step.status == "running"
        )

        pending = sum(
            1
            for step in steps
            if step.status == "pending"
        )

        return {
            "workflow_id": workflow.id,
            "status": workflow.status,
            "current_stage": workflow.current_stage,
            "progress": workflow.progress,
            "steps": {
                "total": len(steps),
                "completed": completed,
                "failed": failed,
                "running": running,
                "pending": pending,
            },
        }