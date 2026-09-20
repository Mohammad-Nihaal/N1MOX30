from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from app.services.captions.caption_service import CaptionService


class CaptionsStageHandler:
    """
    Workflow handler for the Captions stage.

    Consumes completed Script, Voice, and Video outputs.

    Responsibilities:
    - Generate caption segments
    - Generate an SRT sidecar
    - Burn captions into the rendered MP4 using FFmpeg
    - Return the final captioned video path
    """

    def __init__(
        self,
        caption_service: CaptionService | None = None,
    ):
        self.caption_service = (
            caption_service or CaptionService()
        )

        self.ffmpeg_binary = "ffmpeg"

    # ================================================================
    # MAIN HANDLER
    # ================================================================

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

        script_output = self._parse_output(
            previous_outputs.get("script"),
            "Script",
        )

        voice_output = self._parse_output(
            previous_outputs.get("voice"),
            "Voice",
        )

        video_output = self._parse_output(
            previous_outputs.get("video"),
            "Video",
        )

        if not script_output:
            raise ValueError(
                "Captions stage requires a completed Script stage output."
            )

        if not voice_output:
            raise ValueError(
                "Captions stage requires a completed Voice stage output."
            )

        if not video_output:
            raise ValueError(
                "Captions stage requires a completed Video stage output."
            )

        # ============================================================
        # GENERATE CAPTIONS
        # ============================================================

        caption_result = (
            self.caption_service.generate_captions(
                topic=topic,
                platform=platform,
                command=command,
                script=script_output,
                voice=voice_output,
                video=video_output,
            )
        )

        # ============================================================
        # LOCATE VIDEO
        # ============================================================

        video_path = self._extract_video_path(
            video_output
        )

        if not video_path:
            raise ValueError(
                "Captions stage could not locate the rendered video file."
            )

        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(
                f"Rendered video does not exist: {video_file}"
            )

        # ============================================================
        # EXTRACT CAPTION SEGMENTS
        # ============================================================

        captions = (
            caption_result.get("captions")
            if isinstance(caption_result, dict)
            else None
        )

        segments = (
            captions.get("segments")
            if isinstance(captions, dict)
            else None
        )

        if not isinstance(segments, list) or not segments:
            raise ValueError(
                "CaptionService returned no caption segments."
            )

        # ============================================================
        # CREATE SRT
        # ============================================================

        srt_path = (
            video_file.parent
            / f"{video_file.stem}.srt"
        )

        srt_content = self._segments_to_srt(
            segments
        )

        srt_path.write_text(
            srt_content,
            encoding="utf-8",
        )

        # ============================================================
        # BURN CAPTIONS INTO VIDEO
        # ============================================================

        captioned_video_path = (
            video_file.parent
            / f"{video_file.stem}-captioned.mp4"
        )

        render_result = self._burn_captions(
            video_path=video_file,
            srt_path=srt_path,
            output_path=captioned_video_path,
        )

        if not render_result["success"]:
            return {
                "stage": "captions",
                "status": "failed",
                "execution": "caption_service",
                "error": render_result["error"],
                "captions": caption_result,
                "render": {
                    "status": "failed",
                    "format": "embedded",
                    "file_path": None,
                    "srt_path": str(srt_path),
                    "url": None,
                },
            }

        # ============================================================
        # FINAL RESULT
        # ============================================================

        final_size = (
            captioned_video_path.stat().st_size
        )

        result = dict(caption_result)

        result["caption_status"] = "rendered"

        result["render"] = {
            "status": "completed",
            "format": "embedded",
            "file_path": str(
                captioned_video_path
            ),
            "srt_path": str(srt_path),
            "url": None,
            "file_size_bytes": final_size,
        }

        result["production"] = {
            **(
                result.get("production")
                or {}
            ),
            "ready_for_caption_render": True,
            "ready_for_video_pipeline": True,
            "captions_burned_into_video": True,
            "final_video_path": str(
                captioned_video_path
            ),
        }

        return {
            "stage": "captions",
            "status": "completed",
            "execution": "caption_service",
            "captions": result,
            "video": {
                "status": "captioned",
                "source_path": str(video_file),
                "final_path": str(
                    captioned_video_path
                ),
                "captioned": True,
            },
        }

    # ================================================================
    # VIDEO PATH EXTRACTION
    # ================================================================

    @staticmethod
    def _extract_video_path(
        video_output: dict[str, Any],
    ) -> str | None:

        possible_objects: list[Any] = [
            video_output,
            video_output.get("video"),
            video_output.get("render"),
            video_output.get("output"),
        ]

        for obj in possible_objects:

            if not isinstance(obj, dict):
                continue

            for key in (
                "file_path",
                "output_path",
                "path",
                "storage_path",
                "local_path",
            ):
                value = obj.get(key)

                if value:
                    return str(value)

        # Recursive fallback for nested video results.
        def search(
            value: Any,
        ) -> str | None:

            if isinstance(value, dict):

                for key in (
                    "file_path",
                    "output_path",
                    "storage_path",
                    "local_path",
                ):
                    candidate = value.get(key)

                    if candidate:
                        candidate_path = Path(
                            str(candidate)
                        )

                        if candidate_path.suffix.lower() == ".mp4":
                            return str(candidate_path)

                for child in value.values():

                    result = search(child)

                    if result:
                        return result

            elif isinstance(value, list):

                for child in value:

                    result = search(child)

                    if result:
                        return result

            return None

        return search(video_output)

    # ================================================================
    # SRT
    # ================================================================

    @classmethod
    def _segments_to_srt(
        cls,
        segments: list[dict[str, Any]],
    ) -> str:

        lines: list[str] = []

        for index, segment in enumerate(
            segments,
            start=1,
        ):

            if not isinstance(segment, dict):
                continue

            start = cls._segment_time(
                segment,
                "start",
            )

            end = cls._segment_time(
                segment,
                "end",
            )

            text = str(
                segment.get("text")
                or segment.get("caption")
                or segment.get("content")
                or ""
            ).strip()

            if not text:
                continue

            lines.extend(
                [
                    str(index),
                    (
                        f"{cls._format_srt_time(start)}"
                        f" --> "
                        f"{cls._format_srt_time(end)}"
                    ),
                    text,
                    "",
                ]
            )

        return "\n".join(lines)

    @staticmethod
    def _segment_time(
        segment: dict[str, Any],
        field: str,
    ) -> float:

        value = segment.get(field)

        if value is None:
            value = segment.get(
                f"{field}_seconds"
            )

        if value is None:
            value = 0.0

        if isinstance(value, str):

            value = value.strip()

            if ":" in value:

                parts = value.split(":")

                try:

                    if len(parts) == 3:
                        hours = float(parts[0])
                        minutes = float(parts[1])
                        seconds = float(parts[2])

                        return (
                            hours * 3600
                            + minutes * 60
                            + seconds
                        )

                    if len(parts) == 2:
                        minutes = float(parts[0])
                        seconds = float(parts[1])

                        return (
                            minutes * 60
                            + seconds
                        )

                except ValueError:
                    return 0.0

        try:
            return max(
                float(value),
                0.0,
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _format_srt_time(
        seconds: float,
    ) -> str:

        milliseconds = int(
            round(
                max(seconds, 0.0)
                * 1000
            )
        )

        hours = milliseconds // 3_600_000

        milliseconds %= 3_600_000

        minutes = milliseconds // 60_000

        milliseconds %= 60_000

        secs = milliseconds // 1_000

        milliseconds %= 1_000

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d},"
            f"{milliseconds:03d}"
        )

    # ================================================================
    # FFMPEG CAPTION BURN-IN
    # ================================================================

    def _burn_captions(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
    ) -> dict[str, Any]:

        ffmpeg = self.ffmpeg_binary

        escaped_srt = (
            str(srt_path.resolve())
            .replace("\\", "/")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )

        subtitle_filter = (
            f"subtitles='{escaped_srt}':"
            "force_style="
            "'FontName=Arial,"
            "FontSize=22,"
            "Bold=1,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "BorderStyle=1,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            "MarginV=45'"
        )

        command = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vf",
            subtitle_filter,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        try:

            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except OSError as exc:

            return {
                "success": False,
                "error": str(exc),
                "command": command,
            }

        if completed.returncode != 0:

            return {
                "success": False,
                "error": (
                    completed.stderr[-10000:]
                    if completed.stderr
                    else "FFmpeg caption rendering failed."
                ),
                "command": command,
            }

        if not output_path.exists():

            return {
                "success": False,
                "error": (
                    "FFmpeg completed but did not "
                    "create the captioned video."
                ),
                "command": command,
            }

        if output_path.stat().st_size <= 0:

            return {
                "success": False,
                "error": (
                    "FFmpeg created an empty captioned video."
                ),
                "command": command,
            }

        return {
            "success": True,
            "error": None,
            "command": command,
        }

    # ================================================================
    # OUTPUT PARSER
    # ================================================================

    @staticmethod
    def _parse_output(
        value: Any,
        stage_name: str,
    ) -> dict[str, Any] | None:

        if value is None:
            return None

        if isinstance(value, str):

            try:
                value = json.loads(value)

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Captions stage received invalid persisted "
                    f"{stage_name} JSON."
                ) from exc

        if not isinstance(value, dict):

            raise ValueError(
                f"Captions stage received invalid "
                f"{stage_name} output."
            )

        return value


captions_stage_handler = CaptionsStageHandler()