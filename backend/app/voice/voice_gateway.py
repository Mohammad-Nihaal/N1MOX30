from __future__ import annotations

from typing import Any

from app.models.user import User

from app.voice.actions.voice_action_service import (
    VoiceActionService,
)
from app.voice.responses.natural_response_service import (
    NaturalResponseService,
)
from app.voice.stt.speech_to_text_service import (
    SpeechToTextService,
)
from app.voice.understanding.voice_understanding_service import (
    VoiceUnderstandingService,
)
from app.voice.wakeword.wake_word_service import (
    WakeWordService,
)


class VoiceGateway:
    """
    Unified N1MOX Phase 4 gateway.

    One request moves through:

        wake word
            ↓
        transcript normalization
            ↓
        understanding
            ↓
        action execution
            ↓
        natural response
    """

    def __init__(self, db):
        self.db = db

        self.wake_word = WakeWordService()
        self.stt = SpeechToTextService()
        self.understanding = VoiceUnderstandingService()
        self.actions = VoiceActionService(db)
        self.responses = NaturalResponseService()

    def process_text(
        self,
        *,
        user: User,
        transcript: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        context = context or {}

        wake_detected = self.wake_word.detect(
            transcript
        )

        cleaned = self.wake_word.strip_wake_word(
            transcript
        )

        transcript_result = (
            self.stt.normalize_transcript(
                cleaned
            )
        )

        normalized = transcript_result["text"]

        intent = self.understanding.understand(
            normalized,
            context=context,
        )

        action_result = self.actions.execute(
            user_id=user.id,
            intent=intent,
        )

        response = self.responses.generate(
            intent=intent,
            action_result=action_result,
            creator_context=context,
        )

        return {
            "wake_word_detected": wake_detected,
            "transcript": normalized,
            "stt": transcript_result,
            "intent": intent,
            "action": action_result,
            "response": response,
            "status": "completed",
        }
