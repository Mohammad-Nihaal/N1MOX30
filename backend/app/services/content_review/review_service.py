from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.schemas.content_review import (
    ContentReviewRequest,
    ContentReviewResponse,
    ReviewIssue,
)


class ContentReviewService:
    """
    Final quality gate for N1MOX30 content.

    Provider-neutral quality review layer.
    """

    def review(
        self,
        request: ContentReviewRequest,
    ) -> ContentReviewResponse:
        issues: list[ReviewIssue] = []
        strengths: list[str] = []
        checks: dict[str, bool] = {}
        recommendations: list[str] = []

        self._check_content(
            request,
            issues,
            strengths,
            checks,
        )

        self._check_video(
            request,
            issues,
            strengths,
            checks,
        )

        self._check_timeline(
            request,
            issues,
            strengths,
            checks,
        )

        self._check_subtitles(
            request,
            issues,
            strengths,
            checks,
        )

        self._check_thumbnail(
            request,
            issues,
            strengths,
            checks,
        )

        self._check_metadata(
            request,
            issues,
            strengths,
            checks,
        )

        score = self._calculate_score(
            checks,
            issues,
        )

        blocking = any(
            issue.severity == "critical"
            for issue in issues
        )

        required_checks = (
            "content_complete",
            "video_available",
            "timeline_valid",
            "metadata_complete",
        )

        ready = (
            score >= 75
            and not blocking
            and all(
                checks.get(check, False)
                for check in required_checks
            )
        )

        quality_level = self._quality_level(score)

        if ready:
            summary = (
                "Content passed the final N1MOX30 quality gate "
                "and is ready for the next publishing workflow."
            )
        elif blocking:
            summary = (
                "Content requires correction before it can "
                "pass the final quality gate."
            )
        else:
            summary = (
                "Content is usable but should be improved "
                "before publishing."
            )

        return ContentReviewResponse(
            ready=ready,
            overall_score=score,
            quality_level=quality_level,
            issues=issues,
            strengths=strengths,
            checks=checks,
            recommendations=self._build_recommendations(issues),
            summary=summary,
            reviewed_at=datetime.now(
                timezone.utc,
            ).isoformat(),
        )

    def _check_content(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        title_ok = bool(
            request.title.strip()
        )

        script_ok = len(
            request.script.strip()
        ) >= 20

        content_complete = (
            title_ok
            and script_ok
        )

        checks["title_present"] = title_ok
        checks["script_present"] = script_ok
        checks["content_complete"] = content_complete

        if not title_ok:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="content",
                    field="title",
                    message="A title is missing.",
                    recommendation=(
                        "Generate or provide a final title."
                    ),
                )
            )

        if not script_ok:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="content",
                    field="script",
                    message=(
                        "The script is missing or too short."
                    ),
                    recommendation=(
                        "Generate a complete final script."
                    ),
                )
            )

        if content_complete:
            strengths.append(
                "Core content contains a title and usable script."
            )

    def _check_video(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        video_available = False

        if request.video_path:
            try:
                video_available = Path(
                    request.video_path
                ).is_file()
            except OSError:
                video_available = False

        checks["video_available"] = video_available

        if request.video_path and not video_available:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="video",
                    field="video_path",
                    message=(
                        "The final video path does not "
                        "point to an available file."
                    ),
                    recommendation=(
                        "Render the final video again."
                    ),
                )
            )
        elif video_available:
            strengths.append(
                "A final rendered video file is available."
            )
        else:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="video",
                    field="video_path",
                    message=(
                        "No final video file was supplied."
                    ),
                    recommendation=(
                        "Render the final video before publishing."
                    ),
                )
            )

    def _check_timeline(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        timeline = request.timeline or {}

        clips = timeline.get(
            "clips",
            [],
        )

        duration = timeline.get(
            "duration_seconds",
            request.duration_seconds,
        )

        clips_ok = (
            isinstance(clips, list)
            and len(clips) > 0
        )

        try:
            duration_ok = float(duration) > 0
        except (
            TypeError,
            ValueError,
        ):
            duration_ok = False

        timeline_valid = (
            clips_ok
            and duration_ok
        )

        checks["timeline_has_clips"] = clips_ok
        checks["timeline_duration_valid"] = duration_ok
        checks["timeline_valid"] = timeline_valid

        if not clips_ok:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="timeline",
                    message=(
                        "The video timeline contains "
                        "no usable clips."
                    ),
                    recommendation=(
                        "Build or repair the final timeline."
                    ),
                )
            )

        if not duration_ok:
            issues.append(
                ReviewIssue(
                    severity="critical",
                    category="timeline",
                    field="duration_seconds",
                    message=(
                        "The timeline has no valid duration."
                    ),
                    recommendation=(
                        "Set a positive final duration."
                    ),
                )
            )

        if timeline_valid:
            strengths.append(
                "The timeline contains clips and a valid duration."
            )

    def _check_subtitles(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        subtitles_present = len(
            request.subtitles or []
        ) > 0

        checks["subtitles_present"] = subtitles_present

        if subtitles_present:
            strengths.append(
                "Subtitle segments are available."
            )
        else:
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="subtitles",
                    message=(
                        "No subtitle segments were supplied."
                    ),
                    recommendation=(
                        "Generate subtitles before publishing."
                    ),
                )
            )

    def _check_thumbnail(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        thumbnail = request.thumbnail or {}

        thumbnail_path = thumbnail.get(
            "image_path"
        )

        thumbnail_available = False

        if thumbnail_path:
            try:
                thumbnail_available = Path(
                    str(thumbnail_path)
                ).is_file()
            except OSError:
                thumbnail_available = False

        score = thumbnail.get(
            "overall_score"
        )

        score_ok = False

        try:
            score_ok = float(score) >= 60
        except (
            TypeError,
            ValueError,
        ):
            score_ok = False

        thumbnail_valid = (
            thumbnail_available
            or score_ok
        )

        checks["thumbnail_available"] = thumbnail_available
        checks["thumbnail_score_valid"] = score_ok
        checks["thumbnail_valid"] = thumbnail_valid

        if thumbnail_available:
            strengths.append(
                "A rendered thumbnail is available."
            )

        if not thumbnail_valid:
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="thumbnail",
                    message=(
                        "A verified thumbnail was not supplied."
                    ),
                    recommendation=(
                        "Render and select a final thumbnail."
                    ),
                )
            )

    def _check_metadata(
        self,
        request: ContentReviewRequest,
        issues: list[ReviewIssue],
        strengths: list[str],
        checks: dict[str, bool],
    ) -> None:
        description_ok = len(
            request.description.strip()
        ) >= 10

        hashtags_ok = len(
            request.hashtags
        ) > 0

        metadata = request.metadata or {}

        metadata_title = bool(
            metadata.get("title")
            or request.title.strip()
        )

        metadata_complete = (
            metadata_title
            and description_ok
            and hashtags_ok
        )

        checks["description_present"] = description_ok
        checks["hashtags_present"] = hashtags_ok
        checks["metadata_complete"] = metadata_complete

        if not description_ok:
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="metadata",
                    field="description",
                    message=(
                        "The description is missing or too short."
                    ),
                    recommendation=(
                        "Generate a platform-ready description."
                    ),
                )
            )

        if not hashtags_ok:
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="metadata",
                    field="hashtags",
                    message="No hashtags were supplied.",
                    recommendation=(
                        "Generate relevant hashtags."
                    ),
                )
            )

        if metadata_complete:
            strengths.append(
                "Core publishing metadata is present."
            )

    def _calculate_score(
        self,
        checks: dict[str, bool],
        issues: list[ReviewIssue],
    ) -> float:
        weights = {
            "content_complete": 25,
            "video_available": 20,
            "timeline_valid": 20,
            "subtitles_present": 10,
            "thumbnail_valid": 10,
            "metadata_complete": 15,
        }

        total_weight = sum(
            weights.values()
        )

        earned = sum(
            weight
            for check, weight in weights.items()
            if checks.get(check, False)
        )

        score = (
            earned / total_weight
        ) * 100

        for issue in issues:
            if issue.severity == "critical":
                score -= 15
            elif issue.severity == "warning":
                score -= 3

        return round(
            max(
                0.0,
                min(
                    100.0,
                    score,
                ),
            ),
            2,
        )

    def _quality_level(
        self,
        score: float,
    ) -> str:
        if score >= 90:
            return "excellent"

        if score >= 75:
            return "good"

        if score >= 60:
            return "needs_improvement"

        return "not_ready"

    def _build_recommendations(
        self,
        issues: list[ReviewIssue],
    ) -> list[str]:
        recommendations: list[str] = []

        for issue in issues:
            if issue.recommendation:
                recommendations.append(
                    issue.recommendation
                )

        return list(
            dict.fromkeys(
                recommendations
            )
        )


content_review_service = ContentReviewService()
