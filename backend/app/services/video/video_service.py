from __future__ import annotations
import json
import subprocess
from pathlib import Path
from typing import Any
from app.services.video_rendering.ffmpeg_renderer import FFmpegVideoRenderer
class VideoService:
    """
    N1MOX30 Stage 10 video production service.
    Converts completed Script + Voice + Visuals outputs into a real
    renderable video using the local FFmpeg renderer.
    Supports:
        YouTube long-form: 12-20 minutes
        Shorts/Reels/TikTok: <= 60 seconds
    """
    SUPPORTED_PLATFORMS = {
        "youtube",
        "youtube_shorts",
        "instagram",
        "instagram_reels",
        "tiktok",
        "x",
        "twitter",
    }
    YOUTUBE_MIN_SECONDS = 720
    YOUTUBE_MAX_SECONDS = 1200
    SHORT_MAX_SECONDS = 60
    def __init__(self) -> None:
        self.renderer = FFmpegVideoRenderer()
        self.output_dir = Path("storage") / "rendered"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    # ================================================================
    # PUBLIC API
    # ================================================================
    def create_video_manifest(
        self,
        topic: str,
        platform: str,
        command: str,
        visuals: dict[str, Any],
        voice: dict[str, Any],
        script: dict[str, Any],
    ) -> dict[str, Any]:
        topic = str(topic or "").strip()
        platform = str(platform or "youtube").strip().lower()
        command = str(command or "").strip()
        if platform not in self.SUPPORTED_PLATFORMS:
            platform = "youtube"
        normalized_visuals = self._normalize_visuals(visuals)
        normalized_voice = self._normalize_voice(voice)
        normalized_script = self._normalize_script(script)
        if not normalized_visuals:
            raise ValueError("Video stage requires completed Visuals output.")
        if not normalized_voice:
            raise ValueError("Video stage requires completed Voice output.")
        if not normalized_script:
            raise ValueError("Video stage requires completed Script output.")
        scenes = normalized_visuals.get("scenes") or []
        visual_requirements = normalized_visuals.get(
            "visual_requirements"
        ) or []
        overlays = normalized_visuals.get("overlays") or []
        # ------------------------------------------------------------
        # IMPORTANT COMPATIBILITY FIX
        #
        # VisualService stores real generated files inside:
        #
        # visual_requirements[*].file_path
        # visual_requirements[*].asset_path
        #
        # Convert those requirements into renderable scene assets.
        # ------------------------------------------------------------
        scenes = self._merge_renderable_assets(
            scenes=scenes,
            visual_requirements=visual_requirements,
        )
        if not scenes:
            raise ValueError(
                "Video stage found no renderable visual assets."
            )
        total_duration = self._calculate_total_duration(
            normalized_visuals=normalized_visuals,
            normalized_voice=normalized_voice,
            scenes=scenes,
        )
        total_duration = self._validate_and_normalize_duration(
            platform=platform,
            duration_seconds=total_duration,
        )
        resolution = self._get_resolution(platform)
        scene_tracks = self._build_scene_tracks(
            scenes=scenes,
            overlays=overlays,
            visual_requirements=visual_requirements,
        )
        audio_path = self._voice_path(normalized_voice)
        if not audio_path or not Path(audio_path).exists():
            raise ValueError(
                f"Video stage could not find Voice audio file: {audio_path}"
            )
        width, height = [int(x) for x in resolution.split("x")]
        video_clips = []
        for scene in scene_tracks:
            path = scene.get("file_path")
            if not path or not Path(path).exists():
                continue
            start_time = float(scene.get("start_seconds", 0.0))
            duration = float(scene.get("duration_seconds", 5.0))
            end_time = start_time + duration
            video_clips.append({
                "id": str(scene.get("scene_id") or f"scene_{len(video_clips)+1:03d}"),
                "clip_type": "image",
                "file_path": str(path),
                "start_time": start_time,
                "end_time": end_time,
                "layer": 0,
            })
        audio_clip = {
            "id": "voice_main",
            "clip_type": "voice",
            "file_path": str(audio_path),
            "start_time": 0.0,
            "end_time": float(total_duration),
            "layer": 10,
        }
        timeline = {
            "topic": topic,
            "platform": platform,
            "command": command,
            "width": width,
            "height": height,
            "fps": 30,
            "duration_seconds": float(total_duration),
            "background_color": "#000000",
            "tracks": [
                {
                    "id": "video_track_1",
                    "track_type": "video",
                    "visible": True,
                    "muted": False,
                    "clips": video_clips,
                },
                {
                    "id": "voice_track",
                    "track_type": "audio",
                    "visible": True,
                    "muted": False,
                    "clips": [audio_clip],
                },
            ],
            "render_config": {
                "video_codec": "libx264",
                "audio_codec": "aac",
                "pixel_format": "yuv420p",
                "fps": 30,
                "resolution": resolution,
            },
        }
        safe_topic = "".join(
            c if c.isalnum() else "_"
            for c in topic.lower()
        ).strip("_")
        if not safe_topic:
            safe_topic = "nimox30_video"
        output_path = (
            self.output_dir
            / f"{safe_topic}_{platform}.mp4"
        )
        render_result = self.renderer.render(
            timeline,
            output_path,
        )
        if isinstance(render_result, dict):
            render_success = bool(render_result.get("success"))
            render_error = (
                render_result.get("error")
                or render_result.get("error_message")
            )
        else:
            render_success = bool(getattr(render_result, "success", False))
            render_error = (
                getattr(render_result, "error_message", None)
                or getattr(render_result, "error", None)
            )

        if not render_success:
            raise RuntimeError(
                render_error or "FFmpeg video rendering failed."
            )
        rendered_duration = self._probe_duration(output_path)
        self._validate_final_duration(
            platform=platform,
            duration_seconds=rendered_duration,
        )
        return {
            "stage": "video",
            "status": "completed",
            "execution": "video_service",
            "provider": "ffmpeg",
            "topic": topic,
            "platform": platform,
            "command": command,
            "video_status": "rendered",
            "rendered": True,
            "ready_for_captions": True,
            "duration_seconds": rendered_duration,
            "resolution": resolution,
            "fps": 30,
            "format": "mp4",
            "video": {
                "file_path": str(output_path),
                "asset_path": str(output_path),
                "file_url": None,
                "mime_type": "video/mp4",
                "duration_seconds": rendered_duration,
                "ready_for_captions": True,
                "ready_for_upload": True,
            },
            "production": {
                "rendered": True,
                "render_provider": "ffmpeg",
                "source_visual_count": len(scene_tracks),
                "audio_attached": True,
                "ready_for_caption_render": True,
            },
        }
    # ================================================================
    # VISUAL COMPATIBILITY
    # ================================================================
    def _merge_renderable_assets(
        self,
        scenes: Any,
        visual_requirements: Any,
    ) -> list[dict[str, Any]]:
        existing = scenes if isinstance(scenes, list) else []
        requirements = (
            visual_requirements
            if isinstance(visual_requirements, list)
            else []
        )
        by_scene: dict[str, dict[str, Any]] = {}
        for scene in existing:
            if not isinstance(scene, dict):
                continue
            scene_id = str(
                scene.get("scene_id")
                or scene.get("id")
                or ""
            ).strip()
            if scene_id:
                by_scene[scene_id] = dict(scene)
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            scene_id = str(
                requirement.get("scene_id")
                or requirement.get("id")
                or ""
            ).strip()
            file_path = (
                requirement.get("file_path")
                or requirement.get("asset_path")
                or requirement.get("path")
            )
            if not file_path:
                continue
            path = Path(str(file_path))
            if not path.exists():
                continue
            if scene_id in by_scene:
                scene = by_scene[scene_id]
            else:
                scene = {
                    "scene_id": scene_id or f"scene_{len(by_scene)+1:03d}",
                    "scene_order": len(by_scene) + 1,
                }
            scene["file_path"] = str(path)
            scene["asset_path"] = str(path)
            scene["asset_type"] = requirement.get(
                "asset_type",
                "generated_image",
            )
            scene["ready_for_video"] = True
            scene["provider_status"] = requirement.get(
                "provider_status",
                "generated",
            )
            if requirement.get("start_seconds") is not None:
                scene["start_seconds"] = requirement["start_seconds"]
            if requirement.get("end_seconds") is not None:
                scene["end_seconds"] = requirement["end_seconds"]
            if requirement.get("duration_seconds") is not None:
                scene["duration_seconds"] = requirement[
                    "duration_seconds"
                ]
            if requirement.get("prompt"):
                scene["visual_prompt"] = requirement["prompt"]
            by_scene[scene["scene_id"]] = scene
        result = list(by_scene.values())
        result.sort(
            key=lambda item: self._number(
                item.get("scene_order"),
                item.get("start_seconds"),
                0,
            )
        )
        return result
    # ================================================================
    # SCENE TRACKS
    # ================================================================
    def _build_scene_tracks(
        self,
        scenes: list[dict[str, Any]],
        overlays: list[dict[str, Any]],
        visual_requirements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        tracks: list[dict[str, Any]] = []
        for index, scene in enumerate(scenes):
            path = self._scene_path(scene)
            if not path:
                continue
            if not Path(path).exists():
                continue
            start = self._number(
                scene.get("start_seconds"),
                0.0,
            )
            duration = self._number(
                scene.get("duration_seconds"),
                None,
            )
            end = self._number(
                scene.get("end_seconds"),
                None,
            )
            if duration is None and end is not None:
                duration = max(0.1, end - start)
            if duration is None:
                duration = 5.0
            scene_id = str(
                scene.get("scene_id")
                or f"scene_{index + 1:03d}"
            )
            tracks.append(
                {
                    "scene_id": scene_id,
                    "order": index + 1,
                    "file_path": path,
                    "asset_path": path,
                    "asset_type": scene.get(
                        "asset_type",
                        "generated_image",
                    ),
                    "start_seconds": start,
                    "duration_seconds": duration,
                    "end_seconds": start + duration,
                    "transition": scene.get(
                        "transition",
                        "clean_cut",
                    ),
                }
            )
        if not tracks:
            raise ValueError(
                "Video stage found no renderable visual assets."
            )
        return tracks
    # ================================================================
    # NORMALIZATION
    # ================================================================
    def _normalize_visuals(
        self,
        visuals: Any,
    ) -> dict[str, Any]:
        value = self._parse_dict(visuals)
        if isinstance(value.get("visual_plan"), dict):
            value = value["visual_plan"]
        if isinstance(value.get("visual_plan"), dict):
            value = value["visual_plan"]
        return value
    def _normalize_voice(
        self,
        voice: Any,
    ) -> dict[str, Any]:
        """
        Normalize Voice wrapper shapes without peeling into voice_config.
        Persisted shapes look like:
        {
            "stage": "voice",
            "voice": {
                "voice": {...voice_config...},
                "audio": {"file_path": "..."},
                "narration": {...},
                ...
            }
        }
        Blindly unwrapping every nested `voice` key drops `audio.file_path`
        and causes: "Video stage could not find Voice audio file: None".
        """
        value = self._parse_dict(voice)
        def looks_like_voice_result(payload: dict[str, Any]) -> bool:
            return any(
                key in payload
                for key in (
                    "stage",
                    "status",
                    "execution",
                    "provider",
                    "timeline",
                    "narration",
                    "audio",
                    "estimated_duration_seconds",
                )
            )
        # Unwrap handler/service wrappers only. Stop at voice_config.
        for _ in range(2):
            nested = value.get("voice")
            if not isinstance(nested, dict):
                break
            if looks_like_voice_result(nested):
                value = nested
                continue
            break
        return value
    def _normalize_script(
        self,
        script: Any,
    ) -> dict[str, Any]:
        value = self._parse_dict(script)
        if isinstance(value.get("script"), dict):
            value = value["script"]
        if isinstance(value.get("script"), dict):
            value = value["script"]
        return value
    def _parse_dict(
        self,
        value: Any,
    ) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return {}
        return {}
    # ================================================================
    # DURATION
    # ================================================================
    def _calculate_total_duration(
        self,
        normalized_visuals: dict[str, Any],
        normalized_voice: dict[str, Any],
        scenes: list[dict[str, Any]],
    ) -> float:
        candidates: list[float] = []
        voice_duration = self._voice_duration(
            normalized_voice
        )
        if voice_duration > 0:
            candidates.append(voice_duration)
        for scene in scenes:
            end = self._number(
                scene.get("end_seconds"),
                None,
            )
            start = self._number(
                scene.get("start_seconds"),
                0.0,
            )
            duration = self._number(
                scene.get("duration_seconds"),
                None,
            )
            if end is not None:
                candidates.append(end)
            elif duration is not None:
                candidates.append(
                    start + duration
                )
        duration = max(candidates) if candidates else 0.0
        return duration
    def _validate_and_normalize_duration(
        self,
        platform: str,
        duration_seconds: float,
    ) -> float:
        duration = float(duration_seconds or 0)
        if platform == "youtube":
            if duration < self.YOUTUBE_MIN_SECONDS:
                raise ValueError(
                    f"YouTube long-form video is {duration:.2f}s; "
                    f"minimum is {self.YOUTUBE_MIN_SECONDS}s "
                    f"(12 minutes)."
                )
            if duration > self.YOUTUBE_MAX_SECONDS:
                raise ValueError(
                    f"YouTube long-form video is {duration:.2f}s; "
                    f"maximum is {self.YOUTUBE_MAX_SECONDS}s "
                    f"(20 minutes)."
                )
        else:
            if duration <= 0:
                raise ValueError(
                    "Short-form video requires a positive duration."
                )
            if duration > self.SHORT_MAX_SECONDS:
                raise ValueError(
                    f"{platform} video exceeds the "
                    f"{self.SHORT_MAX_SECONDS}s limit."
                )
        return duration
    def _validate_final_duration(
        self,
        platform: str,
        duration_seconds: float,
    ) -> None:
        self._validate_and_normalize_duration(
            platform,
            duration_seconds,
        )
    # ================================================================
    # VOICE
    # ================================================================
    def _voice_duration(
        self,
        voice: dict[str, Any],
    ) -> float:
        candidates = [
            voice.get("duration_seconds"),
            voice.get("estimated_duration_seconds"),
        ]
        audio = voice.get("audio")
        if isinstance(audio, dict):
            candidates.extend(
                [
                    audio.get("duration_seconds"),
                    audio.get("duration"),
                ]
            )
        best = 0.0
        for value in candidates:
            try:
                number = float(value)
                if number > best:
                    best = number
            except (TypeError, ValueError):
                continue
        return best
    def _voice_path(
        self,
        voice: dict[str, Any],
    ) -> str | None:
        candidates = [
            voice.get("audio_path"),
            voice.get("file_path"),
            voice.get("audio_file"),
            voice.get("path"),
        ]
        audio = voice.get("audio")
        if isinstance(audio, dict):
            candidates.extend(
                [
                    audio.get("audio_path"),
                    audio.get("file_path"),
                    audio.get("path"),
                ]
            )
        for candidate in candidates:
            if candidate:
                path = Path(str(candidate))
                if path.exists():
                    return str(path)
        return None
    # ================================================================
    # VISUAL PATH
    # ================================================================
    def _scene_path(
        self,
        scene: dict[str, Any],
    ) -> str | None:
        candidates = [
            scene.get("file_path"),
            scene.get("asset_path"),
            scene.get("file"),
            scene.get("path"),
            scene.get("source"),
        ]
        asset = scene.get("asset")
        if isinstance(asset, dict):
            candidates.extend(
                [
                    asset.get("file_path"),
                    asset.get("asset_path"),
                    asset.get("path"),
                ]
            )
        for candidate in candidates:
            if candidate:
                path = Path(str(candidate))
                if path.exists():
                    return str(path)
        return None
    # ================================================================
    # RESOLUTION
    # ================================================================
    def _get_resolution(
        self,
        platform: str,
    ) -> str:
        if platform in {
            "youtube_shorts",
            "instagram_reels",
            "tiktok",
        }:
            return "1080x1920"
        if platform == "instagram":
            return "1080x1080"
        return "1920x1080"
    # ================================================================
    # FFMPEG PROBE
    # ================================================================
    def _probe_duration(
        self,
        path: Path,
    ) -> float:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            return float(
                result.stdout.strip()
            )
        except Exception as exc:
            raise RuntimeError(
                f"Could not determine rendered video duration: {exc}"
            ) from exc
    # ================================================================
    # HELPERS
    # ================================================================
    def _number(
        self,
        *values: Any,
    ) -> float | None:
        for value in values:
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return None
video_service = VideoService()
