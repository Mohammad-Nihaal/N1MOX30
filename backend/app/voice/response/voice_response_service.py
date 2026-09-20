from typing import Any, Dict


class VoiceResponseService:
    """
    Natural-language response layer for N1MOX.

    This layer generates the text that will eventually be converted
    into speech by the TTS provider added later.
    """

    def generate_response(
        self,
        intent: str,
        action: str | None = None,
        parameters: Dict[str, Any] | None = None,
        result: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        parameters = parameters or {}
        result = result or {}

        if intent == "create_video":
            topic = parameters.get("topic", "your requested topic")

            message = (
                f"Absolutely. I'll take care of the video workflow for "
                f"{topic}. I'll handle the production stages and keep you "
                "updated as the work progresses."
            )

        elif intent == "workflow_status":
            message = (
                "I'll check the active workflows and tell you what's "
                "currently running."
            )

        elif intent == "completed_work":
            message = (
                "I'll check the completed work and give you the latest "
                "results."
            )

        elif intent == "workflow_failures":
            message = (
                "I'll check for failed workflow steps and identify what "
                "needs attention."
            )

        elif intent == "scheduled_content":
            message = (
                "I'll check your content schedule and tell you what is "
                "coming up."
            )

        elif intent == "help":
            message = (
                "I'm N1MOX. You can ask me to create content, control "
                "workflows, check progress, review failures, or manage "
                "your scheduled content."
            )

        else:
            message = (
                "I'm listening. Tell me what you'd like N1MOX to do."
            )

        return {
            "success": True,
            "text": message,
            "voice_ready": True,
            "emotion": self._select_emotion(intent),
            "speaking_style": "natural",
            "provider": "provider_neutral",
        }

    def _select_emotion(self, intent: str) -> str:
        if intent == "create_video":
            return "confident"

        if intent in {
            "workflow_failures",
            "workflow_status",
        }:
            return "focused"

        if intent == "help":
            return "friendly"

        return "natural"

    def health(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "voice_ready": True,
            "provider": "provider_neutral",
            "mode": "natural_response",
        }
