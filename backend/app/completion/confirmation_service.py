import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.automation.workflow_types import StepStatus, WorkflowStatus
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow


class CompletionConfirmationService:
    """Confirms whether an automation workflow actually completed."""

    def __init__(self, db: Session):
        self.db = db

    def confirm(
        self,
        workflow_id: str,
        user_id: str,
        force: bool = False,
    ) -> dict[str, Any]:
        workflow = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.user_id == user_id,
            )
            .first()
        )

        if not workflow:
            raise ValueError("Workflow not found.")

        steps = (
            self.db.query(AutomationStep)
            .filter(AutomationStep.workflow_id == workflow.id)
            .order_by(AutomationStep.step_order.asc())
            .all()
        )

        checks = []

        checks.append(
            self._check(
                "workflow_status",
                workflow.status == WorkflowStatus.COMPLETED.value,
                f"Workflow status: {workflow.status}",
            )
        )

        checks.append(
            self._check(
                "workflow_progress",
                float(workflow.progress or 0) >= 100,
                f"Workflow progress: {workflow.progress or 0}%",
            )
        )

        checks.append(
            self._check(
                "steps_present",
                bool(steps),
                f"{len(steps)} workflow steps found.",
            )
        )

        failed_steps = [
            step for step in steps
            if step.status == StepStatus.FAILED.value
        ]

        checks.append(
            self._check(
                "no_failed_steps",
                not failed_steps,
                (
                    "No failed steps."
                    if not failed_steps
                    else f"{len(failed_steps)} failed step(s) found."
                ),
            )
        )

        completed_steps = [
            step for step in steps
            if step.status == StepStatus.COMPLETED.value
        ]

        checks.append(
            self._check(
                "all_steps_completed",
                bool(steps) and len(completed_steps) == len(steps),
                f"{len(completed_steps)}/{len(steps)} steps completed.",
            )
        )

        output_check = self._check_outputs(steps)
        checks.append(output_check)

        passed = sum(1 for check in checks if check["passed"])
        score = passed / len(checks) if checks else 0

        confirmed = all(check["passed"] for check in checks)

        if confirmed:
            status = "confirmed"
            message = "Workflow completion confirmed."
        elif force and workflow.status == WorkflowStatus.COMPLETED.value:
            status = "needs_review"
            message = "Workflow finished but completion checks need review."
        else:
            status = "failed"
            message = "Workflow completion could not be confirmed."

        return {
            "workflow_id": workflow.id,
            "status": status,
            "confirmed": confirmed,
            "score": round(score, 3),
            "checks": checks,
            "message": message,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

    def _check_outputs(
        self,
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        completed = [
            step for step in steps
            if step.status == StepStatus.COMPLETED.value
        ]

        missing = []

        for step in completed:
            output = step.output_data

            if output is None:
                missing.append(step.stage)
                continue

            if isinstance(output, str):
                try:
                    parsed = json.loads(output)
                    if parsed in ({}, [], None):
                        missing.append(step.stage)
                except (json.JSONDecodeError, TypeError):
                    if not output.strip():
                        missing.append(step.stage)

            elif isinstance(output, (dict, list)) and not output:
                missing.append(step.stage)

        return self._check(
            "outputs_available",
            not missing,
            (
                "Required step outputs are available."
                if not missing
                else f"Missing outputs: {', '.join(missing)}"
            ),
        )

    @staticmethod
    def _check(
        name: str,
        passed: bool,
        detail: str,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "passed": passed,
            "detail": detail,
        }