from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.automation_step import AutomationStep
from app.models.automation_workflow import AutomationWorkflow
from app.models.workflow_types import StepStatus, WorkflowStatus


class ActionPermissionService:
    """
    Central permission/approval layer for workflow actions.

    N1MOX itself does not impose usage quotas.
    Permissions only determine whether an action may execute automatically.
    """

    APPROVAL_REQUIRED_ACTIONS = {
        "publish",
        "schedule_publish",
        "delete",
        "overwrite",
        "external_post",
    }

    SAFE_ACTIONS = {
        "research",
        "strategy",
        "hooks",
        "script",
        "voice",
        "visuals",
        "video",
        "captions",
        "thumbnail",
        "metadata",
        "quality_review",
        "draft",
        "save",
    }

    def __init__(self, db: Session):
        self.db = db

    def evaluate_action(
        self,
        workflow: AutomationWorkflow,
        action: str,
        require_publish_approval: bool = True,
        require_content_approval: bool = False,
    ) -> dict[str, Any]:
        normalized = action.strip().lower()

        if normalized in {"publish", "schedule_publish", "external_post"}:
            if require_publish_approval:
                return self._approval_result(
                    action=normalized,
                    reason="Publishing approval is required by creator preferences.",
                )

        if normalized in {"overwrite", "delete"}:
            return self._approval_result(
                action=normalized,
                reason="This action can modify or remove an existing external result.",
            )

        if require_content_approval and normalized in {
            "video",
            "script",
            "thumbnail",
            "metadata",
            "draft",
        }:
            return self._approval_result(
                action=normalized,
                reason="Content approval is required by creator preferences.",
            )

        if normalized in self.SAFE_ACTIONS:
            return {
                "action": normalized,
                "allowed": True,
                "approval_required": False,
                "status": "approved",
                "reason": "Action is allowed automatically.",
            }

        if normalized in self.APPROVAL_REQUIRED_ACTIONS:
            return self._approval_result(
                action=normalized,
                reason="This action requires explicit creator approval.",
            )

        # Unknown actions default to approval rather than being silently executed.
        return self._approval_result(
            action=normalized,
            reason="Unknown actions require explicit approval.",
        )

    def request_approval(
        self,
        workflow: AutomationWorkflow,
        action: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        workflow.status = WorkflowStatus.PAUSED.value

        self.db.commit()
        self.db.refresh(workflow)

        return {
            "workflow_id": str(workflow.id),
            "action": action,
            "allowed": False,
            "approval_required": True,
            "status": "pending_approval",
            "reason": reason or "Creator approval is required.",
            "requested_at": datetime.utcnow().isoformat(),
        }

    def approve_action(
        self,
        workflow: AutomationWorkflow,
        action: str,
    ) -> dict[str, Any]:
        return {
            "workflow_id": str(workflow.id),
            "action": action,
            "allowed": True,
            "approval_required": False,
            "status": "approved",
            "approved_at": datetime.utcnow().isoformat(),
        }

    def reject_action(
        self,
        workflow: AutomationWorkflow,
        action: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        workflow.status = WorkflowStatus.FAILED.value

        self.db.commit()
        self.db.refresh(workflow)

        return {
            "workflow_id": str(workflow.id),
            "action": action,
            "allowed": False,
            "approval_required": True,
            "status": "rejected",
            "reason": reason or "Creator rejected the action.",
            "rejected_at": datetime.utcnow().isoformat(),
        }

    def workflow_permissions(
        self,
        workflow: AutomationWorkflow,
        require_publish_approval: bool = True,
        require_content_approval: bool = False,
    ) -> dict[str, Any]:
        steps = (
            self.db.query(AutomationStep)
            .filter(AutomationStep.workflow_id == workflow.id)
            .order_by(AutomationStep.order_index.asc())
            .all()
        )

        permissions = []

        for step in steps:
            action = self._action_for_step(step)

            result = self.evaluate_action(
                workflow=workflow,
                action=action,
                require_publish_approval=require_publish_approval,
                require_content_approval=require_content_approval,
            )

            permissions.append(
                {
                    "step_id": str(step.id),
                    "stage": step.stage,
                    **result,
                }
            )

        return {
            "workflow_id": str(workflow.id),
            "workflow_status": workflow.status,
            "permissions": permissions,
            "approval_required": any(
                item["approval_required"] for item in permissions
            ),
        }

    @staticmethod
    def _action_for_step(step: AutomationStep) -> str:
        stage = (step.stage or "").strip().lower()

        mapping = {
            "research": "research",
            "strategy": "strategy",
            "hooks": "hooks",
            "script": "script",
            "voice": "voice",
            "visuals": "visuals",
            "video": "video",
            "captions": "captions",
            "thumbnail": "thumbnail",
            "metadata": "metadata",
            "publish": "publish",
            "scheduling": "schedule_publish",
            "quality": "quality_review",
        }

        return mapping.get(stage, stage or "unknown")

    @staticmethod
    def _approval_result(action: str, reason: str) -> dict[str, Any]:
        return {
            "action": action,
            "allowed": False,
            "approval_required": True,
            "status": "pending_approval",
            "reason": reason,
        }
