from __future__ import annotations

import json
from typing import Any

from app.services.metadata.metadata_service import MetadataService


class MetadataStageHandler:
    """
    Workflow handler for the Metadata stage.

    Consumes completed outputs from previous workflow stages and
    delegates SEO and metadata generation to MetadataService.
    """

    def __init__(
        self,
        metadata_service: MetadataService | None = None,
    ):
        self.metadata_service = (
            metadata_service
            or MetadataService()
        )

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute metadata generation using workflow context.
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

        research_output = self._parse_output(
            previous_outputs.get("research"),
            "Research",
        )

        strategy_output = self._parse_output(
            previous_outputs.get("strategy"),
            "Strategy",
        )

        hooks_output = self._parse_output(
            previous_outputs.get("hooks"),
            "Hooks",
        )

        script_output = self._parse_output(
            previous_outputs.get("script"),
            "Script",
        )

        voice_output = self._parse_output(
            previous_outputs.get("voice"),
            "Voice",
        )

        visuals_output = self._parse_output(
            previous_outputs.get("visuals"),
            "Visuals",
        )

        video_output = self._parse_output(
            previous_outputs.get("video"),
            "Video",
        )

        captions_output = self._parse_output(
            previous_outputs.get("captions"),
            "Captions",
        )

        thumbnail_output = self._parse_output(
            previous_outputs.get("thumbnail"),
            "Thumbnail",
        )

        if not topic:
            raise ValueError(
                "Metadata stage requires a workflow topic."
            )

        if not script_output:
            raise ValueError(
                "Metadata stage requires a completed Script stage output."
            )

        if not thumbnail_output:
            raise ValueError(
                "Metadata stage requires a completed Thumbnail stage output."
            )

        result = self.metadata_service.generate_metadata(
            topic=topic,
            platform=platform,
            command=command,
            research=research_output,
            strategy=strategy_output,
            hooks=hooks_output,
            script=script_output,
            thumbnail=thumbnail_output,
            captions=captions_output,
        )

        return {
            "stage": "metadata",
            "status": "completed",
            "execution": "metadata_service",
            "metadata": result,
        }

    @staticmethod
    def _parse_output(
        value: Any,
        stage_name: str,
    ) -> dict[str, Any]:
        """
        Parse persisted workflow output safely.
        """

        if value is None:
            return {}

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Metadata stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Metadata stage received invalid "
                f"{stage_name} output."
            )

        return value


metadata_stage_handler = MetadataStageHandler()