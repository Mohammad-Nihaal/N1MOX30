from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VOICE_STORAGE = PROJECT_ROOT / "storage" / "voice"
VOICE_STORAGE.mkdir(parents=True, exist_ok=True)


COMMAND_PATTERNS = {
    "create_content": [
        r"\bcreate\b",
        r"\bmake\b",
        r"\bgenerate\b",
        r"\bwrite\b",
        r"\bproduce\b",
    ],
    "start_pipeline": [
        r"\bstart\b.*\bworkflow\b",
        r"\brun\b.*\bpipeline\b",
        r"\bstart\b.*\bproduction\b",
        r"\bcreate\b.*\bvideo\b",
    ],
    "check_status": [
        r"\bstatus\b",
        r"\bprogress\b",
        r"\bhow.*doing\b",
        r"\bwhere.*at\b",
        r"\bwhat.*status\b",
    ],
    "schedule": [
        r"\bschedule\b",
        r"\bpost\b.*\blater\b",
        r"\bpublish\b.*\blater\b",
    ],
    "publish": [
        r"\bpublish\b",
        r"\bpost\b.*\bnow\b",
    ],
    "stop": [
        r"\bstop\b",
        r"\bcancel\b",
        r"\babort\b",
    ],
}


def _now() -> str:
    return datetime.utcnow().isoformat()


def normalize_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def extract_topic(text: str) -> str:
    text = normalize_text(text)

    patterns = [
        r"\babout\s+(.+)$",
        r"\bon\s+(.+)$",
        r"\bfor\s+(.+)$",
        r"\btopic\s*[:\-]\s*(.+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            topic = match.group(1).strip(" .!?")
            if topic:
                return topic

    return text.strip(" .!?")


def understand_command(text: str) -> dict:
    normalized = normalize_text(text)
    lowered = normalized.lower()

    intent = "unknown"
    confidence = 0.35

    for candidate, patterns in COMMAND_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                intent = candidate
                confidence = 0.90
                break
        if intent != "unknown":
            break

    topic = extract_topic(normalized)

    if intent == "check_status":
        topic = ""

    return {
        "command_id": f"voice_{uuid.uuid4().hex}",
        "text": normalized,
        "intent": intent,
        "confidence": confidence,
        "topic": topic,
        "created_at": _now(),
    }


def transcribe_input(text: str) -> dict:
    """
    Provider-neutral STT boundary.

    Real microphone/browser STT can call this boundary later.
    For now, text input is treated as the transcript.
    """
    transcript = normalize_text(text)

    return {
        "status": "completed",
        "provider": "text_fallback",
        "transcript": transcript,
        "created_at": _now(),
    }


def execute_voice_command(
    user_id: int,
    text: str,
    workflow_state: dict | None = None,
) -> dict:
    transcript = transcribe_input(text)
    command = understand_command(transcript["transcript"])

    state = workflow_state or {}

    if command["intent"] == "create_content":
        action = "create_content"
        message = (
            f"I understood. I'll prepare creator content"
            + (f" about {command['topic']}." if command["topic"] else ".")
        )

    elif command["intent"] == "start_pipeline":
        action = "start_pipeline"
        message = (
            f"I'll start the creator production pipeline"
            + (f" for {command['topic']}." if command["topic"] else ".")
        )

    elif command["intent"] == "check_status":
        action = "check_status"
        completed = state.get("completed_stages", [])
        total = state.get("total_stages", 13)
        message = (
            f"The workflow has completed {len(completed)} "
            f"of {total} stages."
        )

    elif command["intent"] == "schedule":
        action = "schedule"
        message = "I understood the scheduling request."

    elif command["intent"] == "publish":
        action = "publish"
        message = (
            "I understood the publishing request. "
            "Publishing remains subject to the connected account and authorization."
        )

    elif command["intent"] == "stop":
        action = "stop"
        message = "I understood the stop request."

    else:
        action = "clarify"
        message = (
            "I didn't fully understand that command. "
            "Try asking me to create content, start the pipeline, "
            "check status, schedule, publish, or stop."
        )

    return {
        "status": "completed",
        "user_id": user_id,
        "transcript": transcript,
        "command": command,
        "action": action,
        "message": message,
        "voice_response": {
            "status": "text_ready",
            "text": message,
        },
        "workflow_state": state,
        "created_at": _now(),
    }


def save_voice_command(result: dict) -> str:
    path = VOICE_STORAGE / f"{result['command']['command_id']}.json"

    path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return str(path)
def execute_voice_action(
    user_id: int,
    command_result: dict,
) -> dict:
    """
    Execute an understood N1MOX voice action against the
    creator production system.
    """

    action = command_result.get("action")
    topic = (
        command_result
        .get("command", {})
        .get("topic")
        or "AI creator automation"
    )

    if action in ("create_content", "start_pipeline"):

        try:
            from app.services.production.engine import (
                create_job,
                execute_extended_production,
            )

            job = create_job(
                user_id=user_id,
                topic=topic,
            )

            result = execute_extended_production(job)

            return {
                "status": "completed",
                "action": action,
                "execution": result,
                "message": (
                    f"N1MOX completed the production workflow "
                    f"for {topic}."
                ),
            }

        except Exception as exc:

            return {
                "status": "fallback",
                "action": action,
                "message": (
                    f"N1MOX accepted the production request for "
                    f"{topic}, but execution needs attention."
                ),
                "error": str(exc),
            }

    if action == "check_status":

        state = command_result.get("workflow_state", {})

        completed = state.get("completed_stages", [])
        total = state.get("total_stages", 13)

        return {
            "status": "completed",
            "action": action,
            "completed": len(completed),
            "total": total,
            "progress_percent": (
                round((len(completed) / total) * 100, 2)
                if total
                else 0
            ),
            "message": (
                f"N1MOX workflow progress is "
                f"{len(completed)} of {total} stages."
            ),
        }

    if action == "schedule":

        try:
            from app.services.production.engine import (
                create_job,
                schedule_production,
            )

            job = create_job(
                user_id=user_id,
                topic=topic,
            )

            scheduled = schedule_production(job)

            return {
                "status": "completed",
                "action": action,
                "execution": scheduled,
                "message": "The content has been placed into the N1MOX scheduling queue.",
            }

        except Exception as exc:

            return {
                "status": "fallback",
                "action": action,
                "message": "Scheduling was understood but could not be completed.",
                "error": str(exc),
            }

    if action == "publish":

        return {
            "status": "authorization_required",
            "action": action,
            "message": (
                "Publishing was understood. "
                "A connected creator account and publishing authorization "
                "are required before an external upload."
            ),
        }

    if action == "stop":

        return {
            "status": "completed",
            "action": action,
            "message": "N1MOX received the stop command.",
        }

    return {
        "status": "needs_clarification",
        "action": "clarify",
        "message": "N1MOX needs a clearer command.",
    }