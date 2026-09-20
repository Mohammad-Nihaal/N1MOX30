from __future__ import annotations

from typing import Any


class CaptionService:
    """
    Provider-neutral caption generation service.

    This stage converts the completed Script + Voice timing information
    into a caption manifest that can later be rendered into the final video.

    The service intentionally does not claim that captions have been
    rendered into an actual video file.
    """

    SUPPORTED_PLATFORMS = {
        "youtube",
        "youtube_shorts",
        "instagram",
        "instagram_reels",
        "tiktok",
    }

    DEFAULT_MAX_CHARS_PER_LINE = 42
    DEFAULT_MAX_LINES = 2

    def __init__(
        self,
        provider: str = "demo",
        max_chars_per_line: int = DEFAULT_MAX_CHARS_PER_LINE,
        max_lines: int = DEFAULT_MAX_LINES,
    ):
        self.provider = provider.strip().lower() if provider else "demo"
        self.max_chars_per_line = max(1, int(max_chars_per_line))
        self.max_lines = max(1, int(max_lines))

    def create_captions(
        self,
        topic: str,
        platform: str,
        command: str,
        script: dict[str, Any],
        voice: dict[str, Any],
        video: dict[str, Any],
    ) -> dict[str, Any]:
        topic = str(topic or "").strip()
        platform = str(platform or "youtube").strip().lower()
        command = str(command or "").strip()

        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(
                f"CaptionService does not support platform '{platform}'."
            )

        normalized_script = self._normalize_script(script)
        normalized_voice = self._normalize_voice(voice)
        normalized_video = self._normalize_video(video)

        script_sections = self._extract_script_sections(normalized_script)
        voice_timing = self._extract_voice_timing(normalized_voice)

        if not script_sections:
            raise ValueError(
                "CaptionService could not find usable Script sections."
            )

        if not voice_timing:
            raise ValueError(
                "CaptionService could not find usable voice timing information."
            )

        segments = self._build_caption_segments(
            script_sections=script_sections,
            voice_timing=voice_timing,
        )

        if not segments:
            raise ValueError(
                "CaptionService could not build any caption segments."
            )

        total_duration = self._determine_total_duration(
            voice=normalized_voice,
            video=normalized_video,
            voice_timing=voice_timing,
            segments=segments,
        )

        return {
            "stage": "captions",
            "status": "completed",
            "execution": "caption_service",
            "provider": self.provider,
            "topic": topic,
            "platform": platform,
            "command": command,
            "caption_status": "planned",
            "captions": {
                "format": "srt_vtt_ready",
                "segments": segments,
                "segment_count": len(segments),
                "total_duration_seconds": total_duration,
                "max_chars_per_line": self.max_chars_per_line,
                "max_lines": self.max_lines,
                "style": {
                    "font": "Inter",
                    "position": "bottom_center",
                    "safe_zone": True,
                    "high_readability": True,
                    "outline": True,
                    "shadow": True,
                },
            },
            "render": {
                "status": "pending",
                "format": "embedded_or_sidecar",
                "file_path": None,
                "url": None,
            },
            "production": {
                "ready_for_caption_render": True,
                "ready_for_video_pipeline": True,
                "caption_count": len(segments),
                "duration_seconds": total_duration,
            },
            "quality_controls": [
                "Caption timing derived from completed Voice stage timing.",
                "Caption text derived from completed Script stage narration.",
                "Caption segments have valid start and end timestamps.",
                "Caption timing is normalized to seconds.",
                "No fabricated caption render file is returned.",
                "Demo provider does not claim that captions were rendered.",
            ],
        }

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize_script(self, script: Any) -> dict[str, Any]:
        """
        Normalize the various Script wrapper shapes used by the workflow.
        """

        value = self._parse_dict(script)

        # Handler output:
        # {
        #   "stage": "script",
        #   "script": {
        #       ...
        #   }
        # }
        if isinstance(value.get("script"), dict):
            value = value["script"]

        # Service output can itself contain another script wrapper.
        if isinstance(value.get("script"), dict):
            value = value["script"]

        return value

    def _normalize_voice(self, voice: Any) -> dict[str, Any]:
        """
        Normalize the various Voice wrapper shapes.

        Actual persisted workflow shape is:

        {
            "stage": "voice",
            "voice": {
                "stage": "voice",
                ...
                "voice": {...},
                "narration": {...},
                "timeline": [...]
            }
        }

        Therefore we intentionally unwrap more than one level.
        """

        value = self._parse_dict(voice)

        if isinstance(value.get("voice"), dict):
            value = value["voice"]

        if isinstance(value.get("voice"), dict):
            # Only unwrap again when the nested object looks like another
            # service-level wrapper rather than a voice configuration.
            nested = value["voice"]

            if any(
                key in nested
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
            ):
                value = nested

        return value

    def _normalize_video(self, video: Any) -> dict[str, Any]:
        """
        Normalize Video stage output.
        """

        value = self._parse_dict(video)

        if isinstance(value.get("video"), dict):
            value = value["video"]

        if isinstance(value.get("video"), dict):
            value = value["video"]

        return value

    def _parse_dict(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            import json

            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}

            return parsed if isinstance(parsed, dict) else {}

        return {}

    # ------------------------------------------------------------------
    # Script extraction
    # ------------------------------------------------------------------

    def _extract_script_sections(
        self,
        script: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract narration/script sections from multiple supported shapes.
        """

        candidates = [
            script.get("narration_sections"),
            script.get("sections"),
            script.get("script_sections"),
            script.get("timeline"),
            script.get("narration"),
        ]

        for candidate in candidates:
            sections = self._normalize_section_list(candidate)

            if sections:
                return sections

        # Some Script outputs store narration sections deeper inside
        # a production object.
        production = script.get("production")

        if isinstance(production, dict):
            for key in (
                "narration_sections",
                "sections",
                "script_sections",
                "timeline",
            ):
                sections = self._normalize_section_list(
                    production.get(key)
                )

                if sections:
                    return sections

        return []

    def _normalize_section_list(
        self,
        value: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        result: list[dict[str, Any]] = []

        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue

            text = self._extract_text(item)

            if not text:
                continue

            normalized = dict(item)

            if not normalized.get("index"):
                normalized["index"] = index

            normalized["text"] = text

            result.append(normalized)

        return result

    def _extract_text(self, item: dict[str, Any]) -> str:
        for key in (
            "narration",
            "text",
            "script",
            "content",
            "voice_text",
        ):
            value = item.get(key)

            if isinstance(value, str) and value.strip():
                return " ".join(value.split())

        return ""

    # ------------------------------------------------------------------
    # Voice timing extraction
    # ------------------------------------------------------------------

    def _extract_voice_timing(
        self,
        voice: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract timing from Voice output.

        Supported timing fields include:

        estimated_audio_start
        estimated_audio_end
        estimated_duration_seconds

        as well as generic:

        start
        end
        duration
        start_seconds
        end_seconds
        duration_seconds
        """

        candidates = [
            voice.get("timeline"),
        ]

        audio = voice.get("audio")

        if isinstance(audio, dict):
            candidates.extend(
                [
                    audio.get("timeline"),
                    audio.get("section_outputs"),
                ]
            )

        candidates.extend(
            [
                voice.get("section_outputs"),
                voice.get("voice_timeline"),
                voice.get("timing"),
            ]
        )

        for candidate in candidates:
            timing = self._normalize_timing_list(candidate)

            if timing:
                return timing

        return []

    def _normalize_timing_list(
        self,
        value: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        result: list[dict[str, Any]] = []

        running_start = 0.0

        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue

            start = self._first_number(
                item,
                (
                    "start_seconds",
                    "estimated_audio_start_seconds",
                    "audio_start_seconds",
                    "start",
                ),
            )

            end = self._first_number(
                item,
                (
                    "end_seconds",
                    "estimated_audio_end_seconds",
                    "audio_end_seconds",
                    "end",
                ),
            )

            duration = self._first_number(
                item,
                (
                    "duration_seconds",
                    "estimated_duration_seconds",
                    "audio_duration_seconds",
                    "duration",
                ),
            )

            # The actual Voice output uses:
            #
            # estimated_audio_start: "00:00.00"
            # estimated_audio_end: "00:07.35"
            #
            # Handle those explicitly.
            if start is None:
                start = self._first_time_value(
                    item,
                    (
                        "estimated_audio_start",
                        "audio_start",
                        "start_time",
                    ),
                )

            if end is None:
                end = self._first_time_value(
                    item,
                    (
                        "estimated_audio_end",
                        "audio_end",
                        "end_time",
                    ),
                )

            if duration is None:
                duration = self._first_time_value(
                    item,
                    (
                        "estimated_duration",
                        "audio_duration",
                        "duration_time",
                    ),
                )

            # If no explicit start exists but duration exists, continue
            # from the previous segment.
            if start is None:
                start = running_start

            # If end is missing, derive it from duration.
            if end is None and duration is not None:
                end = start + duration

            # If duration is missing, derive it from start/end.
            if duration is None and end is not None:
                duration = max(0.0, end - start)

            if end is None:
                continue

            if duration is None:
                continue

            if end <= start:
                continue

            result.append(
                {
                    "index": self._safe_int(
                        item.get("index"),
                        index,
                    ),
                    "section": str(
                        item.get("section")
                        or item.get("name")
                        or f"section_{index}"
                    ),
                    "start_seconds": round(float(start), 3),
                    "end_seconds": round(float(end), 3),
                    "duration_seconds": round(float(duration), 3),
                    "text": self._extract_text(item),
                }
            )

            running_start = float(end)

        return result

    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert a value to an integer."""
        if value is None or isinstance(value, bool):
            return default

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return default

            try:
                return int(float(text))
            except (TypeError, ValueError):
                return default

        return default

    def _first_number(
        self,
        item: dict[str, Any],
        keys: tuple[str, ...],
    ) -> float | None:
        for key in keys:
            if key not in item:
                continue

            value = item.get(key)

            if isinstance(value, bool):
                continue

            if isinstance(value, (int, float)):
                return float(value)

            if isinstance(value, str):
                stripped = value.strip()

                if not stripped:
                    continue

                try:
                    return float(stripped)
                except ValueError:
                    continue

        return None

    def _first_time_value(
        self,
        item: dict[str, Any],
        keys: tuple[str, ...],
    ) -> float | None:
        for key in keys:
            if key not in item:
                continue

            value = item.get(key)

            parsed = self._parse_time_seconds(value)

            if parsed is not None:
                return parsed

        return None

    def _parse_time_seconds(self, value: Any) -> float | None:
        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if not isinstance(value, str):
            return None

        text = value.strip()

        if not text:
            return None

        # Plain numeric seconds.
        try:
            return float(text)
        except ValueError:
            pass

        # HH:MM:SS.xx
        parts = text.split(":")

        try:
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])

                return (
                    hours * 3600.0
                    + minutes * 60.0
                    + seconds
                )

            # MM:SS.xx
            if len(parts) == 2:
                minutes = float(parts[0])
                seconds = float(parts[1])

                return minutes * 60.0 + seconds

        except ValueError:
            return None

        return None

    # ------------------------------------------------------------------
    # Caption generation
    # ------------------------------------------------------------------

    def _build_caption_segments(
        self,
        script_sections: list[dict[str, Any]],
        voice_timing: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Pair Script narration with Voice timing.

        Voice timing is authoritative for timestamps.
        Script narration is authoritative for caption text.
        """

        segments: list[dict[str, Any]] = []

        timing_by_index = {
            int(item["index"]): item
            for item in voice_timing
            if item.get("index") is not None
        }

        for position, script_section in enumerate(
            script_sections,
            start=1,
        ):
            script_index = self._safe_int(
                script_section.get("index"),
                position,
            )

            timing = timing_by_index.get(script_index)

            # If the indices do not match, use positional matching.
            if timing is None and position <= len(voice_timing):
                timing = voice_timing[position - 1]

            if timing is None:
                continue

            text = self._extract_text(script_section)

            if not text:
                text = str(timing.get("text") or "").strip()

            if not text:
                continue

            start = float(timing["start_seconds"])
            end = float(timing["end_seconds"])

            caption_chunks = self._split_text_for_captions(text)

            if not caption_chunks:
                continue

            chunk_count = len(caption_chunks)
            total_duration = max(0.01, end - start)

            for chunk_index, chunk in enumerate(caption_chunks):
                chunk_start = start + (
                    total_duration * chunk_index / chunk_count
                )

                chunk_end = start + (
                    total_duration * (chunk_index + 1) / chunk_count
                )

                segments.append(
                    {
                        "id": len(segments) + 1,
                        "section_index": script_index,
                        "section": str(
                            script_section.get("section")
                            or timing.get("section")
                            or f"section_{script_index}"
                        ),
                        "start_seconds": round(chunk_start, 3),
                        "end_seconds": round(chunk_end, 3),
                        "duration_seconds": round(
                            chunk_end - chunk_start,
                            3,
                        ),
                        "text": chunk,
                        "display": {
                            "line_count": self._line_count(chunk),
                            "safe_zone": True,
                            "high_readability": True,
                        },
                    }
                )

        return segments

    def _split_text_for_captions(
        self,
        text: str,
    ) -> list[str]:
        """
        Split narration into readable caption chunks without changing
        the underlying narration content.
        """

        normalized = " ".join(str(text or "").split())

        if not normalized:
            return []

        words = normalized.split()

        chunks: list[str] = []
        current = ""

        for word in words:
            candidate = (
                word
                if not current
                else f"{current} {word}"
            )

            if len(candidate) <= self.max_chars_per_line:
                current = candidate
                continue

            if current:
                chunks.append(current)

            # Handle an unusually long individual word.
            if len(word) > self.max_chars_per_line:
                pieces = self._split_long_word(word)

                if pieces:
                    chunks.extend(pieces[:-1])
                    current = pieces[-1]
                else:
                    current = word
            else:
                current = word

        if current:
            chunks.append(current)

        return chunks

    def _split_long_word(self, word: str) -> list[str]:
        if len(word) <= self.max_chars_per_line:
            return [word]

        result: list[str] = []

        start = 0

        while start < len(word):
            result.append(
                word[
                    start : start + self.max_chars_per_line
                ]
            )

            start += self.max_chars_per_line

        return result

    def _line_count(self, text: str) -> int:
        if len(text) <= self.max_chars_per_line:
            return 1

        return min(
            self.max_lines,
            2,
        )

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    def _determine_total_duration(
        self,
        voice: dict[str, Any],
        video: dict[str, Any],
        voice_timing: list[dict[str, Any]],
        segments: list[dict[str, Any]],
    ) -> float:
        candidates: list[float] = []

        estimated_voice_duration = self._first_number(
            voice,
            (
                "estimated_duration_seconds",
                "duration_seconds",
            ),
        )

        if estimated_voice_duration is not None:
            candidates.append(estimated_voice_duration)

        audio = voice.get("audio")

        if isinstance(audio, dict):
            audio_duration = self._first_number(
                audio,
                (
                    "duration_seconds",
                    "estimated_duration_seconds",
                ),
            )

            if audio_duration is not None:
                candidates.append(audio_duration)

        if voice_timing:
            candidates.append(
                max(
                    float(item["end_seconds"])
                    for item in voice_timing
                )
            )

        if segments:
            candidates.append(
                max(
                    float(item["end_seconds"])
                    for item in segments
                )
            )

        video_duration = self._first_number(
            video,
            (
                "duration_seconds",
                "total_duration_seconds",
            ),
        )

        if video_duration is not None:
            candidates.append(video_duration)

        if not candidates:
            return 0.0

        # Preserve the largest known timeline rather than shortening the
        # caption manifest.
        return round(max(candidates), 3)

    def generate_captions(
        self,
        topic: str,
        platform: str,
        command: str,
        script: dict[str, Any],
        voice: dict[str, Any],
        video: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Backward-compatible public method used by CaptionsStageHandler.

        The canonical implementation is create_captions().
        Keeping this alias preserves the existing handler contract.
        """
        return self.create_captions(
            topic=topic,
            platform=platform,
            command=command,
            script=script,
            voice=voice,
            video=video,
        )


caption_service = CaptionService()
