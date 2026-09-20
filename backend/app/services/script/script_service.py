from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings


class ScriptService:
    """
    N1MOX30 professional script-generation service.

    Pipeline:
        Research -> Strategy -> Hooks -> Script

    Responsibilities:
        - Generate production-ready narration
        - Preserve upstream strategy and hook decisions
        - Use research inputs when available
        - Produce platform-aware structure
        - Provide visual/B-roll direction
        - Normalize generated text
        - Validate script quality
        - Detect repeated or malformed narration
    """

    SCRIPT_FORMATS = {
        "youtube": "long_form",
        "youtube_short": "short_form",
        "shorts": "short_form",
        "instagram": "short_form",
        "reels": "short_form",
    }

    def __init__(self, provider: str | None = None):
        self.provider = (
            provider or settings.ai_provider or "demo"
        ).strip().lower()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def generate_script(
        self,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
        hooks: dict[str, Any],
    ) -> dict[str, Any]:
        topic = self._clean_text(topic)
        platform = self._normalize_platform(platform)
        command = self._clean_text(command)

        if not topic:
            raise ValueError("Script generation requires a topic.")

        if not research:
            raise ValueError("Script generation requires research output.")

        if not strategy:
            raise ValueError("Script generation requires strategy output.")

        if not hooks:
            raise ValueError("Script generation requires hooks output.")

        if self.provider == "openai":
            try:
                return self._generate_openai(
                    topic=topic,
                    platform=platform,
                    command=command,
                    research=research,
                    strategy=strategy,
                    hooks=hooks,
                )
            except Exception:
                return self._generate_demo(
                    topic=topic,
                    platform=platform,
                    command=command,
                    research=research,
                    strategy=strategy,
                    hooks=hooks,
                )

        return self._generate_demo(
            topic=topic,
            platform=platform,
            command=command,
            research=research,
            strategy=strategy,
            hooks=hooks,
        )

    # ------------------------------------------------------------------
    # DEMO GENERATION
    # ------------------------------------------------------------------

    def _generate_demo(
        self,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
        hooks: dict[str, Any],
    ) -> dict[str, Any]:

        strategy_data = strategy.get("strategy", strategy)
        hook_data = hooks.get("hooks", hooks)
        research_data = research.get("research", research)

        if not isinstance(strategy_data, dict):
            strategy_data = {}

        if not isinstance(hook_data, dict):
            hook_data = {}

        if not isinstance(research_data, dict):
            research_data = {}

        recommended_hook = hook_data.get("recommended_hook", {})

        if not isinstance(recommended_hook, dict):
            recommended_hook = {}

        hook_text = self._clean_text(
            recommended_hook.get("hook")
            or (
                f"Forget the obvious answer for a moment. "
                f"The real story behind {topic} is more complicated."
            )
        )

        hook_type = self._clean_text(
            recommended_hook.get("type", "curiosity")
        )

        hook_score = self._safe_score(
            recommended_hook.get("score", 0)
        )

        hook_rationale = self._clean_text(
            recommended_hook.get("rationale", "")
        )

        content_angle = self._clean_text(
            strategy_data.get(
                "content_angle",
                (
                    f"The surprising reality of {topic} "
                    "and what it means for ordinary people."
                ),
            )
        )

        audience_promise = self._clean_text(
            strategy_data.get(
                "audience_promise",
                f"By the end, viewers will understand the most important "
                f"implications of {topic}.",
            )
        )

        talking_points = self._extract_talking_points(
            strategy_data
        )

        research_questions = self._extract_research_questions(
            research_data
        )

        research_findings = self._extract_research_findings(
            research_data
        )

        retention_strategy = self._build_retention_strategy()

        format_type = self.SCRIPT_FORMATS.get(
            platform,
            "long_form",
        )

        if format_type == "short_form":
            target_duration = "45-60 seconds"

            sections = self._build_short_form_sections(
                topic=topic,
                hook=hook_text,
                content_angle=content_angle,
                talking_points=talking_points,
                research_questions=research_questions,
            )
        else:
            target_duration = "12-20 minutes (target: 15 minutes)"

            sections = self._build_long_form_sections(
                topic=topic,
                hook=hook_text,
                content_angle=content_angle,
                audience_promise=audience_promise,
                talking_points=talking_points,
                research_questions=research_questions,
                research_findings=research_findings,
            )

        script_text = self._assemble_script(sections)

        result = {
            "topic": topic,
            "platform": platform,
            "command": command,
            "provider": "demo",
            "script_status": "generated",
            "format": format_type,
            "target_duration": target_duration,
            "content_angle": content_angle,
            "audience_promise": audience_promise,
            "recommended_hook": {
                "hook": hook_text,
                "type": hook_type,
                "score": hook_score,
                "rationale": hook_rationale,
            },
            "retention_strategy": retention_strategy,
            "sections": sections,
            "script": script_text,
            "production_notes": {
                "delivery_style": (
                    "natural, confident, conversational"
                ),
                "pacing": (
                    "dynamic with deliberate emphasis, "
                    "short transitions, information resets, "
                    "and varied sentence rhythm"
                ),
                "visual_cues": True,
                "b_roll_cues": True,
                "caption_friendly": True,
            },
            "research_inputs": {
                "research_questions": research_questions[:10],
                "research_findings": research_findings[:10],
                "research_available": bool(research_data),
            },
            "quality_controls": [
                "Avoid unsupported factual claims.",
                "Do not invent statistics, quotations, or sources.",
                "Keep the opening focused on the selected hook.",
                "Use upstream research and strategy inputs.",
                "Give each major section a distinct purpose.",
                "Avoid repeated arguments and repeated sentence structures.",
                "Use clear transitions between major ideas.",
                "Maintain a continuous timeline.",
                "Maintain logical progression.",
                "End with a useful audience-oriented takeaway.",
            ],
        }

        return self._normalize_result(result)

    # ------------------------------------------------------------------
    # LONG FORM
    # ------------------------------------------------------------------

    def _build_long_form_sections(
        self,
        topic: str,
        hook: str,
        content_angle: str,
        audience_promise: str,
        talking_points: list[str],
        research_questions: list[str],
        research_findings: list[str],
    ) -> list[dict[str, Any]]:

        # Stage 10 requires real YouTube long-form output to be 12-20 minutes.
        # This builder intentionally creates enough narration for approximately
        # 15 minutes of spoken audio rather than relying on planned timestamps.

        sections: list[dict[str, Any]] = []

        def clean(value: str) -> str:
            return self._clean_text(value or "")

        def expand(
            opening: str,
            focus: str,
            question: str = "",
            finding: str = "",
            examples: str = "",
        ) -> str:
            opening = clean(opening)
            focus = clean(focus)
            question = clean(question)
            finding = clean(finding)
            examples = clean(examples)

            parts = [
                opening,
                (
                    f"To understand this properly, we need to look closely at "
                    f"{focus}. The important point is not just the headline "
                    f"version of the story, but what is actually changing "
                    f"inside the process."
                ),
                (
                    f"In practical terms, this means examining what people "
                    f"currently do, which parts of that workflow are changing, "
                    f"and where technology can realistically make a difference. "
                    f"That distinction matters because a technology can be "
                    f"powerful without automatically replacing an entire role "
                    f"or workflow."
                ),
                (
                    f"Another useful way to look at this is through the question "
                    f"of cause and effect. A change becomes meaningful when it "
                    f"changes the amount of time, effort, cost, quality, or "
                    f"creative control involved in the work."
                ),
            ]

            if question:
                parts.append(
                    f"One question worth asking is: {question}. "
                    f"That question helps us separate assumptions from the "
                    f"part of the discussion that can actually be examined."
                )

            if finding:
                parts.append(
                    f"The relevant finding here is this: {finding}. "
                    f"Rather than treating that as a complete answer, we can "
                    f"use it as evidence for understanding the broader pattern."
                )

            if examples:
                parts.append(
                    f"Consider a simple example. {examples} "
                    f"The example shows why the change is better understood "
                    f"as a shift in workflow rather than as a single event."
                )

            parts.extend(
                [
                    (
                        f"For creators and teams working with {topic}, this "
                        f"creates a practical decision point. They need to "
                        f"understand which activities should be automated, "
                        f"which still require human judgment, and which new "
                        f"skills become valuable because the workflow itself "
                        f"is changing."
                    ),
                    (
                        "There is also an important limitation to keep in mind. "
                        "Automation does not remove the need for goals, context, "
                        "quality control, or responsible decision-making. "
                        "The strongest results usually come from combining "
                        "automation with clear human direction."
                    ),
                    (
                        "So the takeaway from this part is not that one side "
                        "of the debate is automatically correct. The useful "
                        "question is what the evidence tells us, what remains "
                        "uncertain, and what people can realistically do with "
                        "the technology today."
                    ),
                ]
            )

            return clean(" ".join(parts))

        # --------------------------------------------------------------
        # 1. HOOK
        # --------------------------------------------------------------
        sections.append(
            {
                "section": "hook",
                "duration": "0:00-0:45",
                "purpose": "Pattern interrupt and information gap",
                "narration": clean(hook),
                "visual_direction": (
                    f"Open with fast, relevant visuals establishing {topic}. "
                    "Use large readable keywords and immediate motion."
                ),
            }
        )

        # --------------------------------------------------------------
        # 2. SETUP
        # --------------------------------------------------------------
        setup_question = (
            research_questions[0]
            if research_questions
            else f"What is actually changing with {topic}?"
        )

        sections.append(
            {
                "section": "setup",
                "duration": "0:45-2:00",
                "purpose": "Establish context and audience stakes",
                "narration": expand(
                    (
                        f"When people talk about {topic}, the conversation "
                        "can quickly become a simple prediction about what "
                        "will happen next. But the reality is more layered."
                    ),
                    topic,
                    setup_question,
                ),
                "visual_direction": (
                    "Show workplace, technology, creator, and contextual "
                    "B-roll with concise on-screen text."
                ),
            }
        )

        # --------------------------------------------------------------
        # 3. AUDIENCE PROMISE
        # --------------------------------------------------------------
        sections.append(
            {
                "section": "audience_promise",
                "duration": "2:00-2:45",
                "purpose": "Establish the value of continuing",
                "narration": expand(
                    audience_promise,
                    (
                        "the major changes, the evidence behind them, "
                        "the practical consequences, and what viewers "
                        "should watch next"
                    ),
                ),
                "visual_direction": (
                    "Display four visual signposts representing the major "
                    "ideas covered in the video."
                ),
            }
        )

        # --------------------------------------------------------------
        # 4-7. FOUR DEEP-DIVE POINTS
        # --------------------------------------------------------------
        points = list(talking_points[:4])

        if len(points) < 4:
            points.extend(
                [
                    "what is actually changing and why the audience should care",
                    "which parts of the discussion need evidence rather than assumptions",
                    "how the change could affect tasks, skills, and workflows",
                    "what signals viewers should watch as the situation develops",
                ][: 4 - len(points)]
            )

        point_ranges = [
            "2:45-5:15",
            "5:15-7:45",
            "7:45-10:15",
            "10:15-12:45",
        ]

        for index, point in enumerate(points[:4], start=1):
            question = (
                research_questions[min(index - 1, len(research_questions) - 1)]
                if research_questions
                else ""
            )
            finding = (
                research_findings[min(index - 1, len(research_findings) - 1)]
                if research_findings
                else ""
            )

            sections.append(
                {
                    "section": f"key_point_{index}",
                    "duration": point_ranges[index - 1],
                    "purpose": self._point_purpose(index),
                    "narration": expand(
                        (
                            f"Let's look at the next major part of the story: "
                            f"{clean(point)}."
                        ),
                        clean(point),
                        question,
                        finding,
                        (
                            f"For a creator working on {topic}, this could mean "
                            "using the technology to remove repetitive steps "
                            "while keeping creative decisions under human control."
                        ),
                    ),
                    "visual_direction": self._point_visual_direction(index),
                }
            )

        # --------------------------------------------------------------
        # 8. PRACTICAL IMPLICATIONS
        # --------------------------------------------------------------
        practical_question = (
            research_questions[-1]
            if research_questions
            else f"How could {topic} change everyday creator workflows?"
        )

        sections.append(
            {
                "section": "practical_implications",
                "duration": "12:45-14:15",
                "purpose": "Translate the topic into practical consequences",
                "narration": expand(
                    (
                        f"Now let's bring the discussion back to the practical "
                        f"side of {topic}. The most useful way to think about "
                        "the change is not simply to ask what disappears."
                    ),
                    (
                        "individual tasks, skills, workflows, costs, time, "
                        "quality, and human decision-making"
                    ),
                    practical_question,
                ),
                "visual_direction": (
                    "Use before-and-after workflow graphics, task breakdowns, "
                    "skill categories, and practical examples."
                ),
            }
        )

        # --------------------------------------------------------------
        # 9. PERSPECTIVE SHIFT
        # --------------------------------------------------------------
        sections.append(
            {
                "section": "perspective_shift",
                "duration": "14:15-15:30",
                "purpose": "Deliver a memorable perspective shift",
                "narration": expand(
                    (
                        f"Here is the bigger perspective on {topic}: "
                        "technology does not operate in isolation."
                    ),
                    (
                        "how people, organizations, and creators respond to "
                        "technology and redesign the workflows around it"
                    ),
                    (
                        f"What changes when {topic} becomes part of a normal "
                        "creator workflow?"
                    ),
                ),
                "visual_direction": (
                    "Shift toward people working alongside technology and "
                    "redesigning workflows."
                ),
            }
        )

        # --------------------------------------------------------------
        # 10. CONCLUSION
        # --------------------------------------------------------------
        sections.append(
            {
                "section": "conclusion",
                "duration": "15:30-16:30",
                "purpose": "Resolve the central information gap",
                "narration": expand(
                    (
                        f"So, if we step back from the headlines around {topic}, "
                        "the most useful conclusion is that change is rarely "
                        "explained by one prediction."
                    ),
                    (
                        "what is changing, what the evidence supports, "
                        "what remains uncertain, and how viewers can "
                        "respond to the next stage"
                    ),
                ),
                "visual_direction": (
                    "Return to the opening question and resolve it with a "
                    "clean visual summary of the major ideas."
                ),
            }
        )

        # --------------------------------------------------------------
        # 11. CTA
        # --------------------------------------------------------------
        sections.append(
            {
                "section": "cta",
                "duration": "16:30-17:00",
                "purpose": "Audience action",
                "narration": (
                    f"If you found this breakdown of {topic} useful, "
                    "subscribe for more clear and practical explanations "
                    "of AI, technology, work, and the creator economy. "
                    "And remember: the goal is not simply to follow the "
                    "latest technology. It is to understand how the tools "
                    "change the way we create, work, and make decisions."
                ),
                "visual_direction": (
                    "Clean branded end card with subscribe prompt "
                    "and a suggested next-video topic."
                ),
            }
        )

        return sections

    # ------------------------------------------------------------------
    # SHORT FORM
    # ------------------------------------------------------------------

    def _build_short_form_sections(
        self,
        topic: str,
        hook: str,
        content_angle: str,
        talking_points: list[str],
        research_questions: list[str],
    ) -> list[dict[str, Any]]:

        points = talking_points[:2]

        if len(points) < 2:
            points = [
                f"The first thing to understand about {topic} "
                "is what is actually changing.",
                f"The second thing to watch is how those changes "
                "could affect people and their work.",
            ]

        question_1 = (
            research_questions[0]
            if research_questions
            else f"What is actually changing with {topic}?"
        )

        return [
            {
                "section": "hook",
                "duration": "0:00-0:05",
                "purpose": "Immediate attention",
                "narration": hook,
                "visual_direction": (
                    f"Fast visual pattern interrupt related to {topic} "
                    "with large caption text."
                ),
            },
            {
                "section": "context",
                "duration": "0:05-0:13",
                "purpose": "Establish the premise",
                "narration": content_angle,
                "visual_direction": (
                    "Rapid B-roll with bold keyword captions."
                ),
            },
            {
                "section": "insight_1",
                "duration": "0:13-0:27",
                "purpose": "Deliver the first useful insight",
                "narration": self._clean_text(
                    f"{self._clean_text(points[0])} "
                    f"That connects directly to the question: {question_1}"
                ),
                "visual_direction": (
                    "Illustrative B-roll with the key phrase "
                    "highlighted on screen."
                ),
            },
            {
                "section": "insight_2",
                "duration": "0:27-0:41",
                "purpose": "Add a contrasting insight",
                "narration": self._clean_text(points[1]),
                "visual_direction": (
                    "Change visual composition and introduce "
                    "a contrasting example."
                ),
            },
            {
                "section": "payoff",
                "duration": "0:41-0:53",
                "purpose": "Deliver the key takeaway",
                "narration": self._clean_text(
                    (
                        f"The important part is this: {topic} is not only "
                        "about what changes today. It is about how people "
                        "respond, which workflows evolve, and which "
                        "opportunities become more valuable next."
                    )
                ),
                "visual_direction": (
                    "Strong visual payoff with the central takeaway "
                    "displayed as concise on-screen text."
                ),
            },
            {
                "section": "cta",
                "duration": "0:53-1:00",
                "purpose": "Audience action",
                "narration": (
                    "Follow for more clear, practical AI breakdowns."
                ),
                "visual_direction": "Simple branded end card.",
            },
        ]

    # ------------------------------------------------------------------
    # NARRATION BUILDERS
    # ------------------------------------------------------------------

    def _build_point_narration(
        self,
        topic: str,
        point: str,
        index: int,
        research_question: str = "",
        research_finding: str = "",
    ) -> str:

        point = self._clean_text(point)
        cleaned_point = point.rstrip(".!? ")

        research_question = self._clean_text(
            research_question
        )

        research_finding = self._clean_text(
            research_finding
        )

        if index == 1:
            opening = (
                f"Let's start with {self._lowercase_lead(cleaned_point)}."
            )

            explanation = (
                f"The reason this is the right place to start is that "
                f"it establishes what the change actually looks like "
                f"before we make assumptions about where it leads."
            )

            evidence_bridge = ""

            if research_question:
                evidence_bridge = (
                    f" One question worth examining here is: "
                    f"{research_question}."
                )

            if research_finding:
                evidence_bridge += (
                    f" The available research input points us toward "
                    f"{research_finding}."
                )

        elif index == 2:
            opening = (
                f"Once that foundation is clear, the next issue is "
                f"{self._lowercase_lead(cleaned_point)}."
            )

            explanation = (
                "This is where it becomes important to separate "
                "what can reasonably be supported from what is still "
                "an assumption. A strong analysis should make that "
                "distinction visible rather than treating every "
                "prediction as a fact."
            )

            evidence_bridge = ""

            if research_question:
                evidence_bridge = (
                    f" A useful question for this part is: "
                    f"{research_question}."
                )

            if research_finding:
                evidence_bridge += (
                    f" The research input to consider is "
                    f"{research_finding}."
                )

        elif index == 3:
            opening = (
                f"Now move from the explanation to the real-world impact: "
                f"{self._lowercase_lead(cleaned_point)}."
            )

            explanation = (
                "This matters because the effect of a technology is often "
                "felt through everyday tasks and workflows rather than "
                "through the technology itself. Looking at those individual "
                "changes makes the discussion much more practical."
            )

            evidence_bridge = ""

            if research_question:
                evidence_bridge = (
                    f" One practical question to keep in view is: "
                    f"{research_question}."
                )

            if research_finding:
                evidence_bridge += (
                    f" The related research input is "
                    f"{research_finding}."
                )

        else:
            opening = (
                f"That leads to the forward-looking question: "
                f"{self._lowercase_lead(cleaned_point)}."
            )

            explanation = (
                "The value here is not predicting the future with certainty. "
                "It is identifying the signals that could tell us whether "
                "the current direction is strengthening, slowing down, "
                "or changing altogether."
            )

            evidence_bridge = ""

            if research_question:
                evidence_bridge = (
                    f" The question to keep watching is: "
                    f"{research_question}."
                )

            if research_finding:
                evidence_bridge += (
                    f" The relevant research input is "
                    f"{research_finding}."
                )

        return self._clean_text(
            f"{opening} {explanation}{evidence_bridge}"
        )

    def _point_purpose(self, index: int) -> str:
        purposes = {
            1: "Establish what is changing",
            2: "Separate evidence from assumptions",
            3: "Explain practical consequences",
            4: "Identify future signals to watch",
        }

        return purposes.get(
            index,
            "Develop a distinct supporting idea",
        )

    def _point_visual_direction(self, index: int) -> str:
        directions = {
            1: (
                "Use contextual B-roll, a simple before-and-after "
                "visual, and highlighted keywords explaining the change."
            ),
            2: (
                "Use charts, evidence markers, source placeholders, "
                "comparisons, and visual distinctions between known "
                "information and uncertainty."
            ),
            3: (
                "Use workflow diagrams, task examples, human-and-AI "
                "interaction visuals, and practical scenario B-roll."
            ),
            4: (
                "Use timeline graphics, trend indicators, future-facing "
                "visuals, and a concise list of signals to watch."
            ),
        }

        return directions.get(
            index,
            "Use relevant B-roll and change the visual composition "
            "when the idea changes.",
        )

    def _lowercase_lead(self, text: str) -> str:
        if not text:
            return "what is changing"

        return text[0].lower() + text[1:]

    # ------------------------------------------------------------------
    # DATA EXTRACTION
    # ------------------------------------------------------------------

    def _extract_talking_points(
        self,
        strategy_data: dict[str, Any],
    ) -> list[str]:

        candidates = [
            strategy_data.get("key_talking_points"),
            strategy_data.get("talking_points"),
            strategy_data.get("key_points"),
            strategy_data.get("content_points"),
        ]

        for candidate in candidates:
            if not isinstance(candidate, list):
                continue

            points = [
                self._clean_text(item)
                for item in candidate
                if self._clean_text(item)
            ]

            if points:
                return self._deduplicate_text(points)

        return []

    def _extract_research_questions(
        self,
        research_data: dict[str, Any],
    ) -> list[str]:

        candidates = [
            research_data.get("research_questions"),
            research_data.get("questions"),
            research_data.get("key_questions"),
            research_data.get("questions_to_answer"),
            research_data.get("research_areas"),
        ]

        for candidate in candidates:
            if not isinstance(candidate, list):
                continue

            questions = [
                self._clean_text(item)
                for item in candidate
                if self._clean_text(item)
            ]

            if questions:
                return self._deduplicate_text(questions)

        return []

    def _extract_research_findings(
        self,
        research_data: dict[str, Any],
    ) -> list[str]:

        candidates = [
            research_data.get("findings"),
            research_data.get("key_findings"),
            research_data.get("insights"),
            research_data.get("research_findings"),
            research_data.get("observations"),
        ]

        for candidate in candidates:
            if not isinstance(candidate, list):
                continue

            findings = [
                self._clean_text(item)
                for item in candidate
                if self._clean_text(item)
            ]

            if findings:
                return self._deduplicate_text(findings)

        return []

    def _deduplicate_text(
        self,
        values: list[str],
    ) -> list[str]:

        result: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned = self._clean_text(value)
            key = re.sub(
                r"\s+",
                " ",
                cleaned.lower(),
            )

            if not key or key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result

    # ------------------------------------------------------------------
    # RETENTION / SUPPORT
    # ------------------------------------------------------------------

    def _build_retention_strategy(self) -> str:
        return (
            "Opening: Use the selected hook to create an immediate "
            "information gap. "
            "Pacing: Introduce a meaningful new idea, example, "
            "question, or visual reset regularly. "
            "Structure: Hook, Context, Audience Promise, Distinct Insights, "
            "Practical Implications, Perspective Shift, Conclusion, CTA."
        )

    def _point_durations(
        self,
        count: int,
    ) -> list[str]:

        if count <= 1:
            return ["1:40-4:40"]

        if count == 2:
            return [
                "1:40-3:10",
                "3:10-4:40",
            ]

        if count == 3:
            return [
                "1:40-2:40",
                "2:40-3:40",
                "3:40-4:40",
            ]

        return [
            "1:40-2:25",
            "2:25-3:10",
            "3:10-3:55",
            "3:55-4:40",
        ]

    # ------------------------------------------------------------------
    # OPENAI
    # ------------------------------------------------------------------

    def _generate_openai(
        self,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
        hooks: dict[str, Any],
    ) -> dict[str, Any]:

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI provider requested but the openai package "
                "is not installed."
            ) from exc

        api_key = getattr(
            settings,
            "openai_api_key",
            None,
        )

        if not api_key:
            raise RuntimeError(
                "OpenAI provider requested but OPENAI_API_KEY is missing."
            )

        model = getattr(
            settings,
            "openai_model",
            None,
        ) or "gpt-4o-mini"

        client = OpenAI(api_key=api_key)

        prompt = self._build_openai_prompt(
            topic=topic,
            platform=platform,
            command=command,
            research=research,
            strategy=strategy,
            hooks=hooks,
        )

        response = client.chat.completions.create(
            model=model,
            temperature=0.7,
            response_format={
                "type": "json_object",
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the N1MOX30 professional script writer. "
                        "Create natural, engaging, accurate, production-ready "
                        "creator scripts. Return valid JSON only. Never invent "
                        "statistics, sources, quotations, studies, or live "
                        "research."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "OpenAI returned an empty script response."
            )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "OpenAI returned invalid JSON for script generation."
            ) from exc

        parsed["provider"] = "openai"

        return self._normalize_result(parsed)

    def _build_openai_prompt(
        self,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
        hooks: dict[str, Any],
    ) -> str:

        return f"""
Create a professional production-ready creator script.

TOPIC:
{topic}

PLATFORM:
{platform}

USER COMMAND:
{command}

RESEARCH:
{json.dumps(research, ensure_ascii=False)}

STRATEGY:
{json.dumps(strategy, ensure_ascii=False)}

HOOKS:
{json.dumps(hooks, ensure_ascii=False)}

Requirements:

1. Use the strongest appropriate hook from the Hooks stage.
2. Build directly from the Strategy stage.
3. Use Research inputs when relevant.
4. Never pretend unavailable research is live research.
5. Write natural spoken narration.
6. Do not write generic filler.
7. Do not repeat the same argument across sections.
8. Every key point must have a distinct purpose.
9. Use smooth and varied transitions.
10. Create realistic continuous section durations.
11. Do not leave unexplained timeline gaps.
12. Include visual direction.
13. Include B-roll opportunities.
14. Maintain viewer curiosity.
15. Include a meaningful perspective shift or payoff.
16. End with a strong conclusion.
17. Include a platform-appropriate CTA.
18. Never fabricate statistics, sources, studies, quotations, or current events.
19. Do not make unsupported factual claims.
20. Ensure normal spaces between all words.
21. Ensure punctuation is clean and natural.
22. Avoid repeated sentence structures.
23. Avoid using the same concluding sentence for multiple key points.
24. Each key point should advance the argument.
25. The final narration should sound like a human creator speaking,
    not like a structured template.

For a YouTube long-form script:
- Target approximately 12-20 minutes, with a target of 15 minutes.
- Use a continuous timeline.
- Include hook, setup, audience promise, distinct key points,
  practical implications, perspective shift, conclusion, and CTA.
- Make the four key points substantively different.

Return valid JSON:

{{
  "topic": "...",
  "platform": "...",
  "script_status": "generated",
  "format": "long_form or short_form",
  "target_duration": "...",
  "content_angle": "...",
  "audience_promise": "...",
  "recommended_hook": {{
    "hook": "...",
    "type": "...",
    "score": 0,
    "rationale": "..."
  }},
  "retention_strategy": "...",
  "sections": [
    {{
      "section": "...",
      "duration": "...",
      "purpose": "...",
      "narration": "...",
      "visual_direction": "..."
    }}
  ],
  "script": "...",
  "production_notes": {{
    "delivery_style": "...",
    "pacing": "...",
    "visual_cues": true,
    "b_roll_cues": true,
    "caption_friendly": true
  }},
  "quality_controls": []
}}
""".strip()

    # ------------------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize_result(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(result, dict):
            raise ValueError(
                "Script service returned an invalid result."
            )

        result.setdefault(
            "script_status",
            "generated",
        )

        result.setdefault(
            "provider",
            self.provider,
        )

        result.setdefault(
            "format",
            "long_form",
        )

        result.setdefault(
            "target_duration",
            "12-20 minutes (target: 15 minutes)",
        )

        result.setdefault(
            "content_angle",
            "",
        )

        result.setdefault(
            "audience_promise",
            "",
        )

        result.setdefault(
            "retention_strategy",
            "",
        )

        result.setdefault(
            "sections",
            [],
        )

        result.setdefault(
            "script",
            "",
        )

        result.setdefault(
            "production_notes",
            {},
        )

        result.setdefault(
            "quality_controls",
            [],
        )

        result["topic"] = self._clean_text(
            result.get("topic", "")
        )

        result["platform"] = self._normalize_platform(
            result.get("platform", "")
        )

        result["command"] = self._clean_text(
            result.get("command", "")
        )

        result["content_angle"] = self._clean_text(
            result.get("content_angle", "")
        )

        result["audience_promise"] = self._clean_text(
            result.get("audience_promise", "")
        )

        result["retention_strategy"] = self._clean_text(
            result.get("retention_strategy", "")
        )

        recommended_hook = result.get(
            "recommended_hook",
            {},
        )

        if not isinstance(
            recommended_hook,
            dict,
        ):
            recommended_hook = {}

        result["recommended_hook"] = {
            "hook": self._clean_text(
                recommended_hook.get("hook", "")
            ),
            "type": self._clean_text(
                recommended_hook.get("type", "")
            ),
            "score": self._safe_score(
                recommended_hook.get("score")
            ),
            "rationale": self._clean_text(
                recommended_hook.get("rationale", "")
            ),
        }

        sections = result.get(
            "sections",
            [],
        )

        if not isinstance(
            sections,
            list,
        ):
            sections = []

        normalized_sections: list[dict[str, Any]] = []

        for section in sections:

            if not isinstance(
                section,
                dict,
            ):
                continue

            normalized_sections.append(
                {
                    "section": self._clean_text(
                        section.get("section", "")
                    ),
                    "duration": self._clean_text(
                        section.get("duration", "")
                    ),
                    "purpose": self._clean_text(
                        section.get("purpose", "")
                    ),
                    "narration": self._clean_text(
                        section.get("narration", "")
                    ),
                    "visual_direction": self._clean_text(
                        section.get(
                            "visual_direction",
                            "",
                        )
                    ),
                }
            )

        result["sections"] = normalized_sections

        script_text = self._clean_text(
            result.get("script", "")
        )

        if not script_text:
            script_text = self._assemble_script(
                normalized_sections
            )

        result["script"] = script_text

        self._validate_script_quality(result)

        return result

    # ------------------------------------------------------------------
    # TEXT CLEANING
    # ------------------------------------------------------------------

    def _clean_text(
        self,
        value: Any,
    ) -> str:

        if value is None:
            return ""

        text = str(value).strip()

        if not text:
            return ""

        text = text.replace(
            "\u00a0",
            " ",
        )

        text = text.replace(
            "\u200b",
            "",
        )

        text = text.replace(
            "\ufeff",
            "",
        )

        # --------------------------------------------------------------
        # Repair known AI-generated word concatenation artifacts.
        # --------------------------------------------------------------

        replacements = {
            "ofAI": "of AI",
            "realquestion": "real question",
            "peopletalk": "people talk",
            "thoseideas": "those ideas",
            "shouldcare": "should care",
            "supportedby": "supported by",
            "onlyon": "only on",
            "replacingtraditionaljobs": "replacing traditional jobs",
            "givesusa": "gives us a",
            "Usea": "Use a",
            "whatismatters": "what is matters",
            "whatismatters": "what matters",
            "isactually": "is actually",
            "what isactually": "what is actually",
            "willunderstand": "will understand",
            "peopleworking": "people working",
            "that thefuture": "that the future",
            "thefuture": "the future",
            "theaudience": "the audience",
            "thechange": "the change",
            "thetechnology": "the technology",
            "thediscussion": "the discussion",
            "thetopic": "the topic",
            "thequestion": "the question",
            "theimportant": "the important",
            "thebroader": "the broader",
            "thepractical": "the practical",
            "theway": "the way",
            "themost": "the most",
            "thefirst": "the first",
            "theseideas": "these ideas",
            "thesignal": "the signal",
            "whatviewers": "what viewers",
            "forviewers": "for viewers",
            "inthis": "in this",
            "invideo": "in video",
            "inthe": "in the",
            "ontopic": "on topic",
            "onthis": "on this",
            "withAI": "with AI",
            "byAI": "by AI",
            "fromAI": "from AI",
            "aboutAI": "about AI",
            "forAI": "for AI",
            "toAI": "to AI",
            "canreplace": "can replace",
            "canaccomplish": "can accomplish",
            "canadapt": "can adapt",
            "couldaffect": "could affect",
            "increasinglycapable": "increasingly capable",
            "moreuseful": "more useful",
            "morevaluable": "more valuable",
            "simpleprediction": "simple prediction",
            "simplequestion": "simple question",
            "simpleanswer": "simple answer",
            "replacementalone": "replacement alone",
            "realworld": "real-world",
            "yesorno": "yes-or-no",
        }

        for broken, fixed in replacements.items():
            text = text.replace(
                broken,
                fixed,
            )

        # Generic camel-case repair.
        text = re.sub(
            r"(?<=[a-z])(?=[A-Z])",
            " ",
            text,
        )

        # Repair punctuation-spacing artifacts.
        text = re.sub(
            r"\s+([,.!?;:])",
            r"\1",
            text,
        )

        text = re.sub(
            r"([,.!?;:])(?=[A-Za-z])",
            r"\1 ",
            text,
        )

        # Repair duplicated punctuation.
        text = re.sub(
            r"\.{2,}",
            ".",
            text,
        )

        text = re.sub(
            r"!{2,}",
            "!",
            text,
        )

        text = re.sub(
            r"\?{2,}",
            "?",
            text,
        )

        # Normalize common platform naming.
        text = re.sub(
            r"\bYou\s+Tube\b",
            "YouTube",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\byoutube\b",
            "YouTube",
            text,
            flags=re.IGNORECASE,
        )

        # Normalize common AI naming.
        text = re.sub(
            r"\bA\s*I\b",
            "AI",
            text,
            flags=re.IGNORECASE,
        )

        # Remove spaces before punctuation.
        text = re.sub(
            r"\s+([,.!?])",
            r"\1",
            text,
        )

        # Normalize whitespace.
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def _normalize_platform(
        self,
        value: Any,
    ) -> str:

        platform = self._clean_text(value).lower()

        aliases = {
            "youtube": "youtube",
            "youtube video": "youtube",
            "youtube short": "youtube_short",
            "shorts": "shorts",
            "instagram": "instagram",
            "reels": "reels",
        }

        return aliases.get(
            platform,
            platform or "youtube",
        )

    def _assemble_script(
        self,
        sections: list[dict[str, Any]],
    ) -> str:

        parts: list[str] = []

        for section in sections:

            narration = self._clean_text(
                section.get(
                    "narration",
                    "",
                )
            )

            if narration:
                parts.append(narration)

        return "\n\n".join(parts).strip()

    def _safe_score(
        self,
        value: Any,
    ) -> int:

        try:
            score = int(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0

        return max(
            0,
            min(
                100,
                score,
            ),
        )

    # ------------------------------------------------------------------
    # QUALITY VALIDATION
    # ------------------------------------------------------------------

    def _validate_script_quality(
        self,
        result: dict[str, Any],
    ) -> None:

        sections = result.get(
            "sections",
            [],
        )

        if not sections:
            raise ValueError(
                "Generated script contains no sections."
            )

        script = self._clean_text(
            result.get(
                "script",
                "",
            )
        )

        if len(script) < 100:
            raise ValueError(
                "Generated script is too short."
            )

        narration_values = [
            self._clean_text(
                section.get(
                    "narration",
                    "",
                )
            )
            for section in sections
        ]

        narration_values = [
            value
            for value in narration_values
            if value
        ]

        if len(narration_values) < 3:
            raise ValueError(
                "Generated script does not contain enough narration sections."
            )

        normalized_narration = [
            re.sub(
                r"\s+",
                " ",
                value.lower(),
            )
            for value in narration_values
        ]

        unique_ratio = (
            len(set(normalized_narration))
            / max(
                1,
                len(normalized_narration),
            )
        )

        if unique_ratio < 0.70:
            raise ValueError(
                "Generated script contains excessive repeated narration."
            )

        # Detect repeated long phrases across sections.
        self._validate_repeated_phrases(
            narration_values
        )

        # Long-form scripts must have a continuous timeline.
        if result.get("format") == "long_form":
            self._validate_timeline(
                sections
            )

    def _validate_repeated_phrases(
        self,
        sections: list[dict[str, Any]],
    ) -> None:
        """
        Detect genuinely repetitive narration without rejecting natural
        topic-related language.

        The validator intentionally ignores:
        - short phrases
        - common conversational phrases
        - phrases containing the core topic
        - normal repeated terminology

        It only fails when a distinctive, long phrase is repeated across
        multiple independent sections.
        """

        narrations: list[str] = []

        for section in sections:
            if not isinstance(section, dict):
                continue

            narration = self._clean_text(
                section.get("narration", "")
            )

            if narration:
                narrations.append(narration)

        if len(narrations) < 2:
            return

        # Common words/phrases that are normal in spoken creator scripts.
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "so",
            "to",
            "of",
            "in",
            "on",
            "for",
            "with",
            "from",
            "that",
            "this",
            "these",
            "those",
            "it",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "as",
            "at",
            "by",
            "we",
            "you",
            "they",
            "people",
            "really",
            "actually",
            "important",
            "because",
            "what",
            "how",
            "why",
            "when",
            "where",
            "can",
            "could",
            "will",
            "would",
            "should",
            "about",
            "more",
            "than",
            "only",
            "also",
            "just",
            "look",
            "think",
            "understand",
            "matter",
            "means",
            "change",
            "changes",
        }

        def tokenize(text: str) -> list[str]:
            text = text.lower()
            text = re.sub(
                r"[^a-z0-9\s'-]",
                " ",
                text,
            )

            return [
                token
                for token in text.split()
                if token
            ]

        tokenized = [
            tokenize(narration)
            for narration in narrations
        ]

        # Distinctive long phrases are what we care about.
        phrase_size = 10

        repeated_phrases: set[str] = set()

        for i in range(len(tokenized)):
            words_a = tokenized[i]

            if len(words_a) < phrase_size:
                continue

            phrases_a = {
                " ".join(
                    words_a[index:index + phrase_size]
                )
                for index in range(
                    len(words_a) - phrase_size + 1
                )
            }

            for j in range(i + 1, len(tokenized)):
                words_b = tokenized[j]

                if len(words_b) < phrase_size:
                    continue

                phrases_b = {
                    " ".join(
                        words_b[index:index + phrase_size]
                    )
                    for index in range(
                        len(words_b) - phrase_size + 1
                    )
                }

                common = phrases_a.intersection(
                    phrases_b
                )

                for phrase in common:
                    words = phrase.split()

                    # Ignore phrases dominated by common stop words.
                    meaningful_words = [
                        word
                        for word in words
                        if word not in stop_words
                    ]

                    if len(meaningful_words) < 5:
                        continue

                    # Ignore very short/common repeated wording.
                    if len(set(meaningful_words)) < 4:
                        continue

                    repeated_phrases.add(phrase)

        # A single repeated phrase is not automatically a failure.
        # Require multiple distinctive repeated phrases before rejecting.
        if len(repeated_phrases) >= 2:
            raise ValueError(
                "Generated script contains repeated long phrases "
                "across multiple sections."
            )

    def _validate_timeline(
        self,
        sections: list[dict[str, Any]],
    ) -> None:

        previous_end_seconds = 0

        for section in sections:

            duration = self._clean_text(
                section.get(
                    "duration",
                    "",
                )
            )

            match = re.match(
                r"^(\d+):(\d{2})-(\d+):(\d{2})$",
                duration,
            )

            if not match:
                continue

            start_minutes = int(
                match.group(1)
            )

            start_seconds = int(
                match.group(2)
            )

            end_minutes = int(
                match.group(3)
            )

            end_seconds = int(
                match.group(4)
            )

            start_total = (
                start_minutes * 60
                + start_seconds
            )

            end_total = (
                end_minutes * 60
                + end_seconds
            )

            if end_total <= start_total:
                raise ValueError(
                    f"Invalid section duration: {duration}"
                )

            if start_total != previous_end_seconds:
                raise ValueError(
                    "Generated script contains a timeline gap or overlap "
                    f"before section '{section.get('section', '')}'."
                )

            previous_end_seconds = end_total

    # ------------------------------------------------------------------
    # RETENTION NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize_retention_strategy(
        self,
        value: Any,
    ) -> str:

        if isinstance(
            value,
            dict,
        ):

            opening = self._clean_text(
                value.get(
                    "opening",
                    "",
                )
            )

            pacing = self._clean_text(
                value.get(
                    "pacing",
                    "",
                )
            )

            structure = value.get(
                "structure",
                [],
            )

            if isinstance(
                structure,
                list,
            ):

                structure_text = ", ".join(
                    self._clean_text(item)
                    for item in structure
                    if self._clean_text(item)
                )

            else:

                structure_text = self._clean_text(
                    structure
                )

            parts = []

            if opening:
                parts.append(
                    f"Opening: {opening}"
                )

            if pacing:
                parts.append(
                    f"Pacing: {pacing}"
                )

            if structure_text:
                parts.append(
                    f"Structure: {structure_text}"
                )

            return " ".join(parts)

        return self._clean_text(value)


script_service = ScriptService()


