from abc import ABC, abstractmethod
from typing import Any, Dict


class STTProvider(ABC):
    """Provider interface for speech-to-text engines."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        raise NotImplementedError


class DemoSTTProvider(STTProvider):
    """
    Development provider.

    Real cloud/local STT providers can implement the same interface
    without changing the rest of N1MOX.
    """

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        return {
            "success": True,
            "text": "",
            "language": "en",
            "provider": "demo",
            "confidence": 0.0,
            "audio_path": audio_path,
        }


class STTService:
    """Provider-neutral Speech-to-Text service."""

    def __init__(self, provider: STTProvider | None = None):
        self.provider = provider or DemoSTTProvider()

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        if not audio_path or not audio_path.strip():
            return {
                "success": False,
                "text": "",
                "language": None,
                "provider": "none",
                "confidence": 0.0,
                "error": "Audio path is required.",
            }

        try:
            result = self.provider.transcribe(audio_path)

            return {
                "success": bool(result.get("success", True)),
                "text": result.get("text", ""),
                "language": result.get("language"),
                "provider": result.get("provider", "unknown"),
                "confidence": float(result.get("confidence", 0.0)),
                "audio_path": audio_path,
            }

        except Exception as exc:
            return {
                "success": False,
                "text": "",
                "language": None,
                "provider": "unknown",
                "confidence": 0.0,
                "audio_path": audio_path,
                "error": str(exc),
            }

    def provider_name(self) -> str:
        return self.provider.__class__.__name__

    def health(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "provider": self.provider_name(),
            "mode": "provider_neutral",
        }
