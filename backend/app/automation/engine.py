import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.automation.registry import stage_registry
from app.automation.workflow_types import (
    WORKFLOW_STAGES,
    StepStatus,
    WorkflowStage,
    WorkflowStatus,
)
from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow


StageHandler = Callable[
    [dict[str, Any]],
    dict[str, Any],
]


class WorkflowEngine:
    """
    N1MOX30 workflow orchestration engine.

    The engine owns:
    - workflow state
    - execution order
    - persistent step state
    - stage input/output contracts
    - failure handling
    - retry state
    - optional project ownership

    Individual stage implementations remain behind handlers.

    IMPORTANT:
    The SQLAlchemy database session is injected into the
    handler context as `_db`.

    It is intentionally NOT persisted inside step.input_data.
    """

    def __init__(
        self,
        db: Session,
        stage_handlers: dict[
            WorkflowStage,
            StageHandler,
        ]
        | None = None,
    ) -> None:
        self.db = db
        self.stage_handlers = stage_handlers or {}

    # ------------------------------------------------------------------
    # Workflow creation
    # ------------------------------------------------------------------

    def create_workflow(
        self,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
        project_id: str | None = None,
    ) -> AutomationWorkflow:
        """
        Create a workflow and all persistent workflow stages.
        """

        workflow = AutomationWorkflow(
            user_id=user_id,
            project_id=project_id,
            command=command,
            platform=platform,
            topic=topic,
            status=WorkflowStatus.PENDING.value,
            current_stage=None,
            progress=0,
        )

        self.db.add(workflow)
        self.db.flush()

        for index, stage in enumerate(
            WORKFLOW_STAGES,
            start=1,
        ):
            step = AutomationStep(
                workflow_id=workflow.id,
                stage=stage.value,
                step_order=index,
                status=StepStatus.PENDING.value,
                input_data=None,
                output_data=None,
                error_message=None,
                attempts=0,
                started_at=None,
                completed_at=None,
            )

            self.db.add(step)

        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    # ------------------------------------------------------------------
    # Workflow retrieval
    # ------------------------------------------------------------------

    def get_workflow(
        self,
        workflow_id: str,
        user_id: str,
    ) -> AutomationWorkflow | None:
        """
        Return a workflow belonging to the specified user.
        """

        return (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.user_id == user_id,
            )
            .first()
        )

    def get_steps(
        self,
        workflow_id: str,
    ) -> list[AutomationStep]:
        """
        Return workflow steps in execution order.
        """

        return (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id == workflow_id,
            )
            .order_by(
                AutomationStep.step_order.asc(),
            )
            .all()
        )

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def register_handler(
        self,
        stage: WorkflowStage,
        handler: StageHandler,
    ) -> None:
        """
        Register a concrete implementation for a workflow stage.
        """

        if not stage_registry.has(stage):
            raise ValueError(
                f"Cannot register handler for unknown stage: "
                f"{stage.value}"
            )

        if not callable(handler):
            raise TypeError(
                f"Handler for stage '{stage.value}' must be callable."
            )

        self.stage_handlers[stage] = handler

    def register_handlers(
        self,
        handlers: dict[
            WorkflowStage,
            StageHandler,
        ],
    ) -> None:
        """
        Register multiple stage handlers at once.
        """

        for stage, stage_handler in handlers.items():
            self.register_handler(
                stage=stage,
                handler=stage_handler,
            )

    # ------------------------------------------------------------------
    # Workflow execution
    # ------------------------------------------------------------------

    def run_workflow(
        self,
        workflow_id: str,
    ) -> AutomationWorkflow:
        """
        Execute a workflow from its current state.
        """

        workflow = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
            )
            .first()
        )

        if workflow is None:
            raise ValueError(
                f"Workflow '{workflow_id}' was not found."
            )

        if workflow.status == WorkflowStatus.COMPLETED.value:
            return workflow

        if workflow.status in {
            WorkflowStatus.PAUSED.value,
            WorkflowStatus.CANCELLED.value,
        }:
            return workflow

        workflow.status = WorkflowStatus.RUNNING.value
        workflow.error_message = None
        workflow.updated_at = datetime.utcnow()

        self.db.commit()

        steps = self.get_steps(workflow.id)

        if not steps:
            self._fail_workflow(
                workflow=workflow,
                step=None,
                error=ValueError(
                    "Workflow contains no execution steps."
                ),
            )

            self.db.commit()

            return workflow

        total_steps = len(steps)

        for step in steps:
            if workflow.status in {
                WorkflowStatus.PAUSED.value,
                WorkflowStatus.CANCELLED.value,
            }:
                self.db.refresh(workflow)
                return workflow

            if step.status == StepStatus.COMPLETED.value:
                continue

            if step.status == StepStatus.SKIPPED.value:
                continue

            try:
                stage = WorkflowStage(step.stage)

                workflow.current_stage = stage.value

                workflow.progress = int(
                    (
                        (step.step_order - 1)
                        / total_steps
                    )
                    * 100
                )

                workflow.updated_at = datetime.utcnow()

                self.db.commit()

                self._execute_step(
                    workflow=workflow,
                    step=step,
                    stage=stage,
                    total_steps=total_steps,
                )

            except Exception as error:
                self._fail_workflow(
                    workflow=workflow,
                    step=step,
                    error=error,
                )

                self.db.commit()

                return workflow

        workflow.status = WorkflowStatus.COMPLETED.value
        workflow.current_stage = None
        workflow.progress = 100
        workflow.completed_at = datetime.utcnow()
        workflow.error_message = None
        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------

    def _execute_step(
        self,
        workflow: AutomationWorkflow,
        step: AutomationStep,
        stage: WorkflowStage,
        total_steps: int,
    ) -> None:
        """
        Execute one workflow stage.

        The normal persisted input payload contains only serializable
        workflow data.

        The live SQLAlchemy Session is attached separately to the
        handler context under `_db`.
        """

        step.status = StepStatus.RUNNING.value
        step.attempts += 1
        step.started_at = datetime.utcnow()
        step.completed_at = None
        step.error_message = None
        step.updated_at = datetime.utcnow()

        input_payload = self._build_step_input(
            workflow=workflow,
            step=step,
            stage=stage,
        )

        # Persist only JSON-safe input.
        self._persist_step_input(
            step=step,
            input_payload=input_payload,
        )

        self.db.commit()

        handler = self.stage_handlers.get(stage)

        if handler is None:
            output = {
                "stage": stage.value,
                "status": "not_implemented",
                "execution": "skipped",
                "message": (
                    "Stage infrastructure is ready, but a concrete "
                    "execution handler has not yet been connected."
                ),
            }

            step.status = StepStatus.SKIPPED.value

            step.output_data = json.dumps(
                output,
                default=str,
            )

            step.completed_at = datetime.utcnow()
            step.updated_at = datetime.utcnow()

            self.db.commit()

            return

        # --------------------------------------------------------------
        # IMPORTANT FIX
        # --------------------------------------------------------------
        # Stage handlers such as Captions and Thumbnail need the live
        # SQLAlchemy Session.
        #
        # Do NOT put `_db` into input_payload because input_payload is
        # persisted as JSON.
        #
        # Instead create a separate runtime handler context.
        # --------------------------------------------------------------

        handler_context = dict(input_payload)
        handler_context["_db"] = self.db

        output = handler(handler_context)

        if not isinstance(output, dict):
            raise ValueError(
                f"Handler for stage '{stage.value}' "
                "must return a dictionary."
            )

        output = self._normalize_handler_output(
            stage=stage,
            output=output,
        )

        step.output_data = json.dumps(
            output,
            default=str,
        )

        step.status = StepStatus.COMPLETED.value
        step.completed_at = datetime.utcnow()
        step.error_message = None
        step.updated_at = datetime.utcnow()

        workflow.progress = int(
            (step.step_order / total_steps) * 100
        )

        workflow.current_stage = stage.value
        workflow.updated_at = datetime.utcnow()

        self.db.commit()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_step_input(
        self,
        step: AutomationStep,
        input_payload: dict[str, Any],
    ) -> None:
        """
        Persist only serializable workflow input.

        Runtime-only objects such as SQLAlchemy Session are never stored.
        """

        step.input_data = json.dumps(
            input_payload,
            default=str,
        )

    # ------------------------------------------------------------------
    # Handler output normalization
    # ------------------------------------------------------------------

    def _normalize_handler_output(
        self,
        stage: WorkflowStage,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a handler response without destroying
        stage-specific output.
        """

        normalized = dict(output)

        normalized.setdefault(
            "stage",
            stage.value,
        )

        normalized.setdefault(
            "status",
            "completed",
        )

        normalized.setdefault(
            "execution",
            "handler",
        )

        return normalized

    # ------------------------------------------------------------------
    # Input construction
    # ------------------------------------------------------------------

    def _build_step_input(
        self,
        workflow: AutomationWorkflow,
        step: AutomationStep,
        stage: WorkflowStage,
    ) -> dict[str, Any]:
        """
        Build the standard payload passed to a stage handler.

        The returned object MUST remain JSON serializable.
        """

        previous_outputs: dict[str, Any] = {}

        previous_steps = (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id == workflow.id,
                AutomationStep.step_order < step.step_order,
            )
            .order_by(
                AutomationStep.step_order.asc(),
            )
            .all()
        )

        for previous_step in previous_steps:
            if not previous_step.output_data:
                continue

            try:
                previous_outputs[
                    previous_step.stage
                ] = json.loads(
                    previous_step.output_data
                )

            except json.JSONDecodeError:
                previous_outputs[
                    previous_step.stage
                ] = previous_step.output_data

        return {
            "workflow": {
                "id": workflow.id,
                "user_id": workflow.user_id,
                "project_id": workflow.project_id,
                "command": workflow.command,
                "platform": workflow.platform,
                "topic": workflow.topic,
                "status": workflow.status,
            },
            "stage": {
                "name": stage.value,
                "order": step.step_order,
                "status": step.status,
                "attempt": step.attempts,
            },
            "previous_outputs": previous_outputs,
        }

    # ------------------------------------------------------------------
    # Failure handling
    # ------------------------------------------------------------------

    def _fail_workflow(
        self,
        workflow: AutomationWorkflow,
        step: AutomationStep | None,
        error: Exception,
    ) -> None:
        """
        Persist a workflow and step failure.
        """

        message = str(error).strip()

        if not message:
            message = "Unknown workflow execution error."

        if step is not None:
            step.status = StepStatus.FAILED.value
            step.error_message = message
            step.completed_at = None
            step.updated_at = datetime.utcnow()

        workflow.status = WorkflowStatus.FAILED.value
        workflow.error_message = message
        workflow.updated_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    def retry_step(
        self,
        workflow_id: str,
        stage: WorkflowStage,
    ) -> AutomationWorkflow:
        """
        Reset one workflow stage and immediately resume execution
        from that stage.

        Previously completed stages remain completed.
        """

        workflow = (
            self.db.query(AutomationWorkflow)
            .filter(
                AutomationWorkflow.id == workflow_id,
            )
            .first()
        )

        if workflow is None:
            raise ValueError(
                f"Workflow '{workflow_id}' was not found."
            )

        step = (
            self.db.query(AutomationStep)
            .filter(
                AutomationStep.workflow_id == workflow_id,
                AutomationStep.stage == stage.value,
            )
            .first()
        )

        if step is None:
            raise ValueError(
                f"Stage '{stage.value}' was not found "
                f"in workflow '{workflow_id}'."
            )

        # Reset only the requested stage.
        step.status = StepStatus.PENDING.value
        step.error_message = None
        step.completed_at = None
        step.updated_at = datetime.utcnow()

        workflow.status = WorkflowStatus.PENDING.value
        workflow.error_message = None
        workflow.current_stage = stage.value
        workflow.completed_at = None
        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        # run_workflow() skips all previously completed stages
        # and resumes from the requested pending stage.
        self.run_workflow(workflow_id)

        self.db.refresh(workflow)

        return workflow