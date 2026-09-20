from __future__ import annotations

import re


class WakeWordService:
    """
    N1MOX wake-word detection and normalization.

    Supported phrases:
        Hey N1MOX
        Hi N1MOX
        Hello N1MOX
        N1MOX
    """

    WAKE_WORDS = (
        "hey n1mox",
        "hi n1mox",
        "hello n1mox",
        "n1mox",
    )

    def normalize(self, text: str) -> str:
        text = str(text or "").strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    def detect(self, text: str) -> bool:
        normalized = self.normalize(text)

        if not normalized:
            return False

        return any(
            normalized.startswith(word)
            for word in self.WAKE_WORDS
        )

    def strip_wake_word(self, text: str) -> str:
        normalized = self.normalize(text)

        for word in sorted(
            self.WAKE_WORDS,
            key=len,
            reverse=True,
        ):
            if normalized.startswith(word):
                remaining = normalized[len(word):].strip(" ,.!?")

                if remaining:
                    return remaining

                return ""

        return normalized
