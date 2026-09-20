from __future__ import annotations

import os
from datetime import datetime
from typing import Any


class PublishingService:
    """
    Final content publishing service.

    This service validates workflow readiness and prepares content
    for publishing.

    Current providers:
    - demo: Safe simulation only.
    - youtube: Ready for real upload integration.

    A publishing result never claims a successful upload unless a
    real provider upload response confirms it.
    """

    def __init__(
        self,
        provider: str = "demo",
    ):
        self.provider = (
            provider
            .strip()
            .lower()
        )

    def publish_content(
        self,
        *,
        workflow_id: str,
        user_id: str,
        topic: str,
        platform: str,
        metadata: dict[str, Any],
        quality_check: dict[str, Any],
        scheduling: dict[str, Any],
        video: dict[str, Any],
        thumbnail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate publishing readiness and execute the configured
        publishing provider.

        This method intentionally does not report a successful upload
        unless an actual provider confirms the upload.
        """

        normalized_platform = (
            platform
            .strip()
            .lower()
        )

        quality = self._unwrap_stage_data(
            quality_check,
            "quality",
        )

        schedule = self._unwrap_stage_data(
            scheduling,
            "scheduling",
        )

        metadata_data = self._unwrap_stage_data(
            metadata,
            "metadata",
        )

        video_data = self._unwrap_stage_data(
            video,
            "video",
        )

        thumbnail_data = self._unwrap_stage_data(
            thumbnail or {},
            "thumbnail",
        )

        readiness = self._validate_readiness(
            topic=topic,
            platform=normalized_platform,
            metadata=metadata_data,
            quality=quality,
            schedule=schedule,
            video=video_data,
        )

        result = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "topic": topic,
            "platform": normalized_platform,
            "provider": self.provider,
            "status": readiness["status"],
            "ready_to_publish": readiness[
                "ready_to_publish"
            ],
            "published": False,
            "uploaded": False,
            "publish_attempted": False,
            "publish_mode": self.provider,
            "created_at": (
                datetime.utcnow()
                .isoformat()
                + "Z"
            ),
            "content": {
                "title": self._get_title(
                    metadata_data
                ),
                "description": self._get_description(
                    metadata_data
                ),
                "keywords": self._get_keywords(
                    metadata_data
                ),
                "thumbnail_available": bool(
                    thumbnail_data
                ),
                "video_file_path": (
                    readiness.get(
                        "video_file_path"
                    )
                ),
            },
            "schedule": {
                "scheduled": bool(
                    schedule.get("scheduled")
                ),
                "recommended_date": (
                    schedule.get(
                        "recommended_date"
                    )
                ),
                "recommended_time": (
                    schedule.get(
                        "recommended_time"
                    )
                ),
                "timezone": schedule.get(
                    "timezone"
                ),
            },
            "quality": {
                "approved": bool(
                    quality.get("approved")
                ),
                "score": quality.get(
                    "score"
                ),
            },
            "readiness": readiness,
        }

        if not readiness["ready_to_publish"]:
            result["status"] = "blocked"
            result["message"] = (
                "Publishing was not attempted because "
                "the content is not ready."
            )

            return result

        if self.provider == "demo":
            return self._publish_demo(
                result=result,
            )

        if self.provider == "youtube":
            return self._publish_youtube(
                result=result,
            )

        raise ValueError(
            f"Unsupported publishing provider: "
            f"{self.provider}"
        )

    def _validate_readiness(
        self,
        *,
        topic: str,
        platform: str,
        metadata: dict[str, Any],
        quality: dict[str, Any],
        schedule: dict[str, Any],
        video: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate whether content is safe and ready for publishing.
        """

        blockers: list[str] = []
        warnings: list[str] = []

        if not topic:
            blockers.append(
                "Workflow topic is missing."
            )

        if not platform:
            blockers.append(
                "Publishing platform is missing."
            )

        quality_approved = bool(
            quality.get("approved")
        )

        if not quality_approved:
            blockers.append(
                "Quality Check has not approved "
                "this content."
            )

        if not bool(
            schedule.get("scheduled")
        ):
            blockers.append(
                "Scheduling stage did not mark "
                "the content as scheduled."
            )

        title = self._get_title(
            metadata
        )

        if not title:
            blockers.append(
                "Publishing metadata does not "
                "contain a title."
            )

        video_file_path = (
            self._find_video_file_path(
                video
            )
        )

        video_file_exists = bool(
            video_file_path
            and os.path.isfile(
                video_file_path
            )
        )

        if not video_file_path:
            warnings.append(
                "No real video file path is available."
            )

        elif not video_file_exists:
            warnings.append(
                "Video file path exists in workflow "
                "data but the file is not available "
                "on disk."
            )

        return {
            "status": (
                "ready"
                if not blockers
                else "blocked"
            ),
            "ready_to_publish": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "video_file_path": video_file_path,
            "video_file_exists": (
                video_file_exists
            ),
            "real_video_available": (
                video_file_exists
            ),
        }

    def _publish_demo(
        self,
        *,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Safe demo publishing.

        Never claims that content was uploaded.
        """

        real_video_available = bool(
            result["readiness"].get(
                "real_video_available"
            )
        )

        result["publish_attempted"] = False
        result["published"] = False
        result["uploaded"] = False

        if real_video_available:

            result["status"] = (
                "ready_for_provider"
            )

            result["message"] = (
                "Publishing validation completed. "
                "A real video file is available, but "
                "demo mode does not upload content."
            )

        else:

            result["status"] = (
                "waiting_for_video"
            )

            result["message"] = (
                "Publishing validation completed, "
                "but content was not uploaded because "
                "no real rendered video file is "
                "available."
            )

        result["next_action"] = (
            "Connect a real video renderer and "
            "configure a publishing provider."
        )

        return result

    def _publish_youtube(
        self,
        *,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Placeholder for the YouTube publishing adapter.

        Real uploads will only be implemented after:
        1. A real rendered video file exists.
        2. The user's connected account is available.
        3. A valid access token is available.
        4. YouTube upload API integration is enabled.
        """

        real_video_available = bool(
            result["readiness"].get(
                "real_video_available"
            )
        )

        if not real_video_available:

            result["status"] = (
                "waiting_for_video"
            )

            result["message"] = (
                "YouTube publishing was not attempted "
                "because no real video file is available."
            )

            result["next_action"] = (
                "Generate a real video file before "
                "attempting YouTube upload."
            )

            return result

        result["status"] = (
            "provider_not_implemented"
        )

        result["message"] = (
            "A real video file is available, but the "
            "YouTube upload adapter has not been "
            "enabled yet."
        )

        result["next_action"] = (
            "Enable the YouTube upload adapter."
        )

        return result

    @staticmethod
    def _unwrap_stage_data(
        data: Any,
        key: str,
    ) -> dict[str, Any]:
        """
        Extract nested service data from workflow output.
        """

        if not isinstance(
            data,
            dict,
        ):
            return {}

        nested = data.get(key)

        if isinstance(
            nested,
            dict,
        ):
            return nested

        return data

    @staticmethod
    def _get_title(
        metadata: dict[str, Any],
    ) -> str:
        """
        Extract the recommended publishing title.
        """

        return str(
            metadata.get(
                "recommended_title"
            )
            or metadata.get(
                "title"
            )
            or ""
        ).strip()

    @staticmethod
    def _get_description(
        metadata: dict[str, Any],
    ) -> str:
        """
        Extract the publishing description.
        """

        return str(
            metadata.get(
                "description"
            )
            or metadata.get(
                "recommended_description"
            )
            or ""
        ).strip()

    @staticmethod
    def _get_keywords(
        metadata: dict[str, Any],
    ) -> list[str]:
        """
        Extract keywords safely.
        """

        keywords = (
            metadata.get("keywords")
            or metadata.get(
                "recommended_keywords"
            )
            or []
        )

        if not isinstance(
            keywords,
            list,
        ):
            return []

        return [
            str(keyword).strip()
            for keyword in keywords
            if str(keyword).strip()
        ]

    @staticmethod
    def _find_video_file_path(
        video: dict[str, Any],
    ) -> str | None:
        """
        Search common video output structures for
        a real video file path.
        """

        candidates = [
            video.get("file_path"),
            video.get("video_file_path"),
            video.get("output_file"),
            video.get("render_file_path"),
        ]

        render_output = (
            video.get("render_output")
        )

        if isinstance(
            render_output,
            dict,
        ):
            candidates.extend(
                [
                    render_output.get(
                        "file_path"
                    ),
                    render_output.get(
                        "video_file_path"
                    ),
                ]
            )

        render = video.get("render")

        if isinstance(
            render,
            dict,
        ):
            candidates.extend(
                [
                    render.get(
                        "file_path"
                    ),
                    render.get(
                        "video_file_path"
                    ),
                ]
            )

        for candidate in candidates:

            if not candidate:
                continue

            value = str(
                candidate
            ).strip()

            if value:
                return value

        return None


publishing_service = PublishingService()