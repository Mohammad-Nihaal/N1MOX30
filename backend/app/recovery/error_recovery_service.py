from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.automation.engine import WorkflowEngine
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.project_activity import ProjectActivity
from app.models.workflow_types import StepStatus, WorkflowStatus


class ErrorRecoveryService:
    """
    Central error recovery and activity logging layer.

    N1MOX30 should recover automatically whenever the existing workflow
    engine supports a safe retry. All important recovery events are
    recorded so the orchestrator can explain what happened later.
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine(db)

    # -------------------------------------------------
    # ACTIVITY LOGGING
    # -------------------------------------------------

    def log_activity(
        self,
        workflow: AutomationWorkflow,
        activity_type: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        project_id = getattr(workflow, "project_id", None)

        if not project_id:
            return {
                "logged": False,
                "reason": "Workflow is not attached to a project.",
            }

        activity = ProjectActivity(
            project_id=project_id,
            user_id=workflow.user_id,
            activity_type=activity_type,
            title=title,
            description=description,
            workflow_id=workflow.id,
            created_at=datetime.utcnow(),
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        return {
            "logged": True,
            "activity_id": str(activity.id),
            "activity_type": activity_type,
            "title": title,
        }

    # -------------------------------------------------
    # ERROR ANALYSIS
    # -------------------------------------------------

    def inspect_workflow_errors(
        self,
        workflow: AutomationWorkflow,
    ) -> dict[str, Any]:
        steps = (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id == workflow.id
            )
            .order_by(
                AutomationStep.order_index.asc()
            )
            .all()
        )

        failures = []

        for step in steps:
            if step.status != StepStatus.FAILED.value:
                continue

            failures.append(
                {
                    "step_id": str(step.id),
                    "stage": step.stage,
                    "error": getattr(
                        step,
                        "error_message",
                        None,
                    ),
                    "retry_count": getattr(
                        step,
                        "retry_count",
                        0,
                    ),
                }
            )

        return {
            "workflow_id": str(workflow.id),
            "has_errors": bool(failures),
            "failure_count": len(failures),
            "failures": failures,
        }

    # -------------------------------------------------
    # RECOVERY
    # -------------------------------------------------

    def recover_workflow(
        self,
        workflow: AutomationWorkflow,
    ) -> dict[str, Any]:
        error_report = self.inspect_workflow_errors(
            workflow
        )

        if not error_report["has_errors"]:
            return {
                "workflow_id": str(workflow.id),
                "status": "no_recovery_needed",
                "message": "No failed workflow steps were found.",
            }

        self.log_activity(
            workflow=workflow,
            activity_type="error_detected",
            title="Workflow error detected",
            description=(
                f"{error_report['failure_count']} "
                "workflow step(s) failed."
            ),
        )

        recovery_results = []

        for failure in error_report["failures"]:
            stage = failure["stage"]

            try:
                self.log_activity(
                    workflow=workflow,
                    activity_type="recovery_started",
                    title=f"Recovering {stage}",
                    description=(
                        "N1MOX30 is retrying the failed "
                        "workflow stage."
                    ),
                )

                workflow.status = WorkflowStatus.RUNNING.value
                self.db.commit()

                result = self.engine.retry_step(
                    workflow_id=workflow.id,
                    stage=stage,
                    user_id=workflow.user_id,
                )

                self.db.refresh(workflow)

                recovery_results.append(
                    {
                        "stage": stage,
                        "status": "retry_started",
                        "workflow_status": workflow.status,
                        "result": self._safe_result(result),
                    }
                )

                self.log_activity(
                    workflow=workflow,
                    activity_type="recovery_completed",
                    title=f"Recovery attempted for {stage}",
                    description=(
                        "The failed stage was sent through "
                        "the workflow retry mechanism."
                    ),
                )

            except Exception as exc:
                self.db.rollback()

                recovery_results.append(
                    {
                        "stage": stage,
                        "status": "recovery_failed",
                        "error": str(exc),
                    }
                )

                self.log_activity(
                    workflow=workflow,
                    activity_type="recovery_failed",
                    title=f"Recovery failed for {stage}",
                    description=str(exc),
                )

        self.db.refresh(workflow)

        return {
            "workflow_id": str(workflow.id),
            "status": "recovery_processed",
            "workflow_status": workflow.status,
            "recoveries": recovery_results,
        }

    # -------------------------------------------------
    # SINGLE STEP RECOVERY
    # -------------------------------------------------

    def recover_step(
        self,
        workflow: AutomationWorkflow,
        step: AutomationStep,
    ) -> dict[str, Any]:
        if step.workflow_id != workflow.id:
            raise ValueError(
                "Workflow step does not belong to this workflow."
            )

        if step.status != StepStatus.FAILED.value:
            return {
                "step_id": str(step.id),
                "stage": step.stage,
                "status": "no_recovery_needed",
                "message": "Step has not failed.",
            }

        self.log_activity(
            workflow=workflow,
            activity_type="recovery_started",
            title=f"Recovering {step.stage}",
            description=(
                f"Retrying failed step {step.stage}."
            ),
        )

        try:
            workflow.status = WorkflowStatus.RUNNING.value
            self.db.commit()

            result = self.engine.retry_step(
                workflow_id=workflow.id,
                stage=step.stage,
                user_id=workflow.user_id,
            )

            self.db.refresh(workflow)
            self.db.refresh(step)

            self.log_activity(
                workflow=workflow,
                activity_type="recovery_completed",
                title=f"Recovery completed for {step.stage}",
                description=(
                    "The workflow retry mechanism completed "
                    "its recovery attempt."
                ),
            )

            return {
                "step_id": str(step.id),
                "stage": step.stage,
                "status": "recovered",
                "workflow_status": workflow.status,
                "result": self._safe_result(result),
            }

        except Exception as exc:
            self.db.rollback()

            self.log_activity(
                workflow=workflow,
                activity_type="recovery_failed",
                title=f"Recovery failed for {step.stage}",
                description=str(exc),
            )

            return {
                "step_id": str(step.id),
                "stage": step.stage,
                "status": "recovery_failed",
                "error": str(exc),
            }

    # -------------------------------------------------
    # WORKFLOW STATUS
    # -------------------------------------------------

    def get_recovery_status(
        self,
        workflow: AutomationWorkflow,
    ) -> dict[str, Any]:
        error_report = self.inspect_workflow_errors(
            workflow
        )

        steps = (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id == workflow.id
            )
            .all()
        )

        completed = sum(
            1
            for step in steps
            if step.status == StepStatus.COMPLETED.value
        )

        return {
            "workflow_id": str(workflow.id),
            "workflow_status": workflow.status,
            "total_steps": len(steps),
            "completed_steps": completed,
            "failed_steps": error_report["failure_count"],
            "recovery_available": error_report["has_errors"],
            "failures": error_report["failures"],
        }

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------

    @staticmethod
    def _safe_result(
        result: Any,
    ) -> Any:
        if result is None:
            return None

        if isinstance(result, dict):
            return result

        if isinstance(result, (str, int, float, bool)):
            return result

        return str(result)
