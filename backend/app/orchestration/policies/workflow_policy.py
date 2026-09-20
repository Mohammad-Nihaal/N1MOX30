from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class WorkflowPolicy:
    """
    Central execution policy for N1MOX30 workflows.

    This is deliberately policy-based rather than quota-based.

    N1MOX30 does not impose artificial limits on creator work.
    External provider limits, infrastructure capacity, and
    platform API restrictions are handled by the execution
    layer rather than converted into N1MOX usage quotas.
    """

    require_publish_approval: bool = True
    require_content_approval: bool = False
    auto_quality_review: bool = True
    allow_provider_fallback: bool = True
    allow_retry: bool = True

    @classmethod
    def from_preferences(
        cls,
        preferences: dict[str, Any] | None,
    ) -> "WorkflowPolicy":
        """
        Construct workflow policy from creator preferences.
        """

        preferences = preferences or {}

        return cls(
            require_publish_approval=bool(
                preferences.get(
                    "require_publish_approval",
                    True,
                )
            ),
            require_content_approval=bool(
                preferences.get(
                    "require_content_approval",
                    False,
                )
            ),
            auto_quality_review=bool(
                preferences.get(
                    "auto_quality_review",
                    True,
                )
            ),
            allow_provider_fallback=True,
            allow_retry=True,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "require_publish_approval": (
                self.require_publish_approval
            ),
            "require_content_approval": (
                self.require_content_approval
            ),
            "auto_quality_review": (
                self.auto_quality_review
            ),
            "allow_provider_fallback": (
                self.allow_provider_fallback
            ),
            "allow_retry": self.allow_retry,
        }