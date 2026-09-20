from __future__ import annotations

import re
from typing import Any

from app.services.ai.provider_router import ai_provider_router


class VoiceUnderstandingService:

    def understand(
        self,
        text: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        context = context or {}

        normalized = re.sub(
            r"\s+",
            " ",
            str(text or "").strip(),
        )

        lower = normalized.lower()

        if not normalized:
            return {
                "intent": "empty",
                "confidence": 1.0,
                "entities": {},
                "raw_text": normalized,
            }

        workflow_id = self._extract_workflow_id(
            normalized
        )

        # CREATE
        if any(
            phrase in lower
            for phrase in (
                "create a video",
                "create me a video",
                "make a video",
                "make me a video",
                "generate a video",
                "generate me a video",
                "create content",
                "make content",
            )
        ):
            topic = normalized

            match = re.search(
                r"(?:about|on|regarding|for)\s+(.+)$",
                normalized,
                flags=re.IGNORECASE,
            )

            if match:
                topic = match.group(1).strip()

            topic = re.sub(
                r"[.!?]+$",
                "",
                topic,
            ).strip()

            return {
                "intent": "create_content",
                "confidence": 0.97,
                "entities": {
                    "topic": topic,
                    "platform": self._extract_platform(
                        lower
                    ),
                },
                "raw_text": normalized,
            }

        # STATUS
        if any(
            phrase in lower
            for phrase in (
                "what is running",
                "what's running",
                "what are you running",
                "workflow status",
                "workflow statuses",
                "what is in progress",
                "what's in progress",
                "active workflows",
                "show active workflows",
            )
        ):
            return {
                "intent": "workflow_status",
                "confidence": 0.97,
                "entities": {
                    "workflow_id": workflow_id,
                },
                "raw_text": normalized,
            }

        # COMPLETED
        if any(
            phrase in lower
            for phrase in (
                "what did you complete",
                "what have you completed",
                "completed work",
                "show completed work",
                "what have you finished",
                "what did you finish",
            )
        ):
            return {
                "intent": "completed_work",
                "confidence": 0.96,
                "entities": {},
                "raw_text": normalized,
            }

        # ERRORS
        if any(
            phrase in lower
            for phrase in (
                "any errors",
                "any failures",
                "workflow errors",
                "show errors",
                "show failures",
                "what failed",
                "what has failed",
                "did anything fail",
            )
        ):
            return {
                "intent": "workflow_errors",
                "confidence": 0.96,
                "entities": {},
                "raw_text": normalized,
            }

        # SCHEDULE
        if any(
            phrase in lower
            for phrase in (
                "what is scheduled",
                "what's scheduled",
                "show my schedule",
                "show scheduled content",
                "scheduled videos",
                "publishing queue",
                "what am i posting",
            )
        ):
            return {
                "intent": "scheduled_content",
                "confidence": 0.95,
                "entities": {},
                "raw_text": normalized,
            }

        # PAUSE
        if any(
            phrase in lower
            for phrase in (
                "pause workflow",
                "pause the workflow",
                "pause this workflow",
                "pause it",
                "hold workflow",
                "hold the workflow",
            )
        ):
            return {
                "intent": "pause_workflow",
                "confidence": 0.98,
                "entities": {
                    "workflow_id": workflow_id,
                },
                "raw_text": normalized,
            }

        # RESUME
        if any(
            phrase in lower
            for phrase in (
                "resume workflow",
                "resume the workflow",
                "resume this workflow",
                "resume it",
                "continue workflow",
                "continue the workflow",
                "continue it",
            )
        ):
            return {
                "intent": "resume_workflow",
                "confidence": 0.98,
                "entities": {
                    "workflow_id": workflow_id,
                },
                "raw_text": normalized,
            }

        # CANCEL
        if any(
            phrase in lower
            for phrase in (
                "cancel workflow",
                "cancel the workflow",
                "cancel this workflow",
                "cancel it",
                "stop workflow",
                "stop the workflow",
            )
        ):
            return {
                "intent": "cancel_workflow",
                "confidence": 0.98,
                "entities": {
                    "workflow_id": workflow_id,
                },
                "raw_text": normalized,
            }

        # RETRY
        if any(
            phrase in lower
            for phrase in (
                "retry workflow",
                "retry the workflow",
                "retry this workflow",
                "retry it",
                "rerun workflow",
                "rerun the workflow",
                "run it again",
            )
        ):
            return {
                "intent": "retry_workflow",
                "confidence": 0.98,
                "entities": {
                    "workflow_id": workflow_id,
                },
                "raw_text": normalized,
            }

        # HELP
        if lower in (
            "help",
            "what can you do",
            "what can you do for me",
            "how can you help me",
        ):
            return {
                "intent": "help",
                "confidence": 1.0,
                "entities": {},
                "raw_text": normalized,
            }

        # AI FALLBACK
        try:
            result = ai_provider_router.generate(
                prompt=f"""
You are the N1MOX30 voice command understanding layer.

Classify this creator request into exactly one intent:

create_content
workflow_status
completed_work
workflow_errors
scheduled_content
pause_workflow
resume_workflow
cancel_workflow
retry_workflow
help
general_query

Creator request:
{normalized}

Return concise JSON containing:
intent
confidence
entities

Never claim an action was executed.
""",
                temperature=0.1,
            )

            ai_text = str(
                result.get("text", "")
            ).strip()

            if ai_text:
                return {
                    "intent": "general_query",
                    "confidence": 0.70,
                    "entities": {
                        "query": normalized,
                        "ai_interpretation": ai_text,
                    },
                    "raw_text": normalized,
                }

        except Exception:
            pass

        return {
            "intent": "general_query",
            "confidence": 0.50,
            "entities": {
                "query": normalized,
            },
            "raw_text": normalized,
        }

    @staticmethod
    def _extract_platform(
        text: str,
    ) -> str:

        if "instagram" in text or "reel" in text:
            return "instagram"

        if "short" in text or "shorts" in text:
            return "youtube_shorts"

        return "youtube"

    @staticmethod
    def _extract_workflow_id(
        text: str,
    ) -> str | None:

        match = re.search(
            r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(0)

        return None
