from typing import Any

from sqlalchemy.orm import Session

from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.workflow_types import StepStatus


class AIQualityControlService:
    """
    Central AI quality gate for creator workflows.

    This service evaluates completeness, failures, output availability,
    and basic content-quality signals before a workflow proceeds.
    """

    def __init__(self, db: Session):
        self.db = db

    def review_workflow(
        self,
        workflow: AutomationWorkflow,
    ) -> dict[str, Any]:
        steps = (
            self.db.query(AutomationStep)
            .filter(AutomationStep.workflow_id == workflow.id)
            .order_by(AutomationStep.order_index.asc())
            .all()
        )

        checks: list[dict[str, Any]] = []

        checks.append(self._check_steps_exist(steps))
        checks.append(self._check_no_failed_steps(steps))
        checks.append(self._check_completion(steps))
        checks.append(self._check_outputs(steps))
        checks.append(self._check_output_quality(steps))

        passed = sum(1 for check in checks if check["passed"])
        total = len(checks)
        score = round((passed / total) * 100, 2) if total else 0.0

        failed_checks = [
            check["name"]
            for check in checks
            if not check["passed"]
        ]

        if score >= 90 and not failed_checks:
            status = "approved"
        elif score >= 70:
            status = "needs_review"
        else:
            status = "rejected"

        return {
            "workflow_id": str(workflow.id),
            "status": status,
            "score": score,
            "passed_checks": passed,
            "total_checks": total,
            "failed_checks": failed_checks,
            "checks": checks,
        }

    def review_step(
        self,
        step: AutomationStep,
    ) -> dict[str, Any]:
        checks = [
            self._check_step_status(step),
            self._check_step_output(step),
            self._check_step_error(step),
        ]

        passed = sum(1 for check in checks if check["passed"])
        total = len(checks)
        score = round((passed / total) * 100, 2)

        return {
            "step_id": str(step.id),
            "stage": step.stage,
            "score": score,
            "status": "approved" if score == 100 else "needs_review",
            "checks": checks,
        }

    @staticmethod
    def _check_steps_exist(
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        return {
            "name": "workflow_steps_exist",
            "passed": len(steps) > 0,
            "message": (
                "Workflow contains executable steps."
                if steps
                else "Workflow contains no steps."
            ),
        }

    @staticmethod
    def _check_no_failed_steps(
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        failed = [
            step
            for step in steps
            if step.status == StepStatus.FAILED.value
        ]

        return {
            "name": "no_failed_steps",
            "passed": len(failed) == 0,
            "message": (
                "No workflow steps have failed."
                if not failed
                else f"{len(failed)} workflow step(s) failed."
            ),
        }

    @staticmethod
    def _check_completion(
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        if not steps:
            return {
                "name": "all_steps_completed",
                "passed": False,
                "message": "No steps are available for completion review.",
            }

        incomplete = [
            step
            for step in steps
            if step.status != StepStatus.COMPLETED.value
        ]

        return {
            "name": "all_steps_completed",
            "passed": len(incomplete) == 0,
            "message": (
                "All workflow steps are completed."
                if not incomplete
                else f"{len(incomplete)} workflow step(s) are incomplete."
            ),
        }

    @staticmethod
    def _check_outputs(
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        missing = []

        for step in steps:
            if step.status != StepStatus.COMPLETED.value:
                continue

            output = getattr(step, "output_data", None)

            if output is None:
                missing.append(step.stage)

        return {
            "name": "outputs_available",
            "passed": len(missing) == 0,
            "message": (
                "Completed steps have output data."
                if not missing
                else f"Missing outputs: {', '.join(missing)}."
            ),
        }

    @staticmethod
    def _check_output_quality(
        steps: list[AutomationStep],
    ) -> dict[str, Any]:
        weak_outputs = []

        for step in steps:
            if step.status != StepStatus.COMPLETED.value:
                continue

            output = getattr(step, "output_data", None)

            if output is None:
                continue

            if isinstance(output, dict) and not output:
                weak_outputs.append(step.stage)

            elif isinstance(output, str) and not output.strip():
                weak_outputs.append(step.stage)

        return {
            "name": "output_quality",
            "passed": len(weak_outputs) == 0,
            "message": (
                "Workflow outputs contain usable data."
                if not weak_outputs
                else f"Weak outputs detected: {', '.join(weak_outputs)}."
            ),
        }

    @staticmethod
    def _check_step_status(
        step: AutomationStep,
    ) -> dict[str, Any]:
        passed = step.status == StepStatus.COMPLETED.value

        return {
            "name": "step_completed",
            "passed": passed,
            "message": (
                "Step completed successfully."
                if passed
                else f"Step status is {step.status}."
            ),
        }

    @staticmethod
    def _check_step_output(
        step: AutomationStep,
    ) -> dict[str, Any]:
        output = getattr(step, "output_data", None)

        passed = output is not None and (
            not isinstance(output, str) or bool(output.strip())
        )

        return {
            "name": "step_output_available",
            "passed": passed,
            "message": (
                "Step output is available."
                if passed
                else "Step output is missing or empty."
            ),
        }

    @staticmethod
    def _check_step_error(
        step: AutomationStep,
    ) -> dict[str, Any]:
        error = getattr(step, "error_message", None)

        passed = not error

        return {
            "name": "step_error_free",
            "passed": passed,
            "message": (
                "No step error is recorded."
                if passed
                else f"Step contains an error: {error}"
            ),
        }
