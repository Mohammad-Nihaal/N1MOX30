from __future__ import annotations

import re
from typing import Any


class SpeechToTextService:
    """
    Provider-neutral speech-to-text normalization layer.

    The browser can perform STT through Web Speech API.
    Future native/cloud STT providers can plug into this layer
    without changing the N1MOX voice gateway.
    """

    def normalize_transcript(
        self,
        transcript: str,
        *,
        language: str = "en-IN",
        confidence: float | None = None,
    ) -> dict[str, Any]:

        text = str(transcript or "").strip()
        text = re.sub(r"\s+", " ", text)

        return {
            "text": text,
            "language": language,
            "confidence": confidence,
            "provider": "browser_or_external",
            "status": "completed" if text else "empty",
        }

    def from_browser_result(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        transcript = str(
            result.get("transcript", "")
        ).strip()

        confidence = result.get("confidence")

        return self.normalize_transcript(
            transcript,
            language=str(
                result.get("language", "en-IN")
            ),
            confidence=confidence,
        )
