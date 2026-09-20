from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.content import Content
from app.models.automation_workflow import AutomationWorkflow


class ContentVersionService:
    """
    Version history for creator content.

    Every saved version is immutable. A new version is created rather
    than overwriting historical content.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_version(
        self,
        content: Content,
        changes: dict[str, Any],
        created_by: str = "system",
        reason: str | None = None,
    ) -> dict[str, Any]:
        current = self._snapshot_content(content)

        version_number = self._next_version(content)

        version = {
            "version": version_number,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": created_by,
            "reason": reason,
            "changes": changes,
            "snapshot": current,
        }

        history = getattr(content, "version_history", None) or []
        history.append(version)

        content.version_history = history
        content.current_version = version_number
        content.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(content)

        return version

    def get_versions(self, content: Content) -> list[dict[str, Any]]:
        history = getattr(content, "version_history", None) or []
        return list(reversed(history))

    def get_version(
        self,
        content: Content,
        version_number: int,
    ) -> dict[str, Any] | None:
        history = getattr(content, "version_history", None) or []

        for version in history:
            if version.get("version") == version_number:
                return version

        return None

    def restore_version(
        self,
        content: Content,
        version_number: int,
        created_by: str = "system",
    ) -> dict[str, Any]:
        target = self.get_version(content, version_number)

        if not target:
            raise ValueError("Content version not found.")

        snapshot = target.get("snapshot", {})

        changes = {
            key: value
            for key, value in snapshot.items()
            if hasattr(content, key)
        }

        for key, value in changes.items():
            setattr(content, key, value)

        return self.create_version(
            content=content,
            changes={
                "restored_from_version": version_number,
                "restored_fields": list(changes.keys()),
            },
            created_by=created_by,
            reason=f"Restored version {version_number}",
        )

    def compare_versions(
        self,
        content: Content,
        first_version: int,
        second_version: int,
    ) -> dict[str, Any]:
        first = self.get_version(content, first_version)
        second = self.get_version(content, second_version)

        if not first or not second:
            raise ValueError("One or both content versions were not found.")

        first_snapshot = first.get("snapshot", {})
        second_snapshot = second.get("snapshot", {})

        fields = set(first_snapshot) | set(second_snapshot)

        differences = {}

        for field in fields:
            old_value = first_snapshot.get(field)
            new_value = second_snapshot.get(field)

            if old_value != new_value:
                differences[field] = {
                    "version_1": old_value,
                    "version_2": new_value,
                }

        return {
            "content_id": str(content.id),
            "first_version": first_version,
            "second_version": second_version,
            "differences": differences,
        }

    def snapshot_workflow(
        self,
        workflow: AutomationWorkflow,
        created_by: str = "system",
        reason: str | None = None,
    ) -> dict[str, Any]:
        return {
            "workflow_id": str(workflow.id),
            "status": workflow.status,
            "command": getattr(workflow, "command", None),
            "platform": getattr(workflow, "platform", None),
            "topic": getattr(workflow, "topic", None),
            "created_at": (
                workflow.created_at.isoformat()
                if getattr(workflow, "created_at", None)
                else None
            ),
            "created_by": created_by,
            "reason": reason,
        }

    @staticmethod
    def _snapshot_content(content: Content) -> dict[str, Any]:
        fields = [
            "title",
            "idea",
            "script",
            "caption",
            "hashtags",
            "status",
            "platform",
        ]

        return {
            field: getattr(content, field, None)
            for field in fields
        }

    @staticmethod
    def _next_version(content: Content) -> int:
        current = getattr(content, "current_version", None)

        if current is not None:
            return int(current) + 1

        history = getattr(content, "version_history", None) or []

        if not history:
            return 1

        return max(
            int(item.get("version", 0))
            for item in history
        ) + 1
