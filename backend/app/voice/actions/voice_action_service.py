from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.automation_workflow import AutomationWorkflow
from app.services.automation_service import AutomationService
from app.voice.control.voice_workflow_control_service import (
    VoiceWorkflowControlService,
)


class VoiceActionService:
    """
    Maps understood N1MOX voice intents to real actions.
    """

    def __init__(self, db: Session):
        self.db = db
        self.control = VoiceWorkflowControlService(db)

    def execute(
        self,
        *,
        user_id: str,
        intent: dict[str, Any],
    ) -> dict[str, Any]:

        name = intent.get(
            "intent",
            "general_query",
        )

        entities = intent.get(
            "entities",
            {},
        )

        # ----------------------------------------------------
        # CREATE CONTENT
        # ----------------------------------------------------

        if name == "create_content":

            topic = str(
                entities.get("topic") or ""
            ).strip()

            platform = str(
                entities.get("platform")
                or "youtube"
            ).strip().lower()

            if not topic:
                return {
                    "executed": False,
                    "message": (
                        "I need the video topic "
                        "before I can create the workflow."
                    ),
                }

            command = (
                f"Create a {platform} video "
                f"about {topic}"
            )

            workflow = AutomationService(self.db).get_engine().create_workflow(
                user_id=user_id,
                command=command,
                platform=platform,
                topic=topic,
            )

            return {
                "executed": True,
                "action": "create_content_workflow",
                "workflow_id": workflow.id,
                "status": str(workflow.status),
                "message": (
                    "The content workflow has been created."
                ),
            }

        # ----------------------------------------------------
        # WORKFLOW STATUS
        # ----------------------------------------------------

        if name == "workflow_status":

            workflows = (
                self.db.query(
                    AutomationWorkflow
                )
                .filter(
                    AutomationWorkflow.user_id
                    == user_id
                )
                .order_by(
                    AutomationWorkflow.created_at.desc()
                )
                .limit(10)
                .all()
            )

            active = []

            for workflow in workflows:

                status = str(
                    workflow.status
                ).split(".")[-1].lower()

                if status in {
                    "pending",
                    "running",
                    "paused",
                }:
                    active.append(workflow)

            return {
                "executed": True,
                "action": "get_workflow_status",
                "count": len(active),
                "message": (
                    f"You have {len(active)} "
                    f"active workflow"
                    f"{'s' if len(active) != 1 else ''}."
                ),
            }

        # ----------------------------------------------------
        # COMPLETED WORK
        # ----------------------------------------------------

        if name == "completed_work":

            workflows = (
                self.db.query(
                    AutomationWorkflow
                )
                .filter(
                    AutomationWorkflow.user_id
                    == user_id
                )
                .order_by(
                    AutomationWorkflow.updated_at.desc()
                )
                .limit(10)
                .all()
            )

            completed = [
                workflow
                for workflow in workflows
                if str(
                    workflow.status
                ).split(".")[-1].lower()
                == "completed"
            ]

            return {
                "executed": True,
                "action": "get_completed_work",
                "count": len(completed),
                "message": (
                    f"N1MOX has {len(completed)} "
                    f"completed workflow"
                    f"{'s' if len(completed) != 1 else ''}."
                ),
            }

        # ----------------------------------------------------
        # ERRORS
        # ----------------------------------------------------

        if name == "workflow_errors":

            workflows = (
                self.db.query(
                    AutomationWorkflow
                )
                .filter(
                    AutomationWorkflow.user_id
                    == user_id
                )
                .order_by(
                    AutomationWorkflow.updated_at.desc()
                )
                .limit(10)
                .all()
            )

            failed = [
                workflow
                for workflow in workflows
                if str(
                    workflow.status
                ).split(".")[-1].lower()
                == "failed"
            ]

            return {
                "executed": True,
                "action": "get_workflow_errors",
                "count": len(failed),
                "message": (
                    f"I found {len(failed)} failed "
                    f"workflow"
                    f"{'s' if len(failed) != 1 else ''}."
                ),
            }

        # ----------------------------------------------------
        # SCHEDULED CONTENT
        # ----------------------------------------------------

        if name == "scheduled_content":

            return {
                "executed": True,
                "action": "get_scheduled_content",
                "message": (
                    "Your scheduling system is connected. "
                    "The publishing queue is available "
                    "through the scheduling system."
                ),
            }

        # ----------------------------------------------------
        # STEP 34 — PAUSE
        # ----------------------------------------------------

        if name == "pause_workflow":

            workflow_id = entities.get(
                "workflow_id"
            )

            if not workflow_id:
                return {
                    "executed": False,
                    "action": "pause_workflow",
                    "message": (
                        "Tell me the workflow ID "
                        "you want me to pause."
                    ),
                }

            return self.control.pause(
                workflow_id=str(workflow_id),
                user_id=user_id,
            )

        # ----------------------------------------------------
        # STEP 34 — RESUME
        # ----------------------------------------------------

        if name == "resume_workflow":

            workflow_id = entities.get(
                "workflow_id"
            )

            if not workflow_id:
                return {
                    "executed": False,
                    "action": "resume_workflow",
                    "message": (
                        "Tell me the workflow ID "
                        "you want me to resume."
                    ),
                }

            return self.control.resume(
                workflow_id=str(workflow_id),
                user_id=user_id,
            )

        # ----------------------------------------------------
        # STEP 34 — CANCEL
        # ----------------------------------------------------

        if name == "cancel_workflow":

            workflow_id = entities.get(
                "workflow_id"
            )

            if not workflow_id:
                return {
                    "executed": False,
                    "action": "cancel_workflow",
                    "message": (
                        "Tell me the workflow ID "
                        "you want me to cancel."
                    ),
                }

            return self.control.cancel(
                workflow_id=str(workflow_id),
                user_id=user_id,
            )

        # ----------------------------------------------------
        # STEP 34 — RETRY
        # ----------------------------------------------------

        if name == "retry_workflow":

            workflow_id = entities.get(
                "workflow_id"
            )

            if not workflow_id:
                return {
                    "executed": False,
                    "action": "retry_workflow",
                    "message": (
                        "Tell me the workflow ID "
                        "you want me to retry."
                    ),
                }

            return self.control.retry(
                workflow_id=str(workflow_id),
                user_id=user_id,
            )

        return {
            "executed": False,
            "action": None,
            "message": (
                "No executable workflow action "
                "was requested."
            ),
        }
