from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.research import Research
from app.services.ai.provider_router import (
    ai_provider_router,
)


# =================================================
# JSON STORAGE HELPERS
# =================================================


def serialize_list(
    values: list[str] | None,
) -> str | None:
    """Convert a list into JSON text for database storage."""

    if not values:
        return None

    return json.dumps(values)


def deserialize_list(
    value: str | None,
) -> list[str]:
    """Convert stored JSON text back into a list."""

    if not value:
        return []

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return [
                str(item)
                for item in parsed
                if str(item).strip()
            ]

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        pass

    return []


# =================================================
# TEXT CLEANING
# =================================================


def clean_ai_response(
    text: str,
) -> str:
    """Remove common provider logs and formatting artifacts."""

    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"\x1B\[[0-?]*[ -/]*[@-~]",
        "",
        text,
    )

    lines: list[str] = []

    ignored_patterns = [
        "[provider-transport-fetch]",
        "[model-fetch]",
        "[provider]",
        "model.run via",
        "provider:",
        "thinking...",
    ]

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        lower_line = stripped.lower()

        if any(
            pattern in lower_line
            for pattern in ignored_patterns
        ):
            continue

        if re.match(
            r"^\d{2}:\d{2}:\d{2}\s+\[",
            stripped,
        ):
            continue

        lines.append(stripped)

    cleaned = "\n".join(lines)

    replacements = {
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "â€¦": "...",
        "Â": "",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(
            old,
            new,
        )

    return cleaned.strip()


# =================================================
# AI PROVIDER
# =================================================


def generate_ai_research_text(
    *,
    prompt: str,
    temperature: float = 0.4,
) -> tuple[str, str | None]:
    """
    Generate research using the configured AI provider.

    Returns:
        tuple:
            cleaned_text
            provider_name
    """

    result = ai_provider_router.generate(
        prompt=prompt,
        temperature=temperature,
    )

    text = result.get(
        "text",
        "",
    )

    provider = result.get(
        "provider"
    )

    cleaned = clean_ai_response(
        text
    )

    if not cleaned:
        raise RuntimeError(
            "AI provider returned an empty response."
        )

    return (
        cleaned,
        provider,
    )


# =================================================
# SECTION PARSING
# =================================================


def parse_text_section(
    *,
    text: str,
    section_name: str,
    next_sections: list[str],
) -> str:
    """Extract one named section from AI output."""

    escaped_section = re.escape(
        section_name
    )

    if next_sections:

        next_pattern = "|".join(
            re.escape(section)
            for section in next_sections
        )

        pattern = (
            rf"{escaped_section}\s*:\s*"
            rf"(.*?)"
            rf"(?=\n\s*(?:{next_pattern})\s*:|\Z)"
        )

    else:

        pattern = (
            rf"{escaped_section}\s*:\s*"
            rf"(.*)"
        )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    return match.group(1).strip()


def parse_list_section(
    *,
    text: str,
    section_name: str,
    next_sections: list[str],
) -> list[str]:
    """Extract bullet or numbered items."""

    section = parse_text_section(
        text=text,
        section_name=section_name,
        next_sections=next_sections,
    )

    if not section:
        return []

    items: list[str] = []

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^(?:[-*•]|\d+[\.\)\-])\s*",
            "",
            line,
        )

        line = line.strip(
            " -•"
        )

        if line:
            items.append(line)

    return items


# =================================================
# SCORE PARSING
# =================================================


def parse_score(
    value: str,
) -> float | None:
    """Extract a score between 0 and 100."""

    if not value:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        value,
    )

    if not match:
        return None

    score = float(
        match.group(1)
    )

    return min(
        max(score, 0.0),
        100.0,
    )


# =================================================
# AI RESEARCH GENERATION
# =================================================


def generate_ai_research(
    *,
    topic: str,
    platform: str,
) -> dict[str, Any]:
    """
    Generate structured creator research using
    the configured AI provider.
    """

    prompt = f"""
You are the creator research intelligence engine
inside N1MOX30.

Analyze the requested topic for a content creator.

PLATFORM:
{platform}

TOPIC:
{topic}

IMPORTANT RULES:

1. Do not ask questions.
2. Do not introduce yourself.
3. Do not mention that you are an AI.
4. Do not invent real-time statistics.
5. Do not claim live data unless provided.
6. Focus on actionable creator insights.
7. Make the research specific to the topic.
8. Avoid generic chatbot advice.
9. Do not include provider logs or metadata.
10. Return EXACTLY the structure below.

KEYWORDS:
- Keyword 1
- Keyword 2
- Keyword 3
- Keyword 4
- Keyword 5
- Keyword 6
- Keyword 7
- Keyword 8

AUDIENCE ANGLES:
- Audience angle 1
- Audience angle 2
- Audience angle 3
- Audience angle 4
- Audience angle 5

CONTENT OPPORTUNITIES:
- Content opportunity 1
- Content opportunity 2
- Content opportunity 3
- Content opportunity 4
- Content opportunity 5

COMPETITOR INSIGHTS:
- Insight 1
- Insight 2
- Insight 3
- Insight 4
- Insight 5

RESEARCH SUMMARY:
Write a concise, useful research summary.

OPPORTUNITY SCORE:
Number from 0 to 100

TREND SCORE:
Number from 0 to 100
"""

    text, provider = generate_ai_research_text(
        prompt=prompt,
        temperature=0.4,
    )

    keywords = parse_list_section(
        text=text,
        section_name="KEYWORDS",
        next_sections=[
            "AUDIENCE ANGLES",
            "CONTENT OPPORTUNITIES",
            "COMPETITOR INSIGHTS",
            "RESEARCH SUMMARY",
            "OPPORTUNITY SCORE",
            "TREND SCORE",
        ],
    )

    audience_angles = parse_list_section(
        text=text,
        section_name="AUDIENCE ANGLES",
        next_sections=[
            "CONTENT OPPORTUNITIES",
            "COMPETITOR INSIGHTS",
            "RESEARCH SUMMARY",
            "OPPORTUNITY SCORE",
            "TREND SCORE",
        ],
    )

    content_opportunities = parse_list_section(
        text=text,
        section_name="CONTENT OPPORTUNITIES",
        next_sections=[
            "COMPETITOR INSIGHTS",
            "RESEARCH SUMMARY",
            "OPPORTUNITY SCORE",
            "TREND SCORE",
        ],
    )

    competitor_insights = parse_list_section(
        text=text,
        section_name="COMPETITOR INSIGHTS",
        next_sections=[
            "RESEARCH SUMMARY",
            "OPPORTUNITY SCORE",
            "TREND SCORE",
        ],
    )

    research_summary = parse_text_section(
        text=text,
        section_name="RESEARCH SUMMARY",
        next_sections=[
            "OPPORTUNITY SCORE",
            "TREND SCORE",
        ],
    )

    opportunity_score_text = parse_text_section(
        text=text,
        section_name="OPPORTUNITY SCORE",
        next_sections=[
            "TREND SCORE",
        ],
    )

    trend_score_text = parse_text_section(
        text=text,
        section_name="TREND SCORE",
        next_sections=[],
    )

    opportunity_score = parse_score(
        opportunity_score_text
    )

    trend_score = parse_score(
        trend_score_text
    )

    # Minimum validation.
    if (
        len(keywords) < 3
        or len(audience_angles) < 2
        or len(content_opportunities) < 2
        or len(competitor_insights) < 2
        or len(research_summary) < 30
    ):
        raise ValueError(
            "AI response did not contain complete "
            "research sections."
        )

    return {
        "platform": platform,
        "topic": topic,
        "keywords": keywords[:10],
        "audience_angles": audience_angles[:10],
        "content_opportunities": (
            content_opportunities[:10]
        ),
        "competitor_insights": (
            competitor_insights[:10]
        ),
        "research_summary": research_summary,
        "opportunity_score": opportunity_score,
        "trend_score": trend_score,
        "provider": provider,
    }


# =================================================
# DETERMINISTIC FALLBACK RESEARCH
# =================================================


def generate_fallback_research(
    *,
    topic: str,
    platform: str,
) -> dict[str, Any]:
    """
    Generate reliable deterministic research when
    an AI provider is unavailable.
    """

    topic_clean = topic.strip()

    platform_name = platform.capitalize()

    return {
        "platform": platform,
        "topic": topic_clean,

        "keywords": [
            topic_clean,
            f"{topic_clean} trends",
            f"{topic_clean} latest",
            f"{topic_clean} explained",
            f"{topic_clean} tips",
            f"{topic_clean} facts",
            f"best {topic_clean}",
            f"{topic_clean} viral",
        ],

        "audience_angles": [
            (
                f"Beginner-friendly explanation of "
                f"{topic_clean}"
            ),
            (
                f"Quick facts about "
                f"{topic_clean}"
            ),
            (
                f"Common mistakes people make with "
                f"{topic_clean}"
            ),
            (
                f"Latest trends and updates around "
                f"{topic_clean}"
            ),
            (
                f"Expert tips and interesting insights "
                f"about {topic_clean}"
            ),
        ],

        "content_opportunities": [
            (
                f"Create a short educational video about "
                f"{topic_clean}"
            ),
            (
                f"Create a Top 5 list related to "
                f"{topic_clean}"
            ),
            (
                f"Explain surprising facts about "
                f"{topic_clean}"
            ),
            (
                f"Compare different opinions around "
                f"{topic_clean}"
            ),
            (
                f"Create a beginner guide for "
                f"{topic_clean}"
            ),
        ],

        "competitor_insights": [
            (
                "Use a stronger opening hook within "
                "the first few seconds."
            ),
            (
                "Keep the content focused on one "
                "clear audience question."
            ),
            (
                "Use short, easy-to-understand sections "
                "for better retention."
            ),
            (
                "Include a unique opinion, example, "
                "or perspective."
            ),
            (
                "End with a clear takeaway or "
                "audience question."
            ),
        ],

        "research_summary": (
            f"{topic_clean} has several useful content "
            f"opportunities for {platform_name}. Focus "
            f"on a strong hook, clear audience value, "
            f"simple storytelling, and a unique angle "
            f"to make the content more competitive."
        ),

        "opportunity_score": None,

        "trend_score": None,

        "provider": "deterministic_fallback",
    }


# =================================================
# NORMALIZATION
# =================================================


def normalize_research_result(
    *,
    result: dict[str, Any],
    topic: str,
    platform: str,
) -> dict[str, Any]:
    """Normalize research output into a safe structure."""

    fallback = generate_fallback_research(
        topic=topic,
        platform=platform,
    )

    normalized = {
        "platform": platform,
        "topic": topic,

        "keywords": (
            result.get("keywords")
            or fallback["keywords"]
        ),

        "audience_angles": (
            result.get("audience_angles")
            or fallback["audience_angles"]
        ),

        "content_opportunities": (
            result.get("content_opportunities")
            or fallback["content_opportunities"]
        ),

        "competitor_insights": (
            result.get("competitor_insights")
            or fallback["competitor_insights"]
        ),

        "research_summary": (
            result.get("research_summary")
            or fallback["research_summary"]
        ),

        "opportunity_score": (
            result.get("opportunity_score")
        ),

        "trend_score": (
            result.get("trend_score")
        ),

        "provider": result.get(
            "provider"
        ),
    }

    return normalized


# =================================================
# SCORE CALCULATIONS
# =================================================


def calculate_opportunity_score(
    *,
    keywords: list[str],
    audience_angles: list[str],
    content_opportunities: list[str],
) -> float:
    """Calculate a deterministic opportunity score."""

    score = (
        len(keywords) * 5
        + len(audience_angles) * 8
        + len(content_opportunities) * 10
    )

    return float(
        min(score, 100)
    )


def calculate_trend_score(
    *,
    topic: str,
    keywords: list[str],
    content_opportunities: list[str],
) -> float:
    """Calculate a deterministic trend score."""

    topic_score = min(
        len(topic.strip()) * 2,
        30,
    )

    keyword_score = min(
        len(keywords) * 6,
        40,
    )

    opportunity_score = min(
        len(content_opportunities) * 6,
        30,
    )

    score = (
        topic_score
        + keyword_score
        + opportunity_score
    )

    return float(
        min(score, 100)
    )


# =================================================
# DATABASE OPERATIONS
# =================================================


def save_research(
    *,
    db: Session,
    user_id: str,
    platform: str,
    topic: str,
    keywords: list[str],
    audience_angles: list[str],
    content_opportunities: list[str],
    competitor_insights: list[str],
    research_summary: str | None,
    opportunity_score: float | None,
    trend_score: float | None,
    provider: str | None,
    research_status: str = "completed",
    error_message: str | None = None,
) -> Research:
    """Save research to the database."""

    research = Research(
        user_id=user_id,
        platform=platform,
        topic=topic,
        keywords=serialize_list(keywords),
        audience_angles=serialize_list(
            audience_angles
        ),
        content_opportunities=serialize_list(
            content_opportunities
        ),
        competitor_insights=serialize_list(
            competitor_insights
        ),
        research_summary=research_summary,
        opportunity_score=opportunity_score,
        trend_score=trend_score,
        provider=provider,
        research_status=research_status,
        error_message=error_message,
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return research


def get_research(
    *,
    db: Session,
    user_id: str,
    research_id: str,
) -> Research | None:
    """Get one research record belonging to a user."""

    return (
        db.query(Research)
        .filter(
            Research.id == research_id,
            Research.user_id == user_id,
        )
        .first()
    )


def get_research_history(
    *,
    db: Session,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Research], int]:
    """Get paginated research history."""

    query = (
        db.query(Research)
        .filter(
            Research.user_id == user_id
        )
    )

    total = query.count()

    research_items = (
        query
        .order_by(
            Research.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return research_items, total


def delete_research(
    *,
    db: Session,
    user_id: str,
    research_id: str,
) -> bool:
    """Delete one research record."""

    research = get_research(
        db=db,
        user_id=user_id,
        research_id=research_id,
    )

    if not research:
        return False

    db.delete(research)
    db.commit()

    return True


# =================================================
# RESPONSE CONVERSION
# =================================================


def research_to_response(
    research: Research,
) -> dict[str, Any]:
    """Convert database research into an API response."""

    return {
        "id": research.id,
        "user_id": research.user_id,
        "platform": research.platform,
        "topic": research.topic,

        "keywords": deserialize_list(
            research.keywords
        ),

        "audience_angles": deserialize_list(
            research.audience_angles
        ),

        "content_opportunities": deserialize_list(
            research.content_opportunities
        ),

        "competitor_insights": deserialize_list(
            research.competitor_insights
        ),

        "research_summary": (
            research.research_summary
        ),

        "opportunity_score": (
            research.opportunity_score
        ),

        "trend_score": (
            research.trend_score
        ),

        "provider": research.provider,

        "research_status": (
            research.research_status
        ),

        "error_message": (
            research.error_message
        ),

        "created_at": research.created_at,

        "updated_at": research.updated_at,
    }