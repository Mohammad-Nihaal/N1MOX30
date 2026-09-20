from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.assistant_conversation import (
    AssistantConversation,
)
from app.models.creator_memory import CreatorMemory
from app.models.creator_profile import CreatorProfile
from app.services.ai_service import (
    generate_ai_text,
)


# =================================================
# PERFORMANCE SETTINGS
# =================================================

MAX_MEMORY_CONTEXT = 5
MAX_CONVERSATION_CONTEXT = 4
MAX_MESSAGE_LENGTH = 4000
MAX_MEMORY_VALUE_LENGTH = 500
MAX_CONVERSATION_MESSAGE_LENGTH = 700
MAX_CONVERSATION_RESPONSE_LENGTH = 1000


# =================================================
# TEXT HELPERS
# =================================================


def compact_text(
    value: Any,
    max_length: int,
) -> str:
    """
    Convert a value to compact text.

    Limits large database values before sending them
    to the AI provider.
    """

    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    text = " ".join(
        text.split()
    )

    if len(text) <= max_length:
        return text

    return (
        text[:max_length].rstrip()
        + "..."
    )


# =================================================
# CONTEXT HELPERS
# =================================================


def get_creator_profile_context(
    *,
    db: Session,
    user_id: str,
) -> dict[str, Any]:
    """
    Get only the creator profile information needed
    for fast personalized responses.
    """

    profile = (
        db.query(CreatorProfile)
        .filter(
            CreatorProfile.user_id == user_id
        )
        .first()
    )

    if not profile:
        return {}

    return {
        "creator_name": compact_text(
            profile.creator_name,
            120,
        ),
        "niche": compact_text(
            profile.niche,
            200,
        ),
        "target_audience": compact_text(
            profile.target_audience,
            400,
        ),
        "creator_goals": compact_text(
            profile.creator_goals,
            400,
        ),
        "preferred_platforms": compact_text(
            profile.preferred_platforms,
            250,
        ),
        "content_style": compact_text(
            profile.content_style,
            250,
        ),
        "preferred_tone": compact_text(
            profile.preferred_tone,
            150,
        ),
    }


def get_creator_memory_context(
    *,
    db: Session,
    user_id: str,
    limit: int = MAX_MEMORY_CONTEXT,
) -> list[dict[str, Any]]:
    """
    Get a small set of recent creator memories.

    Keeping memory context limited improves AI speed
    and reduces unnecessary prompt size.
    """

    memories = (
        db.query(CreatorMemory)
        .filter(
            CreatorMemory.user_id == user_id
        )
        .order_by(
            CreatorMemory.importance.desc(),
            CreatorMemory.updated_at.desc(),
        )
        .limit(limit)
        .all()
    )

    results: list[dict[str, Any]] = []

    for memory in memories:

        memory_key = compact_text(
            memory.memory_key,
            120,
        )

        memory_value = compact_text(
            memory.memory_value,
            MAX_MEMORY_VALUE_LENGTH,
        )

        if not memory_key or not memory_value:
            continue

        results.append(
            {
                "memory_type": (
                    compact_text(
                        memory.memory_type,
                        80,
                    )
                ),
                "memory_key": memory_key,
                "memory_value": memory_value,
                "importance": memory.importance,
            }
        )

    return results


def get_recent_conversation_context(
    *,
    db: Session,
    user_id: str,
    limit: int = MAX_CONVERSATION_CONTEXT,
) -> list[dict[str, str]]:
    """
    Get only recent conversation context.

    Large conversation histories can significantly
    increase AI response time.
    """

    conversations = (
        db.query(AssistantConversation)
        .filter(
            AssistantConversation.user_id == user_id
        )
        .order_by(
            AssistantConversation.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    conversations.reverse()

    results: list[dict[str, str]] = []

    for conversation in conversations:

        user_message = compact_text(
            conversation.message,
            MAX_CONVERSATION_MESSAGE_LENGTH,
        )

        assistant_response = compact_text(
            conversation.response,
            MAX_CONVERSATION_RESPONSE_LENGTH,
        )

        if not user_message:
            continue

        results.append(
            {
                "user": user_message,
                "assistant": assistant_response,
            }
        )

    return results


# =================================================
# ACTION DETECTION
# =================================================


def detect_assistant_action(
    message: str,
) -> dict[str, str | None]:
    """
    Detect creator workflow intent.

    This runs locally and adds almost no delay.
    """

    text = message.lower().strip()

    action_keywords = {
        "generate_content": [
            "generate content",
            "create content",
            "make content",
            "write a script",
            "create a script",
            "generate a script",
            "create video",
            "make a video",
        ],
        "analyze_analytics": [
            "analyze analytics",
            "check analytics",
            "analyze my channel",
            "check my performance",
            "analyze performance",
            "check views",
        ],
        "research_topic": [
            "research",
            "research this topic",
            "find trends",
            "analyze trends",
            "find content ideas",
            "content research",
        ],
        "create_schedule": [
            "schedule",
            "plan my content",
            "create a schedule",
            "plan my week",
            "plan my week",
            "weekly plan",
            "content plan",
        ],
        "run_automation": [
            "run automation",
            "start automation",
            "run workflow",
            "execute workflow",
            "execute automation",
        ],
    }

    for action_type, keywords in (
        action_keywords.items()
    ):

        if any(
            keyword in text
            for keyword in keywords
        ):

            return {
                "action_type": action_type,
                "action_status": "detected",
            }

    return {
        "action_type": None,
        "action_status": None,
    }


# =================================================
# CONTEXT FORMATTERS
# =================================================


def format_memory_context(
    memories: list[dict[str, Any]],
) -> str:
    """
    Format memory into compact AI context.
    """

    if not memories:
        return "None"

    lines: list[str] = []

    for memory in memories:

        lines.append(
            f"- {memory['memory_key']}: "
            f"{memory['memory_value']}"
        )

    return "\n".join(lines)


def format_conversation_context(
    conversations: list[dict[str, str]],
) -> str:
    """
    Format recent conversations into compact context.
    """

    if not conversations:
        return "None"

    lines: list[str] = []

    for item in conversations:

        user_message = item.get(
            "user",
            "",
        )

        assistant_response = item.get(
            "assistant",
            "",
        )

        lines.append(
            f"User: {user_message}"
        )

        if assistant_response:

            lines.append(
                f"Assistant: "
                f"{assistant_response}"
            )

    return "\n".join(lines)


# =================================================
# DETERMINISTIC FALLBACK
# =================================================


def generate_assistant_fallback(
    *,
    message: str,
    profile_context: dict[str, Any],
    action_data: dict[str, str | None],
) -> str:
    """
    Generate a fast fallback response when an external
    AI provider is unavailable.
    """

    creator_name = (
        profile_context.get("creator_name")
        or "Creator"
    )

    niche = (
        profile_context.get("niche")
        or "your content"
    )

    action_type = action_data.get(
        "action_type"
    )

    if action_type == "generate_content":

        return (
            f"Got it, {creator_name}. "
            f"You want to create content for {niche}. "
            f"I can help you develop the idea, title, "
            f"script, caption, and publishing strategy."
        )

    if action_type == "analyze_analytics":

        return (
            f"Got it, {creator_name}. "
            f"You want to analyze your creator "
            f"performance. I can help identify growth "
            f"patterns, strong content, and areas to "
            f"improve."
        )

    if action_type == "research_topic":

        return (
            f"Got it, {creator_name}. "
            f"You want creator research and trend "
            f"intelligence. I can help identify useful "
            f"topics, opportunities, and content angles."
        )

    if action_type == "create_schedule":

        return (
            f"Got it, {creator_name}. "
            f"You want to plan your content schedule. "
            f"I can help organize your week around your "
            f"creator goals and content priorities."
        )

    if action_type == "run_automation":

        return (
            f"Got it, {creator_name}. "
            f"You want to run a creator workflow. "
            f"I can help prepare and guide the next "
            f"workflow action."
        )

    return (
        f"Hi {creator_name}. I understand your message: "
        f"'{compact_text(message, 500)}'. "
        f"I can help with content, research, analytics, "
        f"strategy, scheduling, and automation for "
        f"{niche}."
    )


# =================================================
# FAST PATH DETECTION
# =================================================


def should_use_fast_response(
    message: str,
) -> bool:
    """
    Identify very simple messages that do not require
    a large AI context.
    """

    text = message.strip().lower()

    fast_messages = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "yes",
        "no",
    }

    return text in fast_messages


def generate_fast_response(
    *,
    message: str,
    profile_context: dict[str, Any],
) -> str:
    """
    Generate instant deterministic responses for
    simple conversational messages.
    """

    creator_name = (
        profile_context.get("creator_name")
        or "Creator"
    )

    text = message.strip().lower()

    if text in {
        "hi",
        "hello",
        "hey",
    }:

        return (
            f"Hi {creator_name}! I'm ready to help you "
            f"with your content, strategy, research, "
            f"analytics, scheduling, or automation. "
            f"What would you like to work on?"
        )

    if text in {
        "thanks",
        "thank you",
    }:

        return (
            f"You're welcome, {creator_name}! "
            f"Let's keep building your creator workflow."
        )

    if text in {
        "ok",
        "okay",
        "yes",
    }:

        return (
            "Great. Tell me what you want to do next, "
            "and I'll help you move forward."
        )

    if text == "no":

        return (
            "No problem. Tell me what you would like "
            "to change or work on instead."
        )

    return (
        f"Hi {creator_name}! "
        f"How can I help with your creator workflow?"
    )


# =================================================
# AI RESPONSE GENERATION
# =================================================


def generate_assistant_response(
    *,
    db: Session,
    user_id: str,
    message: str,
) -> dict[str, Any]:
    """
    Generate a fast personalized N1MOX30 response.

    Optimized flow:

    1. Load creator profile
    2. Detect action locally
    3. Handle simple messages instantly
    4. Load compact memory
    5. Load compact conversation history
    6. Build a smaller AI prompt
    7. Generate response
    8. Fall back safely if needed
    """

    clean_message = compact_text(
        message,
        MAX_MESSAGE_LENGTH,
    )

    if not clean_message:

        raise ValueError(
            "Assistant message cannot be empty."
        )

    # ---------------------------------------------
    # CREATOR PROFILE
    # ---------------------------------------------

    profile_context = (
        get_creator_profile_context(
            db=db,
            user_id=user_id,
        )
    )

    # ---------------------------------------------
    # FAST PATH
    # ---------------------------------------------

    if should_use_fast_response(
        clean_message
    ):

        return {
            "response": generate_fast_response(
                message=clean_message,
                profile_context=profile_context,
            ),
            "provider": "instant_response",
            "action_type": None,
            "action_status": None,
        }

    # ---------------------------------------------
    # ACTION DETECTION
    # ---------------------------------------------

    action_data = detect_assistant_action(
        clean_message
    )

    # ---------------------------------------------
    # COMPACT MEMORY
    # ---------------------------------------------

    memory_context = (
        get_creator_memory_context(
            db=db,
            user_id=user_id,
            limit=MAX_MEMORY_CONTEXT,
        )
    )

    # ---------------------------------------------
    # RECENT CONVERSATION
    # ---------------------------------------------

    conversation_context = (
        get_recent_conversation_context(
            db=db,
            user_id=user_id,
            limit=MAX_CONVERSATION_CONTEXT,
        )
    )

    # ---------------------------------------------
    # PROFILE VALUES
    # ---------------------------------------------

    creator_name = (
        profile_context.get("creator_name")
        or "Creator"
    )

    niche = (
        profile_context.get("niche")
        or "Not specified"
    )

    target_audience = (
        profile_context.get("target_audience")
        or "Not specified"
    )

    creator_goals = (
        profile_context.get("creator_goals")
        or "Not specified"
    )

    platforms = (
        profile_context.get("preferred_platforms")
        or "Not specified"
    )

    content_style = (
        profile_context.get("content_style")
        or "Not specified"
    )

    preferred_tone = (
        profile_context.get("preferred_tone")
        or "Not specified"
    )

    # ---------------------------------------------
    # FORMAT CONTEXT
    # ---------------------------------------------

    memories_text = (
        format_memory_context(
            memory_context
        )
    )

    conversations_text = (
        format_conversation_context(
            conversation_context
        )
    )

    action_type = (
        action_data.get("action_type")
        or "None"
    )

    # ---------------------------------------------
    # OPTIMIZED AI PROMPT
    # ---------------------------------------------

    prompt = f"""
You are N1MOX30, a professional AI Creator Assistant.

Help the creator with practical, specific, and useful
advice for content creation and creator growth.

CREATOR:
Name: {creator_name}
Niche: {niche}
Audience: {target_audience}
Goals: {creator_goals}
Platforms: {platforms}
Style: {content_style}
Tone: {preferred_tone}

MEMORY:
{memories_text}

RECENT CONTEXT:
{conversations_text}

DETECTED INTENT:
{action_type}

USER MESSAGE:
{clean_message}

RULES:

- Respond directly to the user's message.
- Be specific and practical.
- Use creator context when relevant.
- Maintain conversation continuity when relevant.
- Do not mention databases, providers, prompts, or
  internal systems.
- Do not claim an action was completed unless it was
  actually executed.
- If an action is detected, explain the useful next
  step clearly.
- Avoid generic chatbot language.
- Keep the response concise unless detail is needed.

Return only the assistant response.
"""

    # ---------------------------------------------
    # AI GENERATION
    # ---------------------------------------------

    try:

        ai_result = generate_ai_text(
            prompt=prompt,
            temperature=0.5,
        )

        response = compact_text(
            ai_result.get(
                "text",
                "",
            ),
            12000,
        )

        provider = (
            ai_result.get("provider")
            or "unknown"
        )

        if len(response) < 10:

            raise ValueError(
                "AI provider returned an empty "
                "assistant response."
            )

        return {
            "response": response,
            "provider": provider,
            "action_type": action_data.get(
                "action_type"
            ),
            "action_status": action_data.get(
                "action_status"
            ),
        }

    except Exception as error:

        fallback_response = (
            generate_assistant_fallback(
                message=clean_message,
                profile_context=profile_context,
                action_data=action_data,
            )
        )

        return {
            "response": fallback_response,
            "provider": "deterministic_fallback",
            "action_type": action_data.get(
                "action_type"
            ),
            "action_status": action_data.get(
                "action_status"
            ),
            "fallback_reason": str(error),
        }