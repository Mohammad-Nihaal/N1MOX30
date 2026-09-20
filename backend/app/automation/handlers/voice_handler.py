from __future__ import annotations

import json
from typing import Any

from app.services.voice.voice_service import VoiceService


class VoiceStageHandler:
    """
    Automation handler for the N1MOX30 Voice stage.

    Consumes:
        - Completed Script output

    Produces:
        - Provider-neutral voice/audio planning output
    """

    def __init__(
        self,
        voice_service: VoiceService | None = None,
    ):
        self.voice_service = (
            voice_service or VoiceService()
        )

    def __call__(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        workflow = payload.get(
            "workflow",
            {},
        )

        topic = str(
            workflow.get(
                "topic",
                "",
            )
        ).strip()

        platform = str(
            workflow.get(
                "platform",
                "youtube",
            )
        ).strip().lower()

        command = str(
            workflow.get(
                "command",
                "",
            )
        ).strip()

        if not topic:
            raise ValueError(
                "Voice stage requires a workflow topic."
            )

        previous_outputs = payload.get(
            "previous_outputs",
            {},
        )

        script_output = previous_outputs.get(
            "script",
            {},
        )

        if not script_output:
            raise ValueError(
                "Voice stage requires completed script output."
            )

        script_data = self._normalize_script_output(
            script_output
        )

        result = self.voice_service.generate_voice(
            topic=topic,
            platform=platform,
            command=command,
            script=script_data,
        )

        return {
            "stage": "voice",
            "status": "completed",
            "execution": "voice_service",
            "voice": result,
        }

    def _normalize_script_output(
        self,
        script_output: Any,
    ) -> dict[str, Any] | str:
        """
        Normalize the persisted Script stage output.

        The workflow engine can provide previous output as a
        dictionary or as serialized JSON text.
        """

        if isinstance(
            script_output,
            dict,
        ):
            return script_output

        if isinstance(
            script_output,
            str,
        ):
            value = script_output.strip()

            if not value:
                raise ValueError(
                    "Voice stage received empty script output."
                )

            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                # Let VoiceService handle a non-JSON string if
                # necessary, rather than silently altering it.
                return value

            if not isinstance(
                parsed,
                dict,
            ):
                raise ValueError(
                    "Voice stage requires script JSON to be an object."
                )

            return parsed

        raise ValueError(
            "Voice stage received an unsupported script output type."
        )


voice_stage_handler = VoiceStageHandler()