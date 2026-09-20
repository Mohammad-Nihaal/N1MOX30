from __future__ import annotations

import subprocess
import uuid
from pathlib import Path
from typing import Any

from app.services.video_rendering.ffmpeg_renderer import FFmpegVideoRenderer


class VideoService:
    """N1MOX30 Stage 10 real video assembly and duration validation."""

    SUPPORTED_PLATFORMS = {
        "youtube",
        "youtube_shorts",
        "instagram",
        "instagram_reels",
        "tiktok",
        "x",
        "twitter",
    }

    DEFAULT_RESOLUTION = {
        "youtube": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
        "youtube_shorts": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
        "instagram": {"width": 1080, "height": 1350, "aspect_ratio": "4:5"},
        "instagram_reels": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
        "tiktok": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
        "x": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
        "twitter": {"width": 1920, "height": 1080, "aspect_ratio": "16:9"},
    }

    DEFAULT_FPS = 30
    YOUTUBE_MIN = 12 * 60
    YOUTUBE_MAX = 20 * 60
    SHORT_MAX = 60

    def __init__(
        self,
        provider: str = "ffmpeg",
        output_directory: str | Path = "storage/rendered",
    ) -> None:
        self.provider = str(provider or "ffmpeg").strip().lower()
        self.output_directory = Path(output_directory)
        self.renderer = FFmpegVideoRenderer()

    def create_video_manifest(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        visuals: dict[str, Any],
        voice: dict[str, Any],
        script: dict[str, Any],
    ) -> dict[str, Any]:
        platform = str(platform or "youtube").strip().lower()
        if platform not in self.SUPPORTED_PLATFORMS:
            platform = "youtube"

        visuals = self._unwrap(visuals, "visuals", "visual_plan")
        voice = self._unwrap(voice, "voice")
        script = self._unwrap(script, "script")

        scenes = visuals.get("scenes") or []
        if not isinstance(scenes, list) or not scenes:
            raise ValueError("Video stage requires completed Visuals scenes.")

        duration = self._duration(visuals, voice, scenes)
        self._validate_duration(platform, duration)

        resolution = self.DEFAULT_RESOLUTION[platform]
        voice_audio = self._voice_path(voice)

        clips: list[dict[str, Any]] = []
        for i, scene in enumerate(scenes):
            if not isinstance(scene, dict):
                continue
            path = self._scene_path(scene, visuals)
            if not path:
                continue

            start = self._number(scene.get("start_seconds"), 0.0)
            end = self._number(scene.get("end_seconds"), start)
            scene_duration = self._number(
                scene.get("duration_seconds"), max(0.1, end - start)
            )
            if scene_duration <= 0:
                continue

            clips.append({
                "type": "image" if self._is_image(path) else "video",
                "path": str(path),
                "start_seconds": start,
                "duration_seconds": scene_duration,
                "z_index": i,
            })

        if not clips:
            raise ValueError("Video stage found no renderable visual assets.")

        if voice_audio:
            clips.append({
                "type": "voice",
                "path": str(voice_audio),
                "start_seconds": 0.0,
                "duration_seconds": duration,
                "z_index": 1000,
            })

        timeline = {
            "width": resolution["width"],
            "height": resolution["height"],
            "fps": self.DEFAULT_FPS,
            "duration_seconds": duration,
            "background": "#000000",
            "clips": clips,
        }

        self.output_directory.mkdir(parents=True, exist_ok=True)
        output_path = self.output_directory / (
            f"n1mox30-{platform}-{uuid.uuid4().hex[:12]}.mp4"
        )

        result = self.renderer.render(timeline, output_path)
        success = bool(getattr(result, "success", False))

        if not success or not output_path.exists() or output_path.stat().st_size == 0:
            error = getattr(result, "error", None) or "FFmpeg did not produce a valid MP4."
            raise RuntimeError(f"Stage 10 render failed: {error}")

        actual_duration = self._probe_duration(output_path)
        self._validate_duration(platform, actual_duration)

        return {
            "stage": "video",
            "status": "completed",
            "execution": "ffmpeg_renderer",
            "provider": "ffmpeg",
            "video_status": "rendered",
            "topic": str(topic or "").strip(),
            "platform": platform,
            "command": str(command or "").strip(),
            "render": {
                "container": "mp4",
                "video_codec": "h264",
                "audio_codec": "aac",
                "width": resolution["width"],
                "height": resolution["height"],
                "fps": self.DEFAULT_FPS,
                "duration_seconds": actual_duration,
            },
            "render_output": {
                "status": "rendered",
                "provider": "ffmpeg",
                "file_path": str(output_path),
                "file_url": None,
                "mime_type": "video/mp4",
                "size_bytes": output_path.stat().st_size,
            },
            "scenes": clips,
            "audio": {
                "source_path": str(voice_audio) if voice_audio else None,
                "ready_for_render": bool(voice_audio),
            },
            "production_summary": {
                "total_scenes": len(clips) - (1 if voice_audio else 0),
                "total_duration_seconds": actual_duration,
                "assembly_status": "rendered",
                "render_status": "completed",
                "ready_for_captions": True,
            },
            "ready_for_captions": True,
        }

    def _validate_duration(self, platform: str, seconds: float) -> None:
        if platform == "youtube":
            if seconds < self.YOUTUBE_MIN:
                raise ValueError(
                    f"YouTube long-form video is {seconds:.1f}s. "
                    "Minimum is 720s (12 minutes)."
                )
            if seconds > self.YOUTUBE_MAX:
                raise ValueError(
                    f"YouTube long-form video is {seconds:.1f}s. "
                    "Maximum is 1200s (20 minutes)."
                )
        else:
            if seconds > self.SHORT_MAX:
                raise ValueError(
                    f"{platform} video is {seconds:.1f}s. "
                    "Maximum is 60 seconds."
                )

    def _duration(self, visuals: dict[str, Any], voice: dict[str, Any], scenes: list[Any]) -> float:
        summary = visuals.get("production_summary")
        if isinstance(summary, dict):
            value = self._number(summary.get("total_duration_seconds"), 0)
            if value > 0:
                return value

        latest = 0.0
        for scene in scenes:
            if isinstance(scene, dict):
                latest = max(latest, self._number(scene.get("end_seconds"), 0))
        if latest > 0:
            return latest

        value = self._number(voice.get("estimated_duration_seconds"), 0)
        if value > 0:
            return value

        audio = voice.get("audio")
        if isinstance(audio, dict):
            return self._number(audio.get("duration_seconds"), 0)

        return 0.0

    def _scene_path(self, scene: dict[str, Any], visuals: dict[str, Any]) -> str | None:
        candidates = [
            scene.get("file_path"),
            scene.get("asset_path"),
            scene.get("path"),
            scene.get("file_url"),
            scene.get("asset_url"),
        ]
        asset = scene.get("asset")
        if isinstance(asset, dict):
            candidates += [
                asset.get("file_path"),
                asset.get("asset_path"),
                asset.get("path"),
                asset.get("file_url"),
                asset.get("asset_url"),
            ]

        for value in candidates:
            if not value:
                continue
            p = Path(str(value))
            if p.exists():
                return str(p)
            if not p.is_absolute():
                root = Path("storage") / str(value).lstrip("/\\")
                if root.exists():
                    return str(root)
        return None

    def _voice_path(self, voice: dict[str, Any]) -> str | None:
        audio = voice.get("audio")
        candidates = []
        if isinstance(audio, dict):
            candidates += [audio.get("file_path"), audio.get("path"), audio.get("url")]
        candidates += [voice.get("file_path"), voice.get("path")]

        for value in candidates:
            if not value:
                continue
            p = Path(str(value))
            if p.exists():
                return str(p)
        return None

    def _probe_duration(self, path: Path) -> float:
        command = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Unable to probe rendered video: {completed.stderr.strip()}")
        return float(completed.stdout.strip())

    @staticmethod
    def _unwrap(value: dict[str, Any], *keys: str) -> dict[str, Any]:
        current = dict(value or {})
        for key in keys:
            nested = current.get(key)
            if isinstance(nested, dict):
                current = dict(nested)
        return current

    @staticmethod
    def _number(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _is_image(path: str) -> bool:
        return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


video_service = VideoService()
