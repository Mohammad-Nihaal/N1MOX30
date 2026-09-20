from __future__ import annotations

import re
from typing import Any


class MetadataService:
    """
    Provider-neutral metadata and SEO intelligence service.

    Generates upload-ready metadata without claiming that metadata
    has already been published to an external platform.
    """

    SUPPORTED_PLATFORMS = {
        "youtube",
        "youtube_shorts",
        "instagram",
        "instagram_reels",
        "tiktok",
    }

    PLATFORM_CONFIG = {
        "youtube": {
            "title_limit": 100,
            "description_limit": 5000,
            "tag_limit": 500,
            "supports_tags": True,
        },
        "youtube_shorts": {
            "title_limit": 100,
            "description_limit": 5000,
            "tag_limit": 500,
            "supports_tags": True,
        },
        "instagram": {
            "title_limit": 2200,
            "description_limit": 2200,
            "tag_limit": 30,
            "supports_tags": False,
        },
        "instagram_reels": {
            "title_limit": 2200,
            "description_limit": 2200,
            "tag_limit": 30,
            "supports_tags": False,
        },
        "tiktok": {
            "title_limit": 4000,
            "description_limit": 4000,
            "tag_limit": 5,
            "supports_tags": False,
        },
    }

    def __init__(
        self,
        provider: str = "demo",
    ):
        self.provider = str(
            provider or "demo"
        ).strip().lower()

    def generate_metadata(
        self,
        topic: str,
        platform: str,
        command: str,
        research: dict[str, Any] | None = None,
        strategy: dict[str, Any] | None = None,
        hooks: dict[str, Any] | None = None,
        script: dict[str, Any] | None = None,
        thumbnail: dict[str, Any] | None = None,
        captions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate SEO and publishing metadata.
        """

        topic = self._clean_text(topic)
        platform = self._clean_text(
            platform
        ).lower()
        command = self._clean_text(command)

        if not topic:
            raise ValueError(
                "MetadataService requires a topic."
            )

        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(
                f"Unsupported platform: {platform}"
            )

        config = self.PLATFORM_CONFIG[platform]

        research = self._normalize_dict(research)
        strategy = self._normalize_dict(strategy)
        hooks = self._normalize_dict(hooks)
        script = self._normalize_dict(script)
        thumbnail = self._normalize_dict(thumbnail)
        captions = self._normalize_dict(captions)

        context = self._build_context(
            topic=topic,
            command=command,
            research=research,
            strategy=strategy,
            hooks=hooks,
            script=script,
            thumbnail=thumbnail,
            captions=captions,
        )

        titles = self._generate_titles(
            topic=topic,
            context=context,
            limit=config["title_limit"],
        )

        description = self._generate_description(
            topic=topic,
            context=context,
            limit=config["description_limit"],
        )

        keywords = self._generate_keywords(
            topic=topic,
            context=context,
        )

        tags = self._generate_tags(
            keywords=keywords,
            limit=config["tag_limit"],
            supports_tags=config["supports_tags"],
        )

        hashtags = self._generate_hashtags(
            topic=topic,
            keywords=keywords,
            platform=platform,
        )

        audience = self._build_audience_metadata(
            strategy=strategy,
        )

        category = self._determine_category(
            topic=topic,
            strategy=strategy,
        )

        seo_score = self._calculate_seo_score(
            titles=titles,
            description=description,
            keywords=keywords,
            tags=tags,
            hashtags=hashtags,
        )

        recommended_title = (
            titles[0]
            if titles
            else topic
        )

        return {
            "stage": "metadata",
            "status": "completed",
            "execution": "metadata_service",
            "provider": self.provider,
            "metadata_status": "ready",
            "topic": topic,
            "platform": platform,
            "command": command,
            "titles": titles,
            "recommended_title": recommended_title,
            "description": description,
            "keywords": keywords,
            "tags": tags,
            "hashtags": hashtags,
            "category": category,
            "audience": audience,
            "seo": {
                "score": seo_score,
                "search_intent": (
                    "informational"
                ),
                "primary_keyword": (
                    keywords[0]
                    if keywords
                    else topic
                ),
                "keyword_count": len(keywords),
                "tag_count": len(tags),
                "hashtag_count": len(hashtags),
            },
            "platform_config": config,
            "upload_ready": {
                "title": recommended_title,
                "description": description,
                "tags": tags,
                "hashtags": hashtags,
                "category": category,
            },
            "quality_controls": [
                "Topic included in metadata.",
                "Multiple title options generated.",
                "Description generated for search discovery.",
                "Keywords generated from topic context.",
                "Tags generated where supported.",
                "Hashtags generated for platform discovery.",
                "SEO score calculated.",
                "Metadata remains provider-neutral.",
                "No publishing action performed.",
            ],
        }

    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------

    def _build_context(
        self,
        topic: str,
        command: str,
        research: dict[str, Any],
        strategy: dict[str, Any],
        hooks: dict[str, Any],
        script: dict[str, Any],
        thumbnail: dict[str, Any],
        captions: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "topic": topic,
            "command": command,
            "audience": self._extract_text(
                strategy,
                [
                    "target_audience",
                    "audience",
                    "primary_audience",
                ],
            ),
            "angle": self._extract_text(
                strategy,
                [
                    "content_angle",
                    "angle",
                    "strategy",
                ],
            ),
            "hook": self._extract_text(
                hooks,
                [
                    "recommended_hook",
                    "hook",
                    "primary_hook",
                ],
            ),
            "research_summary": self._extract_text(
                research,
                [
                    "summary",
                    "key_insight",
                    "main_insight",
                ],
            ),
            "thumbnail_concept": self._extract_text(
                thumbnail,
                [
                    "recommended_concept",
                    "name",
                ],
            ),
            "script_summary": self._extract_text(
                script,
                [
                    "summary",
                    "script_summary",
                ],
            ),
        }

    # ---------------------------------------------------------
    # Titles
    # ---------------------------------------------------------

    def _generate_titles(
        self,
        topic: str,
        context: dict[str, Any],
        limit: int,
    ) -> list[str]:

        candidates = [
            f"{topic}: What You Need to Know",
            f"The Truth About {topic}",
            f"{topic} Is Changing Everything",
            f"What Happens Next With {topic}?",
            f"{topic}: The Future Explained",
        ]

        titles: list[str] = []

        for title in candidates:
            cleaned = self._clean_text(title)

            if not cleaned:
                continue

            if len(cleaned) > limit:
                cleaned = cleaned[:limit].rstrip()

            if cleaned not in titles:
                titles.append(cleaned)

        return titles

    # ---------------------------------------------------------
    # Description
    # ---------------------------------------------------------

    def _generate_description(
        self,
        topic: str,
        context: dict[str, Any],
        limit: int,
    ) -> str:

        parts = [
            f"Explore {topic} and understand what it means for the future.",
        ]

        hook = context.get("hook")

        if hook:
            parts.append(
                f"This video explores the key question: {hook}"
            )

        angle = context.get("angle")

        if angle:
            parts.append(
                f"Content angle: {angle}."
            )

        audience = context.get("audience")

        if audience:
            parts.append(
                f"Created for: {audience}."
            )

        parts.append(
            f"Watch this video to learn about {topic}, "
            "discover the important ideas, and understand "
            "the bigger picture."
        )

        description = "\n\n".join(parts)

        if len(description) > limit:
            description = description[:limit].rstrip()

        return description

    # ---------------------------------------------------------
    # Keywords
    # ---------------------------------------------------------

    def _generate_keywords(
        self,
        topic: str,
        context: dict[str, Any],
    ) -> list[str]:

        base_keywords = [
            topic,
            f"{topic} explained",
            f"{topic} future",
            f"{topic} trends",
            f"{topic} impact",
        ]

        words = self._topic_words(topic)

        keywords = list(base_keywords)

        for word in words:
            if len(word) >= 3:
                keywords.append(word)

        unique_keywords: list[str] = []

        for keyword in keywords:
            keyword = self._clean_text(keyword)

            if (
                keyword
                and keyword.lower()
                not in {
                    item.lower()
                    for item in unique_keywords
                }
            ):
                unique_keywords.append(keyword)

        return unique_keywords

    # ---------------------------------------------------------
    # Tags
    # ---------------------------------------------------------

    def _generate_tags(
        self,
        keywords: list[str],
        limit: int,
        supports_tags: bool,
    ) -> list[str]:

        if not supports_tags:
            return []

        tags: list[str] = []

        for keyword in keywords:
            tag = self._clean_text(keyword)

            if tag and tag not in tags:
                tags.append(tag)

        if isinstance(limit, int) and limit > 0:
            return tags[: min(len(tags), 25)]

        return tags

    # ---------------------------------------------------------
    # Hashtags
    # ---------------------------------------------------------

    def _generate_hashtags(
        self,
        topic: str,
        keywords: list[str],
        platform: str,
    ) -> list[str]:

        hashtags: list[str] = []

        for keyword in keywords:
            compact = re.sub(
                r"[^A-Za-z0-9]",
                "",
                keyword.title(),
            )

            if not compact:
                continue

            hashtag = f"#{compact}"

            if hashtag not in hashtags:
                hashtags.append(hashtag)

        topic_hashtag = re.sub(
            r"[^A-Za-z0-9]",
            "",
            topic.title(),
        )

        if topic_hashtag:
            hashtag = f"#{topic_hashtag}"

            if hashtag not in hashtags:
                hashtags.insert(0, hashtag)

        max_count = 15

        if platform == "tiktok":
            max_count = 5

        if platform.startswith("instagram"):
            max_count = 15

        return hashtags[:max_count]

    # ---------------------------------------------------------
    # Audience
    # ---------------------------------------------------------

    def _build_audience_metadata(
        self,
        strategy: dict[str, Any],
    ) -> dict[str, Any]:

        audience = self._extract_text(
            strategy,
            [
                "target_audience",
                "audience",
                "primary_audience",
            ],
        )

        return {
            "target_audience": (
                audience
                or "General audience interested in the topic"
            ),
            "content_type": "educational",
            "discovery_goal": "organic_search",
        }

    # ---------------------------------------------------------
    # Category
    # ---------------------------------------------------------

    def _determine_category(
        self,
        topic: str,
        strategy: dict[str, Any],
    ) -> str:

        topic_lower = topic.lower()

        if any(
            word in topic_lower
            for word in [
                "ai",
                "technology",
                "software",
                "computer",
                "robot",
            ]
        ):
            return "Science & Technology"

        if any(
            word in topic_lower
            for word in [
                "business",
                "money",
                "finance",
                "startup",
                "market",
            ]
        ):
            return "Education"

        return "Education"

    # ---------------------------------------------------------
    # SEO Score
    # ---------------------------------------------------------

    def _calculate_seo_score(
        self,
        titles: list[str],
        description: str,
        keywords: list[str],
        tags: list[str],
        hashtags: list[str],
    ) -> float:

        score = 0.0

        if titles:
            score += 20

        if len(description) >= 100:
            score += 25
        elif description:
            score += 15

        if len(keywords) >= 5:
            score += 20
        elif keywords:
            score += 10

        if tags:
            score += 15

        if hashtags:
            score += 10

        return round(
            min(score, 100),
            2,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_dict(
        value: Any,
    ) -> dict[str, Any]:

        if isinstance(value, dict):
            return value

        return {}

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str:

        return " ".join(
            str(value or "").split()
        ).strip()

    def _extract_text(
        self,
        data: dict[str, Any],
        keys: list[str],
    ) -> str:

        for key in keys:
            value = data.get(key)

            if isinstance(value, str):
                text = self._clean_text(value)

                if text:
                    return text

        return ""

    @staticmethod
    def _topic_words(
        topic: str,
    ) -> list[str]:

        return [
            word
            for word in re.findall(
                r"[A-Za-z0-9]+",
                topic.lower(),
            )
            if word
        ]


metadata_service = MetadataService()