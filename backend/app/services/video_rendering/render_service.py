import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset
from app.models.video_timeline import VideoTimeline
from app.services.video_rendering.base import (
    BaseVideoRenderer,
    RenderResult,
)
from app.services.video_rendering.ffmpeg_renderer import (
    FFmpegVideoRenderer,
)


class VideoRenderService:
    """
    High-level N1MOX30 rendering orchestration.

    Responsibilities:

    - load timeline
    - validate timeline
    - select renderer
    - render output
    - register rendered video as MediaAsset
    """

    def __init__(
        self,
        db: Session,
        renderer: BaseVideoRenderer | None = None,
        output_directory: str | Path = "storage/rendered",
    ):
        self.db = db

        self.renderer = (
            renderer
            or FFmpegVideoRenderer()
        )

        self.output_directory = Path(
            output_directory,
        )

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def environment_status(self) -> dict:
        return self.renderer.validate_environment()

    # ================================================================
    # RENDER TIMELINE
    # ================================================================

    def render_timeline(
        self,
        timeline: VideoTimeline,
    ) -> tuple[RenderResult, MediaAsset | None]:

        if timeline.is_locked is False:
            # Rendering is allowed for editable timelines.
            # Locking is reserved for finalized workflow stages.
            pass

        document = self._load_timeline_document(
            timeline,
        )

        validation = self._validate_document(
            document,
        )

        if not validation["valid"]:
            return (
                RenderResult(
                    success=False,
                    provider=self.renderer.provider_name,
                    error_message=(
                        "; ".join(
                            validation["errors"]
                        )
                    ),
                ),
                None,
            )

        output_directory = (
            self.output_directory
            / timeline.user_id
            / timeline.id
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_directory
            / (
                f"render-{uuid4()}.mp4"
            )
        )

        result = self.renderer.render(
            timeline=document,
            output_path=output_path,
        )

        if not result.success:
            return result, None

        asset = self._register_rendered_asset(
            timeline=timeline,
            result=result,
        )

        return result, asset

    # ================================================================
    # LOAD DOCUMENT
    # ================================================================

    @staticmethod
    def _load_timeline_document(
        timeline: VideoTimeline,
    ) -> dict:

        try:
            return json.loads(
                timeline.timeline_json
                or "{}",
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Timeline contains invalid JSON."
            ) from exc

    # ================================================================
    # VALIDATION
    # ================================================================

    @staticmethod
    def _validate_document(
        document: dict,
    ) -> dict:

        errors: list[str] = []

        if not document:
            errors.append(
                "Timeline document is empty."
            )

        if document.get(
            "width",
            0,
        ) <= 0:

            errors.append(
                "Timeline width is invalid."
            )

        if document.get(
            "height",
            0,
        ) <= 0:

            errors.append(
                "Timeline height is invalid."
            )

        if document.get(
            "fps",
            0,
        ) <= 0:

            errors.append(
                "Timeline FPS is invalid."
            )

        if document.get(
            "duration_seconds",
            0,
        ) < 0:

            errors.append(
                "Timeline duration is invalid."
            )

        return {
            "valid": not errors,
            "errors": errors,
        }

    # ================================================================
    # REGISTER MEDIA ASSET
    # ================================================================

    def _register_rendered_asset(
        self,
        timeline: VideoTimeline,
        result: RenderResult,
    ) -> MediaAsset:

        output_path = Path(
            result.output_path,
        )

        asset = MediaAsset(
            user_id=timeline.user_id,
            project_id=None,
            content_id=timeline.content_id,
            asset_type="video",
            media_type="video/mp4",
            name=(
                f"{timeline.name} Render"
            ),
            description=(
                "Rendered video generated "
                "from N1MOX30 video timeline."
            ),
            original_filename=output_path.name,
            storage_provider="local",
            storage_path=str(
                output_path,
            ),
            public_url=None,
            provider_asset_id=None,
            mime_type="video/mp4",
            file_extension=".mp4",
            file_size_bytes=result.file_size_bytes,
            width=result.width,
            height=result.height,
            duration_seconds=result.duration_seconds,
            frame_rate=result.fps,
            scene_number=None,
            asset_role="rendered_video",
            status="completed",
            retry_count=0,
            max_retries=3,
            error_message=None,
            metadata_json=json.dumps(
                {
                    "renderer": result.provider,
                    "timeline_id": timeline.id,
                    "timeline_version": timeline.version,
                    "render_metadata": result.metadata,
                }
            ),
        )

        self.db.add(
            asset,
        )

        self.db.commit()

        self.db.refresh(
            asset,
        )

        return asset