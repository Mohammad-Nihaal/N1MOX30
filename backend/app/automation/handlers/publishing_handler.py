from __future__ import annotations

import json
from typing import Any

from app.services.publishing.publishing_service import (
    PublishingService,
)


class PublishingStageHandler:
    """
    Workflow handler for the final Publishing stage.

    Collects completed workflow outputs and delegates publishing
    validation/execution to PublishingService.
    """

    def __init__(
        self,
        publishing_service: PublishingService | None = None,
    ):
        self.publishing_service = (
            publishing_service
            or PublishingService()
        )

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the Publishing stage.
        """

        workflow = context.get("workflow") or {}

        workflow_id = str(
            workflow.get("id") or ""
        ).strip()

        user_id = str(
            workflow.get("user_id") or ""
        ).strip()

        topic = str(
            workflow.get("topic") or ""
        ).strip()

        platform = str(
            workflow.get("platform") or "youtube"
        ).strip().lower()

        previous_outputs = (
            context.get("previous_outputs") or {}
        )

        metadata_output = self._parse_output(
            previous_outputs.get("metadata"),
            "Metadata",
        )

        quality_check_output = self._parse_output(
            previous_outputs.get("quality_check"),
            "Quality Check",
        )

        scheduling_output = self._parse_output(
            previous_outputs.get("scheduling"),
            "Scheduling",
        )

        video_output = self._parse_output(
            previous_outputs.get("video"),
            "Video",
        )

        thumbnail_output = self._parse_output(
            previous_outputs.get("thumbnail"),
            "Thumbnail",
            required=False,
        )

        if not metadata_output:
            raise ValueError(
                "Publishing stage requires a completed "
                "Metadata stage output."
            )

        if not quality_check_output:
            raise ValueError(
                "Publishing stage requires a completed "
                "Quality Check stage output."
            )

        if not scheduling_output:
            raise ValueError(
                "Publishing stage requires a completed "
                "Scheduling stage output."
            )

        if not video_output:
            raise ValueError(
                "Publishing stage requires a completed "
                "Video stage output."
            )

        result = self.publishing_service.publish_content(
            workflow_id=workflow_id,
            user_id=user_id,
            topic=topic,
            platform=platform,
            metadata=metadata_output,
            quality_check=quality_check_output,
            scheduling=scheduling_output,
            video=video_output,
            thumbnail=thumbnail_output,
        )

        return {
            "stage": "publishing",
            "status": "completed",
            "execution": "publishing_service",
            "publishing": result,
        }

    @staticmethod
    def _parse_output(
        value: Any,
        stage_name: str,
        required: bool = True,
    ) -> dict[str, Any]:
        """
        Safely parse persisted workflow output.
        """

        if value is None:
            if required:
                raise ValueError(
                    f"Publishing stage requires a completed "
                    f"{stage_name} stage output."
                )

            return {}

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Publishing stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Publishing stage received invalid "
                f"{stage_name} output."
            )

        return value


publishing_stage_handler = PublishingStageHandler()