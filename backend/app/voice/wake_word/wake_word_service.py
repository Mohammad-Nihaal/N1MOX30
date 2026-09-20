from typing import Any, Dict, List


class WakeWordService:
    """
    Provider-neutral wake-word detection foundation.

    The service accepts text/audio-event representations now and keeps
    the detector abstraction independent from any specific wake-word
    provider. A real microphone/audio detector can be plugged in later.
    """

    DEFAULT_WAKE_WORDS = (
        "hey nimox",
        "hey n1mox",
        "hi nimox",
        "hi n1mox",
    )

    def __init__(self, wake_words: List[str] | None = None):
        self.wake_words = tuple(
            word.strip().lower()
            for word in (wake_words or list(self.DEFAULT_WAKE_WORDS))
            if word.strip()
        )

    def detect(self, text: str) -> Dict[str, Any]:
        normalized = " ".join(text.strip().lower().split())

        for wake_word in self.wake_words:
            if normalized == wake_word:
                return {
                    "detected": True,
                    "wake_word": wake_word,
                    "command": "",
                    "confidence": 1.0,
                }

            prefix = f"{wake_word} "
            if normalized.startswith(prefix):
                command = text.strip()[len(wake_word):].strip()

                return {
                    "detected": True,
                    "wake_word": wake_word,
                    "command": command,
                    "confidence": 1.0,
                }

        return {
            "detected": False,
            "wake_word": None,
            "command": "",
            "confidence": 0.0,
        }

    def is_wake_word(self, text: str) -> bool:
        result = self.detect(text)
        return bool(result["detected"])

    def strip_wake_word(self, text: str) -> str:
        result = self.detect(text)
        return result["command"]

    def get_configuration(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "wake_words": list(self.wake_words),
            "primary_wake_word": "hey n1mox",
            "mode": "provider_neutral",
        }
