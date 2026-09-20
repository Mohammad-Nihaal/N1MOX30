from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.creator_memory_service import CreatorMemoryService
from app.services.creator_preferences.preference_service import (
    CreatorPreferenceService,
)
from app.services.creator_profile_service import (
    get_creator_profile,
)


class WorkflowContextBuilder:
    """
    Build creator-aware context for central workflow orchestration.

    Uses the project's existing service contracts directly:
    - creator profile: module-level service functions
    - creator preferences: service instance whose methods accept db
    - creator memory: static service methods whose methods accept db

    No creator usage quotas are imposed here.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.memory_service = CreatorMemoryService()
        self.preference_service = CreatorPreferenceService()

    def build(
        self,
        *,
        user_id: str,
        command: str,
        platform: str,
        topic: str,
    ) -> dict[str, Any]:
        return {
            "creator": {
                "user_id": user_id,
                "profile": self._get_profile(user_id=user_id),
                "preferences": self._get_preferences(user_id=user_id),
                "memory": self._get_memory(user_id=user_id),
            },
            "request": {
                "command": command,
                "platform": platform,
                "topic": topic,
            },
        }

    def _get_profile(self, *, user_id: str) -> dict[str, Any]:
        try:
            result = get_creator_profile(
                db=self.db,
                user_id=user_id,
            )
            return self._to_dict(result)
        except Exception:
            return {}

    def _get_preferences(self, *, user_id: str) -> dict[str, Any]:
        try:
            return self.preference_service.get_context(
                db=self.db,
                user_id=user_id,
            )
        except Exception:
            return {}

    def _get_memory(self, *, user_id: str) -> list[dict[str, Any]]:
        try:
            return self.memory_service.get_memory_context(
                db=self.db,
                user_id=user_id,
            )
        except Exception:
            return []

    @staticmethod
    def _to_dict(value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if hasattr(value, "model_dump"):
            try:
                result = value.model_dump()
                if isinstance(result, dict):
                    return result
            except Exception:
                pass

        if hasattr(value, "__dict__"):
            return {
                key: item
                for key, item in value.__dict__.items()
                if not key.startswith("_")
            }

        return {}
