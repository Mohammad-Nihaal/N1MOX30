from typing import Any, Dict


class VoiceAssistantService:
    """
    Provider-neutral foundation for the N1MOX voice assistant.

    Step 28 establishes the assistant layer.
    Speech-to-text, wake word detection, LLM understanding,
    voice synthesis and workflow execution are added by Steps 29-34.
    """

    def understand(
        self,
        transcript: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        text = transcript.strip()
        normalized = text.lower()

        intent = "conversation"
        action = None
        parameters: Dict[str, Any] = {}
        requires_confirmation = False

        if any(
            phrase in normalized
            for phrase in [
                "create me a video",
                "create a video",
                "make me a video",
                "make a video",
            ]
        ):
            intent = "create_video"
            action = "create_video"

            topic = text

            for phrase in [
                "create me a video about",
                "create a video about",
                "make me a video about",
                "make a video about",
            ]:
                if phrase in normalized:
                    index = normalized.find(phrase)
                    topic = text[index + len(phrase):].strip()
                    break

            parameters["topic"] = topic
            requires_confirmation = False

        elif any(
            phrase in normalized
            for phrase in [
                "what is running",
                "what's running",
                "what are you running",
                "show running workflows",
            ]
        ):
            intent = "workflow_status"
            action = "workflow_status"

        elif any(
            phrase in normalized
            for phrase in [
                "what is completed",
                "what's completed",
                "what have you completed",
                "show completed",
            ]
        ):
            intent = "completed_work"
            action = "completed_work"

        elif any(
            phrase in normalized
            for phrase in [
                "what failed",
                "what has failed",
                "show failures",
            ]
        ):
            intent = "workflow_failures"
            action = "workflow_failures"

        elif any(
            phrase in normalized
            for phrase in [
                "what is scheduled",
                "what's scheduled",
                "show scheduled",
                "show my schedule",
            ]
        ):
            intent = "scheduled_content"
            action = "scheduled_content"

        elif any(
            phrase in normalized
            for phrase in [
                "help",
                "what can you do",
                "what can you do for me",
            ]
        ):
            intent = "help"

        return {
            "intent": intent,
            "action": action,
            "parameters": parameters,
            "requires_confirmation": requires_confirmation,
        }

    def respond(
        self,
        intent: str,
        action: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> str:

        parameters = parameters or {}

        if intent == "create_video":
            topic = parameters.get("topic", "your requested topic")
            return (
                f"Got it. I can create the video workflow for {topic}. "
                "N1MOX will handle the production pipeline."
            )

        if intent == "workflow_status":
            return "I can report the workflows currently running and their progress."

        if intent == "completed_work":
            return "I can report the work N1MOX has completed."

        if intent == "workflow_failures":
            return "I can report failed workflow steps and recovery status."

        if intent == "scheduled_content":
            return "I can report your scheduled content and upcoming publishing tasks."

        if intent == "help":
            return (
                "You can ask me to create content, check workflow progress, "
                "review completed work, inspect failures, or check scheduled content."
            )

        return "I'm ready. Tell me what you want N1MOX to do."

    def process(
        self,
        transcript: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        understanding = self.understand(transcript, context)

        message = self.respond(
            understanding["intent"],
            understanding["action"],
            understanding["parameters"],
        )

        suggestions = []

        if understanding["intent"] == "conversation":
            suggestions = [
                "Create a video",
                "Show running workflows",
                "Show completed work",
                "Show scheduled content",
            ]

        return {
            "success": True,
            "message": message,
            "intent": understanding["intent"],
            "action": understanding["action"],
            "parameters": understanding["parameters"],
            "requires_confirmation": understanding["requires_confirmation"],
            "assistant_state": "ready",
            "suggestions": suggestions,
        }
