from __future__ import annotations

from typing import Any


class QualityService:
    """
    Provider-neutral quality assurance service.

    Validates completed workflow outputs and produces a structured
    readiness report. This service does not publish content and does
    not modify previous workflow outputs.
    """

    REQUIRED_STAGES = [
        "research",
        "strategy",
        "hooks",
        "script",
        "voice",
        "visuals",
        "video",
        "captions",
        "thumbnail",
        "metadata",
    ]

    def __init__(
        self,
        provider: str = "demo",
    ):
        self.provider = str(
            provider or "demo"
        ).strip().lower()

    def run_quality_check(
        self,
        topic: str,
        platform: str,
        command: str,
        outputs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate workflow outputs and generate a final readiness report.
        """

        topic = self._clean_text(topic)
        platform = self._clean_text(platform).lower()
        command = self._clean_text(command)
        outputs = self._normalize_dict(outputs)

        if not topic:
            raise ValueError(
                "QualityService requires a topic."
            )

        if not outputs:
            raise ValueError(
                "QualityService requires workflow outputs."
            )

        stage_results = self._validate_stages(
            outputs=outputs,
        )

        warnings = self._build_warnings(
            outputs=outputs,
            stage_results=stage_results,
        )

        errors = self._build_errors(
            stage_results=stage_results,
        )

        checks = self._run_content_checks(
            outputs=outputs,
        )

        score = self._calculate_quality_score(
            stage_results=stage_results,
            warnings=warnings,
            errors=errors,
            checks=checks,
        )

        approved = (
            not errors
            and score >= 70
        )

        status = (
            "approved"
            if approved
            else "needs_review"
        )

        recommendations = (
            self._build_recommendations(
                warnings=warnings,
                errors=errors,
                checks=checks,
                score=score,
            )
        )

        return {
            "stage": "quality_check",
            "status": "completed",
            "execution": "quality_service",
            "provider": self.provider,
            "quality_status": status,
            "approved": approved,
            "score": score,
            "topic": topic,
            "platform": platform,
            "command": command,
            "stage_results": stage_results,
            "checks": checks,
            "warnings": warnings,
            "errors": errors,
            "recommendations": recommendations,
            "summary": self._build_summary(
                score=score,
                approved=approved,
                warnings=warnings,
                errors=errors,
            ),
            "quality_controls": [
                "Required workflow stages validated.",
                "Missing outputs detected.",
                "Metadata readiness checked.",
                "Caption readiness checked.",
                "Video readiness checked.",
                "Thumbnail readiness checked.",
                "Overall quality score calculated.",
                "Approval decision generated.",
                "No publishing action performed.",
            ],
        }

    # ---------------------------------------------------------
    # Stage Validation
    # ---------------------------------------------------------

    def _validate_stages(
        self,
        outputs: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:

        results: dict[str, dict[str, Any]] = {}

        for stage in self.REQUIRED_STAGES:
            value = outputs.get(stage)

            valid = self._has_usable_output(
                value
            )

            results[stage] = {
                "present": value is not None,
                "valid": valid,
                "status": (
                    "passed"
                    if valid
                    else "failed"
                ),
            }

        return results

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------

    def _build_warnings(
        self,
        outputs: dict[str, Any],
        stage_results: dict[str, dict[str, Any]],
    ) -> list[str]:

        warnings: list[str] = []

        metadata = self._normalize_dict(
            outputs.get("metadata")
        )

        metadata_payload = self._normalize_dict(
            metadata.get("metadata")
            if metadata
            else {}
        )

        seo = self._normalize_dict(
            metadata_payload.get("seo")
        )

        seo_score = self._safe_float(
            seo.get("score")
        )

        if seo_score and seo_score < 70:
            warnings.append(
                "SEO score is below the recommended threshold."
            )

        video = self._normalize_dict(
            outputs.get("video")
        )

        video_payload = self._normalize_dict(
            video.get("video")
            if video
            else {}
        )

        render_output = self._normalize_dict(
            video_payload.get("render_output")
        )

        render_status = self._clean_text(
            render_output.get("status")
        ).lower()

        if (
            render_status
            and render_status != "completed"
        ):
            warnings.append(
                "Video render output is not completed."
            )

        captions = self._normalize_dict(
            outputs.get("captions")
        )

        if captions:
            caption_payload = self._normalize_dict(
                captions.get("captions")
            )

            if not caption_payload:
                warnings.append(
                    "Caption payload is empty."
                )

        thumbnail = self._normalize_dict(
            outputs.get("thumbnail")
        )

        if thumbnail:
            thumbnail_payload = self._normalize_dict(
                thumbnail.get("thumbnail")
            )

            if not thumbnail_payload:
                warnings.append(
                    "Thumbnail payload is empty."
                )

        return warnings

    # ---------------------------------------------------------
    # Errors
    # ---------------------------------------------------------

    def _build_errors(
        self,
        stage_results: dict[str, dict[str, Any]],
    ) -> list[str]:

        errors: list[str] = []

        for stage, result in stage_results.items():
            if not result.get("valid"):
                errors.append(
                    f"Required stage '{stage}' "
                    "does not have usable output."
                )

        return errors

    # ---------------------------------------------------------
    # Content Checks
    # ---------------------------------------------------------

    def _run_content_checks(
        self,
        outputs: dict[str, Any],
    ) -> dict[str, Any]:

        metadata = self._normalize_dict(
            outputs.get("metadata")
        )

        metadata_payload = self._normalize_dict(
            metadata.get("metadata")
        )

        titles = (
            metadata_payload.get("titles")
            or []
        )

        keywords = (
            metadata_payload.get("keywords")
            or []
        )

        description = self._clean_text(
            metadata_payload.get("description")
        )

        seo = self._normalize_dict(
            metadata_payload.get("seo")
        )

        video = self._normalize_dict(
            outputs.get("video")
        )

        video_payload = self._normalize_dict(
            video.get("video")
        )

        captions = self._normalize_dict(
            outputs.get("captions")
        )

        captions_payload = self._normalize_dict(
            captions.get("captions")
        )

        thumbnail = self._normalize_dict(
            outputs.get("thumbnail")
        )

        thumbnail_payload = self._normalize_dict(
            thumbnail.get("thumbnail")
        )

        return {
            "title_options": {
                "passed": len(titles) > 0,
                "count": len(titles),
            },
            "description": {
                "passed": len(description) >= 30,
                "length": len(description),
            },
            "keywords": {
                "passed": len(keywords) >= 3,
                "count": len(keywords),
            },
            "seo_score": {
                "passed": self._safe_float(
                    seo.get("score")
                ) >= 70,
                "score": self._safe_float(
                    seo.get("score")
                ),
            },
            "video_payload": {
                "passed": bool(video_payload),
            },
            "captions_payload": {
                "passed": bool(captions_payload),
            },
            "thumbnail_payload": {
                "passed": bool(thumbnail_payload),
            },
        }

    # ---------------------------------------------------------
    # Score
    # ---------------------------------------------------------

    def _calculate_quality_score(
        self,
        stage_results: dict[str, dict[str, Any]],
        warnings: list[str],
        errors: list[str],
        checks: dict[str, Any],
    ) -> float:

        total_stages = len(stage_results)

        passed_stages = sum(
            1
            for result in stage_results.values()
            if result.get("valid")
        )

        stage_score = (
            (passed_stages / total_stages) * 60
            if total_stages
            else 0
        )

        check_values = [
            value
            for value in checks.values()
            if isinstance(value, dict)
        ]

        passed_checks = sum(
            1
            for value in check_values
            if value.get("passed")
        )

        check_score = (
            (passed_checks / len(check_values)) * 40
            if check_values
            else 0
        )

        score = stage_score + check_score

        score -= len(warnings) * 3
        score -= len(errors) * 10

        return round(
            max(0, min(score, 100)),
            2,
        )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    def _build_recommendations(
        self,
        warnings: list[str],
        errors: list[str],
        checks: dict[str, Any],
        score: float,
    ) -> list[str]:

        recommendations: list[str] = []

        if errors:
            recommendations.append(
                "Resolve all required stage errors before publishing."
            )

        if warnings:
            recommendations.append(
                "Review workflow warnings before final publishing."
            )

        seo_check = self._normalize_dict(
            checks.get("seo_score")
        )

        if not seo_check.get("passed"):
            recommendations.append(
                "Improve metadata keywords, title, and description for SEO."
            )

        if score < 90:
            recommendations.append(
                "Review content outputs and improve weak areas before publishing."
            )

        if not recommendations:
            recommendations.append(
                "Content passed automated quality checks and is ready for the next workflow stage."
            )

        return recommendations

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    @staticmethod
    def _build_summary(
        score: float,
        approved: bool,
        warnings: list[str],
        errors: list[str],
    ) -> str:

        if approved:
            return (
                f"Quality check approved with a score of "
                f"{score}/100."
            )

        if errors:
            return (
                f"Quality check found {len(errors)} required "
                f"issue(s) with a score of {score}/100."
            )

        return (
            f"Quality check requires review with a score of "
            f"{score}/100 and {len(warnings)} warning(s)."
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
    def _has_usable_output(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, dict):
            return bool(value)

        if isinstance(value, list):
            return bool(value)

        return True

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


quality_service = QualityService()