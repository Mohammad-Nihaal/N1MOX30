import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.subtitles.base import (
    BaseSubtitleProvider,
    SubtitleSegment,
)


class SubtitleService:
    """
    N1MOX30 subtitle orchestration service.

    Provides:

    - intelligent text segmentation
    - deterministic timing
    - SRT generation
    - WebVTT generation
    - timeline-ready caption clips
    - styling metadata
    """

    def __init__(
        self,
        provider: BaseSubtitleProvider | None = None,
    ):
        self.provider = provider

    # ================================================================
    # GENERATION
    # ================================================================

    def generate(
        self,
        text: str,
        duration_seconds: float,
    ) -> list[SubtitleSegment]:

        cleaned_text = self.clean_text(
            text,
        )

        if not cleaned_text:
            return []

        if duration_seconds <= 0:
            duration_seconds = 1.0

        if self.provider is not None:

            return self.provider.generate(
                text=cleaned_text,
                duration_seconds=duration_seconds,
            )

        return self._generate_deterministic(
            text=cleaned_text,
            duration_seconds=duration_seconds,
        )

    # ================================================================
    # DETERMINISTIC TIMING
    # ================================================================

    def _generate_deterministic(
        self,
        text: str,
        duration_seconds: float,
    ) -> list[SubtitleSegment]:

        sentences = self._split_sentences(
            text,
        )

        if not sentences:
            sentences = [
                text,
            ]

        total_words = sum(
            len(
                sentence.split()
            )
            for sentence in sentences
        )

        if total_words <= 0:
            return []

        segments: list[
            SubtitleSegment
        ] = []

        current_time = 0.0

        for sentence in sentences:

            word_count = len(
                sentence.split()
            )

            proportion = (
                word_count
                / total_words
            )

            segment_duration = (
                duration_seconds
                * proportion
            )

            start_time = current_time

            end_time = min(
                duration_seconds,
                current_time
                + segment_duration,
            )

            chunks = self._split_for_readability(
                sentence,
            )

            if len(chunks) == 1:

                segments.append(
                    SubtitleSegment(
                        id=str(uuid4()),
                        start_time=round(
                            start_time,
                            3,
                        ),
                        end_time=round(
                            end_time,
                            3,
                        ),
                        text=sentence.strip(),
                        metadata={
                            "timing": "deterministic",
                        },
                    )
                )

            else:

                chunk_word_count = sum(
                    len(
                        chunk.split()
                    )
                    for chunk in chunks
                )

                chunk_cursor = start_time

                for chunk in chunks:

                    chunk_words = len(
                        chunk.split()
                    )

                    chunk_duration = (
                        segment_duration
                        * (
                            chunk_words
                            / chunk_word_count
                        )
                    )

                    chunk_end = min(
                        end_time,
                        chunk_cursor
                        + chunk_duration,
                    )

                    segments.append(
                        SubtitleSegment(
                            id=str(uuid4()),
                            start_time=round(
                                chunk_cursor,
                                3,
                            ),
                            end_time=round(
                                chunk_end,
                                3,
                            ),
                            text=chunk.strip(),
                            metadata={
                                "timing": (
                                    "deterministic"
                                ),
                            },
                        )
                    )

                    chunk_cursor = chunk_end

            current_time = end_time

        return self._normalize_segments(
            segments,
            duration_seconds,
        )

    # ================================================================
    # SENTENCE SPLITTING
    # ================================================================

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:

        parts = re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    # ================================================================
    # READABILITY
    # ================================================================

    @staticmethod
    def _split_for_readability(
        sentence: str,
        max_words: int = 12,
    ) -> list[str]:

        words = sentence.split()

        if len(words) <= max_words:
            return [
                sentence,
            ]

        chunks: list[str] = []

        current: list[str] = []

        for word in words:

            current.append(
                word,
            )

            if len(current) >= max_words:

                chunks.append(
                    " ".join(current),
                )

                current = []

        if current:
            chunks.append(
                " ".join(current),
            )

        return chunks

    # ================================================================
    # NORMALIZATION
    # ================================================================

    @staticmethod
    def _normalize_segments(
        segments: list[SubtitleSegment],
        duration_seconds: float,
    ) -> list[SubtitleSegment]:

        normalized: list[
            SubtitleSegment
        ] = []

        for segment in segments:

            start = max(
                0.0,
                min(
                    segment.start_time,
                    duration_seconds,
                ),
            )

            end = max(
                start,
                min(
                    segment.end_time,
                    duration_seconds,
                ),
            )

            if end <= start:
                continue

            normalized.append(
                SubtitleSegment(
                    id=segment.id,
                    start_time=round(
                        start,
                        3,
                    ),
                    end_time=round(
                        end,
                        3,
                    ),
                    text=segment.text.strip(),
                    confidence=segment.confidence,
                    words=segment.words,
                    metadata=segment.metadata,
                )
            )

        return normalized

    # ================================================================
    # CLEAN TEXT
    # ================================================================

    @staticmethod
    def clean_text(
        text: str,
    ) -> str:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ================================================================
    # SRT
    # ================================================================

    def to_srt(
        self,
        segments: list[SubtitleSegment],
    ) -> str:

        blocks: list[str] = []

        for index, segment in enumerate(
            segments,
            start=1,
        ):

            blocks.append(
                "\n".join(
                    [
                        str(index),
                        (
                            f"{self._format_srt_time(segment.start_time)}"
                            " --> "
                            f"{self._format_srt_time(segment.end_time)}"
                        ),
                        segment.text,
                    ]
                )
            )

        if not blocks:
            return ""

        return (
            "\n\n".join(
                blocks,
            )
            + "\n"
        )

    # ================================================================
    # WEBVTT
    # ================================================================

    def to_webvtt(
        self,
        segments: list[SubtitleSegment],
    ) -> str:

        lines = [
            "WEBVTT",
            "",
        ]

        for segment in segments:

            lines.extend(
                [
                    (
                        f"{self._format_vtt_time(segment.start_time)}"
                        " --> "
                        f"{self._format_vtt_time(segment.end_time)}"
                    ),
                    segment.text,
                    "",
                ]
            )

        return "\n".join(
            lines,
        )

    # ================================================================
    # TIMELINE CLIPS
    # ================================================================

    def to_timeline_clips(
        self,
        segments: list[SubtitleSegment],
        track_id: str,
        style: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        style = style or self.default_style()

        clips: list[dict[str, Any]] = []

        for index, segment in enumerate(
            segments,
        ):

            clips.append(
                {
                    "id": str(uuid4()),
                    "track_id": track_id,
                    "media_asset_id": None,
                    "clip_type": "caption",
                    "name": (
                        f"Caption {index + 1}"
                    ),
                    "start_time": (
                        segment.start_time
                    ),
                    "end_time": (
                        segment.end_time
                    ),
                    "source_start": 0.0,
                    "source_end": None,
                    "layer": style.get(
                        "layer",
                        100,
                    ),
                    "volume": 1.0,
                    "opacity": 1.0,
                    "x": style.get(
                        "x",
                        0.5,
                    ),
                    "y": style.get(
                        "y",
                        0.85,
                    ),
                    "width": style.get(
                        "width",
                        0.9,
                    ),
                    "height": style.get(
                        "height",
                        0.15,
                    ),
                    "rotation": 0.0,
                    "playback_rate": 1.0,
                    "text": segment.text,
                    "metadata": {
                        "subtitle_id": segment.id,
                        "style": style,
                        "confidence": (
                            segment.confidence
                        ),
                        "words": segment.words,
                    },
                }
            )

        return clips

    # ================================================================
    # DEFAULT STYLE
    # ================================================================

    @staticmethod
    def default_style() -> dict[str, Any]:

        return {
            "font_family": "Arial",
            "font_size": 54,
            "font_weight": 700,
            "text_color": "#FFFFFF",
            "background_color": "#000000",
            "background_opacity": 0.65,
            "outline": True,
            "outline_width": 3,
            "alignment": "center",
            "x": 0.5,
            "y": 0.85,
            "width": 0.9,
            "height": 0.15,
            "layer": 100,
        }

    # ================================================================
    # WRITE FILE
    # ================================================================

    @staticmethod
    def write_file(
        content: str,
        path: str | Path,
    ) -> str:

        destination = Path(
            path,
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_text(
            content,
            encoding="utf-8",
        )

        return str(destination)

    # ================================================================
    # TIME FORMATTING
    # ================================================================

    @staticmethod
    def _format_srt_time(
        seconds: float,
    ) -> str:

        total_ms = max(
            0,
            int(
                round(
                    seconds * 1000,
                )
            ),
        )

        hours = total_ms // 3_600_000

        remainder = (
            total_ms
            % 3_600_000
        )

        minutes = remainder // 60_000

        remainder %= 60_000

        secs = remainder // 1000

        milliseconds = (
            remainder
            % 1000
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d},"
            f"{milliseconds:03d}"
        )

    @staticmethod
    def _format_vtt_time(
        seconds: float,
    ) -> str:

        total_ms = max(
            0,
            int(
                round(
                    seconds * 1000,
                )
            ),
        )

        hours = total_ms // 3_600_000

        remainder = (
            total_ms
            % 3_600_000
        )

        minutes = remainder // 60_000

        remainder %= 60_000

        secs = remainder // 1000

        milliseconds = (
            remainder
            % 1000
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d}."
            f"{milliseconds:03d}"
        )