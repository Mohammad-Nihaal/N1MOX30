from __future__ import annotations

import json
from typing import Any

from app.services.scheduling.scheduling_service import (
    SchedulingService,
)


class SchedulingStageHandler:
    """
    Workflow handler for the Scheduling stage.

    Uses completed Strategy, Metadata, and Quality Check outputs
    to generate a publishing schedule recommendation.
    """

    def __init__(
        self,
        scheduling_service: SchedulingService | None = None,
    ):
        self.scheduling_service = (
            scheduling_service
            or SchedulingService()
        )

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute content scheduling.
        """

        workflow = context.get("workflow") or {}

        topic = str(
            workflow.get("topic") or ""
        ).strip()

        platform = str(
            workflow.get("platform") or "youtube"
        ).strip().lower()

        command = str(
            workflow.get("command") or ""
        ).strip()

        previous_outputs = (
            context.get("previous_outputs") or {}
        )

        if not topic:
            raise ValueError(
                "Scheduling stage requires a workflow topic."
            )

        strategy_output = self._parse_output(
            previous_outputs.get("strategy"),
            "Strategy",
        )

        metadata_output = self._parse_output(
            previous_outputs.get("metadata"),
            "Metadata",
        )

        quality_check_output = self._parse_output(
            previous_outputs.get("quality_check"),
            "Quality Check",
        )

        if not metadata_output:
            raise ValueError(
                "Scheduling stage requires a completed Metadata "
                "stage output."
            )

        if not quality_check_output:
            raise ValueError(
                "Scheduling stage requires a completed Quality Check "
                "stage output."
            )

        result = self.scheduling_service.create_schedule(
            topic=topic,
            platform=platform,
            command=command,
            strategy=strategy_output,
            metadata=metadata_output,
            quality_check=quality_check_output,
        )

        return {
            "stage": "scheduling",
            "status": (
                "completed"
                if result.get("status") == "ready"
                else "blocked"
            ),
            "execution": "scheduling_service",
            "scheduling": result,
        }

    @staticmethod
    def _parse_output(
        value: Any,
        stage_name: str,
    ) -> dict[str, Any]:
        """
        Safely parse persisted workflow output.
        """

        if value is None:
            return {}

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Scheduling stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Scheduling stage received invalid "
                f"{stage_name} output."
            )

        return value


scheduling_stage_handler = SchedulingStageHandler()