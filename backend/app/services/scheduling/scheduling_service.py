from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class SchedulingService:
    """
    Smart content scheduling service.

    Generates a publishing schedule recommendation based on:
    - platform
    - content strategy
    - metadata
    - quality approval
    - workflow readiness

    This service does not publish content.
    """

    DEFAULT_TIMEZONE = "Asia/Kolkata"

    PLATFORM_DEFAULTS = {
        "youtube": {
            "recommended_hours": [17, 18, 19],
            "frequency": "weekly",
        },
        "instagram": {
            "recommended_hours": [11, 18, 20],
            "frequency": "daily",
        },
        "tiktok": {
            "recommended_hours": [12, 18, 21],
            "frequency": "daily",
        },
        "facebook": {
            "recommended_hours": [12, 17, 19],
            "frequency": "weekly",
        },
        "twitter": {
            "recommended_hours": [9, 13, 18],
            "frequency": "daily",
        },
    }

    def __init__(
        self,
        provider: str = "demo",
        timezone: str | None = None,
    ):
        self.provider = str(
            provider or "demo"
        ).strip().lower()

        self.timezone = str(
            timezone or self.DEFAULT_TIMEZONE
        ).strip()

    def create_schedule(
        self,
        topic: str,
        platform: str,
        command: str,
        strategy: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        quality_check: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a recommended publishing schedule.

        Does not publish content or create external platform jobs.
        """

        topic = self._clean_text(topic)

        platform = (
            self._clean_text(platform).lower()
            or "youtube"
        )

        command = self._clean_text(command)

        strategy = self._normalize_dict(strategy)
        metadata = self._normalize_dict(metadata)
        quality_check = self._normalize_dict(
            quality_check
        )

        if not topic:
            raise ValueError(
                "SchedulingService requires a topic."
            )

        quality_payload = self._extract_quality_payload(
            quality_check
        )

        approved = bool(
            quality_payload.get("approved")
        )

        quality_score = self._safe_float(
            quality_payload.get("score")
        )

        if not approved:
            return {
                "stage": "scheduling",
                "status": "blocked",
                "execution": "scheduling_service",
                "provider": self.provider,
                "topic": topic,
                "platform": platform,
                "timezone": self.timezone,
                "scheduled": False,
                "reason": (
                    "Content was not approved by the "
                    "Quality Check stage."
                ),
                "quality_score": quality_score,
                "recommended_publish_at": None,
                "recommended_date": None,
                "recommended_time": None,
                "strategy": None,
            }

        platform_settings = (
            self._get_platform_settings(
                platform
            )
        )

        recommended_hour = (
            self._select_publish_hour(
                platform_settings
            )
        )

        publish_datetime = (
            self._calculate_publish_datetime(
                recommended_hour
            )
        )

        metadata_payload = (
            self._extract_metadata_payload(
                metadata
            )
        )

        strategy_payload = (
            self._extract_strategy_payload(
                strategy
            )
        )

        publishing_frequency = (
            self._determine_frequency(
                platform_settings=platform_settings,
                strategy=strategy_payload,
            )
        )

        title = self._extract_recommended_title(
            metadata_payload
        )

        reason = (
            self._build_schedule_reason(
                platform=platform,
                hour=recommended_hour,
                quality_score=quality_score,
                frequency=publishing_frequency,
            )
        )

        return {
            "stage": "scheduling",
            "status": "ready",
            "execution": "scheduling_service",
            "provider": self.provider,
            "topic": topic,
            "platform": platform,
            "timezone": self.timezone,
            "scheduled": True,
            "quality_score": quality_score,
            "recommended_publish_at": (
                publish_datetime.isoformat()
            ),
            "recommended_date": (
                publish_datetime.date().isoformat()
            ),
            "recommended_time": (
                publish_datetime.strftime("%H:%M")
            ),
            "recommended_hour": recommended_hour,
            "publishing_frequency": (
                publishing_frequency
            ),
            "recommended_title": title,
            "reason": reason,
            "strategy": {
                "platform_defaults": (
                    platform_settings
                ),
                "content_strategy_available": bool(
                    strategy_payload
                ),
                "metadata_available": bool(
                    metadata_payload
                ),
            },
            "schedule_controls": [
                "Quality approval required.",
                "No publishing action performed.",
                "No external platform schedule created.",
                "Recommended time generated.",
                "Timezone included.",
                "Publishing frequency included.",
            ],
        }

    # ---------------------------------------------------------
    # Platform Configuration
    # ---------------------------------------------------------

    def _get_platform_settings(
        self,
        platform: str,
    ) -> dict[str, Any]:

        return self.PLATFORM_DEFAULTS.get(
            platform,
            {
                "recommended_hours": [17, 18, 19],
                "frequency": "weekly",
            },
        )

    # ---------------------------------------------------------
    # Schedule Calculation
    # ---------------------------------------------------------

    @staticmethod
    def _select_publish_hour(
        platform_settings: dict[str, Any],
    ) -> int:

        hours = (
            platform_settings.get(
                "recommended_hours"
            )
            or [18]
        )

        try:
            return int(
                hours[len(hours) // 2]
            )
        except (
            TypeError,
            ValueError,
            IndexError,
        ):
            return 18

    @staticmethod
    def _calculate_publish_datetime(
        recommended_hour: int,
    ) -> datetime:

        now = datetime.now()

        publish_datetime = now.replace(
            hour=recommended_hour,
            minute=0,
            second=0,
            microsecond=0,
        )

        if publish_datetime <= now:
            publish_datetime += timedelta(
                days=1
            )

        return publish_datetime

    # ---------------------------------------------------------
    # Quality
    # ---------------------------------------------------------

    @staticmethod
    def _extract_quality_payload(
        quality_check: dict[str, Any],
    ) -> dict[str, Any]:

        nested = quality_check.get(
            "quality_check"
        )

        if isinstance(nested, dict):
            return nested

        return quality_check

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    @staticmethod
    def _extract_metadata_payload(
        metadata: dict[str, Any],
    ) -> dict[str, Any]:

        nested = metadata.get("metadata")

        if isinstance(nested, dict):
            return nested

        return metadata

    @staticmethod
    def _extract_recommended_title(
        metadata: dict[str, Any],
    ) -> str | None:

        title = metadata.get(
            "recommended_title"
        )

        if title:
            return str(title).strip()

        titles = metadata.get("titles")

        if isinstance(titles, list) and titles:
            first_title = titles[0]

            if isinstance(first_title, str):
                return first_title.strip()

            if isinstance(first_title, dict):
                for key in (
                    "title",
                    "text",
                    "value",
                ):
                    value = first_title.get(key)

                    if value:
                        return str(value).strip()

        return None

    # ---------------------------------------------------------
    # Strategy
    # ---------------------------------------------------------

    @staticmethod
    def _extract_strategy_payload(
        strategy: dict[str, Any],
    ) -> dict[str, Any]:

        nested = strategy.get("strategy")

        if isinstance(nested, dict):
            return nested

        return strategy

    @staticmethod
    def _determine_frequency(
        platform_settings: dict[str, Any],
        strategy: dict[str, Any],
    ) -> str:

        for key in (
            "publishing_frequency",
            "posting_frequency",
            "frequency",
        ):
            value = strategy.get(key)

            if value:
                return str(value).strip().lower()

        return str(
            platform_settings.get(
                "frequency",
                "weekly",
            )
        )

    # ---------------------------------------------------------
    # Reason
    # ---------------------------------------------------------

    @staticmethod
    def _build_schedule_reason(
        platform: str,
        hour: int,
        quality_score: float,
        frequency: str,
    ) -> str:

        return (
            f"Content is approved with a quality score of "
            f"{quality_score}/100. "
            f"The recommended {platform} publishing time is "
            f"{hour:02d}:00 based on the current platform "
            f"scheduling strategy, with a recommended "
            f"{frequency} publishing frequency."
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

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float:

        try:
            return float(value or 0)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0


scheduling_service = SchedulingService()
