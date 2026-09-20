from __future__ import annotations

import json
from typing import Any

from app.services.visuals.visual_service import VisualService


class VisualsStageHandler:
    """
    Automation handler for the Visuals stage.

    Consumes:
        - Script stage output
        - Voice stage output

    Produces:
        - Provider-independent visual production plan
    """

    def __init__(
        self,
        visual_service: VisualService | None = None,
    ) -> None:
        self.visual_service = visual_service or VisualService()

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
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

        # --------------------------------------------------------------
        # Require Script output
        # --------------------------------------------------------------

        script_output = previous_outputs.get("script")

        if script_output is None:
            raise ValueError(
                "Visuals stage requires a completed Script stage output."
            )

        script_output = self._parse_output(
            script_output,
            "Script",
        )

        # --------------------------------------------------------------
        # Require Voice output
        # --------------------------------------------------------------

        voice_output = previous_outputs.get("voice")

        if voice_output is None:
            raise ValueError(
                "Visuals stage requires a completed Voice stage output."
            )

        voice_output = self._parse_output(
            voice_output,
            "Voice",
        )

        # --------------------------------------------------------------
        # Generate visual plan
        # --------------------------------------------------------------

        result = self.visual_service.generate_visual_plan(
            topic=topic,
            platform=platform,
            command=command,
            script=script_output,
            voice=voice_output,
        )

        return {
            "stage": "visuals",
            "status": "completed",
            "execution": "visual_service",
            "visuals": result,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_output(
        self,
        output: Any,
        stage_name: str,
    ) -> dict[str, Any]:
        """
        Normalize persisted workflow output into a dictionary.
        """

        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Visuals stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(output, dict):
            raise ValueError(
                f"Visuals stage received invalid {stage_name} output."
            )

        return output


visuals_stage_handler = VisualsStageHandler()