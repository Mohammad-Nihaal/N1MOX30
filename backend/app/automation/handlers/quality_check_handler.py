from __future__ import annotations

import json
from typing import Any

from app.services.quality.quality_service import QualityService


class QualityCheckStageHandler:
    """
    Workflow handler for the Quality Check stage.

    Collects all completed workflow outputs and sends them to
    QualityService for validation and readiness evaluation.
    """

    def __init__(
        self,
        quality_service: QualityService | None = None,
    ):
        self.quality_service = (
            quality_service
            or QualityService()
        )

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the workflow quality check.
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
                "Quality Check stage requires a workflow topic."
            )

        outputs = {
            "research": self._parse_output(
                previous_outputs.get("research"),
                "Research",
            ),
            "strategy": self._parse_output(
                previous_outputs.get("strategy"),
                "Strategy",
            ),
            "hooks": self._parse_output(
                previous_outputs.get("hooks"),
                "Hooks",
            ),
            "script": self._parse_output(
                previous_outputs.get("script"),
                "Script",
            ),
            "voice": self._parse_output(
                previous_outputs.get("voice"),
                "Voice",
            ),
            "visuals": self._parse_output(
                previous_outputs.get("visuals"),
                "Visuals",
            ),
            "video": self._parse_output(
                previous_outputs.get("video"),
                "Video",
            ),
            "captions": self._parse_output(
                previous_outputs.get("captions"),
                "Captions",
            ),
            "thumbnail": self._parse_output(
                previous_outputs.get("thumbnail"),
                "Thumbnail",
            ),
            "metadata": self._parse_output(
                previous_outputs.get("metadata"),
                "Metadata",
            ),
        }

        result = self.quality_service.run_quality_check(
            topic=topic,
            platform=platform,
            command=command,
            outputs=outputs,
        )

        return {
            "stage": "quality_check",
            "status": "completed",
            "execution": "quality_service",
            "quality_check": result,
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
                    f"Quality Check stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Quality Check stage received invalid "
                f"{stage_name} output."
            )

        return value


quality_check_stage_handler = QualityCheckStageHandler()