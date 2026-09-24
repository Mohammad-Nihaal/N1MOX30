from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.video.video_service import VideoService


class VideoStageHandler:
    def __init__(self, video_service: VideoService | None = None):
        self.video_service = video_service or VideoService()

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        workflow = context.get("workflow") or {}
        previous_outputs = context.get("previous_outputs") or {}

        topic = str(workflow.get("topic") or "").strip()
        platform = str(workflow.get("platform") or "youtube").strip().lower()
        command = str(workflow.get("command") or "").strip()

        script_output = self._unwrap(previous_outputs.get("script"), "script")
        voice_output = self._unwrap_voice(previous_outputs.get("voice"))
        visuals_output = self._unwrap(previous_outputs.get("visuals"), "visuals")

        return self.video_service.create_video_manifest(
            topic=topic,
            platform=platform,
            command=command,
            visuals=visuals_output,
            voice=voice_output,
            script=script_output,
            user_id=str(context.get("user_id") or "") or None,
            db=context.get("_db"),
        )

    def _unwrap(self, value: Any, stage_name: str) -> dict[str, Any]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Video stage received invalid persisted {stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Video stage received invalid {stage_name} output."
            )

        inner = value.get(stage_name)

        if isinstance(inner, dict):
            return inner

        return value

    def _unwrap_voice(self, value: Any) -> dict[str, Any]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Video stage received invalid persisted voice JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                "Video stage received invalid voice output."
            )

        # Voice handler wrapper:
        # { stage, status, execution, voice: { ... } }
        voice = value.get("voice")

        if isinstance(voice, dict):
            value = voice

            # Voice service may itself return:
            # { ..., voice: {...}, narration: {...}, audio: {...} }
            nested_voice = value.get("voice")

            if isinstance(nested_voice, dict):
                value["voice_profile"] = nested_voice

        audio = value.get("audio")

        if not isinstance(audio, dict):
            audio = {}
            value["audio"] = audio

        candidates = [
            audio.get("file_path"),
            audio.get("audio_path"),
            audio.get("path"),
            value.get("audio_path"),
            value.get("file_path"),
            value.get("audio_file"),
            value.get("path"),
        ]

        for candidate in candidates:
            if not candidate:
                continue

            path = Path(str(candidate))

            if path.exists() and path.is_file():
                resolved = str(path)

                # Make the path available in every common location.
                value["audio_path"] = resolved
                value["file_path"] = resolved
                audio["file_path"] = resolved
                audio["audio_path"] = resolved
                audio["path"] = resolved

                return value

        raise ValueError(
            "Video stage could not locate the persisted Voice WAV file."
        )


video_stage_handler = VideoStageHandler()
