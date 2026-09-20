from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.services.video_rendering.base import (
    BaseVideoRenderer,
    RenderResult,
)


class FFmpegVideoRenderer(BaseVideoRenderer):
    """
    FFmpeg renderer for N1MOX30.

    Responsibilities:
    - Render image/video scenes
    - Scale and pad media to timeline dimensions
    - Respect scene timing
    - Add voice/audio tracks
    - Mix audio
    - Produce H.264/AAC MP4 output
    """

    provider_name = "ffmpeg"

    def __init__(
        self,
        ffmpeg_binary: str | None = None,
        ffprobe_binary: str | None = None,
    ) -> None:
        self.ffmpeg_binary = (
            ffmpeg_binary
            or shutil.which("ffmpeg")
            or "ffmpeg"
        )

        self.ffprobe_binary = (
            ffprobe_binary
            or shutil.which("ffprobe")
            or "ffprobe"
        )

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def validate_environment(self) -> dict[str, Any]:
        ffmpeg_path = shutil.which(self.ffmpeg_binary)

        if ffmpeg_path is None and Path(
            self.ffmpeg_binary
        ).exists():
            ffmpeg_path = self.ffmpeg_binary

        ffprobe_path = shutil.which(self.ffprobe_binary)

        if ffprobe_path is None and Path(
            self.ffprobe_binary
        ).exists():
            ffprobe_path = self.ffprobe_binary

        return {
            "provider": self.provider_name,
            "available": bool(
                ffmpeg_path and ffprobe_path
            ),
            "ffmpeg": ffmpeg_path,
            "ffprobe": ffprobe_path,
        }

    # ================================================================
    # RENDER
    # ================================================================

    def render(
        self,
        timeline: dict[str, Any],
        output_path: str | Path,
    ) -> RenderResult:

        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        validation = self._validate_timeline(
            timeline
        )

        if not validation["valid"]:
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message="; ".join(
                    validation["errors"]
                ),
            )

        clips = self._collect_media_clips(
            timeline.get(
                "tracks",
                [],
            )
        )

        if not clips:
            return self._render_blank_video(
                timeline,
                output,
            )

        command = self._build_ffmpeg_command(
            timeline=timeline,
            clips=clips,
            output=output,
        )

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except OSError as exc:
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=str(exc),
                metadata={
                    "command": command,
                },
            )

        if completed.returncode != 0:
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=(
                    completed.stderr[-10000:]
                    if completed.stderr
                    else "FFmpeg rendering failed."
                ),
                metadata={
                    "command": command,
                    "stdout": completed.stdout[-5000:]
                    if completed.stdout
                    else "",
                },
            )

        if not output.exists():
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=(
                    "FFmpeg completed successfully "
                    "but did not create the output file."
                ),
                metadata={
                    "command": command,
                },
            )

        file_size = output.stat().st_size

        if file_size <= 0:
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=(
                    "FFmpeg created an empty output file."
                ),
                metadata={
                    "command": command,
                },
            )

        duration = self._probe_duration(
            output
        )

        width = int(
            timeline.get(
                "width",
                1920,
            )
        )

        height = int(
            timeline.get(
                "height",
                1080,
            )
        )

        fps = float(
            timeline.get(
                "fps",
                30,
            )
        )

        return RenderResult(
            success=True,
            output_path=str(output),
            duration_seconds=duration,
            width=width,
            height=height,
            fps=fps,
            file_size_bytes=file_size,
            mime_type="video/mp4",
            provider=self.provider_name,
            metadata={
                "command": command,
            },
        )

    # ================================================================
    # PROBE
    # ================================================================

    def _probe_duration(
        self,
        path: Path,
    ) -> float:

        try:
            completed = subprocess.run(
                [
                    self.ffprobe_binary,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if completed.returncode == 0:
                return float(
                    completed.stdout.strip()
                )

        except (
            OSError,
            ValueError,
        ):
            pass

        return 0.0

    # ================================================================
    # TIMELINE VALIDATION
    # ================================================================

    def _validate_timeline(
        self,
        timeline: dict[str, Any],
    ) -> dict[str, Any]:

        errors: list[str] = []

        width = timeline.get("width")
        height = timeline.get("height")
        fps = timeline.get("fps")
        duration = timeline.get(
            "duration_seconds",
            0,
        )

        if not width or width <= 0:
            errors.append(
                "Timeline width must be greater than zero."
            )

        if not height or height <= 0:
            errors.append(
                "Timeline height must be greater than zero."
            )

        if not fps or fps <= 0:
            errors.append(
                "Timeline FPS must be greater than zero."
            )

        if duration < 0:
            errors.append(
                "Timeline duration cannot be negative."
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    # ================================================================
    # COLLECT CLIPS
    # ================================================================

    def _collect_media_clips(
        self,
        tracks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        clips: list[dict[str, Any]] = []

        for track in tracks:

            if track.get(
                "visible",
                True,
            ) is False:
                continue

            if track.get(
                "muted",
                False,
            ):
                continue

            track_type = track.get(
                "track_type",
                "video",
            )

            for clip in track.get(
                "clips",
                [],
            ):

                clip_type = clip.get(
                    "clip_type",
                    "video",
                )

                if clip_type not in {
                    "video",
                    "image",
                    "audio",
                    "voice",
                }:
                    continue

                clips.append(
                    {
                        **clip,
                        "track_type": track_type,
                    }
                )

        clips.sort(
            key=lambda item: (
                float(
                    item.get(
                        "start_time",
                        0,
                    )
                ),
                int(
                    item.get(
                        "layer",
                        0,
                    )
                ),
            )
        )

        return clips

    # ================================================================
    # BUILD FFMPEG COMMAND
    # ================================================================

    def _build_ffmpeg_command(
        self,
        timeline: dict[str, Any],
        clips: list[dict[str, Any]],
        output: Path,
    ) -> list[str]:

        width = int(
            timeline.get(
                "width",
                1920,
            )
        )

        height = int(
            timeline.get(
                "height",
                1080,
            )
        )

        fps = int(
            timeline.get(
                "fps",
                30,
            )
        )

        duration = float(
            timeline.get(
                "duration_seconds",
                0,
            )
        )

        if duration <= 0:
            duration = max(
                (
                    float(
                        clip.get(
                            "end_time",
                            0,
                        )
                    )
                    for clip in clips
                ),
                default=1.0,
            )

        background = self._normalize_color(
            timeline.get(
                "background_color",
                "#000000",
            )
        )

        video_clips = [
            clip
            for clip in clips
            if clip.get("clip_type")
            in {
                "video",
                "image",
            }
        ]

        audio_clips = [
            clip
            for clip in clips
            if clip.get("clip_type")
            in {
                "audio",
                "voice",
            }
        ]

        command = [
            self.ffmpeg_binary,
            "-y",
        ]

        input_index: dict[str, int] = {}

        input_counter = 0

        # ------------------------------------------------------------
        # INPUTS
        # ------------------------------------------------------------

        for clip in clips:

            media_path = self._resolve_media_path(
                clip
            )

            if not media_path:
                continue

            path = Path(media_path)

            if not path.exists():
                continue

            clip_id = clip.get("id")

            if not clip_id:
                continue

            input_index[clip_id] = input_counter

            if clip.get(
                "clip_type"
            ) == "image":

                command.extend(
                    [
                        "-loop",
                        "1",
                        "-i",
                        str(path),
                    ]
                )

            else:

                command.extend(
                    [
                        "-i",
                        str(path),
                    ]
                )

            input_counter += 1

        if not input_index:
            return self._build_blank_command(
                width=width,
                height=height,
                fps=fps,
                duration=duration,
                background=background,
                output=output,
            )

        filter_parts: list[str] = []

        # ============================================================
        # BASE VIDEO
        # ============================================================

        base_label = "[base]"

        filter_parts.append(
            (
                f"color=c={background}:"
                f"s={width}x{height}:"
                f"r={fps}:"
                f"d={duration}"
                f"{base_label}"
            )
        )

        current_video = base_label

        # Keep the actual clips that have valid inputs.
        renderable_video_clips: list[
            tuple[dict[str, Any], int]
        ] = []

        for clip in video_clips:

            clip_id = clip.get("id")

            if clip_id not in input_index:
                continue

            renderable_video_clips.append(
                (
                    clip,
                    input_index[clip_id],
                )
            )

        # ============================================================
        # VIDEO SCENES
        # ============================================================

        for position, (
            clip,
            index,
        ) in enumerate(
            renderable_video_clips
        ):

            start = max(
                float(
                    clip.get(
                        "start_time",
                        0,
                    )
                ),
                0.0,
            )

            end = min(
                float(
                    clip.get(
                        "end_time",
                        duration,
                    )
                ),
                duration,
            )

            clip_duration = max(
                end - start,
                0.1,
            )

            label = f"[scene{position}]"

            # IMPORTANT:
            #
            # The input label connects DIRECTLY to trim.
            #
            # Correct:
            #
            # [0:v]trim=...
            #
            # NOT:
            #
            # [0:v],trim=...
            #
            # Also the output label connects DIRECTLY to the
            # preceding filter.
            #
            # Correct:
            #
            # ...setpts=PTS+0/TB[scene0]
            #
            # NOT:
            #
            # ...setpts=PTS+0/TB,[scene0]

            filter_parts.append(
                (
                    f"[{index}:v]"
                    f"trim=duration={clip_duration},"
                    f"setpts=PTS-STARTPTS,"
                    f"scale={width}:{height}:"
                    "force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:"
                    f"(ow-iw)/2:(oh-ih)/2:"
                    f"color={background},"
                    f"fps={fps},"
                    f"setpts=PTS+{start}/TB"
                    f"{label}"
                )
            )

            next_video = (
                "[vout]"
                if position
                == len(renderable_video_clips) - 1
                else f"[mix{position}]"
            )

            filter_parts.append(
                (
                    f"{current_video}"
                    f"{label}"
                    f"overlay="
                    f"enable='between(t,{start},{end})'"
                    f"{next_video}"
                )
            )

            current_video = next_video

        video_map = current_video

        # ============================================================
        # AUDIO
        # ============================================================

        audio_inputs: list[str] = []

        for position, clip in enumerate(
            audio_clips
        ):

            clip_id = clip.get("id")

            if clip_id not in input_index:
                continue

            index = input_index[clip_id]

            start = max(
                float(
                    clip.get(
                        "start_time",
                        0,
                    )
                ),
                0.0,
            )

            end = min(
                float(
                    clip.get(
                        "end_time",
                        duration,
                    )
                ),
                duration,
            )

            clip_duration = max(
                end - start,
                0.1,
            )

            label = f"[audio{position}]"

            delay_ms = int(
                start * 1000
            )

            filter_parts.append(
                (
                    f"[{index}:a]"
                    f"atrim=duration={clip_duration},"
                    "asetpts=PTS-STARTPTS,"
                    f"adelay={delay_ms}|{delay_ms},"
                    f"apad=whole_dur={duration},"
                    f"atrim=duration={duration}"
                    f"{label}"
                )
            )

            audio_inputs.append(
                label
            )

        # ============================================================
        # AUDIO MIX
        # ============================================================

        audio_map: str | None = None

        if audio_inputs:

            audio_map = "[aout]"

            filter_parts.append(
                (
                    "".join(audio_inputs)
                    + f"amix=inputs={len(audio_inputs)}:"
                    "duration=longest:"
                    "dropout_transition=0,"
                    f"atrim=duration={duration}"
                    f"{audio_map}"
                )
            )

        # ============================================================
        # FILTER COMPLEX
        # ============================================================

        command.extend(
            [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                video_map,
            ]
        )

        if audio_map:

            command.extend(
                [
                    "-map",
                    audio_map,
                ]
            )

        else:

            command.extend(
                [
                    "-an",
                ]
            )

        # ============================================================
        # ENCODING
        # ============================================================

        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                "-t",
                str(duration),
            ]
        )

        if audio_map:

            command.extend(
                [
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                ]
            )

        command.append(
            str(output)
        )

        return command

    # ================================================================
    # RESOLVE MEDIA PATH
    # ================================================================

    @staticmethod
    def _resolve_media_path(
        clip: dict[str, Any],
    ) -> str | None:

        for key in (
            "storage_path",
            "file_path",
            "path",
            "local_path",
        ):

            value = clip.get(key)

            if value:
                return str(value)

        metadata = clip.get(
            "metadata"
        )

        if isinstance(
            metadata,
            dict,
        ):

            for key in (
                "storage_path",
                "file_path",
                "path",
                "local_path",
            ):

                value = metadata.get(key)

                if value:
                    return str(value)

        return None

    # ================================================================
    # COLOR
    # ================================================================

    @staticmethod
    def _normalize_color(
        value: Any,
    ) -> str:

        color = str(
            value or "#000000"
        ).strip()

        if color.startswith("#"):
            color = color[1:]

        if len(color) != 6:
            color = "000000"

        return f"0x{color}"

    # ================================================================
    # BLANK VIDEO
    # ================================================================

    def _build_blank_command(
        self,
        width: int,
        height: int,
        fps: int,
        duration: float,
        background: str,
        output: Path,
    ) -> list[str]:

        return [
            self.ffmpeg_binary,
            "-y",
            "-f",
            "lavfi",
            "-i",
            (
                f"color=c={background}:"
                f"s={width}x{height}:"
                f"r={fps}:"
                f"d={duration}"
            ),
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ]

    # ================================================================
    # RENDER BLANK VIDEO
    # ================================================================

    def _render_blank_video(
        self,
        timeline: dict[str, Any],
        output: Path,
    ) -> RenderResult:

        width = int(
            timeline.get(
                "width",
                1920,
            )
        )

        height = int(
            timeline.get(
                "height",
                1080,
            )
        )

        fps = int(
            timeline.get(
                "fps",
                30,
            )
        )

        duration = float(
            timeline.get(
                "duration_seconds",
                1,
            )
        )

        background = self._normalize_color(
            timeline.get(
                "background_color",
                "#000000",
            )
        )

        command = self._build_blank_command(
            width=width,
            height=height,
            fps=fps,
            duration=duration,
            background=background,
            output=output,
        )

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except OSError as exc:
            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=str(exc),
                metadata={
                    "command": command,
                },
            )

        if completed.returncode != 0:

            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=(
                    completed.stderr[-10000:]
                    if completed.stderr
                    else "FFmpeg blank video rendering failed."
                ),
                metadata={
                    "command": command,
                },
            )

        if not output.exists():

            return RenderResult(
                success=False,
                provider=self.provider_name,
                error_message=(
                    "FFmpeg completed without "
                    "creating the blank video."
                ),
                metadata={
                    "command": command,
                },
            )

        file_size = output.stat().st_size

        duration_result = self._probe_duration(
            output
        )

        return RenderResult(
            success=True,
            output_path=str(output),
            duration_seconds=duration_result,
            width=width,
            height=height,
            fps=float(fps),
            file_size_bytes=file_size,
            mime_type="video/mp4",
            provider=self.provider_name,
            metadata={
                "command": command,
            },
        )