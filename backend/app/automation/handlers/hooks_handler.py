from __future__ import annotations

from typing import Any

from app.services.hooks.hook_service import HookService


class HooksStageHandler:
    """
    Concrete N1MOX30 workflow handler for the hooks stage.

    The handler consumes the outputs of both Research and Strategy,
    then delegates hook generation, classification, scoring, and
    ranking to HookService.
    """

    def __init__(
        self,
        hook_service: HookService | None = None,
    ) -> None:
        self.hook_service = hook_service or HookService()

    def __call__(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        workflow = payload.get("workflow", {})

        topic = str(
            workflow.get("topic", "")
        ).strip()

        platform = str(
            workflow.get("platform", "youtube")
        ).strip().lower()

        command = str(
            workflow.get("command", "")
        ).strip()

        if not topic:
            raise ValueError(
                "Hooks stage requires a workflow topic."
            )

        previous_outputs = payload.get(
            "previous_outputs",
            {},
        )

        research_output = previous_outputs.get(
            "research",
            {},
        )

        strategy_output = previous_outputs.get(
            "strategy",
            {},
        )

        if not research_output:
            raise ValueError(
                "Hooks stage requires completed research output."
            )

        if not strategy_output:
            raise ValueError(
                "Hooks stage requires completed strategy output."
            )

        result = self.hook_service.generate_hooks(
            topic=topic,
            platform=platform,
            command=command,
            research=research_output,
            strategy=strategy_output,
        )

        return {
            "stage": "hooks",
            "status": "completed",
            "execution": "hook_service",
            "hooks": result,
        }


hooks_stage_handler = HooksStageHandler()