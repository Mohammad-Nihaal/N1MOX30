from __future__ import annotations

from typing import Any

from app.services.strategy.strategy_service import StrategyService


class StrategyStageHandler:
    """
    Concrete N1MOX30 workflow handler for the strategy stage.

    The handler consumes the research output produced by the previous
    workflow stage and passes it into StrategyService.
    """

    def __init__(
        self,
        strategy_service: StrategyService | None = None,
    ) -> None:
        self.strategy_service = (
            strategy_service or StrategyService()
        )

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
                "Strategy stage requires a workflow topic."
            )

        previous_outputs = payload.get(
            "previous_outputs",
            {},
        )

        research_output = previous_outputs.get(
            "research",
            {},
        )

        if not research_output:
            raise ValueError(
                "Strategy stage requires completed research output."
            )

        result = self.strategy_service.create_strategy(
            topic=topic,
            platform=platform,
            command=command,
            research=research_output,
        )

        return {
            "stage": "strategy",
            "status": "completed",
            "execution": "strategy_service",
            "strategy": result,
        }


strategy_stage_handler = StrategyStageHandler()