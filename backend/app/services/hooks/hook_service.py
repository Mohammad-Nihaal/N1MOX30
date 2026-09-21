from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings


class HookService:
    """
    N1MOX30 Hook Intelligence Engine V2.

    Design goals:
    - desire-first openings
    - relatable audience/character framing
    - curiosity and information gaps
    - concrete specificity
    - pattern interruption
    - proof-aware language without fabricated proof
    - platform-aware hook construction
    - transparent scoring
    - multiple candidates before recommendation

    The output contract remains compatible with the existing
    HooksStageHandler and downstream Script/Production stages.
    """

    HOOK_TYPES = (
        "desire",
        "character_desire",
        "curiosity",
        "story",
        "contrarian",
        "emotional",
        "pattern_interrupt",
        "problem",
        "information_gap",
    )

    PLATFORM_RULES = {
        "youtube": {
            "max_words": 24,
            "priority": "clear promise + curiosity",
        },
        "youtube_shorts": {
            "max_words": 18,
            "priority": "fast desire + pattern interrupt",
        },
        "instagram": {
            "max_words": 18,
            "priority": "desire + relatable identity",
        },
        "instagram_reels": {
            "max_words": 18,
            "priority": "desire + relatable identity",
        },
        "tiktok": {
            "max_words": 16,
            "priority": "pattern interrupt + curiosity",
        },
        "linkedin": {
            "max_words": 24,
            "priority": "specific outcome + credibility",
        },
        "x": {
            "max_words": 22,
            "priority": "specificity + curiosity",
        },
    }

    GENERIC_OPENERS = (
        "in today's world",
        "did you know",
        "here's the thing",
        "let's talk about",
        "you won't believe",
        "this changes everything",
        "the shocking truth",
        "game changer",
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

        normalized_topic = topic.strip()
        normalized_platform = platform.strip().lower() or "youtube"
        normalized_command = command.strip()

        if not normalized_topic:
            raise ValueError("Hook generation requires a topic.")

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

    # =========================================================
    # V2 DEMO ENGINE
    # =========================================================

    def _generate_demo_hooks(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
    ) -> dict[str, Any]:

        strategy_data = strategy.get("strategy", strategy)

        audience_promise = str(
            strategy_data.get("audience_promise", "")
        ).strip()

        audience = str(
            strategy_data.get("target_audience", "")
        ).strip()

        angle = str(
            strategy_data.get(
                "content_angle",
                f"The practical reality of {topic}.",
            )
        ).strip()

        desired_outcome = self._extract_desire(
            topic=topic,
            strategy=strategy_data,
            command=command,
            audience_promise=audience_promise,
        )

        relatable_character = self._extract_character(
            audience=audience,
            command=command,
            topic=topic,
        )

        specificity = self._specificity_signal(
            topic=topic,
            research=research,
            strategy=strategy_data,
        )

        proof_available = bool(
            research.get("sources")
            or research.get("evidence")
            or research.get("findings")
            or research.get("data")
        )

        hooks = [
            self._candidate(
                f"If you want to {desired_outcome}, start with {topic}.",
                "desire",
                "Directly leads with the viewer's desired outcome.",
            ),
            self._candidate(
                f"If you're {relatable_character}, this is what {topic} means for you.",
                "character_desire",
                "Connects the subject to a recognizable viewer identity.",
            ),
            self._candidate(
                f"Most people look at {topic} and miss the part that actually matters.",
                "information_gap",
                "Creates a concrete information gap without inventing facts.",
            ),
            self._candidate(
                f"The fastest way to rethink {topic} is to start with what you actually want.",
                "curiosity",
                "Opens a question around the viewer's desired result.",
            ),
            self._candidate(
                f"Forget the usual {topic} debate. Ask this instead.",
                "pattern_interrupt",
                "Breaks the expected framing and creates an open loop.",
            ),
            self._candidate(
                f"{topic}: useful idea, or another distraction? Here's the test.",
                "contrarian",
                "Introduces tension without asserting an unsupported conclusion.",
            ),
            self._candidate(
                f"Here's the problem with trying to understand {topic} from the headline alone.",
                "problem",
                "Frames a recognizable mistake and promises clarification.",
            ),
            self._candidate(
                f"Imagine getting the result you want from {topic} without doing more of everything.",
                "story",
                "Places the viewer inside a desirable scenario.",
            ),
            self._candidate(
                f"If {specificity}, the way you approach {topic} should change.",
                "emotional",
                "Uses a concrete contextual signal to create urgency.",
            ),
        ]

        scored = []

        for item in hooks:
            score_details = self._score_hook(
                hook=item["hook"],
                hook_type=item["type"],
                platform=platform,
                proof_available=proof_available,
                desired_outcome=desired_outcome,
            )

            scored.append(
                {
                    **item,
                    "score": score_details["total"],
                    "score_breakdown": score_details,
                }
            )

        scored.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        recommended = scored[0]

        return {
            "topic": topic,
            "platform": platform,
            "command": command,
            "provider": "demo",
            "hook_status": "generated",
            "engine_version": "2.0",
            "generation_basis": {
                "strategy_angle": angle,
                "audience_promise": audience_promise,
                "target_audience": audience,
                "desired_outcome": desired_outcome,
                "relatable_character": relatable_character,
                "research_available": bool(research),
                "proof_available": proof_available,
            },
            "hooks": scored,
            "recommended_hook": recommended,
            "scoring": {
                "method": "hook_intelligence_v2",
                "scale": "0-100",
                "factors": [
                    "desire_strength",
                    "relatable_character",
                    "curiosity",
                    "specificity",
                    "pattern_interrupt",
                    "clarity",
                    "emotional_pull",
                    "retention_potential",
                    "platform_fit",
                    "proof_awareness",
                ],
            },
        }

    @staticmethod
    def _candidate(
        hook: str,
        hook_type: str,
        rationale: str,
    ) -> dict[str, Any]:

        return {
            "hook": hook.strip(),
            "type": hook_type,
            "rationale": rationale,
        }

    def _score_hook(
        self,
        *,
        hook: str,
        hook_type: str,
        platform: str,
        proof_available: bool,
        desired_outcome: str,
    ) -> dict[str, Any]:

        text = hook.strip()
        lower = text.lower()

        desire_words = (
            "want",
            "get",
            "grow",
            "save",
            "learn",
            "build",
            "reach",
            "make",
            "without",
            "faster",
        )

        curiosity_words = (
            "what",
            "why",
            "how",
            "miss",
            "actually",
            "instead",
            "test",
        )

        character_words = (
            "you're",
            "you are",
            "creator",
            "beginner",
            "student",
            "founder",
            "business",
            "person",
        )

        specificity_score = 6

        if len(text.split()) <= self._platform_limit(platform):
            specificity_score += 4

        if re.search(r"\d", text):
            specificity_score += 3

        if desired_outcome and desired_outcome.lower() in lower:
            specificity_score += 2

        desire_score = min(
            20,
            8
            + sum(
                2 for word in desire_words
                if word in lower
            ),
        )

        character_score = min(
            15,
            5
            + sum(
                2 for word in character_words
                if word in lower
            ),
        )

        curiosity_score = min(
            15,
            5
            + sum(
                2 for word in curiosity_words
                if word in lower
            ),
        )

        pattern_score = 12 if hook_type == "pattern_interrupt" else 6

        clarity_score = 10

        if len(text.split()) > self._platform_limit(platform) + 5:
            clarity_score -= 4

        if any(opener in lower for opener in self.GENERIC_OPENERS):
            clarity_score -= 5

        emotional_score = 8

        if hook_type in {
            "desire",
            "character_desire",
            "emotional",
            "story",
        }:
            emotional_score += 4

        platform_score = 8

        rules = self.PLATFORM_RULES.get(
            platform,
            self.PLATFORM_RULES["youtube"],
        )

        if rules["priority"].split("+")[0].strip() in hook_type:
            platform_score += 2

        proof_score = 5

        if proof_available:
            proof_score = 8

        total = min(
            100,
            desire_score
            + character_score
            + curiosity_score
            + specificity_score
            + pattern_score
            + clarity_score
            + emotional_score
            + platform_score
            + proof_score,
        )

        return {
            "total": int(total),
            "desire_strength": int(desire_score),
            "relatable_character": int(character_score),
            "curiosity": int(curiosity_score),
            "specificity": int(specificity_score),
            "pattern_interrupt": int(pattern_score),
            "clarity": int(clarity_score),
            "emotional_pull": int(emotional_score),
            "platform_fit": int(platform_score),
            "proof_awareness": int(proof_score),
        }

    @classmethod
    def _platform_limit(cls, platform: str) -> int:
        return int(
            cls.PLATFORM_RULES.get(
                platform,
                cls.PLATFORM_RULES["youtube"],
            )["max_words"]
        )

    @staticmethod
    def _extract_desire(
        *,
        topic: str,
        strategy: dict[str, Any],
        command: str,
        audience_promise: str,
    ) -> str:

        for value in (
            strategy.get("desired_outcome"),
            strategy.get("desired_result"),
            strategy.get("goal"),
            audience_promise,
        ):
            if value:
                cleaned = str(value).strip()
                if cleaned:
                    return cleaned.rstrip(".")

        if command:
            command_lower = command.lower()

            if "grow" in command_lower:
                return "grow your audience"
            if "views" in command_lower:
                return "get more views"
            if "sales" in command_lower:
                return "generate more sales"
            if "followers" in command_lower:
                return "grow your following"
            if "money" in command_lower:
                return "make more money"

        return f"get a useful result from {topic}"

    @staticmethod
    def _extract_character(
        *,
        audience: str,
        command: str,
        topic: str,
    ) -> str:

        if audience:
            return audience

        text = f"{command} {topic}".lower()

        if "creator" in text:
            return "a creator trying to grow"
        if "student" in text:
            return "a student trying to get ahead"
        if "business" in text or "business owner" in text:
            return "a business owner trying to grow"
        if "founder" in text:
            return "a founder building from scratch"

        return "someone trying to get ahead"

    @staticmethod
    def _specificity_signal(
        *,
        topic: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
    ) -> str:

        for source in (
            research.get("findings"),
            research.get("evidence"),
            strategy.get("content_angle"),
        ):
            if isinstance(source, str) and source.strip():
                return source.strip()[:120]

            if isinstance(source, list) and source:
                return str(source[0])[:120]

        return topic

    # =========================================================
    # OPENAI ENGINE
    # =========================================================

    def _generate_openai_hooks(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
    ) -> dict[str, Any]:

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI package is not installed in the backend environment."
            ) from exc

        client = OpenAI(
            api_key=settings.openai_api_key,
        )

        prompt = f"""
You are N1MOX30 Hook Intelligence Engine V2.

Your job is to create hooks that feel written by a highly experienced
human creator, not generic AI copy.

PRIMARY PRINCIPLE:
Lead with the viewer's desired outcome whenever appropriate.

Then make the viewer feel:
"I need to know what happens next."

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

Generate 9 distinct hooks.

Required hook types:
1. desire
2. character_desire
3. curiosity
4. story
5. contrarian
6. emotional
7. pattern_interrupt
8. problem
9. information_gap

Every hook must:
- feel natural when spoken aloud
- be specific to the topic
- avoid generic AI wording
- avoid fake urgency
- avoid fabricated statistics
- avoid fabricated proof
- avoid unsupported income/results claims
- avoid "you won't believe"
- avoid "this changes everything"
- avoid empty superlatives
- create a reason to continue watching
- fit the target platform
- preferably expose a desired outcome, identity, tension, or unanswered question

For character_desire hooks, use a recognizable audience identity
only when supported by the strategy/research.

For proof-aware hooks, only use proof that actually exists in the
supplied research.

Score every hook from 0-100 using:
- desire strength
- relatable character
- curiosity
- specificity
- pattern interruption
- clarity
- emotional pull
- retention potential
- platform fit
- proof awareness

Return ONLY valid JSON:

{{
  "hooks": [
    {{
      "hook": "...",
      "type": "...",
      "score": 0,
      "rationale": "...",
      "score_breakdown": {{
        "desire_strength": 0,
        "relatable_character": 0,
        "curiosity": 0,
        "specificity": 0,
        "pattern_interrupt": 0,
        "clarity": 0,
        "emotional_pull": 0,
        "platform_fit": 0,
        "proof_awareness": 0
      }}
    }}
  ],
  "recommended_hook": {{
    "hook": "...",
    "type": "...",
    "score": 0,
    "rationale": "..."
  }},
  "scoring": {{
    "method": "hook_intelligence_v2",
    "scale": "0-100",
    "factors": [
      "desire_strength",
      "relatable_character",
      "curiosity",
      "specificity",
      "pattern_interrupt",
      "clarity",
      "emotional_pull",
      "retention_potential",
      "platform_fit",
      "proof_awareness"
    ]
  }}
}}
"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are N1MOX30's Hook Intelligence Engine V2. "
                        "Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt.strip(),
                },
            ],
            temperature=0.85,
            response_format={
                "type": "json_object",
            },
        )

        text = response.choices[0].message.content or ""

        result = self._parse_json(text)

        result["provider"] = "openai"
        result["hook_status"] = "generated"
        result["engine_version"] = "2.0"

        return result

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:

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

    # =========================================================
    # NORMALIZATION / CONTRACT SAFETY
    # =========================================================

    def _normalize_result(
        self,
        *,
        result: dict[str, Any],
        topic: str,
        platform: str,
        command: str,
    ) -> dict[str, Any]:

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
            "engine_version",
            "2.0",
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

            breakdown = item.get(
                "score_breakdown",
                {},
            )

            if not isinstance(breakdown, dict):
                breakdown = {}

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
                    "score_breakdown": breakdown,
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
                    "score_breakdown": {},
                }
            )

        normalized["recommended_hook"] = recommended

        normalized.setdefault(
            "scoring",
            {
                "method": "hook_intelligence_v2",
                "scale": "0-100",
                "factors": [],
            },
        )

        return normalized


hook_service = HookService()
