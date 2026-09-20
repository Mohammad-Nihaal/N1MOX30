from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


class StrategyService:
    """
    N1MOX30 content strategy intelligence service.

    Converts structured research into a concrete creator strategy that
    downstream stages such as hooks and script generation can consume.

    Providers:
        - demo
        - openai

    The service is deliberately independent from the workflow engine.
    """

    def __init__(self) -> None:
        self.provider = str(
            getattr(settings, "ai_provider", "demo")
        ).lower().strip()

    def create_strategy(
        self,
        *,
        topic: str,
        platform: str,
        command: str = "",
        research: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a structured content strategy from research.
        """
        normalized_topic = topic.strip()
        normalized_platform = platform.strip().lower() or "youtube"
        normalized_command = command.strip()

        if not normalized_topic:
            raise ValueError(
                "Strategy topic cannot be empty."
            )

        normalized_research = research or {}

        if self.provider == "openai":
            result = self._create_openai_strategy(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
                research=normalized_research,
            )
        else:
            result = self._create_demo_strategy(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
                research=normalized_research,
            )

        return self._normalize_result(
            result=result,
            topic=normalized_topic,
            platform=normalized_platform,
            command=normalized_command,
        )

    def _create_demo_strategy(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deterministic development strategy.

        This mode uses the available research structure without claiming
        additional external research.
        """
        research_data = research.get("research", research)

        research_angles = research_data.get(
            "research_angles",
            [],
        )

        key_questions = research_data.get(
            "key_questions",
            [],
        )

        recommended_direction = research_data.get(
            "recommended_content_direction",
            "",
        )

        return {
            "topic": topic,
            "platform": platform,
            "command": command,
            "provider": "demo",
            "strategy_status": "planned",

            "content_angle": (
                f"The surprising reality of {topic} and what it "
                "actually means for ordinary people and creators."
            ),

            "audience_promise": (
                f"By the end of this {platform} piece, viewers will "
                f"understand the most important implications of {topic} "
                "and what they should pay attention to next."
            ),

            "target_audience": {
                "primary": (
                    "Curious viewers who want practical and "
                    "understandable explanations."
                ),
                "secondary": [
                    "students",
                    "professionals",
                    "creators",
                    "technology enthusiasts",
                ],
            },

            "format": {
                "type": (
                    "educational_explainer"
                    if platform == "youtube"
                    else "short_form_explainer"
                ),
                "platform": platform,
                "recommended_length": (
                    "8-12 minutes"
                    if platform == "youtube"
                    else "45-90 seconds"
                ),
            },

            "positioning": {
                "primary": "Useful and evidence-conscious",
                "tone": "clear, confident, conversational",
                "differentiator": (
                    "Focus on practical consequences rather than "
                    "generic predictions."
                ),
            },

            "retention_strategy": {
                "opening": (
                    "Start with a surprising claim or question that "
                    "creates an immediate information gap."
                ),
                "pacing": (
                    "Introduce a meaningful new idea, example, or "
                    "question regularly to maintain momentum."
                ),
                "structure": [
                    "Hook",
                    "Context",
                    "Unexpected insight",
                    "Evidence/examples",
                    "Practical implications",
                    "Key takeaway",
                    "Call to action",
                ],
            },

            "key_talking_points": [
                (
                    "What is actually changing and why the audience "
                    "should care."
                ),
                (
                    "Which parts of the topic are supported by "
                    "evidence versus speculation."
                ),
                (
                    "The practical opportunities and challenges "
                    "created by the change."
                ),
                (
                    "What viewers should watch for next."
                ),
            ],

            "research_inputs": {
                "angles": research_angles,
                "questions": key_questions,
                "recommended_direction": recommended_direction,
            },

            "cta_strategy": (
                "End with one useful takeaway and invite viewers to "
                "share their perspective or experience."
            ),

            "risk_controls": [
                "Avoid unsupported statistics.",
                "Clearly distinguish evidence from speculation.",
                "Avoid sensational claims that cannot be substantiated.",
                "Keep the audience promise aligned with the final script.",
            ],
        }

    def _create_openai_strategy(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate a structured strategy using the configured OpenAI model.
        """
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI package is not installed in the backend "
                "environment."
            ) from exc

        client = OpenAI(
            api_key=settings.openai_api_key,
        )

        prompt = f"""
You are N1MOX30's senior content strategy agent.

Create a professional content strategy from the supplied research.

Topic:
{topic}

Platform:
{platform}

Original command:
{command or "(not provided)"}

Research:
{json.dumps(research, indent=2, default=str)}

Return ONLY valid JSON with this structure:

{{
  "content_angle": "...",
  "audience_promise": "...",
  "target_audience": {{
    "primary": "...",
    "secondary": ["...", "..."]
  }},
  "format": {{
    "type": "...",
    "platform": "...",
    "recommended_length": "..."
  }},
  "positioning": {{
    "primary": "...",
    "tone": "...",
    "differentiator": "..."
  }},
  "retention_strategy": {{
    "opening": "...",
    "pacing": "...",
    "structure": ["...", "..."]
  }},
  "key_talking_points": ["...", "...", "..."],
  "cta_strategy": "...",
  "risk_controls": ["...", "..."]
}}

Requirements:

- Build on the supplied research.
- Do not invent research sources.
- Do not claim live browsing.
- Do not invent statistics.
- Clearly distinguish evidence from speculation.
- Make the strategy useful to downstream hook and script agents.
- Optimize for audience value and retention without using misleading
  clickbait.
"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are N1MOX30's senior content strategy "
                        "agent. Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt.strip(),
                },
            ],
            temperature=0.6,
            response_format={
                "type": "json_object",
            },
        )

        text = response.choices[0].message.content or ""

        result = self._parse_json(text)

        result["provider"] = "openai"
        result["strategy_status"] = "planned"

        return result

    @staticmethod
    def _parse_json(
        text: str,
    ) -> dict[str, Any]:
        """
        Parse an AI JSON response.
        """
        cleaned = text.strip()

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
                "The AI strategy response was not valid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "The AI strategy response must be a JSON object."
            )

        return result

    @staticmethod
    def _normalize_result(
        *,
        result: dict[str, Any],
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:
        """
        Guarantee a stable strategy contract for downstream stages.
        """
        normalized = dict(result)

        normalized["topic"] = topic
        normalized["platform"] = platform
        normalized["command"] = command

        normalized.setdefault(
            "provider",
            "demo",
        )

        normalized.setdefault(
            "strategy_status",
            "planned",
        )

        normalized.setdefault(
            "content_angle",
            "",
        )

        normalized.setdefault(
            "audience_promise",
            "",
        )

        normalized.setdefault(
            "target_audience",
            {},
        )

        normalized.setdefault(
            "format",
            {},
        )

        normalized.setdefault(
            "positioning",
            {},
        )

        normalized.setdefault(
            "retention_strategy",
            {},
        )

        normalized.setdefault(
            "key_talking_points",
            [],
        )

        normalized.setdefault(
            "research_inputs",
            {},
        )

        normalized.setdefault(
            "cta_strategy",
            "",
        )

        normalized.setdefault(
            "risk_controls",
            [],
        )

        if not isinstance(
            normalized["key_talking_points"],
            list,
        ):
            normalized["key_talking_points"] = []

        if not isinstance(
            normalized["risk_controls"],
            list,
        ):
            normalized["risk_controls"] = []

        return normalized


strategy_service = StrategyService()