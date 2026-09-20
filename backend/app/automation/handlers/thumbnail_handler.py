from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.services.thumbnails.thumbnail_service import (
    ThumbnailService,
)


class ThumbnailStageHandler:
    """
    Workflow handler for the Thumbnail stage.

    Consumes completed outputs from previous workflow stages and
    delegates thumbnail generation to ThumbnailService.

    The workflow engine provides the active SQLAlchemy Session through
    the internal `_db` context value.
    """

    def __init__(
        self,
        thumbnail_service: ThumbnailService | None = None,
    ):
        self.thumbnail_service = (
            thumbnail_service
            or ThumbnailService()
        )

    def __call__(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute thumbnail generation using workflow context.
        """

        workflow = context.get("workflow") or {}

        db = context.get("_db")

        if not isinstance(db, Session):
            raise ValueError(
                "Thumbnail stage requires an active database session."
            )

        topic = str(
            workflow.get("topic") or ""
        ).strip()

        platform = str(
            workflow.get("platform") or "youtube"
        ).strip().lower()

        command = str(
            workflow.get("command") or ""
        ).strip()

        user_id = str(
            workflow.get("user_id") or ""
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

        if not topic:
            raise ValueError(
                "Thumbnail stage requires a workflow topic."
            )

        if not user_id:
            raise ValueError(
                "Thumbnail stage requires a workflow user_id."
            )

        if not script_output:
            raise ValueError(
                "Thumbnail stage requires a completed "
                "Script stage output."
            )

        if not video_output:
            raise ValueError(
                "Thumbnail stage requires a completed "
                "Video stage output."
            )

        result = self.thumbnail_service.generate_thumbnail(
            db=db,
            user_id=user_id,
            title=topic,
            topic=topic,
            platform=platform,
            command=command,
            research=research_output,
            strategy=strategy_output,
            hooks=hooks_output,
            script=script_output,
            voice=voice_output,
            visuals=visuals_output,
            video=video_output,
            captions=captions_output,
        )

        return {
            "stage": "thumbnail",
            "status": "completed",
            "execution": "thumbnail_service",
            "thumbnail": result,
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
                    f"Thumbnail stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):
            raise ValueError(
                f"Thumbnail stage received invalid "
                f"{stage_name} output."
            )

        return value


thumbnail_stage_handler = ThumbnailStageHandler()