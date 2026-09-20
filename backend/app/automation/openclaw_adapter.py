from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.openclaw_provider import OpenClawProvider


class OpenClawAdapter:
    """Production adapter from N1MOX workflows to the installed OpenClaw CLI."""

    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = settings.openclaw_enabled if enabled is None else enabled
        self.provider = OpenClawProvider()

    def is_available(self) -> bool:
        return bool(self.enabled and self.provider.is_available())

    def execute(
        self,
        *,
        agent: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("OpenClaw integration is disabled.")
        if not self.provider.is_available():
            raise RuntimeError("OpenClaw CLI is not installed or not available on PATH.")
        context = context or {}
        prompt = (
            f"You are the N1MOX30 agent '{agent}'.\n"
            "Execute the following creator-workflow task accurately.\n\n"
            f"TASK:\n{task.strip()}\n\n"
            f"CONTEXT:\n{context}"
        )
        output = self.provider.generate(prompt)
        if not output:
            raise RuntimeError("OpenClaw returned an empty response.")
        return {
            "status": "completed",
            "agent": agent,
            "provider": "openclaw",
            "output": output,
        }


openclaw_adapter = OpenClawAdapter()
