from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


class ResearchService:
    """
    N1MOX30 research service.

    This service creates structured research intelligence for a content
    workflow. It supports the existing N1MOX30 AI provider architecture
    without pretending that live web research has occurred.

    Current providers:
        - demo
        - openai

    Live browsing/search can be connected later through a dedicated
    research provider without changing the workflow interface.
    """

    def __init__(self) -> None:
        self.provider = str(getattr(settings, "ai_provider", "demo")).lower()

    def research(
        self,
        topic: str,
        platform: str = "youtube",
        command: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate structured research intelligence for a topic.

        Args:
            topic: Main content topic.
            platform: Target platform.
            command: Original user command, when available.

        Returns:
            Structured research dictionary.
        """
        normalized_topic = topic.strip()
        normalized_platform = platform.strip().lower() or "youtube"
        normalized_command = (command or "").strip()

        if not normalized_topic:
            raise ValueError("Research topic cannot be empty.")

        if self.provider == "openai":
            result = self._research_with_openai(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
            )
        else:
            result = self._research_demo(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
            )

        return self._normalize_result(
            result=result,
            topic=normalized_topic,
            platform=normalized_platform,
            command=normalized_command,
        )

    def _research_demo(
        self,
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:
        """
        Deterministic research planning mode.

        Important:
        This does not claim to have performed live web research.
        """
        return {
            "topic": topic,
            "platform": platform,
            "command": command,
            "provider": "demo",
            "live_research": False,
            "research_status": "planning",
            "summary": (
                f"Research planning for '{topic}'. "
                "The topic should be validated against current audience "
                "interest, competing content, search demand, and recent "
                "developments before publication."
            ),
            "audience": {
                "primary": (
                    "Viewers interested in practical, understandable "
                    "information about the topic."
                ),
                "intent": [
                    "learn",
                    "understand implications",
                    "discover useful insights",
                ],
            },
            "key_questions": [
                f"What is changing around {topic}?",
                f"Why does {topic} matter to the target audience?",
                f"What are the strongest arguments or evidence related to {topic}?",
                f"What misconceptions exist around {topic}?",
                f"What practical takeaway can the audience get from {topic}?",
            ],
            "research_angles": [
                "Current developments",
                "Audience pain points",
                "Contrarian or surprising perspective",
                "Practical implications",
                "Evidence and examples",
            ],
            "competitor_research": {
                "status": "not_performed",
                "note": (
                    "No competitor channels or videos were inspected in "
                    "demo mode."
                ),
            },
            "trend_research": {
                "status": "not_performed",
                "note": (
                    "No live trend source was queried in demo mode."
                ),
            },
            "sources": [],
            "source_policy": (
                "Only verified sources should be added when a live research "
                "provider is connected."
            ),
            "recommended_content_direction": (
                f"Build a high-retention {platform} piece around a strong "
                f"audience problem or surprising insight related to {topic}."
            ),
        }

    def _research_with_openai(
        self,
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:
        """
        Use the existing OpenAI configuration for structured research
        planning.

        The model is explicitly instructed not to invent live sources or
        claim that it browsed the internet.
        """
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI package is not installed in the backend environment."
            ) from exc

        api_key = getattr(settings, "openai_api_key", None)

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured, but the AI provider is set "
                "to openai."
            )

        model = getattr(
            settings,
            "openai_model",
            None,
        ) or "gpt-4o-mini"

        client = OpenAI(api_key=api_key)

        system_prompt = """
You are the research-planning intelligence layer of N1MOX30.

Your job is to produce structured research intelligence that can be passed
to downstream creator agents such as strategy, hooks, script, metadata,
thumbnail, and quality-control systems.

Important constraints:
- Do not claim that you browsed the internet.
- Do not invent URLs, articles, studies, statistics, creators, videos,
  trends, or other sources.
- If current live information is unavailable, clearly mark it as requiring
  verification.
- Separate general reasoning from verified evidence.
- Focus on useful creator intelligence.
- Return valid JSON only.
"""

        user_prompt = f"""
Create research intelligence for:

Topic:
{topic}

Target platform:
{platform}

Original user command:
{command or "(not provided)"}

Return JSON with these fields:

{{
  "summary": "...",
  "audience": {{
    "primary": "...",
    "intent": ["..."]
  }},
  "key_questions": ["..."],
  "research_angles": ["..."],
  "competitor_research": {{
    "status": "not_performed",
    "note": "..."
  }},
  "trend_research": {{
    "status": "not_performed",
    "note": "..."
  }},
  "sources": [],
  "source_policy": "...",
  "recommended_content_direction": "..."
}}

Do not create fake sources.
Do not say that current trends or competitor data were checked.
"""

        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.strip(),
                },
                {
                    "role": "user",
                    "content": user_prompt.strip(),
                },
            ],
        )

        content = response.choices[0].message.content or ""

        parsed = self._parse_json(content)

        if not isinstance(parsed, dict):
            raise RuntimeError(
                "OpenAI research response did not contain a JSON object."
            )

        parsed["provider"] = "openai"
        parsed["live_research"] = False
        parsed["research_status"] = "planning"

        return parsed

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        """
        Parse a JSON response while tolerating markdown code fences.
        """
        cleaned = content.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "The AI research response was not valid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "The AI research response must be a JSON object."
            )

        return result

    @staticmethod
    def _normalize_result(
        result: dict[str, Any],
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:
        """
        Guarantee a stable contract for downstream workflow stages.
        """
        normalized = dict(result)

        normalized["topic"] = topic
        normalized["platform"] = platform
        normalized["command"] = command

        normalized.setdefault("provider", "demo")
        normalized.setdefault("live_research", False)
        normalized.setdefault("research_status", "planning")
        normalized.setdefault("summary", "")
        normalized.setdefault("audience", {})
        normalized.setdefault("key_questions", [])
        normalized.setdefault("research_angles", [])
        normalized.setdefault(
            "competitor_research",
            {
                "status": "not_performed",
                "note": "No competitor research performed.",
            },
        )
        normalized.setdefault(
            "trend_research",
            {
                "status": "not_performed",
                "note": "No live trend research performed.",
            },
        )
        normalized.setdefault("sources", [])
        normalized.setdefault(
            "source_policy",
            "Only verified sources should be added.",
        )
        normalized.setdefault("recommended_content_direction", "")

        if not isinstance(normalized["key_questions"], list):
            normalized["key_questions"] = []

        if not isinstance(normalized["research_angles"], list):
            normalized["research_angles"] = []

        if not isinstance(normalized["sources"], list):
            normalized["sources"] = []

        return normalized


research_service = ResearchService()