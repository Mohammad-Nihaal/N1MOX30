from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


class HookService:
    """
    N1MOX30 Hook Intelligence Service.

    Generates multiple hook concepts, classifies them by hook type,
    evaluates their potential, and selects a recommended hook.

    The service consumes research + strategy output from previous
    workflow stages.

    Providers:
        - demo
        - openai
    """

    HOOK_TYPES = (
        "curiosity",
        "story",
        "contrarian",
        "emotional",
        "pattern_interrupt",
        "problem",
        "information_gap",
    )

    def __init__(self) -> None:
        self.provider = str(
            getattr(settings, "ai_provider", "demo")
        ).lower().strip()

    def generate_hooks(
        self,
        *,
        topic: str,
        platform: str,
        command: str = "",
        research: dict[str, Any] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate and rank hooks using research and strategy context.
        """
        normalized_topic = topic.strip()
        normalized_platform = platform.strip().lower() or "youtube"
        normalized_command = command.strip()

        if not normalized_topic:
            raise ValueError(
                "Hook generation requires a topic."
            )

        normalized_research = research or {}
        normalized_strategy = strategy or {}

        if self.provider == "openai":
            result = self._generate_openai_hooks(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
                research=normalized_research,
                strategy=normalized_strategy,
            )
        else:
            result = self._generate_demo_hooks(
                topic=normalized_topic,
                platform=normalized_platform,
                command=normalized_command,
                research=normalized_research,
                strategy=normalized_strategy,
            )

        return self._normalize_result(
            result=result,
            topic=normalized_topic,
            platform=normalized_platform,
            command=normalized_command,
        )

    def _generate_demo_hooks(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deterministic development hook generation.

        The scoring model is intentionally transparent so the workflow
        can be tested without an external AI provider.
        """
        strategy_data = strategy.get(
            "strategy",
            strategy,
        )

        angle = strategy_data.get(
            "content_angle",
            f"The surprising reality of {topic}.",
        )

        audience_promise = strategy_data.get(
            "audience_promise",
            "",
        )

        hooks = [
            {
                "hook": (
                    f"What if everything you were told about "
                    f"{topic} is only half the story?"
                ),
                "type": "curiosity",
                "score": 92,
                "rationale": (
                    "Creates an information gap without revealing "
                    "the conclusion."
                ),
            },
            {
                "hook": (
                    f"Imagine waking up and discovering that "
                    f"{topic} has already changed the way you work."
                ),
                "type": "story",
                "score": 88,
                "rationale": (
                    "Uses a scenario to place the viewer inside "
                    "the subject immediately."
                ),
            },
            {
                "hook": (
                    f"{topic} isn't simply about the future of work. "
                    "It may change what we consider a valuable job."
                ),
                "type": "contrarian",
                "score": 91,
                "rationale": (
                    "Challenges a common framing and creates a "
                    "reason to keep watching."
                ),
            },
            {
                "hook": (
                    f"If {topic} is moving faster than most people "
                    "realize, what happens to those who wait?"
                ),
                "type": "emotional",
                "score": 86,
                "rationale": (
                    "Creates urgency while keeping the claim "
                    "appropriately cautious."
                ),
            },
            {
                "hook": (
                    f"Forget the usual AI-versus-jobs debate for a "
                    f"moment. The real question about {topic} is "
                    "much bigger."
                ),
                "type": "pattern_interrupt",
                "score": 94,
                "rationale": (
                    "Interrupts the expected framing and opens "
                    "a larger question."
                ),
            },
            {
                "hook": (
                    f"Here's the problem with predicting how "
                    f"{topic} will affect everyone."
                ),
                "type": "problem",
                "score": 89,
                "rationale": (
                    "Starts with a clearly defined problem and "
                    "promises an explanation."
                ),
            },
            {
                "hook": (
                    f"There is one part of {topic} that most "
                    "conversations completely overlook."
                ),
                "type": "information_gap",
                "score": 93,
                "rationale": (
                    "Signals missing information and encourages "
                    "the viewer to discover it."
                ),
            },
        ]

        hooks.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return {
            "topic": topic,
            "platform": platform,
            "command": command,
            "provider": "demo",
            "hook_status": "generated",
            "generation_basis": {
                "strategy_angle": angle,
                "audience_promise": audience_promise,
                "research_available": bool(research),
            },
            "hooks": hooks,
            "recommended_hook": hooks[0],
            "scoring": {
                "method": "development_heuristic",
                "scale": "0-100",
                "factors": [
                    "curiosity",
                    "clarity",
                    "information_gap",
                    "emotional_pull",
                    "retention_potential",
                    "platform_fit",
                ],
            },
        }

    def _generate_openai_hooks(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate and score hooks using the configured OpenAI model.
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
You are N1MOX30's expert hook intelligence agent.

Generate high-quality opening hooks using the supplied research and
content strategy.

Topic:
{topic}

Platform:
{platform}

Original command:
{command or "(not provided)"}

Research:
{json.dumps(research, indent=2, default=str)}

Strategy:
{json.dumps(strategy, indent=2, default=str)}

Generate exactly 7 hooks.

Use these hook types exactly once each:

1. curiosity
2. story
3. contrarian
4. emotional
5. pattern_interrupt
6. problem
7. information_gap

Return ONLY valid JSON in this structure:

{{
  "hooks": [
    {{
      "hook": "...",
      "type": "curiosity",
      "score": 0,
      "rationale": "..."
    }}
  ],
  "recommended_hook": {{
    "hook": "...",
    "type": "...",
    "score": 0,
    "rationale": "..."
  }},
  "scoring": {{
    "method": "ai_evaluation",
    "scale": "0-100",
    "factors": [
      "curiosity",
      "clarity",
      "information_gap",
      "emotional_pull",
      "retention_potential",
      "platform_fit"
    ]
  }}
}}

Requirements:

- Scores must be integers from 0 to 100.
- Rank the strongest hook as recommended_hook.
- Hooks must be engaging without misleading claims.
- Do not invent statistics or facts.
- Do not claim live research.
- Make hooks suitable for the target platform.
"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are N1MOX30's hook intelligence agent. "
                        "Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt.strip(),
                },
            ],
            temperature=0.8,
            response_format={
                "type": "json_object",
            },
        )

        text = response.choices[0].message.content or ""

        result = self._parse_json(text)

        result["provider"] = "openai"
        result["hook_status"] = "generated"

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
                "The AI hook response was not valid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "The AI hook response must be a JSON object."
            )

        return result

    def _normalize_result(
        self,
        *,
        result: dict[str, Any],
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:
        """
        Guarantee a stable hook output contract.
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
            "hook_status",
            "generated",
        )

        normalized.setdefault(
            "generation_basis",
            {},
        )

        hooks = normalized.get(
            "hooks",
            [],
        )

        if not isinstance(hooks, list):
            hooks = []

        valid_hooks: list[dict[str, Any]] = []

        for item in hooks:
            if not isinstance(item, dict):
                continue

            hook_text = str(
                item.get("hook", "")
            ).strip()

            hook_type = str(
                item.get("type", "")
            ).strip()

            if not hook_text:
                continue

            if hook_type not in self.HOOK_TYPES:
                continue

            try:
                score = int(
                    item.get("score", 0)
                )
            except (TypeError, ValueError):
                score = 0

            score = max(
                0,
                min(100, score),
            )

            valid_hooks.append(
                {
                    "hook": hook_text,
                    "type": hook_type,
                    "score": score,
                    "rationale": str(
                        item.get(
                            "rationale",
                            "",
                        )
                    ).strip(),
                }
            )

        valid_hooks.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        normalized["hooks"] = valid_hooks[:20]

        recommended = normalized.get(
            "recommended_hook",
        )

        if not isinstance(recommended, dict):
            recommended = (
                valid_hooks[0]
                if valid_hooks
                else {
                    "hook": "",
                    "type": "",
                    "score": 0,
                    "rationale": "",
                }
            )

        normalized["recommended_hook"] = recommended

        normalized.setdefault(
            "scoring",
            {
                "method": "unknown",
                "scale": "0-100",
                "factors": [],
            },
        )

        return normalized


hook_service = HookService()