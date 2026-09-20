from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.automation.workflow_types import (
    WorkflowStage,
    WorkflowStatus,
)
from app.models.automation_workflow import AutomationWorkflow
from app.models.automation_step import AutomationStep
from app.services.automation_service import AutomationService


class VoiceWorkflowControlService:
    """
    Step 34:
    Voice-driven workflow control.

    Supports:
        status
        pause
        resume
        cancel
        retry

    Ownership is always checked before modifying a workflow.
    """

    def __init__(self, db: Session):
        self.db = db

    def _get_workflow(
        self,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow:

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
                "Automation workflow not found."
            )

        return workflow

    @staticmethod
    def _status(
        workflow: AutomationWorkflow,
    ) -> str:

        return str(
            workflow.status
        ).split(".")[-1].lower()

    def status(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any]:

        workflow = self._get_workflow(
            workflow_id,
            user_id,
        )

        steps = (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id
                == workflow.id
            )
            .order_by(
                AutomationStep.step_order.asc()
            )
            .all()
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

        return {
            "executed": True,
            "action": "workflow_status",
            "workflow_id": workflow.id,
            "status": self._status(workflow),
            "current_stage": workflow.current_stage,
            "progress": workflow.progress,
            "completed_steps": completed,
            "failed_steps": failed,
            "total_steps": len(steps),
            "error_message": workflow.error_message,
            "message": (
                f"Workflow is {self._status(workflow)} "
                f"at {workflow.progress}% progress."
            ),
        }

    def pause(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any]:

        workflow = self._get_workflow(
            workflow_id,
            user_id,
        )

        current = self._status(workflow)

        if current == WorkflowStatus.COMPLETED.value:
            return {
                "executed": False,
                "action": "pause_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow is already completed."
                ),
            }

        if current == WorkflowStatus.CANCELLED.value:
            return {
                "executed": False,
                "action": "pause_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow has already been cancelled."
                ),
            }

        if current == WorkflowStatus.PAUSED.value:
            return {
                "executed": False,
                "action": "pause_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow is already paused."
                ),
            }

        workflow.status = WorkflowStatus.PAUSED.value
        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        return {
            "executed": True,
            "action": "pause_workflow",
            "workflow_id": workflow.id,
            "status": workflow.status,
            "current_stage": workflow.current_stage,
            "message": (
                "The workflow has been paused. "
                "It will remain paused until you resume it."
            ),
        }

    def resume(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any]:

        workflow = self._get_workflow(
            workflow_id,
            user_id,
        )

        current = self._status(workflow)

        if current == WorkflowStatus.CANCELLED.value:
            return {
                "executed": False,
                "action": "resume_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "A cancelled workflow cannot be resumed."
                ),
            }

        if current == WorkflowStatus.COMPLETED.value:
            return {
                "executed": False,
                "action": "resume_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow is already completed."
                ),
            }

        if current not in {
            WorkflowStatus.PAUSED.value,
            WorkflowStatus.PENDING.value,
            WorkflowStatus.FAILED.value,
        }:
            return {
                "executed": False,
                "action": "resume_workflow",
                "workflow_id": workflow.id,
                "message": (
                    f"The workflow is currently {current}."
                ),
            }

        if current == WorkflowStatus.FAILED.value:
            return {
                "executed": False,
                "action": "resume_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow has failed. "
                    "Retry the failed stage first."
                ),
            }

        workflow.status = WorkflowStatus.PENDING.value
        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        engine = AutomationService(self.db).get_engine()

        try:
            result = engine.run_workflow(
                workflow.id
            )
        except Exception as error:
            return {
                "executed": False,
                "action": "resume_workflow",
                "workflow_id": workflow.id,
                "message": (
                    f"Workflow resume failed: {error}"
                ),
            }

        return {
            "executed": True,
            "action": "resume_workflow",
            "workflow_id": result.id,
            "status": str(result.status),
            "progress": result.progress,
            "current_stage": result.current_stage,
            "message": (
                "The workflow has been resumed."
            ),
        }

    def cancel(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any]:

        workflow = self._get_workflow(
            workflow_id,
            user_id,
        )

        current = self._status(workflow)

        if current == WorkflowStatus.COMPLETED.value:
            return {
                "executed": False,
                "action": "cancel_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "A completed workflow cannot be cancelled."
                ),
            }

        if current == WorkflowStatus.CANCELLED.value:
            return {
                "executed": False,
                "action": "cancel_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "This workflow is already cancelled."
                ),
            }

        workflow.status = WorkflowStatus.CANCELLED.value
        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        return {
            "executed": True,
            "action": "cancel_workflow",
            "workflow_id": workflow.id,
            "status": workflow.status,
            "message": (
                "The workflow has been cancelled."
            ),
        }

    def retry(
        self,
        *,
        workflow_id: str,
        user_id: str,
    ) -> dict[str, Any]:

        workflow = self._get_workflow(
            workflow_id,
            user_id,
        )

        stage = workflow.current_stage

        if not stage:
            failed_step = (
                self.db.query(AutomationStep)
                .filter(
                    AutomationStep.workflow_id
                    == workflow.id,
                    AutomationStep.status
                    == "failed",
                )
                .order_by(
                    AutomationStep.step_order.desc()
                )
                .first()
            )

            if failed_step:
                stage = failed_step.stage

        if not stage:
            return {
                "executed": False,
                "action": "retry_workflow",
                "workflow_id": workflow.id,
                "message": (
                    "There is no failed or current stage "
                    "available to retry."
                ),
            }

        try:
            workflow_stage = WorkflowStage(stage)
        except ValueError:
            return {
                "executed": False,
                "action": "retry_workflow",
                "workflow_id": workflow.id,
                "message": (
                    f"Unknown workflow stage: {stage}"
                ),
            }

        engine = AutomationService(self.db).get_engine()

        try:
            result = engine.retry_step(
                workflow_id=workflow.id,
                stage=workflow_stage,
            )
        except Exception as error:
            return {
                "executed": False,
                "action": "retry_workflow",
                "workflow_id": workflow.id,
                "message": (
                    f"Workflow retry failed: {error}"
                ),
            }

        return {
            "executed": True,
            "action": "retry_workflow",
            "workflow_id": result.id,
            "status": str(result.status),
            "progress": result.progress,
            "current_stage": result.current_stage,
            "message": (
                f"The {workflow_stage.value} stage "
                "has been retried."
            ),
        }
