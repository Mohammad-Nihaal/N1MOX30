from __future__ import annotations

from typing import Any

from app.services.ai.provider_router import ai_provider_router


class NaturalResponseService:

    def generate(
        self,
        *,
        intent: dict[str, Any],
        action_result: dict[str, Any] | None = None,
        creator_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        action_result = action_result or {}

        intent_name = intent.get(
            "intent",
            "general_query",
        )

        message = action_result.get(
            "message"
        )

        if message:
            return {
                "text": message,
                "provider": "deterministic",
            }

        responses = {
            "pause_workflow":
                "The workflow has been paused.",

            "resume_workflow":
                "The workflow has been resumed.",

            "cancel_workflow":
                "The workflow has been cancelled.",

            "retry_workflow":
                "The workflow retry has started.",

            "workflow_status":
                "I'll check the workflow status.",

            "completed_work":
                "I'll check your completed work.",

            "workflow_errors":
                "I'll check your workflow errors.",

            "scheduled_content":
                "I'll check your scheduled content.",

            "help":
                (
                    "I'm N1MOX. I can create content, "
                    "control workflows, check progress, "
                    "retry failures, and manage your "
                    "creator automation."
                ),
        }

        if intent_name in responses:
            return {
                "text": responses[intent_name],
                "provider": "deterministic",
            }

        query = (
            intent.get("entities", {})
            .get("query", "")
        )

        if query:
            try:
                result = ai_provider_router.generate(
                    prompt=f"""
You are N1MOX30, a concise creator AI assistant.

Respond naturally to:

{query}

Be direct and conversational.
Do not claim an action happened unless
the action result confirms it.
""",
                    temperature=0.6,
                )

                text = str(
                    result.get("text", "")
                ).strip()

                if text:
                    return {
                        "text": text,
                        "provider": result.get(
                            "provider",
                            "ai",
                        ),
                    }

            except Exception:
                pass

        return {
            "text": (
                "I understand your request. "
                "Tell me what you want me to do next."
            ),
            "provider": "fallback",
        }
